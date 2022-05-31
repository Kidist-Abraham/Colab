import os
from flask import Flask, render_template, redirect, request, flash, session
from models import db, connect_db, User, Project, Collaboration, ProjectStack, UserPreferenceSector, UserPreferenceStack, Sector, Stack
from forms import RegisterUserForm, LoginUserForm, AddProjectForm, SectorPreferenceForm, StackPreferenceForm, PreferenceForm, UserProfileForm, PreferenceFormOwnProject
from git import get_stacks, get_collaborators, validate_git_handle_ownership, validate_repo_existence
from schedule import start_scheduler, connect_scheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '<fsa64ghfa78hjfa>')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql:///colab')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

# Connect and start the scheduler
connect_scheduler(app)
start_scheduler()



def check_user_session():
    ''' A function that checks if the username exists in the session and if the username also exists in the database '''
    return True if "username" in session and User.query.filter_by(username=session["username"]).first() else False
        

@app.route("/")
def main_page():
    ''' The main route for that shows the home page  '''
    if check_user_session():
        user = User.query.filter_by(username=session["username"]).first()
        return render_template("home.html", user= user)
    else:
        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    ''' A function for registering a user'''
    form = RegisterUserForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data
        git_handle = form.git_handle.data
        is_organisation = form.is_organisation.data

        # validate if the git account exists and if the account is owned by the email provided by the user
        if validate_git_handle_ownership(git_handle,email,is_organisation):
            new_user = User.register(username=username, email=email, first_name=first_name,last_name=last_name, password=password, git_handle = git_handle, is_organisation = is_organisation)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = new_user.username
            flash(f"Welcome {first_name}")
            return redirect("/")
        else: 
            form.git_handle.errors.append("Your github account doesn't exist publicly or it is not owned by the email you provided.")
            return render_template(
            "add_user_form.html", form=form)

    else:
        return render_template(
            "add_user_form.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    ''' Function to Login the user '''
    form = LoginUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username = username, password=password)

        if user:
            session["username"] = user.username
            return redirect(f"/")

        else:
            form.username.errors = ["Incorrect username or password"]

    return render_template("login_form.html", form=form)


@app.route("/logout", methods=["POST"])
def logout():
    ''' Function to Logout the user '''
    session.pop("username")

    return redirect("/")

@app.route("/profile")
def show_profile():
    '''  A function that redirects to user's detail page '''
    if check_user_session():

        return redirect(f"/users/{session['username']}")
    else:
        return redirect("/")


@app.route("/users/<username>")
def user_detail(username):
    ''' Shows user profile. It shows details like collaborations and owned projects '''
    if check_user_session():
        user = User.query.filter_by(username=username).first()
        projects = user.owned_projects
        collaborations = user.collaborations
        is_self = True if user.username == session["username"] else False
        return render_template("user.html", user = user, collaborations = collaborations, projects=projects, is_self = is_self)
    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    ''' Function to Delete the user '''
    if check_user_session() and session["username"] == username:
        user = User.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()
        session.pop("username")
        return redirect("/")

    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")

@app.route('/users/<username>/edit', methods=["GET", "POST"])
def profile(username):
    """Update profile for current user."""
    if check_user_session() and session["username"] == username:
        user = User.query.filter_by(username=username).first()
        form = UserProfileForm(obj = user)

        if form.validate_on_submit():
            user.username = form.username.data
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            db.session.add(user)
            db.session.commit()
            flash(f"Profile updated")
            return redirect(f"/user/{user.username}")

        else:
            return render_template(
                "edit_user_form.html", form=form)
    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")

