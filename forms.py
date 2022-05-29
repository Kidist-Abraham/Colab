from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, SelectMultipleField, BooleanField
from wtforms.validators import InputRequired, Email, Regexp
class RegisterUserForm(FlaskForm):
    """Form for creating users."""

    username = StringField("Username", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    git_handle = StringField("Git Handle", validators=[InputRequired()])
    is_organisation = BooleanField("Is this an organization?")

class UserProfileForm(FlaskForm):
    """ Form for editing profile. """

    username = StringField('Username', validators=[InputRequired()])
    email = StringField('E-mail', validators=[InputRequired(), Email()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])

class LoginUserForm(FlaskForm):
    """Form for login users."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])



class AddProjectForm(FlaskForm):
    """Form for adding project"""

    title = StringField("Title", validators=[InputRequired()])
    description = StringField("Description")
    git_repo =  StringField("Repository name", validators=[InputRequired()])
    sector = SelectField('Choose the Sector of the Project ? ', coerce=int)


class StackPreferenceForm(FlaskForm):
    """Form for adding a stack Preference """

    stacks = SelectMultipleField('What stack are you interested in ? ', coerce=int)


class SectorPreferenceForm(FlaskForm):
    """Form for adding a stack Preference"""

    sector = SelectField('What sector are you interested in ? ', coerce=int)



class PreferenceForm(FlaskForm):
    """Form for filtering Preference"""

    sectors = SelectMultipleField('What sector are you interested in ? ', coerce=int)
    stacks = SelectMultipleField('What stack are you interested in ? ', coerce=int)
    show_preferences_only = BooleanField("Show preferred projects only") 


class PreferenceFormOwnProject(FlaskForm):
    """Form for filtering owned  Preference"""

    sectors = SelectMultipleField('What sector are you interested in ? ', coerce=int)
    stacks = SelectMultipleField('What stack are you interested in ? ', coerce=int)
