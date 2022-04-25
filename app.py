from flask import Flask, render_template, redirect, request, flash, session
from models import db, connect_db, User, Project, Collaboration, ProjectStack, UserPreferenceSector, UserPreferenceStack, Sector, Stack
from forms import RegisterUserForm, LoginUserForm, AddProjectForm, SectorPreferenceForm, StackPreferenceForm, PreferenceForm, UserProfileForm
from git import get_stacks, get_collaborators, validate_git_handle_ownership, validate_repo_existence
from schedule import start_scheduler, connect_scheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = '<fsa64ghfa78hjfa>'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///colab'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

connect_scheduler(app)
start_scheduler()

def check_user_session():
    return True if "username" in session and User.query.filter_by(username=session["username"]).first() else False
        

@app.route("/")
def main_page():
    if check_user_session():
        user = User.query.filter_by(username=session["username"]).first()
        return render_template("home.html", user= user)
    else:
        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterUserForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data
        git_handle = form.git_handle.data
        is_organisation = form.is_organisation.data

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

    session.pop("username")

    return redirect("/")

@app.route("/profile")
def show_profile():
    if check_user_session():

        return redirect(f"/users/{session['username']}")
    else:
        return redirect("/")


@app.route("/users/<username>")
def user_detail(username):
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
            # Check if the repository is owned by the user

            if not validate_repo_existence(git_repo):
                form.git_repo.errors.append("The repository is private or doesn't exit")
                return render_template(
                "add_project_form.html", form=form)

            if not git_repo.startswith(user.git_handle):
                form.git_repo.errors.append("You can only add a repository that is owned by you")
                return render_template(
                "add_project_form.html", form=form)
            
            

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
    if check_user_session():
        project = Project.query.get_or_404(project_id)
        user = User.query.filter_by(username=session["username"]).first()
        selfProject = True if user.username == project.owned_by else False
        return render_template("project.html", project = project , selfProject=selfProject)
    else:
        return redirect("/")

@app.route("/projects", methods=["GET", "POST"])
def show_projects():
    if check_user_session():
        projects = Project.query.filter(Project.owned_by != session["username"]).all()
        form = PreferenceForm()
        sectors = [(sec.id, sec.name) for sec in Sector.query.all()]
        stacks = [(sta.id, sta.name) for sta in Stack.query.all()]
        form.sectors.choices =  sectors
        form.stacks.choices = stacks
        if form.validate_on_submit():
            _sectors = form.sectors.data
            _stacks = form.stacks.data
            if len(_sectors) > 0 or len(_stacks) > 0:
                query = (db.session.query(Project, ProjectStack, Stack, Sector)
                .outerjoin(ProjectStack, Project.id == ProjectStack.project_id)
                .outerjoin(Stack, ProjectStack.stack_id == Stack.id)
                .outerjoin(Sector, Project.sector_id == Sector.id)
                .filter((Project.owned_by != session["username"]) & ((Stack.id.in_(_stacks)) | (Sector.id.in_(_sectors))))).all()
                filtered_projects = [q[0] for q in query]
                filtered_projects = list(set(filtered_projects))
                return render_template("projects.html", projects = filtered_projects, form = form)

            else:
                return render_template("projects.html", projects = projects, form = form)
        else:
            return render_template("projects.html", projects = projects, form = form)
    else:
        return redirect("/")

@app.route("/owned-projects", methods=["GET", "POST"])
def show_own_projects():
    if check_user_session():
        projects = Project.query.filter(Project.owned_by == session["username"]).all()
        form = PreferenceForm()
        sectors = [(sec.id, sec.name) for sec in Sector.query.all()]
        stacks = [(sta.id, sta.name) for sta in Stack.query.all()]
        form.sectors.choices =  sectors
        form.stacks.choices = stacks
        if form.validate_on_submit():
            _sectors = form.sectors.data
            _stacks = form.stacks.data
            if len(_sectors) > 0 or len(_stacks) > 0:
                query = (db.session.query(Project, ProjectStack, Stack, Sector)
                .outerjoin(ProjectStack, Project.id == ProjectStack.project_id)
                .outerjoin(Stack, ProjectStack.stack_id == Stack.id)
                .outerjoin(Sector, Project.sector_id == Sector.id)
                .filter((Project.owned_by == session["username"]) & ((Stack.id.in_(_stacks)) | (Sector.id.in_(_sectors))))).all()

                filtered_projects = [q[0] for q in query]
                filtered_projects = list(set(filtered_projects))
                return render_template("projects.html", projects = filtered_projects, username=session["username"], form = form)

            else:
                return render_template("projects.html", projects = projects, username=session["username"], form = form)
        else:
            return render_template("projects.html", projects = projects, username=session["username"], form = form)
    else:
        return redirect("/")


@app.route("/projects/<int:project_id>/update", methods=["GET", "POST"])
def update_project(project_id):
    if check_user_session():

        project = Project.query.get_or_404(project_id)
        form = AddProjectForm(obj=project)

        form.sector.choices =  [(sec.id, sec.name) for sec in Sector.query.all()]
        form.sector.data = project.sector_id
        if form.validate_on_submit():
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
    if check_user_session():
        username = session["username"]
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        flash(f"Project deleted")
        return redirect(f"/users/{username}")