@app.route("/users/<username>/projects/add", methods=["GET", "POST"])
def add_project(username):
    ''' Add new Project '''
    if check_user_session():

        user = User.query.filter_by(username= username).first()
        form = AddProjectForm()
        sectors = [(sec.id, sec.name) for sec in Sector.query.all()]
        form.sector.choices =  sectors


        if form.validate_on_submit():
            title = form.title.data
            git_repo = form.git_repo.data
            description = form.description.data
            sector_id = form.sector.data

            
            # Check if the repository exists and is public

            if not validate_repo_existence(git_repo):
                form.git_repo.errors.append("The repository is private or doesn't exit")
                return render_template(
                "add_project_form.html", form=form)

            # Check if the repository is owned by the user
            if not git_repo.startswith(user.git_handle):
                form.git_repo.errors.append("You can only add a repository that is owned by you")
                return render_template(
                "add_project_form.html", form=form)
            
            
            # Create the project

            new_project = Project(title=title, git_repo=git_repo, description=description, owned_by=session["username"], sector_id=sector_id)
            db.session.add(new_project)
            db.session.commit()

            # Add Current stacks in project
            stacks =  get_stacks(git_repo)
            stacks_in_db = Stack.query.filter(Stack.name.in_(stacks)).all()
            new_project.stacks.extend(stacks_in_db)

            # Add current collaborators in project
            collabs =  get_collaborators(git_repo)
            collabs_in_db = User.query.filter(User.git_handle.in_(collabs)).all()
            new_project.collaborators.extend(collabs_in_db)

            db.session.commit()
            flash(f"You created new project")
            return redirect(f"/projects/{new_project.id}")

        else:
            return render_template(
                "add_project_form.html", form=form)
    
    else:

        return redirect("/")



@app.route("/projects/<project_id>")
def show_project(project_id):
    ''' Show project details '''
    if check_user_session():
        project = Project.query.get_or_404(project_id)
        user = User.query.filter_by(username=session["username"]).first()
        selfProject = True if user.username == project.owned_by else False
        return render_template("project.html", project = project , selfProject=selfProject)
    else:
        return redirect("/")

@app.route("/projects", methods=["GET", "POST"])
def show_projects():
    ''' Show registered projects. It also provide filtering with sector and stack or an option to see projects that are marked Preferred'''
    if check_user_session():
        
        form = PreferenceForm()

        # Get all the sectors and stacks and add them to the choices for mutiple field form inputs. 
        sectors = [(sec.id, sec.name) for sec in Sector.query.all()]
        stacks = [(sta.id, sta.name) for sta in Stack.query.all()]
        form.sectors.choices =  sectors
        form.stacks.choices = stacks


        if form.validate_on_submit():
            _sectors = form.sectors.data
            _stacks = form.stacks.data
            preferred_only = form.show_preferences_only.data

            # If sector or stack filter is passed, filter projects by the stacks/sectors. And filter by preference depending on the preferred_only input.
            if len(_sectors) > 0 or len(_stacks) > 0:
                # Creates a query that filters the project with stacks and sectors selected by the user and not owned by the user.
                query = (db.session.query(Project, ProjectStack, Stack, Sector, UserPreferenceSector, UserPreferenceStack)
                .outerjoin(ProjectStack, Project.id == ProjectStack.project_id)
                .outerjoin(Stack, ProjectStack.stack_id == Stack.id)
                .outerjoin(Sector, Project.sector_id == Sector.id)
                .outerjoin(UserPreferenceSector, (Project.sector_id == UserPreferenceSector.sector_id))
                .outerjoin(UserPreferenceStack , (ProjectStack.stack_id == UserPreferenceStack.stack_id))
                .filter((Project.owned_by != session["username"]) & ((Stack.id.in_(_stacks)) | (Sector.id.in_(_sectors)))))

                # If preferred_only is true, filter out the query that have stack and sectors preferred by the user. 
                # If preferred_only is false, don't filter the query further.  

                if preferred_only:
                    query = query.filter(  ((UserPreferenceStack.username == session["username"]) | (UserPreferenceSector.username == session["username"] )) ).all()
                else:
                    query = query.all()
                
                # Select the projects from the query, and use set to get unique projects.
                filtered_projects = [q[0] for q in query]
                filtered_projects = list(set(filtered_projects))
                return render_template("projects.html", projects = filtered_projects, form = form)

            # If sector or stack filter is not passed, but the preferred_only box is checked, filter out the projects only by preferred_only.
            elif preferred_only:
                query = (db.session.query(Project, ProjectStack , UserPreferenceSector, UserPreferenceStack)
                .outerjoin(ProjectStack, Project.id == ProjectStack.project_id)
                .outerjoin(UserPreferenceSector, (Project.sector_id == UserPreferenceSector.sector_id))
                .outerjoin(UserPreferenceStack , (ProjectStack.stack_id == UserPreferenceStack.stack_id))
                .filter((Project.owned_by != session["username"]))
                .filter(((UserPreferenceStack.username == session["username"]) | (UserPreferenceSector.username == session["username"])))).all()

                # Select the projects from the query, and use set to get unique projects.
                filtered_projects = [q[0] for q in query]
                filtered_projects = list(set(filtered_projects))
                return render_template("projects.html", projects = filtered_projects, form = form)

            # If sector or stack filter is not passed and preferred_only box is unchecked, return all projects not owned by the user. 
            else:
                # Get all projects not owned by the user
                projects = Project.query.filter(Project.owned_by != session["username"]).all()
                return render_template("projects.html", projects = projects, form = form)
        # If it is a get request, return all the projects.
        else:
            # Get all projects not owned by the user
            projects = Project.query.filter(Project.owned_by != session["username"]).all()
            return render_template("projects.html", projects = projects, form = form)
    else:
        return redirect("/")

