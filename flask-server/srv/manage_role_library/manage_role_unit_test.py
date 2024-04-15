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
from manage_role_lib import app,db
# Get the absolute path to the directory containing ORM_globals.py
orm_globals_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add the directory containing ORM_globals.py to sys.path
sys.path.insert(0, orm_globals_directory)
from ORM_globals import Keyword,Skill,Role,Spec

class TestCourseLib(unittest.TestCase):
    
    @freeze_time("2022-10-05 09:19:17")
    def test_to_dict(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level="Entry")
        self.assertEqual(role_1.to_dict(), {
            "id": role_1.id,
            "name":role_1.name,
            "mapped_keyw":[],
            "mapped_skills":[],
            "exp_level":"Entry",
            "desc":None,
            'salary': []
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

#Create Role Test
@freeze_time("2022-10-05 09:19:17")
class TestCreateRole(TestApp):
    
    def test_create_role(self):
        request_body = {"role_id":1,"role_name":"Programmer Intern",
                        "role_desc":"To code","exp_level":1}

        response = self.client.post("/create_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 201, "message": "Role saved successfully."})

    def test_create_role_duplicate_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        db.session.add(role_1)
        db.session.commit()

        request_body = {"role_id":1,"role_name":"Matketing Intern",
                        "role_desc":"To do stuffs","exp_level":1}
        response = self.client.post("/create_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json,{"code": 401,"message": "Duplicate role or id."})

    def test_create_role_duplicate_name(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        db.session.add(role_1)
        db.session.commit()

        request_body = {"role_id":1,"role_name":"Programmer Intern",
                        "role_desc":"To do stuffs","exp_level":1}
        response = self.client.post("/create_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json,{"code": 401,"message": "Duplicate role or id."})

    def test_create_role_no_id(self):
        request_body = {"role_name":"Programmer Intern",
                        "role_desc":"To do stuffs","exp_level":1}

        response = self.client.post("/create_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving role to database."})

    def test_create_role_no_exp_level(self):
        request_body = {"role_id":1,"role_name":"Programmer Intern",
                        "role_desc":"To code"}

        response = self.client.post("/create_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving role to database."})

    def test_create_role_non_json_request(self):
        response = self.client.post("/create_role",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code": 403, "message": "Invalid input"})

#Get Role Test
@freeze_time("2022-10-05 09:19:17")
class TestGetRole(TestApp):
    
    def test_get_role(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.get("/get_role/1")

        self.assertEqual(response.json, {"code": 200, "content": 
                                        {'desc': None,'exp_level': 1,
                                        'id': 1,'name': 'Programmer Intern',
                                        'salary': 0}})

    def test_get_keyword_wrong_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.get("/get_role/123")

        self.assertEqual(response.json, {"code": 404, "message": "Role not found"})

#Get All Role Test
@freeze_time("2022-10-05 09:19:17")
class TestGetAllRole(TestApp):
    
    def test_get_all_role(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Marketing Intern",exp_level=1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()

        response = self.client.get("/get_all_roles")

        self.assertEqual(response.json, {"code": 200, "content": 
                                        [{'desc': None,'exp_level': 1,
                                        'id': 1,'name': 'Programmer Intern','salary': 0},
                                        {'desc': None,'exp_level': 1,
                                        'id': 2,'name': 'Marketing Intern','salary': 0}]})

#Update Role Test
@freeze_time("2022-10-05 09:19:17")
class TestUpdateRole(TestApp):
    
    def test_update_role(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        db.session.add(role_1)
        db.session.commit()

        request_body = {"role_id":1,"role_name":"Marketing Intern",
                        "role_desc":"To do some stuffs","exp_level":1}

        response = self.client.post("/update_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 201, "message": "Role updated successfully."})

    def test_update_role_duplicate_name(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Marketing Intern",exp_level=1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.commit()
        request_body = {"role_id":1,"role_name":"Marketing Intern",
                        "role_desc":"To do some stuffs","exp_level":1}

        response = self.client.post("/update_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving role to database."})

    def test_update_role_no_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        db.session.add(role_1)
        db.session.commit()

        request_body = {"role_name":"Marketing Intern",
                        "role_desc":"To do some stuffs","exp_level":1}

        response = self.client.post("/update_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving role to database."})

    def test_update_role_no_name(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        db.session.add(role_1)
        db.session.commit()

        request_body = {"role_id":1,
                        "role_desc":"To do some stuffs","exp_level":1}

        response = self.client.post("/update_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving role to database."})

    def test_update_role_no_name(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        db.session.add(role_1)
        db.session.commit()

        request_body = {"role_id":1,"role_name":"Marketing Intern",
                        "role_desc":"To do some stuffs"}

        response = self.client.post("/update_role",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving role to database."})

    def test_update_role_non_json_request(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.post("/update_role",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code": 403, "message": "Invalid input"})

#Delete Role Test
@freeze_time("2022-10-05 09:19:17")
class TestDeleteRole(TestApp):
    
    def test_delete_role(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.delete("/delete_role/1")

        self.assertEqual(response.json, {"code": 201, "message": "Role deleted successfully."})

    def test_delete_role_no_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.delete("/delete_role")

        self.assertEqual(response.json, None)

    def test_delete_role_wrong_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.delete("/delete_role/123")

        self.assertEqual(response.json, {"code": 404, "message": "No role id not found in Database."})

#Add Role Skill Test
class TestAddRoleSkill(TestApp):
    
    def test_add_role_skill(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        db.session.add(role_1)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        request_body = {"role_id":1,"skill_id":[1,2]}

        response = self.client.post("/add_role_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":201,
                                        "message":"role saved successfully."})

    def test_add_role_skill_no_role_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        db.session.add(role_1)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        request_body = {"skill_id":[1,2]}

        response = self.client.post("/add_role_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving role to database."})

    def test_add_role_skill_no_skill_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        db.session.add(role_1)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        request_body = {"role_id":1}

        response = self.client.post("/add_role_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving role to database."})

    def test_add_role_skill_wrong_role_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        db.session.add(role_1)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        request_body = {"role_id":234,"skill_id":[1,2]}

        response = self.client.post("/add_role_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving role to database."})

    def test_add_role_skill_wrong_skill_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        db.session.add(role_1)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        request_body = {"role_id":"IS111","skill_id":[3,4]}

        response = self.client.post("/add_role_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving role to database."})

    def test_add_role_skill_non_json_request(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        db.session.add(role_1)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        response = self.client.post("/add_role_skill",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code":403,
                                        "message":"Invalid input"})

#Add Role Keyword Test
class TestAddRoleKeyword(TestApp):
    
    def test_add_role_keyword(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Programming")
        db.session.add(role_1)
        db.session.add(keyword_1)
        db.session.add(keyword_2)
        db.session.commit()

        request_body = {"role_id":1,"keyw_id":[1,2]}

        response = self.client.post("/add_role_keyw",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":201,
                                        "message":"Role keyword saved successfully."})

    def test_add_role_keyword_no_role_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Programming")
        db.session.add(role_1)
        db.session.add(keyword_1)
        db.session.add(keyword_2)
        db.session.commit()

        request_body = {"keyw_id":[1,2]}

        response = self.client.post("/add_role_keyw",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving role to database."})

    def test_add_role_keyword_no_keyword_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        db.session.add(role_1)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        request_body = {"role_id":1}

        response = self.client.post("/add_role_keyw",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving role to database."})

    def test_add_role_keyword_wrong_role_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Programming")
        db.session.add(role_1)
        db.session.add(keyword_1)
        db.session.add(keyword_2)
        db.session.commit()

        request_body = {"role_id":234,"keyw_id":[1,2]}

        response = self.client.post("/add_role_keyw",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving role to database."})

    def test_add_role_keyword_wrong_keyword_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Programming")
        db.session.add(role_1)
        db.session.add(keyword_1)
        db.session.add(keyword_2)
        db.session.commit()

        request_body = {"role_id":"IS111","keyw_id":[3,4]}

        response = self.client.post("/add_role_keyw",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving role to database."})

    def test_add_role_skill_non_json_request(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Programming")
        db.session.add(role_1)
        db.session.add(keyword_1)
        db.session.add(keyword_2)
        db.session.commit()

        response = self.client.post("/add_role_keyw",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code":403,
                                        "message":"Invalid input"})

#Get Role Skill Test
class TestGetRoleSkill(TestApp):
    
    def test_get_role_skill(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        role_1.mapped_skills.append(skill_1)
        role_1.mapped_skills.append(skill_2)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.get("/get_role_skill/1")

        self.assertEqual(response.json["code"], 200)
        return_data = sorted(response.json["content"], key=lambda x: x["id"])
        self.assertEqual(return_data,[{'id': 1, 'name': 'Python'},{'id': 2, 'name': 'Programming'}]) 

    def test_get_role_skill_wrong_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        role_1.mapped_skills.append(skill_1)
        role_1.mapped_skills.append(skill_2)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.get("get_role_skill/321")

        self.assertEqual(response.json, {"code":404,
                                        "message":"role not found"})

    def test_get_role_skill_no_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        role_1.mapped_skills.append(skill_1)
        role_1.mapped_skills.append(skill_2)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.get("/get_role_skill/")

        self.assertEqual(response.json, None)

#Get Role Keyword Test
class TestGetRoleKeyword(TestApp):
    
    def test_get_role_keyword(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Programming")
        role_1.mapped_keyw.append(keyword_1)
        role_1.mapped_keyw.append(keyword_2)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.get("/get_role_keyw/1")

        self.assertEqual(response.json["code"], 200)
        return_data = sorted(response.json["content"], key=lambda x: x["id"])
        self.assertEqual(return_data,[{'id': 1, 'name': 'Python'},{'id': 2, 'name': 'Programming'}])                                

    def test_get_role_keyword_wrong_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Programming")
        role_1.mapped_keyw.append(keyword_1)
        role_1.mapped_keyw.append(keyword_2)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.get("/get_role_keyw/321")

        self.assertEqual(response.json, {"code":404,
                                        "message":"role not found"})

    def test_get_role_keyword_no_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Programming")
        role_1.mapped_keyw.append(keyword_1)
        role_1.mapped_keyw.append(keyword_2)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.get("/get_role_keyw/")

        self.assertEqual(response.json, None)

#Delete Role Skill Test
class TestDeleteRoleSkill(TestApp):
    
    def test_delete_role_skill(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        role_1.mapped_skills.append(skill_1)
        role_1.mapped_skills.append(skill_2)
        db.session.add(role_1)
        db.session.commit()

        request_body = {"role_id":1,"skill_id":[1]}

        response = self.client.post("/delete_role_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":201,
                                        "message":"Mapping deleted successfully."})

        response = self.client.get("/get_role_skill/1")

        self.assertEqual(response.json, {"code":200,
                                        "content":[{"id":2,"name":"Programming"}]})

    def test_delete_role_skill_no_role_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        role_1.mapped_skills.append(skill_1)
        role_1.mapped_skills.append(skill_2)
        db.session.add(role_1)
        db.session.commit()

        request_body = {"skill_id":[1]}

        response = self.client.post("/delete_role_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error Handling request"})

    def test_delete_role_skill_no_skill_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        role_1.mapped_skills.append(skill_1)
        role_1.mapped_skills.append(skill_2)
        db.session.add(role_1)
        db.session.commit()

        request_body = {"role_id":"IS111"}

        response = self.client.post("/delete_role_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error Handling request"})

    def test_delete_role_skill_wrong_role_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        role_1.mapped_skills.append(skill_1)
        role_1.mapped_skills.append(skill_2)
        db.session.add(role_1)
        db.session.commit()

        request_body = {"role_id":111,"skill_id":[1]}

        response = self.client.post("/delete_role_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error Handling request"})

    def test_delete_role_skill_non_json_request(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        role_1.mapped_skills.append(skill_1)
        role_1.mapped_skills.append(skill_2)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.post("/delete_role_skill",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code":403,
                                        "message":"Invalid input"})

#Delete Role Keyword Test
class TestDeleteRoleKeyword(TestApp):
    
    def test_delete_role_keyword(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Programming")
        role_1.mapped_keyw.append(keyword_1)
        role_1.mapped_keyw.append(keyword_2)
        db.session.add(role_1)
        db.session.commit()

        request_body = {"role_id":1,"keyw_id":[1]}

        response = self.client.post("/delete_role_keyw",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":201,
                                        "message":"Role Keyword deleted successfully."})

        response = self.client.get("/get_role_keyw/1")

        self.assertEqual(response.json, {"code":200,
                                        "content":[{"id":2,"name":"Programming"}]})

    def test_delete_role_keyword_no_role_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Programming")
        role_1.mapped_keyw.append(keyword_1)
        role_1.mapped_keyw.append(keyword_2)
        db.session.add(role_1)
        db.session.commit()

        request_body = {"keyw_id":[1]}

        response = self.client.post("/delete_role_keyw",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving role to database."})

    def test_delete_role_keyword_no_keyword_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Programming")
        role_1.mapped_keyw.append(keyword_1)
        role_1.mapped_keyw.append(keyword_2)
        db.session.add(role_1)
        db.session.commit()

        request_body = {"role_id":"IS111"}

        response = self.client.post("/delete_role_keyw",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving role to database."})

    def test_delete_role_keyword_wrong_role_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Programming")
        role_1.mapped_keyw.append(keyword_1)
        role_1.mapped_keyw.append(keyword_2)
        db.session.add(role_1)
        db.session.commit()

        request_body = {"role_id":111,"keyw_id":[1]}

        response = self.client.post("/delete_role_keyw",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving role to database."})

    def test_delete_role_keyword_non_json_request(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        keyword_1 = Keyword(id=1,name="Python")
        keyword_2 = Keyword(id=2,name="Programming")
        role_1.mapped_keyw.append(keyword_1)
        role_1.mapped_keyw.append(keyword_2)
        db.session.add(role_1)
        db.session.commit()

        response = self.client.post("/delete_role_keyw",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code":403,
                                        "message":"Invalid input"})


#Get Role Spec Test
class TestGetSpecMapped(TestApp):
    
    def test_get_spec_mapped(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        spec_1 = Spec(id=1,name="Test")
        spec_1.mapped_roles.append(role_1)
        db.session.add(role_1)
        db.session.add(spec_1)
        db.session.commit()

        response = self.client.get("/get_spec_mapped/1")

        self.assertEqual(response.json, {"code":200,
                                        "content":[{'id': 1, 'name': 'Test'}]})

    def test_get_role_spec_wrong_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        spec_1 = Spec(id=1,name="Test")
        spec_1.mapped_roles.append(role_1)
        db.session.add(role_1)
        db.session.add(spec_1)
        db.session.commit()

        response = self.client.get("/get_spec_mapped/321")

        self.assertEqual(response.json, {"code":404,
                                        "message":"role not found"})

    def test_get_role_spec_no_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        spec_1 = Spec(id=1,name="Test")
        spec_1.mapped_roles.append(role_1)
        db.session.add(role_1)
        db.session.add(spec_1)
        db.session.commit()

        response = self.client.get("/get_spec_mapped/")

        self.assertEqual(response.json, None)