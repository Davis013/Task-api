from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import Task

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """
    Get all tasks for the authenticated user.
    Supports filtering by status and priority, plus pagination.

    Query params:
        status   - filter by: todo | in_progress | done
        priority - filter by: low | medium | high
        page     - page number (default 1)
        per_page - results per page (default 10, max 50)
    """
    user_id = get_jwt_identity()

    query = Task.query.filter_by(user_id=user_id)

    # Filters
    status = request.args.get('status')
    priority = request.args.get('priority')

    if status and status in Task.VALID_STATUSES:
        query = query.filter_by(status=status)

    if priority and priority in Task.VALID_PRIORITIES:
        query = query.filter_by(priority=priority)

    # Sorting
    sort_by = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    sort_col = getattr(Task, sort_by, Task.created_at)
    query = query.order_by(sort_col.desc() if order == 'desc' else sort_col.asc())

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'tasks': [t.to_dict() for t in paginated.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': paginated.total,
            'pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }
    }), 200


@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task."""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    status = data.get('status', 'todo')
    priority = data.get('priority', 'medium')

    if status not in Task.VALID_STATUSES:
        return jsonify({'error': f'Invalid status. Choose from: {", ".join(Task.VALID_STATUSES)}'}), 400

    if priority not in Task.VALID_PRIORITIES:
        return jsonify({'error': f'Invalid priority. Choose from: {", ".join(Task.VALID_PRIORITIES)}'}), 400

    # Parse optional due date
    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.fromisoformat(data['due_date'])
        except ValueError:
            return jsonify({'error': 'Invalid due_date format. Use ISO 8601 (e.g. 2025-12-31)'}), 400

    task = Task(
        title=title,
        description=data.get('description', ''),
        status=status,
        priority=priority,
        due_date=due_date,
        user_id=user_id
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({'message': 'Task created', 'task': task.to_dict()}), 201


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get a single task by ID."""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
    return jsonify({'task': task.to_dict()}), 200


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update an existing task."""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'title' in data:
        title = data['title'].strip()
        if not title:
            return jsonify({'error': 'Title cannot be empty'}), 400
        task.title = title

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in Task.VALID_STATUSES:
            return jsonify({'error': f'Invalid status. Choose from: {", ".join(Task.VALID_STATUSES)}'}), 400
        task.status = data['status']

    if 'priority' in data:
        if data['priority'] not in Task.VALID_PRIORITIES:
            return jsonify({'error': f'Invalid priority. Choose from: {", ".join(Task.VALID_PRIORITIES)}'}), 400
        task.priority = data['priority']

    if 'due_date' in data:
        if data['due_date'] is None:
            task.due_date = None
        else:
            try:
                task.due_date = datetime.fromisoformat(data['due_date'])
            except ValueError:
                return jsonify({'error': 'Invalid due_date format. Use ISO 8601'}), 400

    task.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Task updated', 'task': task.to_dict()}), 200


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task."""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': f'Task "{task.title}" deleted'}), 200


@tasks_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Return task counts broken down by status and priority."""
    user_id = get_jwt_identity()

    total = Task.query.filter_by(user_id=user_id).count()

    by_status = {
        s: Task.query.filter_by(user_id=user_id, status=s).count()
        for s in Task.VALID_STATUSES
    }
    by_priority = {
        p: Task.query.filter_by(user_id=user_id, priority=p).count()
        for p in Task.VALID_PRIORITIES
    }

    return jsonify({
        'total': total,
        'by_status': by_status,
        'by_priority': by_priority
    }), 200
