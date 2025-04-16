from flask import Blueprint, request, jsonify
from app.config import db
from app.models import Comments

comments_bp = Blueprint('comments', __name__)


# Comment
# Create a new comment
@comments_bp.route('/add-comment', methods=['POST'])
def add_comment():
    try:
        data = request.get_json()

        name = data.get('name')
        message = data.get('message')

        new_comment = Comments(
            name=name,
            message=message,
        )

        db.session.add(new_comment)
        db.session.commit()

        return jsonify({'message': 'Your comment added successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
# Get all comments    
@comments_bp.route('/get-comments', methods=['GET'])
def get_comment():
    try:
        comments = Comments.query.order_by(Comments.created_at.desc()).all()
        result = [{
            'id': c.id,
            'name': c.name,
            'message': c.message,
            'created_at': c.created_at,
            'updated_at': c.updated_at
        } for c in comments]

        return jsonify(result), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
