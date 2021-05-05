import secrets
import datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from flask_app.models import User

def generateRunId():

    now = datetime.datetime.now()
    now_str = now.strftime("%Y%m%d_%H%M%S")
    return secrets.token_hex(8) + "_" + now_str
    
#==================================================================================
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=24)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8, max=128), EqualTo('password')])
    
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

#==================================================================================
class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=24)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')
    
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
            
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

#==================================================================================
class LoginForm(FlaskForm):
    
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    remember = BooleanField('Remember Me')
    
    submit = SubmitField('Login')
    
#==================================================================================
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
    
    
#==================================================================================
class GenerateStoryForm(FlaskForm):

    runtime_threshold_choices = []
    runtime_threshold_choices.append(('2','2'))
    runtime_threshold_choices.append(('5','5'))
    runtime_threshold_choices.append(('10','10'))
    runtime_threshold_choices.append(('15','15'))
    runtime_threshold_choices.append(('20','20'))
    runtime_threshold_choices.append(('60','60'))

    run_id = StringField('Run ID', validators=[DataRequired()])
    user_id = StringField('User ID')
    domain_full_label = SelectField(u'Domain')
    series = SelectField(u'Series', choices=[('01','01')])
    story_pattern = SelectField(u'Story Pattern')
    random_story_pattern = BooleanField('Random Story Pattern')
    run_count = StringField('Run count', validators=[DataRequired(), NumberRange(min=1,max=10)], default=1)
    neutral_obj_count = StringField('Neutral Objects', validators=[DataRequired(), NumberRange(min=0,max=3)], default=0)
    runtime_threshold = SelectField(u'Runtime Threshold (minutes)*', choices=runtime_threshold_choices)
    
    submit = SubmitField('Generate')
    
class DomainEditorForm(FlaskForm):
    
    domain_id = StringField('Domain ID')
    category = StringField('Category')
    series = StringField('Series')
    
    
    #type
    type_name = StringField('type_name_01')
    type_param_label_01 = StringField('type_param_label_01')
    type_param_type_01 = StringField('type_param_type_01')
    
    type_param_label_01 = StringField('type_param_label_01')
    type_param_type_01 = StringField('type_param_type_01')
    
    type_param_label_01 = StringField('type_param_label_01')
    type_param_type_01 = StringField('type_param_type_01')
    
    type_param_label_01 = StringField('type_param_label_01')
    type_param_type_01 = StringField('type_param_type_01')
    
    type_param_label_01 = StringField('type_param_label_01')
    type_param_type_01 = StringField('type_param_type_01')
    
    
    #actor
    #predicate
    #action
    
    