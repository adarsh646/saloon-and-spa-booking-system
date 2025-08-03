from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables (works locally, ignored in Vercel)
load_dotenv()

app = Flask(__name__)
CORS(app)

# Safe MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise RuntimeError("Missing MONGO_URI environment variable")

client = MongoClient(mongo_uri)
db = client["arise_app"]
users_collection = db["users"]

# Root route for health check
@app.route('/')
def home():
    return jsonify({"status": "Flask backend is live on Vercel"}), 200

# Register route
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 409

    users_collection.insert_one({
        "username": username,
        "email": email,
        "password": password  # 🔐 Hash in production
    })

    return jsonify({"message": "User registered successfully"}), 201

# Required WSGI handler for Vercel
def handler(environ, start_response):
    return app(environ, start_response)
