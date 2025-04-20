from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from database.models import Precondition

precondition_bp = Blueprint('precondition', __name__)

@precondition_bp.route('/get_all_preconditions', methods=['GET'])
@jwt_required()
def get_all_preconditions():
    """获取所有前置条件（用于前端下拉框）"""
    preconditions = Precondition.query.all()
    return jsonify([precondition.to_dict() for precondition in preconditions])