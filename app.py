from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId, errors as bson_errors
import os

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/todoapp"
mongo = PyMongo(app)

# Assign mongo.db.todos to a variable
todos_collection = mongo.db.todos

def create_response(success, data, status_code, message=None):
    response = {
        "success": success,
        "data": data,
        "status_code": status_code
    }
    if message:
        response["message"] = message
    return jsonify(response), status_code

# Root route
@app.route('/')
def root():
    return create_response(False, None, 404, "Resource not found")

# Create a new todo
@app.route('/todos', methods=['POST'])
def create_todo():
    if not request.is_json:
        return create_response(False, None, 400, "Request must be JSON")

    todo = request.json
    
    # Validate required fields
    required_fields = ['title', 'description']
    if not all(field in todo for field in required_fields):
        return create_response(False, None, 400, f"Missing required fields. Required fields are: {', '.join(required_fields)}")
    
    # Validate data types
    if not isinstance(todo.get('title'), str) or not isinstance(todo.get('description'), str):
        return create_response(False, None, 400, "Title and description must be strings")
    
    # Set default value for 'completed' if not provided
    if 'completed' not in todo:
        todo['completed'] = False
    elif not isinstance(todo['completed'], bool):
        return create_response(False, None, 400, "Completed status must be a boolean")
    
    # Remove any extra fields
    valid_fields = required_fields + ['completed']
    todo = {k: v for k, v in todo.items() if k in valid_fields}
    
    result = todos_collection.insert_one(todo)
    todo['_id'] = str(result.inserted_id)
    return create_response(True, todo, 201, "Todo created successfully")
# Get all todos
@app.route('/todos', methods=['GET'])
def get_todos():
    todos = list(todos_collection.find())
    print(todos)
    print(type(todos[0]))
    todos = [{**todo, '_id': str(todo['_id'])} for todo in todos]
    return create_response(True, todos, 200, f"{len(todos)} todos retrieved successfully")

# Get a specific todo
@app.route('/todos/<todo_id>', methods=['GET'])
def get_todo(todo_id):
    try:
        todo = todos_collection.find_one({'_id': ObjectId(todo_id)})
        if todo:
            todo['_id'] = str(todo['_id'])
            return create_response(True, todo, 200, "Todo retrieved successfully")
        return create_response(False, None, 404, "Todo not found")
    except bson_errors.InvalidId:
        return create_response(False, None, 400, "Invalid todo ID")

# Update a todo
@app.route('/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    try:
        update_data = request.json
        result = todos_collection.update_one({'_id': ObjectId(todo_id)}, {'$set': update_data})
        print(result.modified_count)
        if result.modified_count:
            return create_response(True, None, 200, "Todo updated successfully")
        return create_response(False, None, 200, "Todo already updated")
    except bson_errors.InvalidId:
        return create_response(False, None, 400, "Invalid todo ID")

# Delete a todo
@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        result = todos_collection.delete_one({'_id': ObjectId(todo_id)})
        if result.deleted_count:
            return create_response(True, None, 200, "Todo deleted successfully")
        return create_response(False, None, 404, "Todo not found")
    except bson_errors.InvalidId:
        return create_response(False, None, 400, "Invalid todo ID")

# Error handler for 404 Not Found
@app.errorhandler(404)
def not_found(error):
    return create_response(False, None, 404, "Resource not found")

if __name__ == '__main__':
    app.run(debug=True)