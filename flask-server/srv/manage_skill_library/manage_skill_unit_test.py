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
from manage_skill_lib import app,db
# Get the absolute path to the directory containing ORM_globals.py
orm_globals_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add the directory containing ORM_globals.py to sys.path
sys.path.insert(0, orm_globals_directory)
from ORM_globals import Skill,Course,Role

class TestCourseLib(unittest.TestCase):
    
    @freeze_time("2022-10-05 09:19:17")
    def test_to_dict(self):
        skill_1 = Skill(id=1,name="Python")
        self.assertEqual(skill_1.to_dict(), {
            "id": skill_1.id,
            "name":skill_1.name
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

#Create Skill Test
@freeze_time("2022-10-05 09:19:17")
class TestCreateSkill(TestApp):
    
    def test_create_skill(self):
        request_body = {"skill_id":1,"skill_name":"Python"}

        response = self.client.post("/create_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 201, "message": "Skill saved successfully."})

    def test_create_skill_duplicate_id(self):
        skill_1 = Skill(id=1,name="Python")
        db.session.add(skill_1)
        db.session.commit()

        request_body = {"skill_id":1,"skill_name":"Java"}

        response = self.client.post("/create_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json,{"code": 401,"message": "Duplicate skill or id."})

    def test_create_skill_duplicate_name(self):
        skill_1 = Skill(id=1,name="Python")
        db.session.add(skill_1)
        db.session.commit()

        request_body = {"skill_id":2,"skill_name":"Python"}
        response = self.client.post("/create_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json,{"code": 401,"message": "Duplicate skill or id."})

    def test_create_skill_no_id(self):
        request_body = {"skill_name":"Python"}

        response = self.client.post("/create_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving skill to database."})

    def test_create_skill_non_json_request(self):
        response = self.client.post("/create_skill",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code": 403, "message": "Invalid input"})

#Get Skill Test
@freeze_time("2022-10-05 09:19:17")
class TestGetSkill(TestApp):
    
    def test_get_skill(self):
        skill_1 = Skill(id=1,name="Python")
        db.session.add(skill_1)
        db.session.commit()

        response = self.client.get("/get_skill/1")

        self.assertEqual(response.json, {"code":200,
                                        "content": {"id":1,"name":"Python"}})

    def test_get_skill_wrong_id(self):
        skill_1 = Skill(id=1,name="Python")
        db.session.add(skill_1)
        db.session.commit()

        response = self.client.get("/get_skill/123")

        self.assertEqual(response.json, {"code": 404,"message": "Skill not found"})

#Get All Skill Test
@freeze_time("2022-10-05 09:19:17")
class TestGetAllSkill(TestApp):
    
    def test_get_all_course(self):
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Java")
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        response = self.client.get("/get_all_skills")

        self.assertEqual(response.json["code"], 200)
        return_data = sorted(response.json["content"], key=lambda x: x["id"])
        self.assertEqual(return_data,[{'id': 1, 'name': 'Python'},{'id': 2, 'name': 'Java'}]) 

#Update Skill Test
class TestUpdateSkill(TestApp):
    
    def test_update_skill(self):
        skill_1 = Skill(id=1,name="Python")
        db.session.add(skill_1)
        db.session.commit()

        request_body = {"skill_id":1,"skill_name":"Java"}

        response = self.client.post("/update_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":201,
                                        "message":"Skill updated successfully."})
        
    def test_update_skill_duplicate_name(self):
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Java")
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        request_body = {"skill_id":1,"skill_name":"Java"}

        response = self.client.post("/update_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving skill to database."})

    def test_update_skill_wrong_id(self):
        skill_1 = Skill(id=1,name="Python")
        db.session.add(skill_1)
        db.session.commit()

        request_body = {"skill_id":2,"skill_name":"Java"}

        response = self.client.post("/update_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":404,
                                        "message":"Skill id not found in Database."})

    def test_update_skill_no_id(self):
        skill_1 = Skill(id=1,name="Python")
        db.session.add(skill_1)
        db.session.commit()

        request_body = {"skill_name":"Java"}

        response = self.client.post("/update_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving skill to database."})

    def test_update_skill_no_name(self):
        skill_1 = Skill(id=1,name="Python")
        db.session.add(skill_1)
        db.session.commit()

        request_body = {"skill_id":1}

        response = self.client.post("/update_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving skill to database."})

    def test_update_skill_non_json_request(self):
        skill_1 = Skill(id=1,name="Python")
        db.session.add(skill_1)
        db.session.commit()

        response = self.client.post("/update_skill",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code":403,
                                        "message":"Invalid input"})
        
