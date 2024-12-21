from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Initialize Flask app
local_server = True
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret')

# Initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Configure database URI (use environment variable for safety)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql://root:HarshalMYSQL%402002@localhost/farmers')

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define Models
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Farming(db.Model):
    fid = db.Column(db.Integer, primary_key=True)
    farmingtype = db.Column(db.String(100))

class Addagroproducts(db.Model):
    username = db.Column(db.String(50))
    email = db.Column(db.String(50))
    pid = db.Column(db.Integer, primary_key=True)
    productname = db.Column(db.String(100))
    productdesc = db.Column(db.String(300))
    price = db.Column(db.Integer)

class Trig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fid = db.Column(db.String(100))
    action = db.Column(db.String(100))
    timestamp = db.Column(db.String(100))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(1000))

class Register(db.Model):
    rid = db.Column(db.Integer, primary_key=True)
    farmername = db.Column(db.String(50))
    adharnumber = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    phonenumber = db.Column(db.String(50))
    address = db.Column(db.Text)
    farming = db.Column(db.String(50))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/farmerdetails')
@login_required
def farmerdetails():
    query = Register.query.all()
    return render_template('farmerdetails.html', query=query)

@app.route('/agroproducts')
def agroproducts():
    query = Addagroproducts.query.all()
    return render_template('agroproducts.html', query=query)

@app.route('/addagroproduct', methods=['POST', 'GET'])
@login_required
def addagroproduct():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        productname = request.form.get('productname')
        productdesc = request.form.get('productdesc')
        price = request.form.get('price')

        try:
            products = Addagroproducts(username=username, email=email, productname=productname, productdesc=productdesc, price=price)
            db.session.add(products)
            db.session.commit()
            flash("Product Added", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding product: {str(e)}", "danger")

        return redirect('/agroproducts')

    return render_template('addagroproducts.html')

@app.route('/triggers')
@login_required
def triggers():
    query = Trig.query.all()
    return render_template('triggers.html', query=query)

@app.route('/addfarming', methods=['POST', 'GET'])
@login_required
def addfarming():
    if request.method == "POST":
        farmingtype = request.form.get('farming')
        query = Farming.query.filter_by(farmingtype=farmingtype).first()

        if query:
            flash("Farming Type Already Exists", "warning")
            return redirect('/addfarming')

        dep = Farming(farmingtype=farmingtype)
        db.session.add(dep)
        db.session.commit()
        flash("Farming Added", "success")
    
    return render_template('farming.html')

@app.route("/delete/<string:rid>", methods=['POST', 'GET'])
@login_required
def delete(rid):
    post = Register.query.filter_by(rid=rid).first()
    db.session.delete(post)
    db.session.commit()
    flash("Record Deleted Successfully", "warning")
    return redirect('/farmerdetails')

@app.route("/edit/<string:rid>", methods=['POST', 'GET'])
@login_required
def edit(rid):
    if request.method == "POST":
        farmername = request.form.get('farmername')
        adharnumber = request.form.get('adharnumber')
        age = request.form.get('age')
        gender = request.form.get('gender')
        phonenumber = request.form.get('phonenumber')
        address = request.form.get('address')
        farmingtype = request.form.get('farmingtype')
        
        post = Register.query.filter_by(rid=rid).first()
        post.farmername = farmername
        post.adharnumber = adharnumber
        post.age = age
        post.gender = gender
        post.phonenumber = phonenumber
        post.address = address
        post.farming = farmingtype
        db.session.commit()
        flash("Record Updated Successfully", "success")
        return redirect('/farmerdetails')

    posts = Register.query.filter_by(rid=rid).first()
    farming = Farming.query.all()
    return render_template('edit.html', posts=posts, farming=farming)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user:
            flash("Email Already Exists", "warning")
            return render_template('signup.html')

        hashed_password = generate_password_hash(password)
        newuser = User(username=username, email=email, password=hashed_password)
        db.session.add(newuser)
        db.session.commit()
        flash("Signup Successful! Please Login", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login Successful", "primary")
            return redirect(url_for('index'))
        else:
            flash("Invalid Credentials", "warning")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect(url_for('login'))

@app.route('/register', methods=['POST', 'GET'])
@login_required
def register():
    farming = Farming.query.all()

    if request.method == "POST":
        farmername = request.form.get('farmername')
        adharnumber = request.form.get('adharnumber')
        age = request.form.get('age')
        gender = request.form.get('gender')
        phonenumber = request.form.get('phonenumber')
        address = request.form.get('address')
        farmingtype = request.form.get('farmingtype')
        
        query = Register(farmername=farmername, adharnumber=adharnumber, age=age, gender=gender, phonenumber=phonenumber, address=address, farming=farmingtype)
        db.session.add(query)
        db.session.commit()
        return redirect('/farmerdetails')

    return render_template('farmer.html', farming=farming)

@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except:
        return 'My db is not Connected'

if __name__ == '__main__':
    app.run(debug=True)