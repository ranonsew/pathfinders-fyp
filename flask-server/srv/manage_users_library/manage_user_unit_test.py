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
module_directory = os.path.abspath(os.path.join(unit_test_directory))

# Add the directory containing the module to sys.path
sys.path.insert(0, module_directory)

# Now you can import the module
from manage_users import app,db,generate_salt,hash_password

# Get the absolute path to the directory containing ORM_globals.py
orm_globals_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add the directory containing ORM_globals.py to sys.path
sys.path.insert(0, orm_globals_directory)
from ORM_globals import User,Course,Skill

class TestCourseLib(unittest.TestCase):
    
    @freeze_time("2022-10-05 09:19:17")
    def test_to_dict(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com")
        self.assertEqual(user_1.to_dict(), {
            "id": user_1.id,
            "full_name":user_1.full_name,
            "faculty":user_1.faculty,
            "user_email":user_1.user_email,
            'mapped_courses': [],
            "mapped_skills":[],
            "fav_roles": [],
            "password":user_1.password
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

#Create User Test
@freeze_time("2022-10-05 09:19:17")
class TestCreateUser(TestApp):
    
    def test_create_user(self):
        request_body = {"user_id":12345,"user_name":"Tom Thomas",
                        "user_password":"123","user_faculty":"SCIS",
                        "user_email":"tom@abc.com"}

        response = self.client.post("/create_user",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 201, "message": "User saved successfully."})

    def test_create_user_duplicate_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        db.session.add(user_1)
        db.session.commit()

        request_body = {"user_id":12345,"user_name":"Tom Thomas",
                        "user_password":"123","user_faculty":"SCIS",
                        "user_email":"tom@abc.com"}
        response = self.client.post("/create_user",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json,{'code': 401, 'message': 'Duplicate user or id.'})

    def test_create_user_no_id(self):
        request_body = {"user_name":"Tom Thomas",
                        "user_password":"123","user_faculty":"SCIS",
                        "user_email":"tom@abc.com"}
        response = self.client.post("/create_user",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving user to database."})

    def test_create_user_no_name(self):
        request_body = {"user_id":12345,
                        "user_password":"123","user_faculty":"SCIS",
                        "user_email":"tom@abc.com"}
        response = self.client.post("/create_user",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

    def test_create_user_no_password(self):
        request_body = {"user_id":12345,
                        "user_name":"Tom Thomas","user_faculty":"SCIS",
                        "user_email":"tom@abc.com"}
        response = self.client.post("/create_user",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code": 500, "message": "Error saving user to database."})

    def test_create_user_no_faculty(self):
        request_body = {"user_id":12345,
                        "user_name":"Tom Thomas","user_password":"123",
                        "user_email":"tom@abc.com"}
        response = self.client.post("/create_user",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {'code': 201, 'message': 'User saved successfully.'})

    def test_create_user_no_email(self):
        request_body = {"user_id":12345,
                        "user_name":"Tom Thomas","user_password":"123",
                        "user_faculty":"SCIS"}
        response = self.client.post("/create_user",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {'code': 201, 'message': 'User saved successfully.'})

    def test_create_user_non_json_request(self):
        response = self.client.post("/create_user",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code": 403, "message": "Invalid input"})

#Get User Test
@freeze_time("2022-10-05 09:19:17")
class TestGetUser(TestApp):
    
    def test_get_user(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        db.session.add(user_1)
        db.session.commit()

        response = self.client.get("/get_user/12345")

        self.assertEqual(response.json, {"code":200,
                                        "content": {'faculty': 'SOE',
                                                    'full_name': 'Tom',
                                                    'id': 12345,
                                                    'user_email': 'tom@xyz.com',
                                                    'is_admin':False}})

    def test_get_user_wrong_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        db.session.add(user_1)
        db.session.commit()

        response = self.client.get("/get_user/123")

        self.assertEqual(response.json, {"code": 404,"message": "User not found"})

#Get All User Test
@freeze_time("2022-10-05 09:19:17")
class TestGetAllUser(TestApp):
    
    def test_get_all_user(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        db.session.add(user_1)

        salt = generate_salt()
        hashed_password = hash_password("321",salt)
        user_2 = User(id=54321,full_name="Jerry",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="jerry@xyz.com",is_admin=True)
        db.session.add(user_2)
        db.session.commit()

        response = self.client.get("/get_all_users")

        self.assertEqual(response.json["code"], 200)
        return_data = sorted(response.json["content"], key=lambda x: x["id"])
        self.assertEqual(return_data,[{'faculty': 'SOE','full_name': 'Tom',
                                        'id': 12345,'user_email': 'tom@xyz.com','password':user_1.password,
                                        'mapped_skills':[]},
                                        {'faculty': 'SOE','full_name': 'Jerry',
                                        'id': 54321,'user_email': 'jerry@xyz.com','password':user_2.password,
                                        'mapped_skills':[],}])

#Update User Test
class TestUpdateParticulars(TestApp):
    
    def test_update_particulars(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        db.session.add(user_1)
        db.session.commit()

        request_body = {"user_id":12345,"user_name":"Tom Thomas",
                        "user_password":"123","user_faculty":"SCIS",
                        "user_email":"tom@abc.com"}

        response = self.client.post("/update_particulars",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":201,
                                        "message":"User particulars updated successfully."})

    def test_update_particulars_wrong_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        db.session.add(user_1)
        db.session.commit()

        request_body = {"user_id":54321,"user_name":"Tom Thomas",
                        "user_password":"123","user_faculty":"SCIS",
                        "user_email":"tom@abc.com"}

        response = self.client.post("/update_particulars",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":404,
                                        "message":"User id not found in Database."})

    def test_update_particulars_no_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        db.session.add(user_1)
        db.session.commit()

        request_body = {"user_name":"Tom Thomas",
                        "user_password":"123","user_faculty":"SCIS",
                        "user_email":"tom@abc.com"}

        response = self.client.post("/update_particulars",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_update_particulars_no_name(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        db.session.add(user_1)
        db.session.commit()

        request_body = {"user_id":12345,
                        "user_password":"123","user_faculty":"SCIS",
                        "user_email":"tom@abc.com"}

        response = self.client.post("/update_particulars",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_update_particulars_no_faculty(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        db.session.add(user_1)
        db.session.commit()

        request_body = {"user_id":12345,"user_name":"Tom Thomas",
                        "user_password":"123",
                        "user_email":"tom@abc.com"}

        response = self.client.post("/update_particulars",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_update_particulars_no_email(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        db.session.add(user_1)
        db.session.commit()

        request_body = {"user_id":12345,"user_name":"Tom Thomas",
                        "user_password":"123",
                        "user_faculty":"SCIS"}

        response = self.client.post("/update_particulars",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_update_particulars_non_json_request(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        db.session.add(user_1)
        db.session.commit()

        response = self.client.post("/update_particulars",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code":403,
                                        "message":"Invalid input"})

#Delete User Test
class TestDeleteUser(TestApp):
    
    def test_delete_user(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        db.session.add(user_1)
        db.session.commit()

        response = self.client.delete("/delete_user/12345")

        self.assertEqual(response.json, {"code":201,
                                        "message":"User deleted successfully."})

    def test_delete_user_wrong_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        db.session.add(user_1)
        db.session.commit()

        response = self.client.delete("/delete_user/2")

        self.assertEqual(response.json, {"code":404,
                                        "message":"No user id not found in Database."})

#Add User Course Test
class TestAddUserCourse(TestApp):
    
    def test_add_user_course(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        request_body = {"user_id":12345,"course_id":["IS111","CS440"]}

        response = self.client.post("/add_user_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":201,
                                        "message":"User saved successfully."})

    def test_add_user_course_no_user_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        request_body = {"course_id":["IS111","CS440"]}

        response = self.client.post("/add_user_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_add_user_course_no_course_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        request_body = {"user_id":12345}

        response = self.client.post("/add_user_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_add_user_course_wrong_user_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        request_body = {"user_id":54321,"course_id":["IS111","CS440"]}

        response = self.client.post("/add_user_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_add_user_course_wrong_course_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        request_body = {"user_id":12345,"course_id":["IS123","CS445"]}

        response = self.client.post("/add_user_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_add_user_course_non_json_request(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        response = self.client.post("/add_user_course",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code":403,
                                        "message":"Invalid input"})

#Get User Course test
class TestGetUserCourse(TestApp):
    
    def test_get_user_course(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        user_1.mapped_courses.append(course_1)
        user_1.mapped_courses.append(course_2)
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        response = self.client.get("/get_user_courses/12345")

        self.assertEqual(response.json["code"], 200)
        return_data = sorted(response.json["content"], key=lambda x: x["id"])
        self.assertEqual(return_data,[{'id': 'CS440', 'name': 'Foundation of Cybersecurity'},
                                    {'id': 'IS111', 'name': 'Introduction to Programming'}]) 

    def test_get_user_course_wrong_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        user_1.mapped_courses.append(course_1)
        user_1.mapped_courses.append(course_2)
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        response = self.client.get("/get_user_courses/54321")

        self.assertEqual(response.json, {"code":404,
                                        "message":"User not found"})

    def test_get_user_course_no_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        user_1.mapped_courses.append(course_1)
        user_1.mapped_courses.append(course_2)
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        response = self.client.get("/get_user_courses")

        self.assertEqual(response.json, None)

#Get User Skill test
class TestGetUserSkill(TestApp):
    
    def test_get_user_skill(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        user_1.mapped_courses.append(course_1)
        user_1.mapped_courses.append(course_2)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Java")
        course_1.mapped_skills.append(skill_1)
        course_2.mapped_skills.append(skill_2)
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        response = self.client.get("/get_user_skills/12345")

        self.assertEqual(response.json["code"], 200)
        return_data = sorted(response.json["content"], key=lambda x: x["id"])
        self.assertEqual(return_data,[{'id': 1, 'name': 'Python'},
                                    {'id': 2, 'name': 'Java'}]) 

    def test_get_user_skill_wrong_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        user_1.mapped_courses.append(course_1)
        user_1.mapped_courses.append(course_2)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Java")
        course_1.mapped_skills.append(skill_1)
        course_2.mapped_skills.append(skill_2)
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        response = self.client.get("/get_user_skills/54321")

        self.assertEqual(response.json, {"code":404,
                                        "message":"User not found"})

    def test_get_user_course_no_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        user_1.mapped_courses.append(course_1)
        user_1.mapped_courses.append(course_2)
        skill_1 = Skill(id=1,name="Python")
        skill_2 = Skill(id=2,name="Java")
        course_1.mapped_skills.append(skill_1)
        course_2.mapped_skills.append(skill_2)
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.commit()

        response = self.client.get("/get_user_skills")

        self.assertEqual(response.json, None)

#Delete User Course Test
class TestDeleteUserCourse(TestApp):
    
    def test_delete_user_course(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        user_1.mapped_courses.append(course_1)
        user_1.mapped_courses.append(course_2)
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        request_body = {"user_id":12345,"course_id":["IS111"]}

        response = self.client.post("/delete_user_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":201,
                                        "message":"User deleted successfully."})

        response = self.client.get("/get_user_courses/12345")

        self.assertEqual(response.json, {"code":200,
                                        "content":[{'id': "CS440", 
                                                    'name': 'Foundation of Cybersecurity'}]})

    def test_delete_user_course_no_user_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        request_body = {"course_id":["IS111"]}

        response = self.client.post("/delete_user_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_delete_user_course_no_course_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        request_body = {"user_id":12345}

        response = self.client.post("/delete_user_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_delete_user_course_wrong_user_id(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        request_body = {"user_id":54321,"course_id":["IS111"]}

        response = self.client.post("/delete_user_course",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {"code":500,
                                        "message":"Error saving user to database."})

    def test_delete_spec_role_non_json_request(self):
        salt = generate_salt()
        hashed_password = hash_password("123",salt)
        user_1 = User(id=12345,full_name="Tom",
                        password=hashed_password,salt=salt,
                        faculty="SOE",user_email="tom@xyz.com",is_admin=False)
        course_1 = Course(id="IS111",name="Introduction to Programming")
        course_2 = Course(id="CS440",name="Foundation of Cybersecurity")
        db.session.add(user_1)
        db.session.add(course_1)
        db.session.add(course_2)
        db.session.commit()

        response = self.client.post("/delete_user_course",
                                    data="Non JSON Data")

        self.assertEqual(response.json, {"code":403,
                                        "message":"Invalid input"})