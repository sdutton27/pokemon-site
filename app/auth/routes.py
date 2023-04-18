# Simon Dutton

from flask import render_template, request, redirect, url_for
#from app import app
from .forms import SignUpForm, LoginForm# IMPORT ANY FORMS
from ..models import User
#from app import app # just for the images
from flask_login import login_user, logout_user, login_required
from email_validator import validate_email
from flask import Blueprint, flash, get_flashed_messages

# for images
from flask_uploads import configure_uploads, IMAGES, UploadSet 
#maybe for images
# from flask import current_app
# from ..models import db



auth = Blueprint('auth', __name__, template_folder='auth_templates')

# for images

# images = UploadSet('images', IMAGES)
# configure_uploads(current_app, images)

# with current_app.app_context():
#     db.create_all()

@auth.route('/signup', methods=["GET", "POST"])
def signup_page():
    # instantiate the form
    form = SignUpForm()

    if request.method == 'POST':
        if form.validate(): 
            first_name = form.first_name.data
            last_name = form.last_name.data
            email = form.email.data
            password = form.password.data

            is_new_account = True

            # Make sure the user is not in the db yet
            try:
                validation = validate_email(email, check_deliverability=is_new_account)
                email = validation.email
            except: 
                #invalid email
                return render_template('signup.html', invalid_email=email, form = form)
            
            #ADDED THIS SO THAT USER CAN ONLY INPUT ITEM ONCE INTO THE DB
            user_already_exists = User.query.filter_by(email=email).first()
            if not user_already_exists:
                #commenting this out because it looks like we can't get images here.
                # try:
                #     filename = images.save(form.profile_pic.data)
                #     image_file = url_for('static', filename=f'./img/user_img/{filename}')
                #     #image_file = filename # let's try this to save the info
                #     # only add to the db if not already in there

                #     #user = User(first_name, last_name, email, password, filename)

                #     user = User(first_name, last_name, email, password, image_file)
                # except:
                    # create a user without a profile pic
                user = User(first_name, last_name, email, password)
                user.save_to_db() 
                login_user(user)
                return redirect(url_for('home_page'))
            else:
                # user already has an account
                # they are trying to remake an account so tell them instead an email exists
                return render_template('signup.html', used_email=email, form = form)
    
    # if password does not equal confirm password data:
    if form.password.data != form.confirm_password.data:
        print('invalid password')
        return render_template('signup.html', invalid_password=True, form = form)        

    return render_template('signup.html', form = form)


@auth.route('/login', methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate(): # if form is valid
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user: # user was found
                # verify password
                # looks at the password in the database = the password you sent in the form
            if user.password == password:
                    # log in
                login_user(user) #login the user
                    # take the user back to the homepage
                return redirect(url_for('home_page'))
            else:
                    # invalid password
                    print('incorrect username(for security) or password(true)')
                    return render_template('login.html', incorrect_login=True, form = form)
        else: # user was not found
            print('incorrect username(true) or password(just for security)')
            return render_template('login.html', incorrect_login=True, form = form)

    return render_template('login.html', form = form)

@auth.route('/logout')
@login_required
def log_me_out():
    logout_user()
    return redirect(url_for('auth.login_page'))
