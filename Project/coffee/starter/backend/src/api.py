import os
from turtle import title
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from functools import wraps
from jose import jwt
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
# db_drop_and_create_all()
db_drop_and_create_all()

# ROUTES  
'''
@TODO implement endpoint 
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
##this is the endpoint to get drinks 
##a success if the endpoint passes. if not it fails the operation gets aborted
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks=Drink.query.order_by(Drink.id).all()
    try:
        return jsonify({
        'success':True,
        'drinks':[drink.short() for drink in drinks]
        })
    except:
        
        abort(404)
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
##this is the endpoint to get the drinks details as well as allowing a 200 status code. This also auth the get:drink-detail
##the jwt is also included
@app.route('/drinks-detail',methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(jwt):
    drinks=Drink.query.all()
    return jsonify({
    'success':True,
    'drinks':[drink.long() for drink in drinks]
    }),200
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
##this endpoint helps to post new drinks, with the jwt embedded 
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt):
    body= request.get_json()
##if the title and recipe for the coffee is not in the body, return a 422 error code
    if 'title' and 'recipe' not in body:
        abort(422)
        ##this embed the title and recipe of the coffee
        ##return a 200 success code
    try: 
        body= request.get_json() 
        title = body['title']
        recipe = json.dumps(body['recipe'])
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except Exception:
        abort(422)       
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
##this endpoint helps to update existing coffee drinks, embedding the jwt in the patch request 
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(jwt,drink_id):
    drink = Drink.query.get(drink_id)
    body = request.get_json()
##return a 404 error code when the drink does not exist
    if drink is None:
        abort(404)
##if the drink exist, update and return a success
    if 'title' and 'recipe'in body :
        drink.title = body['title']
        drink.recipe = json.dumps(body['recipe'])
    drink.update()
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
##this endpoint helps to delete coffee drinks,  maybe the drinks aren't sold anymore.
##the delete endpoint also embed the jwt as well as the drink id
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    drinks = Drink.query.filter(Drink.id == drink_id ).one_or_none()
    ##if the drink doesn't exist, abort with a 404 error code
    if drinks is  None :
        abort(404)
        ##if the drink parameters exist, delete the drink
    try:
        drinks.delete()
        return jsonify({
            'success': True,
            'delete': drinks.id
        })
    except Exception:
        abort(422)
# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422
'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with appropriate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''
'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response