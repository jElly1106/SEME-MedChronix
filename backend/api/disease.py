""" the router function for the instance of disease ,event and rule table. """

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from database.models import Disease, Event, Rule
from common.utils import upload_images
import os
from datetime import datetime
import json
from common.decorators import admin_required

disease_bp = Blueprint('disease', __name__)

@disease_bp.route('/get_disease_info', methods=['GET'])
@jwt_required()
def get_disease_info():
    """Get the disease information."""
    date = request.get_json()
    disease_id = date['disease_id']
    disease = Disease.query.get(disease_id)
    if disease:
        return jsonify(disease.to_dict())
    else:
        return jsonify({'error': 'Disease not found'}), 404
    
@disease_bp.route('/get_all_events', methods=['GET'])
@jwt_required()
def get_all_events():
    """Get all the events."""
    events = Event.query.all()
    return jsonify([event.to_dict() for event in events])

@disease_bp.route('/get_all_rules', methods=['GET'])
@jwt_required()
def get_all_rule():
    """Get all the rules."""
    rules = Rule.query.all()
    return jsonify([rule.to_dict() for rule in rules])