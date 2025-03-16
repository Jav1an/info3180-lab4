import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from flask import send_from_directory
from app.models import UserProfile
from app.forms import LoginForm, UploadForm



def get_uploaded_images():
    rootdir = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    image_urls = []

    for subdir, _, files in os.walk(rootdir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in valid_extensions):
                relative_path = os.path.relpath(os.path.join(subdir, file), rootdir)
                image_url = url_for('get_image', filename=file)
                image_urls.append(image_url)
    print(image_urls)
    return image_urls
###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    # Instantiate your form class
    form = UploadForm() 
    # Validate file upload on submit
    if form.validate_on_submit():
        # Get file data and save to your uploads folder
        fr = form.file.data
        filename = secure_filename(fr.filename)
        fr.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File Saved and successfully uploaded!', 'success')
        return redirect(url_for('files'))
    return render_template('upload.html', form=form) # Update this to redirect the user to a route that displays all uploaded image files

    


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # change this to actually validate the entire form submission
    # and not just one field
    if form.validate_on_submit():
        # Get the username and password values from the form.
        username = form.username.data
        password = form.password.data
        # Using your model, query database for a user based on the username
        user = UserProfile.query.filter_by(username=username).first()
        # and password submitted. Remember you need to compare the password hash.
        # You will need to import the appropriate function to do so.
        # Then store the result of that query to a `user` variable so it can be
        # passed to the login_user() method below.
        if user is not None and check_password_hash(user.password, password):
            login_user(user)
            flash('You have been successfully logged in.', 'success')
            return redirect(url_for('upload'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template("login.html", form=form)
        # Gets user id, load into session
        # Remember to flash a message to the user
        # The user should be redirected to the upload form instead
    
@app.route('/uploads/<filename>')
def get_image(filename):
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)

@app.route('/files')
@login_required
def files():
    image_urls = get_uploaded_images()
    print(image_urls)
    return render_template('files.html', image_urls=image_urls)

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('home'))


###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
