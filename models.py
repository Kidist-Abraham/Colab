from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()

db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

SECTORS = ["Education", "Transport", "Health", "Finance", "Social", "Entertainment", "Media", "Religion", "Culture", "Telecommunication", "Agriculture", "Construction", "Food", "Energy Industry"]

class User(db.Model):
    __tablename__ = "users"


    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    username = db.Column(db.String(20),
                      primary_key=True,
                      unique = True)

    password = db.Column(db.String,
                     nullable=False)

    email = db.Column(db.String(50), 
                     nullable=False,
                     unique = True) 

    first_name = db.Column(db.String(30),
                     nullable=False)     

    last_name = db.Column(db.String(30),
                     nullable=False)     

    git_handle = db.Column(db.String(50), 
                     nullable=False,
                     unique = True) 

    is_organisation = db.Column(db.Boolean,
                     nullable=False,
                     default=False) 

    collaborations = db.relationship(
        'Project',
        secondary="collaborations",
        backref='collaborators'
    )

    owned_projects = db.relationship("Project", cascade="all, delete-orphan", backref='owner')

    prefered_stacks =  db.relationship(
        'Stack',
        secondary="user_preferences_stacks",
        backref='users'
    )

    prefered_sectors =  db.relationship(
        'Sector',
        secondary="user_preferences_sectors",
        backref='users'
    )


    @classmethod
    def register(cls, username, email, first_name, last_name, git_handle, password, is_organisation):
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        return cls(username=username, email= email, first_name= first_name, last_name = last_name, git_handle=git_handle,is_organisation = is_organisation, password=hashed_utf8)

    @classmethod
    def authenticate(cls, username, password):

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False



class Collaboration(db.Model):
    __tablename__ = "collaborations"


    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    project_id = db.Column( db.Integer,
                    db.ForeignKey('projects.id', ondelete="CASCADE"),
                      nullable=False)                  

    username = db.Column( db.String(20),
                    db.ForeignKey('users.username', ondelete="CASCADE"),
                      nullable=False)



class Project(db.Model):
    __tablename__ = "projects"


    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    '''
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )
    '''
    title = db.Column(db.String(100), 
                     nullable=False) 

    git_repo = db.Column(db.String,
                     nullable=False)    

    description = db.Column(db.String(100))

    owned_by = db.Column( db.String(20),
                    db.ForeignKey('users.username', ondelete="CASCADE"),
                      nullable=False)
    sector_id = db.Column( db.Integer,
                    db.ForeignKey('sectors.id', ondelete="CASCADE"),
                      nullable=False)

    sector = db.relationship("Sector", backref='projects')


    stacks = db.relationship(
        'Stack',
        secondary="project_stacks",
        backref='projects'
    )

class Stack(db.Model):
    __tablename__ = "stacks"


    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    name = db.Column(db.String,
                     nullable=False,
                     unique = True) 

class Sector(db.Model):
    __tablename__ = "sectors"


    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
                   
    name = db.Column(db.String,
                     nullable=False,
                      unique = True) 

    
    @classmethod
    def add_stacks_to_db(cls):
        sectors = [cls(name=sector) for sector in SECTORS]
        db.session.add_all(sectors)
        db.session.commit()

class ProjectStack(db.Model):
    __tablename__ = "project_stacks"


    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    project_id = db.Column( db.Integer,
                    db.ForeignKey('projects.id', ondelete="CASCADE"),
                      nullable=False)  
    
    stack_id = db.Column( db.Integer,
                    db.ForeignKey('stacks.id', ondelete="CASCADE"),
                      nullable=False)  


class UserPreferenceSector(db.Model):
    __tablename__ = "user_preferences_sectors"


    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    username = db.Column( db.String(20),
                    db.ForeignKey('users.username', ondelete="CASCADE"),
                      nullable=False) 
    
    sector_id = db.Column( db.Integer,
                    db.ForeignKey('sectors.id', ondelete="CASCADE"),
                      nullable=False)


class UserPreferenceStack(db.Model):
    __tablename__ = "user_preferences_stacks"


    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    username = db.Column( db.String(20),
                    db.ForeignKey('users.username', ondelete="CASCADE"),
                      nullable=False) 
    
    stack_id = db.Column( db.Integer,
                    db.ForeignKey('stacks.id', ondelete="CASCADE"),
                      nullable=False)

