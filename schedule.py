from flask_apscheduler import APScheduler
from git import get_stacks, get_collaborators
from models import db, connect_db, User, Stack, Collaboration, Project
from datetime import datetime

# set configuration values
class Config:
    SCHEDULER_API_ENABLED = True




# initialize scheduler
scheduler = APScheduler()
# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True

def connect_scheduler(app):
    connect_db(app)
    scheduler.init_app(app)



@scheduler.task('cron', id='update_ptoject_stacks', day='*')
def update_ptoject_stacks():
    ''' Function to update the stack/languages used in all the repositeries '''
    with scheduler.app.app_context():
        projects = Project.query.all()
        for p in projects:
            stacks = get_stacks(p.git_repo)
            existing_stacks = [stack.name for stack in p.stacks]
            new_stacks = [stack for stack in stacks if stack not in existing_stacks]
            if len(new_stacks) > 0:
                stacks_in_db = Stack.query.filter(Stack.name.in_(new_stacks)).all()
                p.stacks.extend(stacks_in_db)
                db.session.commit()



@scheduler.task('cron', id='update_ptoject_collabs', hour='*')
def update_ptoject_collaborators():
    ''' Function to update the contributers in all the repositeries '''
    with scheduler.app.app_context():
        projects = Project.query.all()
        for p in projects:
            collabs = get_collaborators(p.git_repo)
            existing_collabs = [collab.git_handle for collab in p.collaborators]
            new_collabs = [collab for collab in collabs if collab not in existing_collabs] 
            #TODO handle removed collabs
            if len(new_collabs) > 0:
                collabs_in_db = User.query.filter(User.git_handle.in_(new_collabs)).all()
                p.collaborators.extend(collabs_in_db)
                db.session.commit()


'''
@scheduler.task('cron', id='alert_users_on_new_projects', day='*')
def alert_users_on_new_projects():
    with scheduler.app.app_context():
        #TODO filter projects that are created yesterday
        projects = Project.query.filter(Project.timestamp).all()
        for p in projects:
            stacks = get_stacks(p.git_repo)
            existing_stacks = [stack.name for stack in p.stacks]
            new_stacks = [stack for stack in stacks if stack not in existing_stacks]
            if len(new_stacks) > 0:
                stacks_in_db = Stack.query.filter(Stack.name.in_(new_stacks)).all()
                p.stacks.extend(stacks_in_db)
                db.session.commit()

'''
def start_scheduler():
    scheduler.start()