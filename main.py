import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, redirect, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SECRET_KEY'] = 'hard to guess key'

db = SQLAlchemy(app)

# Define the registration form with email, username, password, and confirm_password
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

# Role Model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))  # Store hashed passwords here
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html')


#register
@app.route('/register', methods=['GET', 'POST'])
def regiser():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # Check if the user already exists
        if user is None:
            # Create a new user and save it to the database
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data  # In practice, hash the password before storing it
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('index'))
        else:
            flash('User with that email already exists.', 'danger')
    
    return render_template('register.html', form=form)

# 404 Error page handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# 500 Error page handler
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)