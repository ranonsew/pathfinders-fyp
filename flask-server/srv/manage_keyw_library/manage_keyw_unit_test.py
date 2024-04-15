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
from manage_keyw_lib import app,db

# Get the absolute path to the directory containing ORM_globals.py
orm_globals_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add the directory containing ORM_globals.py to sys.path
sys.path.insert(0, orm_globals_directory)
from ORM_globals import Keyword,Skill,Role

class TestCourseLib(unittest.TestCase):
    
    @freeze_time("2022-10-05 09:19:17")
    def test_to_dict(self):
        keyword_1 = Keyword(id=1,name="Python")
        self.assertEqual(keyword_1.to_dict(), {
            'id': keyword_1.id,
            "name":keyword_1.name,
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

#Create Keyword Test
@freeze_time("2022-10-05 09:19:17")
class TestCreateKeyword(TestApp):
    
    def test_create_keyword(self):
        request_body = {"keyword_id":1,"keyword_name":"Python"}

        response = self.client.post("/create_keyword",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 201, "message": "Keyword saved successfully."})

    def test_create_keyword_duplicate_keyword(self):
        keyword_1 = Keyword(id=1,name="Python")
        db.session.add(keyword_1)
        db.session.commit()

        request_body = {"keyword_id":1,"keyword_name":"Python"}
        response = self.client.post("/create_keyword",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json,{"code": 401,"message": "Duplicate keyword or id."})

    def test_create_keyword_no_id(self):
        request_body = {"keyword_name":"Python"}

        response = self.client.post("/create_keyword",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving keyword to database."})

    def test_create_keyword_no_name(self):
        request_body = {"keyword_id":1}

        response = self.client.post("/create_keyword",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving keyword to database."})

    def test_create_keyword_non_json_request(self):
        response = self.client.post("/create_keyword",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code": 403, "message": "Invalid input"})

#Get Keyword Test
@freeze_time("2022-10-05 09:19:17")
class TestGetKeyword(TestApp):
    
    def test_get_keyword(self):
        keyword_1 = Keyword(id=1,name="Python")
        db.session.add(keyword_1)
        db.session.commit()

        response = self.client.get("/get_keyword/1")

        self.assertEqual(response.json, {"code": 200, "content": {"id":1,"name":"Python"}})

    def test_get_keyword_wrong_id(self):
        keyword_1 = Keyword(id=1,name="Python")
        db.session.add(keyword_1)
        db.session.commit()

        response = self.client.get("/get_keyword/1000")

        self.assertEqual(response.json, {"code": 404, "message": "Keyword not found"})

#Get All Keyword Test
@freeze_time("2022-10-05 09:19:17")
class TestGetAllKeyword(TestApp):
    
    def test_get_all_keyword(self):
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Java")
        db.session.add(keyword_1)
        db.session.add(keyword_2)
        db.session.commit()

        response = self.client.get("/get_all_keywords")

        self.assertEqual(response.json["code"], 200)
        return_data = sorted(response.json["content"], key=lambda x: x["id"])
        self.assertEqual(return_data,[{'id': 1, 'name': 'Python'},{'id': 2, 'name': 'Java'}]) 
        
#Update Keyword Test
@freeze_time("2022-10-05 09:19:17")
class TestUpdateKeyword(TestApp):
    
    def test_update_keyword(self):
        keyword_1 = Keyword(id=1,name="Python")
        db.session.add(keyword_1)
        db.session.commit()
        request_body = {"keyword_id":1,"keyword_name":"Java"}

        response = self.client.post("/update_keyword",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 201, "message": "Keyword updated successfully."})

    def test_update_keyword_duplicate_name(self):
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Java")
        db.session.add(keyword_1)
        db.session.add(keyword_2)
        db.session.commit()
        request_body = {"keyword_id":1,"keyword_name":"Java"}

        response = self.client.post("/update_keyword",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving keyword to database."})

    def test_update_keyword_no_id(self):
        keyword_1 = Keyword(id=1,name="Python")
        db.session.add(keyword_1)
        db.session.commit()
        request_body = {"keyword_name":"Java"}

        response = self.client.post("/update_keyword",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving keyword to database."})

    def test_update_keyword_no_name(self):
        keyword_1 = Keyword(id=1,name="Python")
        db.session.add(keyword_1)
        db.session.commit()
        request_body = {"keyword_name":"Java"}

        response = self.client.post("/update_keyword",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving keyword to database."})

    def test_update_keyword_non_json_request(self):
        keyword_1 = Keyword(id=1,name="Python")
        db.session.add(keyword_1)
        db.session.commit()

        response = self.client.post("/update_keyword",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code": 403, "message": "Invalid input"})

#Delete Keyword Test
@freeze_time("2022-10-05 09:19:17")
class TestDeleteKeyword(TestApp):
    
    def test_delete_keyword(self):
        keyword_1 = Keyword(id=1,name="Python")
        db.session.add(keyword_1)
        db.session.commit()

        response = self.client.delete("/delete_keyword/1")

        self.assertEqual(response.json, {"code": 201, "message": "Keyword deleted successfully."})

    def test_delete_keyword_no_id(self):
        keyword_1 = Keyword(id=1,name="Python")
        db.session.add(keyword_1)
        db.session.commit()

        response = self.client.delete("/delete_keyword")

        self.assertEqual(response.json, None)

    def test_delete_keyword_wrong_id(self):
        keyword_1 = Keyword(id=1,name="Python")
        db.session.add(keyword_1)
        db.session.commit()

        response = self.client.delete("/delete_keyword/123")

        self.assertEqual(response.json, {"code": 404, "message": "No keyword id not found in Database."})

#Get Mapped Role Test
@freeze_time("2022-10-05 09:19:17")
class TestGetMappedRole(TestApp):
    
    def test_get_mapped_role(self):
        keyword_1 = Keyword(id=1,name="Python")
        skill_1 = Skill(id=1,name="Programming")
        role_1 = Role(id=1,name="Programming Intern",exp_level="Entry")
        role_1.mapped_skills.append(skill_1)
        role_1.mapped_keyw.append(keyword_1)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.get("/get_roles_mapped/1")

        self.assertEqual(response.json, {"code": 200, "content": 
                                        [{'desc': None,
                                        'exp_level': 'Entry',
                                        'id': 1,
                                        'name':'Programming Intern', 'salary': []}]})

    def test_get_mapped_role_wrong_id(self):
        keyword_1 = Keyword(id=1,name="Python")
        skill_1 = Skill(id=1,name="Programming")
        role_1 = Role(id=1,name="Programming Intern",exp_level="Entry")
        role_1.mapped_skills.append(skill_1)
        role_1.mapped_keyw.append(keyword_1)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.get("/get_roles_mapped/2")

        self.assertEqual(response.json, {"code": 404,"message": "No mapped roles found"})