import os
import sys
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    print("CRITICAL ERROR: MONGO_URI environment variable is missing.")
    sys.exit(1)

try:
    # Set a timeout so the app doesn't hang forever if the DB is unreachable
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping') # Validate connection
    db = client['hw2_database']
    collection = db['tasks']
    print("Successfully connected to Azure Cosmos DB!")
except Exception as e:
    print(f"Failed to connect to database: {e}")
    collection = None

@app.route('/')
def index():
    """Fetches all tasks and renders the main page."""
    tasks = []
    db_status = "Connected" if collection is not None else "Disconnected"
    
    if collection is not None:
        # Fetch tasks and sort them by the newest added (using MongoDB's default _id)
        tasks = list(collection.find().sort('_id', -1))
        
    return render_template('index.html', tasks=tasks, db_status=db_status)

@app.route('/add', methods=['POST'])
def add_task():
    """Handles form submissions to add a new task."""
    if collection is None:
        return "Database is offline. Cannot add tasks.", 500

    task_name = request.form.get('task_name')
    if task_name and task_name.strip():
        collection.insert_one({"name": task_name.strip()})
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)