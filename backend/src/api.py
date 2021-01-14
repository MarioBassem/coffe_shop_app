import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

## ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    data = request.json
    if data['title'] is None or data['recipe'] is None:
        abort(400)
    drink = Drink(title=data['title'], recipe=json.dumps(data['recipe']))
    drink.insert()
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, **kwargs):
    drink = Drink.query.filter(Drink.id == kwargs['id']).first()
    if drink is None:
        abort(400)
    data = request.json
    if data is None or data['title'] is None or data['recipe'] is None:
        abort(400)

    drink.title = data['title']
    drink.recipe = json.dumps(data['recipe'])
    drink.update()
    formatted_drink = drink.long()
    return jsonify({
        'success': True,
        'drinks': [formatted_drink]
    })


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delte_drinks(payload, **kwargs):

    drink = Drink.query.filter(Drink.id == kwargs['id']).first()
    if drink is None:
        abort(400)

    drink.delete()
    return jsonify({
        'success': True,
        'delete': kwargs['id']
    })


## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(401)
def not_authorized(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "Unauthorized"
                    }), 401

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    'success': False,
                    'error': 400,
                    'message': "Bad request"
                    }), 400