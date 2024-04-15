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
from manage_spec_lib import app,db
# Get the absolute path to the directory containing ORM_globals.py
orm_globals_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add the directory containing ORM_globals.py to sys.path
sys.path.insert(0, orm_globals_directory)
from ORM_globals import Spec,Role

class TestCourseLib(unittest.TestCase):
    
    @freeze_time("2022-10-05 09:19:17")
    def test_to_dict(self):
        spec_1 = Spec(id=1,name="Python")
        self.assertEqual(spec_1.to_dict(), {
            "id": spec_1.id,
            "name":spec_1.name,
            'mapped_roles': []
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

#Create Spec Test
@freeze_time("2022-10-05 09:19:17")
class TestCreateSpec(TestApp):
    
    def test_create_spec(self):
        request_body = {"spec_id":1,"spec_name":"Test"}

        response = self.client.post("/create_spec",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 201, "message": "Specialisation saved successfully."})

    def test_create_spec_duplicate_id(self):
        spec_1 = Spec(id=1,name="Test")
        db.session.add(spec_1)
        db.session.commit()

        request_body = {"spec_id":1,"spec_name":"Test 2"}

        response = self.client.post("/create_spec",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json,{'code': 401, 'message': 'Duplicate specialisation or id.'})

    def test_create_spec_duplicate_name(self):
        spec_1 = Spec(id=1,name="Test")
        db.session.add(spec_1)
        db.session.commit()


        request_body = {"spec_id":2,"spec_name":"Test"}
        response = self.client.post("/create_spec",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json,{'code': 401, 'message': 'Duplicate specialisation or id.'})

    def test_create_spec_no_id(self):
        request_body = {"spec_name":"Test"}

        response = self.client.post("/create_spec",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving specialisation to database."})

    def test_create_spec_non_json_request(self):
        response = self.client.post("/create_spec",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code": 403, "message": "Invalid input"})

#Get Spec Test
@freeze_time("2022-10-05 09:19:17")
class TestGetSpec(TestApp):
    
    def test_get_spec(self):
        spec_1 = Spec(id=1,name="Test")
        db.session.add(spec_1)
        db.session.commit()

        response = self.client.get("/get_spec/1")

        self.assertEqual(response.json, {"code":200,
                                        "content": {"id":1,"name":"Test"}})

    def test_get_spec_wrong_id(self):
        spec_1 = Spec(id=1,name="Test")
        db.session.add(spec_1)
        db.session.commit()

        response = self.client.get("/get_spec/123")

        self.assertEqual(response.json, {"code": 404,"message": "Specialisation not found"})

#Get All Spec Test
@freeze_time("2022-10-05 09:19:17")
class TestGetAllSpec(TestApp):
    
    def test_get_all_spec(self):
        spec_1 = Spec(id=1,name="Test")
        spec_2 = Spec(id=2,name="Test 2")
        db.session.add(spec_1)
        db.session.add(spec_2)
        db.session.commit()

        response = self.client.get("/get_all_specs")

        self.assertEqual(response.json["code"], 200)
        return_data = sorted(response.json["content"], key=lambda x: x["id"])
        self.assertEqual(return_data,[{'id': 1,'mapped_roles': [],
                                        'name': 'Test'},
                                        {'id': 2,'mapped_roles': [],
                                        'name': 'Test 2'}]) 

#Update Spec Test
class TestUpdateSpec(TestApp):
    
    def test_update_spec(self):
        spec_1 = Spec(id=1,name="Test")
        db.session.add(spec_1)
        db.session.commit()

        request_body = {"spec_id":1,"spec_name":"Test 2"}

        response = self.client.post("/update_spec",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":201,
                                        "message":"Specialisation updated successfully."})
        
    def test_update_spec_duplicate_name(self):
        spec_1 = Spec(id=1,name="Test")
        spec_2 = Spec(id=2,name="Test 2")
        db.session.add(spec_1)
        db.session.add(spec_2)
        db.session.commit()

        request_body = {"spec_id":1,"spec_name":"Test 2"}

        response = self.client.post("/update_spec",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving specialisation to database."})

    def test_update_spec_wrong_id(self):
        spec_1 = Spec(id=1,name="Test")
        db.session.add(spec_1)
        db.session.commit()

        request_body = {"spec_id":2,"spec_name":"Test 2"}

        response = self.client.post("/update_spec",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":404,
                                        "message":"Specialisation id not found in Database."})

    def test_update_spec_no_id(self):
        spec_1 = Spec(id=1,name="Test")
        db.session.add(spec_1)
        db.session.commit()

        request_body = {"spec_name":"Java"}

        response = self.client.post("/update_spec",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving specialisation to database."})

    def test_update_spec_no_name(self):
        spec_1 = Spec(id=1,name="Test")
        db.session.add(spec_1)
        db.session.commit()

        request_body = {"spec_id":1}

        response = self.client.post("/update_spec",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving specialisation to database."})

    def test_update_spec_non_json_request(self):
        spec_1 = Spec(id=1,name="Test")
        db.session.add(spec_1)
        db.session.commit()

        response = self.client.post("/update_spec",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code":403,
                                        "message":"Invalid input"})

#Delete Spec Test
class TestDeleteSpec(TestApp):
    
    def test_delete_spec(self):
        spec_1 = Spec(id=1,name="Test")
        db.session.add(spec_1)
        db.session.commit()

        response = self.client.delete("/delete_spec/1")

        self.assertEqual(response.json, {"code":201,
                                        "message":"Specialisation deleted successfully."})

    def test_delete_spec_wrong_id(self):
        spec_1 = Spec(id=1,name="Test")
        db.session.add(spec_1)
        db.session.commit()

        response = self.client.delete("/delete_spec/2")

        self.assertEqual(response.json, {"code":404,
                                        "message":"No specialisation id not found in Database."})

#Add Course Skill Test
class TestAddSpecRole(TestApp):
    
    def test_add_role_skill(self):
        spec_1 = Spec(id=1,name="Test")
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        db.session.add(spec_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        request_body = {"spec_id":1,"role_id":[1,2]}

        response = self.client.post("/add_spec_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":201,
                                        "message":"Mapping saved successfully."})

    def test_add_spec_role_no_spec_id(self):
        spec_1 = Spec(id=1,name="Test")
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        db.session.add(spec_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        request_body = {"role_id":[1,2]}

        response = self.client.post("/add_spec_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving mapping to database."})

    def test_add_spec_role_no_role_id(self):
        spec_1 = Spec(id=1,name="Test")
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        db.session.add(spec_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        request_body = {"spec_id":1}

        response = self.client.post("/add_spec_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving mapping to database."})

    def test_add_spec_role_wrong_spec_id(self):
        spec_1 = Spec(id=1,name="Test")
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        db.session.add(spec_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        request_body = {"spec_id":2,"role_id":[1,2]}

        response = self.client.post("/add_spec_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving mapping to database."})

    def test_add_spec_role_wrong_role_id(self):
        spec_1 = Spec(id=1,name="Test")
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        db.session.add(spec_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        request_body = {"spec_id":1,"role_id":[3,4]}

        response = self.client.post("/add_spec_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving mapping to database."})

    def test_add_spec_role_non_json_request(self):
        spec_1 = Spec(id=1,name="Test")
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        db.session.add(spec_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        response = self.client.post("/add_spec_role",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code":403,
                                        "message":"Invalid input"})

"""#Get Spec Role test
class TestGetSpecRole(TestApp):
    
    def test_get_spec_role(self):
        spec_1 = Spec(id=1,name="Test")
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        spec_1.mapped_roles.append(role_1)
        spec_1.mapped_roles.append(role_2)
        db.session.add(spec_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        response = self.client.get("/get_spec_role/1")

        self.assertEqual(response.json["code"], 200)
        return_data = sorted(response.json["content"], key=lambda x: x["id"])
        self.assertEqual(return_data,[{'desc': None,
                                        'exp_level': 1,
                                        'id': 1,'sala'
                                        'name': 'Programmer Intern'},
                                        {'desc': None,
                                        'exp_level': 2,
                                        'id': 2,
                                        'name': 'Programmer'}]) 

    def test_get_spec_role_wrong_id(self):
        spec_1 = Spec(id=1,name="Test")
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        spec_1.mapped_roles.append(role_1)
        spec_1.mapped_roles.append(role_2)
        db.session.add(spec_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        response = self.client.get("/get_spec_role/123")

        self.assertEqual(response.json, {"code":404,
                                        "message":"Spec Role mapping not found"})

    def test_get_spec_role_no_id(self):
        spec_1 = Spec(id=1,name="Test")
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        spec_1.mapped_roles.append(role_1)
        spec_1.mapped_roles.append(role_2)
        db.session.add(spec_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        response = self.client.get("/get_spec_role")

        self.assertEqual(response.json, None)"""

#Delete Spec Role Test
class TestDeleteSpecRole(TestApp):
    
    def test_delete_spec_role(self):
        spec_1 = Spec(id=1,name="Test")
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        spec_1.mapped_roles.append(role_1)
        spec_1.mapped_roles.append(role_2)
        db.session.add(spec_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        request_body = {"spec_id":1,"role_id":[1]}

        response = self.client.post("/delete_spec_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":201,
                                        "message":"Mapping deleted successfully."})

    def test_delete_spec_role_no_spec_id(self):
        spec_1 = Spec(id=1,name="Test")
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        spec_1.mapped_roles.append(role_1)
        spec_1.mapped_roles.append(role_2)
        db.session.add(spec_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        request_body = {"role_id":[1]}

        response = self.client.post("/delete_spec_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving mapping to database."})

    def test_delete_spec_role_no_role_id(self):
        spec_1 = Spec(id=1,name="Test")
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        spec_1.mapped_roles.append(role_1)
        spec_1.mapped_roles.append(role_2)
        db.session.add(spec_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        request_body = {"spec_id":1}

        response = self.client.post("/delete_spec_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving mapping to database."})

    def test_delete_spec_role_wrong_spec_id(self):
        spec_1 = Spec(id=1,name="Test")
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        spec_1.mapped_roles.append(role_1)
        spec_1.mapped_roles.append(role_2)
        db.session.add(spec_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        request_body = {"spec_id":2,"role_id":[1]}

        response = self.client.post("/delete_spec_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving mapping to database."})

    def test_delete_spec_role_non_json_request(self):
        spec_1 = Spec(id=1,name="Test")
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        spec_1.mapped_roles.append(role_1)
        spec_1.mapped_roles.append(role_2)
        db.session.add(spec_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        response = self.client.post("/delete_spec_role",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code":403,
                                        "message":"Invalid input"})