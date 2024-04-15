#--- Import Python libraries ---
from flask import jsonify, request, Flask
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
import csv

#---- Set up connection to DB ----
db = SQLAlchemy()
app = Flask(__name__)

load_dotenv()

user_name = os.environ.get('DBUSER')
password = os.environ.get('PASSWORD')
host_db = os.environ.get('HOSTDB')
database = os.environ.get('DATABASE')


print(user_name)
print(password)
print(host_db)
print(database)

app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql+pymysql://{user_name}:{password}@{host_db}:3306/{database}'
db.init_app(app)


# ---- Obtain schema from the microservices ----
from ORM_globals import Course
from ORM_globals import Skill
from ORM_globals import Keyword
from ORM_globals import Role
from ORM_globals import Spec
from ORM_globals import Salary

# ---- Read the csv files ----
course_list = []
skill_list = []
role_list = []
salary_list = []
keyword_list = []
spec_list = []

with open("./sample_data/Courses.csv", "r") as file:
    csvreader = csv.reader(file)
    next(csvreader, None)
    for row in csvreader:
        course_code = row[0]
        course_name = row[1]
        course_list.append(Course(id=course_code, name=course_name))
        
with open("./sample_data/Skills.csv", "r") as file:
    csvreader = csv.reader(file)
    next(csvreader, None)
    for row in csvreader:
        skill_id = row[0]
        skill_name = row[1]
        skill_list.append(Skill(id=skill_id, name=skill_name))

with open("./sample_data/Roles.csv", "r") as file:
    csvreader = csv.reader(file)
    next(csvreader, None)
    for row in csvreader:
        role_id = row[0]
        role_name = row[1]
        role_desc = row[2]
        exp_level = row[3]
        role_list.append(Role(id=role_id, name=role_name, desc=role_desc, exp_level=exp_level))

with open("./sample_data/Spec.csv", "r") as file:
    csvreader = csv.reader(file)
    next(csvreader, None)
    for row in csvreader:
        spec_id = row[0]
        spec_name = row[1]
        spec_list.append(Spec(id=spec_id,name=spec_name))

with open("./sample_data/keyword.csv", "r") as file:
    csvreader = csv.reader(file)
    next(csvreader, None)
    for row in csvreader:
        keyw_id = row[0]
        keyw_name = row[1]
        keyword_list.append(Keyword(id=keyw_id, name=keyw_name))


with open("./sample_data/Role-Salary.csv", "r") as file:
    csvreader = csv.reader(file)
    next(csvreader, None)
    for row in csvreader:
        role_id = row[0]
        salary = row[1]
        salary_list.append(Salary(role_id=role_id, amount=salary))

#--- Commit Data ---
with app.app_context():    
    db.session.add_all(course_list)
    db.session.add_all(role_list)
    db.session.add_all(skill_list)
    db.session.add_all(salary_list)
    db.session.add_all(spec_list)
    db.session.add_all(keyword_list)
    db.session.commit()

   