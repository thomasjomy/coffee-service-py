import os

import logging.config
from flask import Flask, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from db import db
from coffee import Coffee

DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///:memory:'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.app_context().push()
db.init_app(app)

# Initialize our logger
logging.config.fileConfig('/config/logging.ini', disable_existing_loggers=False)
log = logging.getLogger(__name__)

@app.route("/coffees", methods=["GET"])
def get_coffees():
    log.debug('Getting coffee list')
    try:
        coffees = [coffee.json for coffee in Coffee.find_all()]
        return jsonify(coffees)
    except SQLAlchemyError as e:
        log.exception('Error getting coffee list: %s', str(e))
        return jsonify({'error': str(e)}), 500


@app.route("/coffee/<int:coffee_id>", methods=["GET"])
def get_coffee(coffee_id):
    log.debug('Getting coffee %d', coffee_id)
    try:
        coffee = Coffee.find_by_id(coffee_id)
        if coffee:
            return jsonify(coffee.json), {'Content-Type': 'application/json',
                                          'Location': f'/coffee/{coffee.id}',
                                          'ETag': f'{coffee.version}'}
        return jsonify({'error': f'Coffee {id} not found'}), 404
    # except Exception as e:
    except SQLAlchemyError as e:
        log.exception('Error getting coffee list: %s', str(e))
        return jsonify({'error': str(e)}), 500


@app.route("/coffee", methods=["POST"])
def create_coffee():
    request_data = request.get_json()
    log.debug('Creating coffee %s', request_data)
    if 'name' not in request_data or request_data['name'] is None or request_data['name'] == '':
        return jsonify({"error": "Missing name"}), 400

    try:
        coffee = Coffee(None, name=request_data['name'], version=1)
        coffee.save()
        return jsonify(coffee.json), 201, {'Content-Type': 'application/json',
                                           'Location': f'/coffee/{coffee.id}',
                                           'ETag': f'{coffee.version}'}
    # except Exception as e:
    except SQLAlchemyError as e:
        log.exception('Error getting coffee list: %s', str(e))
        return jsonify({'error': str(e)}), 500

@app.route("/coffee/<int:coffee_id>", methods=["PUT"])
def update_coffee(coffee_id):
    # Get the request data
    request_data = request.get_json()
    log.debug('Updating coffee %d: %s', coffee_id, request_data)

    if_match_header = int(request.headers.get('If-Match'))

    # Validate fields
    if not request_data.get('name'):
        log.debug('Coffee is missing name: %s', request_data)
        return jsonify({"error": "Missing name"}), 400

    # Find the coffee we want to update
    coffee = Coffee.find_by_id(coffee_id)
    if coffee is None:
        # We did not find the coffee
        log.debug('Coffee with ID %d was not found in the database',
                  coffee_id)
        return jsonify({"error": f"No coffee found with ID {id}"}), 404

    # Validate the version
    if if_match_header != coffee.version:
        log.debug('Update for coffee %s failed. If-Match-Header=%d, Coffee Version=%d',
                  coffee_id, if_match_header, coffee.version)
        return jsonify(
            {
                "error": f"Version conflict for coffee with ID {id}: version = {coffee.version}, "
                         f"If-Match = {if_match_header}"
            }
        ), 409

    # Update the name of the coffee
    coffee.name = request_data['name']

    # Increment the coffee's version
    coffee.version = coffee.version + 1

    # Update the coffee in the database
    coffee.save()

    # Return the updated coffee
    return jsonify(coffee.json), 200, {'Content-Type': 'application/json',
                                  'Location': f'/coffee/{coffee.id}',
                                  'ETag': f'{coffee.version}'}

@app.route("/coffee/<int:coffee_id>", methods=["DELETE"])
def delete_coffee(coffee_id):
    log.debug('Deleting coffee %d', coffee_id)
    coffee = Coffee.find_by_id(coffee_id)
    if coffee is None:
        log.debug('Coffee with ID %s was not found', coffee_id)
        return jsonify({"error": f"No coffee found with ID {id}"}), 404

    coffee.delete()
    log.debug('Coffee %d was successfully deleted', coffee_id)
    return f'Deleted coffee {id}'


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
