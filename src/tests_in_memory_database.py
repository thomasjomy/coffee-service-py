import json
import pytest
from app import app, db
from coffee import Coffee

# Define coffee data we'll use to create test instances
coffee_data = [
    {"name": "Coffee 1", "version": 1},
    {"name": "Coffee 2", "version": 1},
    {"name": "Coffee 3", "version": 1},
]

# Setup our test Flask app
test_app = app
test_app.app_context().push()
db.create_all()
client = test_app.test_client()
test_app.testing = True


@pytest.fixture
def setup_database():
    print("Setting up the test database")
    # Create fresh Coffee instances for this test
    coffee_list = []
    for data in coffee_data:
        coffee = Coffee(None, data["name"], data["version"])
        coffee.save()
        coffee_list.append(coffee)

    # Yield the coffee list so tests can access it
    yield coffee_list

    # Clean up the test data using SQLAlchemy
    for coffee in Coffee.find_all():
        coffee.delete()


def test_get_coffees(setup_database):
    # This is a list of coffees that setup_database inserted into the database
    coffee_list = setup_database

    # Execute a GET to /coffees
    response = client.get('/coffees')

    # Verify that we get a 200 OK HTTP response code
    assert response.status_code == 200

    # Validate the body
    json_list = response.json

    # Validate that we got all of our coffees back
    assert len(json_list) == len(coffee_list)

    # Validate the returned coffees
    index = 0
    for coffee in coffee_list:
        coffee = coffee_list[index]
        assert json_list[index]['id'] == coffee.id
        assert json_list[index]['name'] == coffee.name
        assert json_list[index]['version'] == coffee.version
        index += 1


def test_get_coffee(setup_database):
    # This is the coffee we're going to test getting
    coffee_list = setup_database
    coffee = coffee_list[1]

    # Execute a GET to /coffee/test_coffee.id
    response = client.get(f'/coffee/{coffee.id}')

    # Validate that we get a 200 OK response code
    assert response.status_code == 200

    # Validate the response body
    returned_coffee = response.json
    assert returned_coffee['id'] == coffee.id
    assert returned_coffee['name'] == coffee.name
    assert returned_coffee['version'] == coffee.version


def test_get_coffee_not_found(setup_database):
    # Calculate an invalid coffee ID
    coffee_list = setup_database
    coffee_id = coffee_list[-1].id + 1

    # Execute a GET to /coffee/coffee.id
    response = client.get(f'/coffee/{coffee_id}')

    # Validate that we get a 200 OK response code
    assert response.status_code == 404


def test_create_coffee(setup_database):
    coffee_list = setup_database
    data = {'name': 'Coffee 4'}
    response = client.post('/coffee',
                           data=json.dumps(data),
                           content_type='application/json')

    assert response.status_code == 201

    # Validate the response body
    returned_coffee = response.json
    assert returned_coffee['id'] == coffee_list[-1].id + 1
    assert returned_coffee['name'] == 'Coffee 4'
    assert returned_coffee['version'] == 1


def test_update_coffee(setup_database):
    # Update the second coffee in the list
    coffee_list = setup_database
    coffee = coffee_list[1]

    # Execute a PUT request with an If-Match header that matches the coffee's version
    data = {'name': 'Updated Coffee 2'}
    response = client.put(f'/coffee/{coffee.id}',
                          data=json.dumps(data),
                          headers={
                              'Content-Type': 'application/json',
                              'If-Match': coffee.version
                          })

    # Validate that we get a 200 OK response
    assert response.status_code == 200

    # Validate the response body
    updated_coffee = response.json
    assert updated_coffee['id'] == coffee.id
    assert updated_coffee['name'] == 'Updated Coffee 2'
    assert updated_coffee['version'] == 2


def test_update_coffee_version_conflict(setup_database):
    coffee_list = setup_database
    coffee = coffee_list[1]
    data = {'name': 'Updated Coffee 2'}

    # Attempt to update the coffee with the wrong If-Match header
    response = client.put(f'/coffee/{coffee.id}',
                          data=json.dumps(data),
                          headers={
                              'Content-Type': 'application/json',
                              'If-Match': coffee.version + 1
                          })

    # Validate that we get a 409 Conflict response
    assert response.status_code == 409


def test_update_coffee_not_found(setup_database):
    # Calculate an invalid coffee ID
    coffee_list = setup_database
    test_coffee_id = coffee_list[-1].id + 1
    data = {'name': 'Updated Coffee 2'}
    response = client.put(f'/coffee/{test_coffee_id}',
                          data=json.dumps(data),
                          headers={
                              'Content-Type': 'application/json',
                              'If-Match': 1
                          })

    # Validate that we get a 404 Not Found response
    assert response.status_code == 404


def test_delete_coffee(setup_database):
    # Get a valid coffee
    coffee_list = setup_database
    coffee_id = coffee_list[1].id

    # Delete the coffee
    response = client.delete(f'/coffee/{coffee_id}')

    # Validate that we get a 200 OK response
    assert response.status_code == 200

    # Validate that the coffee is no longer in the database
    response = client.get(f'/coffee/{coffee_id}')
    assert response.status_code == 404


def test_delete_coffee_not_found(setup_database):
    # Calculate an invalid coffee ID
    coffee_list = setup_database
    coffee_id = coffee_list[-1].id + 1

    # Delete the coffee
    response = client.delete(f'/coffee/{coffee_id}')

    # Validate that we get a 404 Not Found  response
    assert response.status_code == 404