@app.route("/owned-projects", methods=["GET", "POST"])
def show_own_projects():
    ''' Show projects that are owned by the user. It also provide filtering with sector and stack'''
    if check_user_session():
        
        form = PreferenceFormOwnProject()
        # Get all the sectors and stacks and add them to the choices for mutiple field form inputs. 
        sectors = [(sec.id, sec.name) for sec in Sector.query.all()]
        stacks = [(sta.id, sta.name) for sta in Stack.query.all()]
        form.sectors.choices =  sectors
        form.stacks.choices = stacks

        if form.validate_on_submit():
            _sectors = form.sectors.data
            _stacks = form.stacks.data

            # If sector or stack filter is passed, filter projects by the stacks/sectors.
            if len(_sectors) > 0 or len(_stacks) > 0:
                query = (db.session.query(Project, ProjectStack, Stack, Sector)
                .outerjoin(ProjectStack, Project.id == ProjectStack.project_id)
                .outerjoin(Stack, ProjectStack.stack_id == Stack.id)
                .outerjoin(Sector, Project.sector_id == Sector.id)
                .filter((Project.owned_by == session["username"]) & ((Stack.id.in_(_stacks)) | (Sector.id.in_(_sectors))))).all()

                # Select the projects from the query, and use set to get unique projects.

                filtered_projects = [q[0] for q in query]
                filtered_projects = list(set(filtered_projects))
                return render_template("projects.html", projects = filtered_projects, username=session["username"], form = form)

            # If sector or stack filter is not passed, return all the projects owned by the user. 
            else:
                # Get all projects owned by the user
                projects = Project.query.filter(Project.owned_by == session["username"]).all()
                return render_template("projects.html", projects = projects, username=session["username"], form = form)

        # If it is a get request, return all the projects owned by the user.
        else:
            # Get all projects owned by the user
            projects = Project.query.filter(Project.owned_by == session["username"]).all()
            return render_template("projects.html", projects = projects, username=session["username"], form = form)
    else:
        return redirect("/")


