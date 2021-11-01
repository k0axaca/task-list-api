from flask import Blueprint, jsonify, request, make_response
from app import db
from app.models.task import Task

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

def make_task_dict(task):
    if task.completed_at:
        completed = True
    else:
        completed = False 

    return {
                "id" : task.task_id,
                "title" : task.title,
                "description" : task.description,
                "is_complete" : completed
            }

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        # gets task by title
        task_title_query = request.args.get("title")
        sort_query = request.args.get("sort")
        # sorts tasks by asc and desc title name
        if sort_query:
            if sort_query == "desc":
                tasks = Task.query.order_by(Task.title.desc())
            elif sort_query == "asc":
                tasks = Task.query.order_by(Task.title.asc())
        
        # gets task by title
        elif task_title_query: 
            tasks = Task.query.filter(title=task_title_query)
        # gets all tasks
        else: 
            tasks = Task.query.all()

        tasks_response = []
        for task in tasks:
            current_task = make_task_dict(task)
            tasks_response.append(current_task)
            
        return jsonify(tasks_response), 200
    # POST
    else: 
        request_body = request.get_json()
        # if post is missing title, desciption, or completed at, do not post and return 400
        if "description" not in request_body or "title" not in request_body or "completed_at" not in request_body:
            return {"details": "Invalid data"}, 400
        # if all required values are given in the request body, return the task info with 201
        else: 
            new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )
        db.session.add(new_task)
        db.session.commit()

        return {"task": make_task_dict(new_task)}, 201

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_one_task(task_id):
    task = Task.query.get(task_id)
    
    # Guard clause 
    if task is None:
        return make_response("", 404)
    
    if request.method == "GET": 
        return {"task": make_task_dict(task)}, 200
        
    elif request.method == "PUT":
        form_data = request.get_json()
        task.title = form_data["title"]
        task.description = form_data["description"]

        db.session.commit()
        return jsonify({"task": make_task_dict(task)}), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return jsonify({"details": (f'Task {task.task_id} "{task.title}" successfully deleted')}), 200

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_mark_complete(task_id):
    task = Task.query.get(task_id)
    # guard clause
    if task is None:
        return make_response("", 404)

    # need to change date so it is "today's date"
    # this is just an example date
    task.completed_at = "09/15/2021"

    return jsonify({"task": make_task_dict(task)}), 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_mark_incomplete(task_id):
    task = Task.query.get(task_id)
    # guard clause
    if task is None:
        return make_response("", 404)

    task.completed_at = None

    return jsonify({"task": make_task_dict(task)}), 200
    

    


    
