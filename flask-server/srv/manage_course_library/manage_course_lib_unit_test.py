import unittest
import flask_testing
import json
from unittest.mock import patch
from freezegun import freeze_time
import os
import sys
# Get the absolute path to the directory containing ORM_globals.py
orm_globals_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Get the directory containing the unit test file
unit_test_directory = os.path.abspath(os.path.dirname(__file__))

# Get the directory containing the module you want to import (manage_course_lib.py)
module_directory = os.path.abspath(os.path.join(unit_test_directory, ""))

# Add the directory containing the module to sys.path
sys.path.insert(0, module_directory)

# Now you can import the module
from manage_course_lib import app,db

# Add the directory containing ORM_globals.py to sys.path
sys.path.insert(0, orm_globals_directory)
from ORM_globals import Course, Skill
import ORM_globals

class TestCourseLib(unittest.TestCase):
    
    @freeze_time("2022-10-05 09:19:17")
    def test_to_dict(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        self.assertEqual(course_1.to_dict(), {
            'id': course_1.id,
            "name":course_1.name,
            "mapped_skills":[]
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

#Create Course Test
@freeze_time("2022-10-05 09:19:17")
class TestCreateCourse(TestApp):
    
    def test_create_course(self):
        request_body = {"course_id":"IS111","course_name":"Intro to Programming"}

        response = self.client.post("/create_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 201, "message": "Course saved successfully."})

    def test_create_course_no_course_name(self):
        request_body = {"course_id":"IS111"}

        response = self.client.post("/create_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json,{"code": 500,"message": "Error saving course to database."})

    def test_create_course_no_course_id(self):
        request_body = {"course_name":"Intro to Programming"}

        response = self.client.post("/create_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json,{"code": 500,"message": "Error saving course to database."})

    def test_create_course_duplicate_id(self):
        course_1 = Course(id="IS111",name="Intro to Programming")
        db.session.add(course_1)
        db.session.commit()
        request_body = {"course_id":"IS111","course_name":"Foundation of Cybersecurity"}

        response = self.client.post("/create_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')
        
    def test_create_course_duplicate_name(self):
        course_1 = Course(id="IS111",name="Intro to Programming")
        db.session.add(course_1)
        db.session.commit()
        request_body = {"course_id":"CS440","course_name":"Intro to Programming"}

        response = self.client.post("/create_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 401,"message": "Duplicate course or id."})

    def test_create_course_non_json_request(self):
        response = self.client.post("/create_course",
                                    data="Non json data")

        self.assertEqual(response.json, {"code": 403,"message": "Invalid input"})

#Get Course Test
@freeze_time("2022-10-05 09:19:17")
class TestGetCourseLib(TestApp):
    
    def test_get_course_lib(self):
        course_1 = Course(id="IS111",name="Intro to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        response = self.client.get("/get_course/IS111")

        self.assertEqual(response.json, {"code":200,
                                        "content": {"id":"IS111","name":"Intro to Programming"}})

    def test_get_course_lib_wrong_id(self):
        course_1 = Course(id="IS111",name="Intro to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        response = self.client.get("/get_course/wrong_id")

        self.assertEqual(response.json, {"code": 404,"message": "Course not found"})

#Get All Course Test
@freeze_time("2022-10-05 09:19:17")
class TestGetAllCourse(TestApp):
    
    def test_get_all_course(self):
        course_1 = Course(id="IS111",name="Intro to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        response = self.client.get("/get_all_courses")

        self.assertEqual(response.json, {"code":200,
                                        "content": [{"id":"IS111","name":"Intro to Programming"},
                                                    {"id":"CS440","name":"Foundation of Cybersecurity"}]})

#Update Course Test
class TestUpdateCourse(TestApp):
    
    def test_update_course(self):
        course_1 = Course(id="IS111",name="Wrong Name")
        db.session.add(course_1)
        db.session.commit()

        request_body = {"course_id":"IS111","course_name":"Intro to Programming"}

        response = self.client.post("/update_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":201,
                                        "message":"Course updated successfully."})

    def test_update_course_duplicate_name(self):
        course_1 = Course(id="IS111",name="Wrong Name")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        request_body = {"course_id":"IS111","course_name":"Foundation of Cybersecurity"}

        response = self.client.post("/update_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving course to database."})

    def test_update_course_wrong_id(self):
        course_1 = Course(id="IS111",name="Wrong Name")
        db.session.add(course_1)
        db.session.commit()

        request_body = {"course_id":"IS321","course_name":"Intro to Programming"}

        response = self.client.post("/update_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":404,
                                        "message":"Course id not found in Database."})

    def test_update_course_no_id(self):
        course_1 = Course(id="IS111",name="Wrong Name")
        db.session.add(course_1)
        db.session.commit()

        request_body = {"course_name":"Intro to Programming"}

        response = self.client.post("/update_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving course to database."})

    def test_update_course_no_name(self):
        course_1 = Course(id="IS111",name="Wrong Name")
        db.session.add(course_1)
        db.session.commit()

        request_body = {"course_id":"IS111"}

        response = self.client.post("/update_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving course to database."})

    def test_update_course_non_json_request(self):
        course_1 = Course(id="IS111",name="Wrong Name")
        db.session.add(course_1)
        db.session.commit()

        response = self.client.post("/update_course",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code":403,
                                        "message":"Invalid input"})

#Delete Course Test
class TestDeleteCourse(TestApp):
    
    def test_delete_course(self):
        course_1 = Course(id="IS111",name="Wrong Name")
        db.session.add(course_1)
        db.session.commit()

        response = self.client.delete("/delete_course/IS111")

        self.assertEqual(response.json, {"code":201,
                                        "message":"Course deleted successfully."})

    def test_delete_course_wrong_id(self):
        course_1 = Course(id="IS111",name="Wrong Name")
        db.session.add(course_1)
        db.session.commit()

        response = self.client.delete("/delete_course/CS440")

        self.assertEqual(response.json, {"code":404,
                                        "message":"No course id not found in Database."})

#Add Course Skill Test
class TestAddCourseSkill(TestApp):
    
    def test_add_course_skill(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        db.session.add(course_1)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        request_body = {"course_id":"IS111","skill_id":[1,2]}

        response = self.client.post("/add_course_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":201,
                                        "message":"User saved successfully."})

    def test_add_course_skill_no_course_id(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        db.session.add(course_1)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        request_body = {"skill_id":[1,2]}

        response = self.client.post("/add_course_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_add_course_skill_no_skill_id(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        db.session.add(course_1)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        request_body = {"course_id":"IS111"}

        response = self.client.post("/add_course_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_add_course_skill_wrong_course_id(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        db.session.add(course_1)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        request_body = {"course_id":"CS440","skill_id":[1,2]}

        response = self.client.post("/add_course_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_add_course_skill_wrong_skill_id(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        db.session.add(course_1)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        request_body = {"course_id":"IS111","skill_id":[3,4]}

        response = self.client.post("/add_course_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_add_course_skill_non_json_request(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        db.session.add(course_1)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        response = self.client.post("/add_course_skill",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code":403,
                                        "message":"Invalid input"})

#Get Skill Mapped
class TestGetSkillsMapped(TestApp):
    
    def test_get_skills_mapped(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        course_1.mapped_skills.append(skill_1)
        course_1.mapped_skills.append(skill_2)
        db.session.add(course_1)
        db.session.commit()

        response = self.client.get("/get_skills_mapped/IS111")

        self.assertEqual(response.json, {"code":200,
                                        "content":[{"id":1,"name":"Python"},
                                                    {"id":2,"name":"Programming"}]})

    def test_get_skills_mapped_wrong_id(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        course_1.mapped_skills.append(skill_1)
        course_1.mapped_skills.append(skill_2)
        db.session.add(course_1)
        db.session.commit()

        response = self.client.get("/get_skills_mapped/CS440")

        self.assertEqual(response.json, {"code":404,
                                        "message":"Course not found"})

    def test_get_skills_mapped_no_id(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        course_1.mapped_skills.append(skill_1)
        course_1.mapped_skills.append(skill_2)
        db.session.add(course_1)
        db.session.commit()

        response = self.client.get("/get_skills_mapped")

        self.assertEqual(response.json, None)

#Delete Course Skill Test
class TestDeleteCourseSkill(TestApp):
    
    def test_delete_course_skill(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        course_1.mapped_skills.append(skill_1)
        course_1.mapped_skills.append(skill_2)
        db.session.add(course_1)
        db.session.commit()

        request_body = {"course_id":"IS111","skill_id":[1]}

        response = self.client.post("/delete_course_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":201,
                                        "message":"Mapping deleted successfully."})

        response = self.client.get("/get_skills_mapped/IS111")

        self.assertEqual(response.json, {"code":200,
                                        "content":[{"id":2,"name":"Programming"}]})

    def test_delete_course_skill_no_course_id(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        course_1.mapped_skills.append(skill_1)
        course_1.mapped_skills.append(skill_2)
        db.session.add(course_1)
        db.session.commit()

        request_body = {"skill_id":[1]}

        response = self.client.post("/delete_course_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error Handling request"})

    def test_delete_course_skill_no_skill_id(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        course_1.mapped_skills.append(skill_1)
        course_1.mapped_skills.append(skill_2)
        db.session.add(course_1)
        db.session.commit()

        request_body = {"course_id":"IS111"}

        response = self.client.post("/delete_course_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error Handling request"})

    def test_delete_course_skill_wrong_course_id(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        course_1.mapped_skills.append(skill_1)
        course_1.mapped_skills.append(skill_2)
        db.session.add(course_1)
        db.session.commit()

        request_body = {"course_id":"CS440","skill_id":[1]}

        response = self.client.post("/delete_course_skill",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error Handling request"})

    def test_delete_course_skill_non_json_request(self):
        course_1 = Course(id="IS111",name="Introduction to Programming")
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Programming")
        course_1.mapped_skills.append(skill_1)
        course_1.mapped_skills.append(skill_2)
        db.session.add(course_1)
        db.session.commit()

        response = self.client.post("/delete_course_skill",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code":403,
                                        "message":"Invalid input"})
