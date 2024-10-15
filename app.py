from flask import Flask, request, jsonify
from mongoengine import connect
from mongoengine.errors import ValidationError, DoesNotExist
from models.model import Todo
import os

app = Flask(__name__)

# Use environment variable for MongoDB connection string, with fallback to local
mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/todoapp')
connect(host=mongodb_uri)

def create_response(success, data, status_code, message=None):
    response = {
        "success": success,
        "data": data,
        "status_code": status_code
    }
    if message:
        response["message"] = message
    return jsonify(response), status_code

@app.route('/')
def root():
    return create_response(False, None, 404, "Resource not found")

@app.route('/todos', methods=['POST'])
def create_todo():
    if not request.is_json:
        return create_response(False, None, 400, "Request must be JSON")

    try:
        todo = Todo(**request.json).save()
        return create_response(True, todo.to_dict(), 201, "Todo created successfully")
    except ValidationError as e:
        return create_response(False, None, 400, f"Invalid data: {e}")

@app.route('/todos', methods=['GET'])
def get_todos():
    todos = [todo.to_dict() for todo in Todo.objects]
    return create_response(True, todos, 200, f"{len(todos)} todos retrieved successfully")

@app.route('/todos/<todo_id>', methods=['GET'])
def get_todo(todo_id):
    try:
        todo = Todo.objects.get(id=todo_id)
        return create_response(True, todo.to_dict(), 200, "Todo retrieved successfully")
    except DoesNotExist:
        return create_response(False, None, 404, "Todo not found")
    except ValidationError:
        return create_response(False, None, 400, "Invalid todo ID")

@app.route('/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    if not request.is_json:
        return create_response(False, None, 400, "Request must be JSON")

    if not request.json:
        return create_response(False, None, 400, "Update data missing")

    try:
        todo = Todo.objects.get(id=todo_id)
        todo.update(**request.json)
        todo.reload()
        return create_response(True, todo.to_dict(), 200, "Todo updated successfully")
    except DoesNotExist:
        return create_response(False, None, 404, "Todo not found")
    except ValidationError as e:
        return create_response(False, None, 400, f"Invalid data: {e}")

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        todo = Todo.objects.get(id=todo_id)
        todo.delete()
        return create_response(True, None, 200, "Todo deleted successfully")
    except DoesNotExist:
        return create_response(False, None, 404, "Todo not found")
    except ValidationError:
        return create_response(False, None, 400, "Invalid todo ID")

@app.errorhandler(404)
def not_found(error):
    return create_response(False, None, 404, "Resource not found")

if __name__ == '__main__':
    app.run(debug=True)