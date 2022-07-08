from email.policy import default
from enum import unique
import bcrypt
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fullstack.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    categories_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    image = db.Column(db.String(260), nullable=False)

    
    def __repr__(self):
        return '<Product {}>'.format(self.title)


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(300), nullable=False)
    products = db.relationship('Product', backref='product', lazy='dynamic')

    def __repr__(self):
        return '<Categories {}>'.format(self.category)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(200), unique=True)
    lastname = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200), nullable=True)


    def __repr__(self):
        return '<User {}>'.format(self.username)


db.create_all()


class ProductsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'price', 'categories_id', 'description', 'image')

class CategoriesSchema(ma.Schema):
    class Meta:
        fields = ('id', 'category')

product_schema = ProductsSchema()
products_schema = ProductsSchema(many=True)

categories_schema = CategoriesSchema(many=True)


@app.route('/products', methods=['GET'])
def get_products():
    all_products = Product.query.all()
    results = products_schema.dump(all_products)
    return jsonify(results)


@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    result = product_schema.dump(product)
    return jsonify(result)


@app.route('/products/categories', methods=['GET'])
def get_categories():
    all_categories = Categories.query.all()
    result = categories_schema.dump(all_categories)
    return jsonify(result)


@app.route('/register', methods=['POST'])
def register_user():
    username = request.json['username']
    lastname = request.json['lastname']
    password = request.json['password']

    user_exists = User.query.filter_by(username=username).first()is not None

    if user_exists:
        return jsonify({'error': "User already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password)
    new_user = User(username=username, lastname=lastname,password=hashed_password)
    db.session.add(new_user)
    db.session.commit()


    return jsonify({
        'id': new_user.id,
        'username': new_user.username,
        'lastname': new_user.lastname
    }) 


@app.route("/login", methods=["POST"])
def login_user():
    username = request.json["username"]
    password = request.json["password"]

    user = User.query.filter_by(username=username).first()

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401
    

    return jsonify({
        "id": user.id,
        "username": user.username
    })


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8080)