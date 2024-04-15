import unittest
import flask_testing
import json
from freezegun import freeze_time
from unittest.mock import patch
import os
import sys
# Get the directory containing the unit test file
unit_test_directory = os.path.abspath(os.path.dirname(__file__))

# Get the directory containing the module you want to import (manage_course_lib.py)
module_directory = os.path.abspath(os.path.join(unit_test_directory, ""))

# Add the directory containing the module to sys.path
sys.path.insert(0, module_directory)

# Now you can import the module
from manage_salary_lib import app,db
# Get the absolute path to the directory containing ORM_globals.py
orm_globals_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add the directory containing ORM_globals.py to sys.path
sys.path.insert(0, orm_globals_directory)
from ORM_globals import Salary,Course,Role

class TestSalaryLib(unittest.TestCase):
    
    @freeze_time("2022-10-05 09:19:17")
    def test_to_dict(self):
        salary_1 = Salary(id=1,amount=100,role_id=1)
        self.assertEqual(salary_1.to_dict(), {
            "id": salary_1.id,
            "amount":salary_1.amount,
            "role_id":salary_1.role_id
        }
        )

class TestApp(flask_testing.TestCase):
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
    app.config['TESTING'] = True

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

#Create Salary Test
@freeze_time("2022-10-05 09:19:17")
class TestCreateSalary(TestApp):
    def test_create_salary(self):
        request_body = {"salary_id":1,"amount":100,"role_id":1}

        response = self.client.post("/create_salary",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 201, "message": "salary saved successfully."})

    def test_create_salary_duplicate_id(self):
        salary_1 = Salary(id=1,amount=100,role_id=1)
        db.session.add(salary_1)
        db.session.commit()

        request_body = {"salary_id":1,"amount":200,"role_id":2}

        response = self.client.post("/create_salary",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json,{"code": 401,"message": "Duplicate salary or id."})

    def test_create_salary_no_salary_id(self):
        request_body = {"amount":100,"role_id":1}

        response = self.client.post("/create_salary",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving salary to database."})

    def test_create_salary_no_role_id(self):
        request_body = {"amount":100,"salary_id":1}

        response = self.client.post("/create_salary",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving salary to database."})

    def test_create_salary_no_amount(self):
        request_body = {"salary_id":1,"role_id":1}

        response = self.client.post("/create_salary",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving salary to database."})

    def test_create_salary_non_json_request(self):
        response = self.client.post("/create_salary",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code": 403, "message": "Invalid input"})

#Get All Salary Test
@freeze_time("2022-10-05 09:19:17")
class TestGetAllSalary(TestApp):
    def test_get_all_salary(self):
        salary_1 = Salary(id=1,amount=100,role_id=1)
        salary_2 = Salary(id=2,amount=200,role_id=2)
        db.session.add(salary_1)
        db.session.add(salary_2)
        db.session.commit()

        response = self.client.get("/get_all_salary")

        self.assertEqual(response.json["code"], 200)
        return_data = sorted(response.json["content"], key=lambda x: x["id"])
        self.assertEqual(return_data,[{'id':1,'amount':100,'role_id':1},
                                        {'id':2,'amount':200,'role_id':2}])

#Delete Salary Test
class TestDeleteSalary(TestApp):
    def test_delete_salary(self):
        salary_1 = Salary(id=1,amount=100,role_id=1)
        db.session.add(salary_1)
        db.session.commit()

        response = self.client.delete("/delete_salary/1")

        self.assertEqual(response.json, {"code":201,
                                        "message":"Salary deleted successfully."})

    def test_delete_salary_wrong_id(self):
        salary_1 = Salary(id=1,amount=100,role_id=1)
        db.session.add(salary_1)
        db.session.commit()

        response = self.client.delete("/delete_salary/2")

        self.assertEqual(response.json, {"code":404,
                                        "message":"No salary id not found in Database."})