@app.route("/projects/<int:project_id>/update", methods=["GET", "POST"])
def update_project(project_id):
    ''' Edit a project '''
    if check_user_session():
        user = User.query.filter_by(username= session["username"]).first()
        project = Project.query.get_or_404(project_id)
        form = AddProjectForm(obj=project)

        form.sector.choices =  [(sec.id, sec.name) for sec in Sector.query.all()]
        form.sector.data = project.sector_id
        if form.validate_on_submit():

            # Check if the repository exists and is public

            if not validate_repo_existence(form.git_repo.data):
                form.git_repo.errors.append("The repository is private or doesn't exit")
                return render_template(
                "add_project_form.html", form=form)

            # Check if the repository is owned by the user
            if not form.git_repo.data.startswith(user.git_handle):
                form.git_repo.errors.append("You can only add a repository that is owned by you")
                return render_template(
                "add_project_form.html", form=form)

            # update project
            project.title = form.title.data
            project.git_repo = form.git_repo.data
            project.description = form.description.data
            project.sector_id = form.sector.data
            db.session.add(project)
            db.session.commit()
            flash(f"Project updated")
            return redirect(f"/projects/{project.id}")

        else:
            return render_template(
                "add_project_form.html", form=form)
    
    else:

        return redirect("/")


@app.route("/projects/<int:project_id>/delete", methods=["POST"])
def delete_project(project_id):
    ''' Delete project'''
    if check_user_session():
        username = session["username"]
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        flash(f"Project deleted")
        return redirect(f"/users/{username}")





# Preferences

@app.route("/preferences", methods=["GET", "POST"])
def preferences():
    if check_user_session():
        user = User.query.filter_by(username=session["username"]).first()

        # Get previously preferred stacks and sectors
        user_prefered_stacks = user.prefered_stacks
        user_prefered_sectors = user.prefered_sectors
        prefered_stacks =[st.id for st in user_prefered_stacks]
        prefered_sectors =[se.id for se in user_prefered_sectors]

        # Get all the sectors and stacks and add them to the choices for mutiple field form inputs. 
        form = PreferenceForm()
        sectors = [(sec.id, sec.name) for sec in Sector.query.all()]
        stacks = [(sta.id, sta.name) for sta in Stack.query.all()]
        form.sectors.choices =  sectors
        form.stacks.choices = stacks

        
        
        if form.validate_on_submit():
            _sectors = form.sectors.data
            _stacks = form.stacks.data

            # Save new stacks and sectors preferences which are not part of previously added preferences
            new_sectors = [se for se in _sectors if se not in prefered_sectors]
            new_stacks = [st for st in _stacks if st not in prefered_stacks]

            # Save stacks and sectors that will be deleted. Those are preferences that were part of previously added preferences 
            # but are not selected now.

            tobe_deleted_sectors = [se for se in prefered_sectors if se not in _sectors]
            tobe_deleted_stacks = [st for st in prefered_stacks if st not in _stacks]

            # Delete sectors
            if len(tobe_deleted_sectors) > 0:
                UserPreferenceSector.query.filter(UserPreferenceSector.sector_id.in_(tobe_deleted_sectors)).delete()
                db.session.commit()

            # Delete stacks
            if len(tobe_deleted_stacks) > 0:
                UserPreferenceStack.query.filter(UserPreferenceStack.stack_id.in_(tobe_deleted_stacks)).delete()
                db.session.commit()
            
            # Add new sectors
            if len(new_sectors) > 0:
                sectors_in_db = Sector.query.filter(Sector.id.in_(new_sectors)).all()
                user.prefered_sectors.extend(sectors_in_db)
                db.session.commit()

            # Add new stacks
            if len(new_stacks) > 0:
                stacks_in_db = Stack.query.filter(Stack.id.in_(new_stacks)).all()
                user.prefered_stacks.extend(stacks_in_db)
                db.session.commit()


            return redirect("/preferences")

        else:
            # On Get request, update form selection to the previously selected preferences 
            form.stacks.data = prefered_stacks
            form.sectors.data = prefered_sectors
            return render_template("preferences.html", prefered_stacks = user_prefered_stacks, prefered_sectors= user_prefered_sectors, form = form)
    else:
        return redirect("/")