#Delete Skill Test
class TestDeleteSkill(TestApp):
    
    def test_delete_course(self):
        skill_1 = Skill(id=1,name="Python")
        db.session.add(skill_1)
        db.session.commit()

        response = self.client.delete("/delete_skill/1")

        self.assertEqual(response.json, {"code":201,
                                        "message":"Skill deleted successfully."})

    def test_delete_skill_wrong_id(self):
        skill_1 = Skill(id=1,name="Python")
        db.session.add(skill_1)
        db.session.commit()

        response = self.client.delete("/delete_skill/2")

        self.assertEqual(response.json, {"code":404,
                                        "message":"No skill id not found in Database."})
        
#Get Course Mapped test
class TestGetCourseMapped(TestApp):
    
    def test_get_course_mapped(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        skill_1 = Skill(id=1,name="Python")
        course_1.mapped_skills.append(skill_1)
        course_2.mapped_skills.append(skill_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.add(skill_1)
        db.session.commit()

        response = self.client.get("/get_course_mapped/1")

        self.assertEqual(response.json["code"], 200)

        return_data = sorted(response.json["content"], key=lambda x: x["id"])
        self.assertEqual(return_data, [{'id': 'CS440', 
                                        'name': 'Foundation of Cybersecurity'}
                                        ,{'id': 'IS111', 
                                        'name': 'Introduction to Programming'}])

    def test_get_course_mapped_wrong_id(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        skill_1 = Skill(id=1,name="Python")
        course_1.mapped_skills.append(skill_1)
        course_2.mapped_skills.append(skill_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.add(skill_1)
        db.session.commit()

        response = self.client.get("/get_course_mapped/123")

        self.assertEqual(response.json, {"code":404,
                                        "message":"No mapped course found"})

    def test_get_course_mapped_no_id(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        skill_1 = Skill(id=1,name="Python")
        course_1.mapped_skills.append(skill_1)
        course_2.mapped_skills.append(skill_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.add(skill_1)
        db.session.commit()

        response = self.client.get("/get_course_mapped")

        self.assertEqual(response.json, None)

#Get Roles Mapped test
class TestGetRolesMapped(TestApp):
    @freeze_time("2022-10-05 09:19:17")
    def test_get_roles_mapped(self):
        """role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        skill_1 = Skill(id=1,name="Python")
        role_1.mapped_skills.append(skill_1)
        role_2.mapped_skills.append(skill_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.add(skill_1)
        db.session.commit()

        response = self.client.get("/get_roles_mapped/1")

        self.assertEqual(response.json["code"], 200)
        return_data = sorted(response.json["content"], key=lambda x: x["id"])
        self.assertEqual(return_data,[{'desc': None,
                                        'exp_level': 1,
                                        'id': 1,
                                        'name': 'Programmer Intern','salary': []},
                                        {'desc': None,
                                        'exp_level': 2,
                                        'id': 2,
                                        'name': 'Programmer','salary': []}])""" 

    def test_get_roles_mapped_wrong_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        skill_1 = Skill(id=1,name="Python")
        role_1.mapped_skills.append(skill_1)
        role_2.mapped_skills.append(skill_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.add(skill_1)
        db.session.commit()

        response = self.client.get("/get_roles_mapped/123")

        self.assertEqual(response.json, {"code":404,
                                        "message":"No mapped roles found"})

    def test_get_roles_mapped_no_id(self):
        role_1 = Role(id=1,name="Programmer Intern",exp_level=1)
        role_2 = Role(id=2,name="Programmer",exp_level=2)
        skill_1 = Skill(id=1,name="Python")
        role_1.mapped_skills.append(skill_1)
        role_2.mapped_skills.append(skill_1)
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.add(skill_1)
        db.session.commit()

        response = self.client.get("/get_course_mapped")

        self.assertEqual(response.json, None)

