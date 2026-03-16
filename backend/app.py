from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///legacyai.db')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Memory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

# Routes
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    # Simplified login - in production, verify credentials
    access_token = create_access_token(identity=data['username'])
    return jsonify(access_token=access_token)

@app.route('/api/memories', methods=['GET'])
@jwt_required()
def get_memories():
    memories = Memory.query.all()
    return jsonify([{
        'id': m.id,
        'title': m.title,
        'content': m.content,
        'date_created': m.date_created.isoformat()
    } for m in memories])

@app.route('/api/memories', methods=['POST'])
@jwt_required()
def add_memory():
    data = request.get_json()
    memory = Memory(user_id=1, title=data['title'], content=data['content'])
    db.session.add(memory)
    db.session.commit()
    return jsonify({'message': 'Memory added successfully'})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'legacy-ai-backend'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=False)