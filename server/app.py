from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from waitress import serve


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

resource_tag_association = db.Table(
    'resource_tag',
    db.Column('resource_id', db.Integer, db.ForeignKey('resources.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class resources(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    tags = db.relationship('Tag', secondary=resource_tag_association, backref='resources')

    def __init__(self, title, description, type, link, tags):
        self.title = title
        self.description = description
        self.type = type
        self.link = link
        self.tags = tags

class tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self, name):
        self.name = name
        return f'<Tag {self.name}>'

@app.route('/')
def home():
    return jsonify({'message': 'Hello, World!'})

@app.route('/get_resources', methods=['GET'])
def get_resources():
    resources_list = resources.query.all()
    return jsonify([{
        'id': r._id,
        'title': r.title,
        'description': r.description,
        'type': r.type,
        'link': r.link,
        'tags': r.tags
    } for r in resources_list])

@app.route('/add_resource', methods=['POST'])
def add_resource():
    data = request.get_json()
    new_resource = resources(
        title=data.get("title"),
        description=data.get("description"),
        type=data.get("type"),
        link=data.get("link"),
        tags=data.get("tags")
    )
    db.session.add(new_resource)
    db.session.commit()
    # Here you would typically add the product to the database
    return jsonify({'message': f'Resource {new_resource.title} added with type {new_resource.type}'}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)