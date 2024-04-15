#--- Import Python libraries ---
from flask import jsonify, request, Flask
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa


# ---- Set up connection to DB ----
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
from ORM_globals import User
from ORM_globals import Spec
from ORM_globals import Salary


#--- Define Test data ---
with app.app_context():

    course_one = Course(id="IS111", name="Intro to Programming")
    course_two = Course(id="IS112", name="Data Management")
    course_three =  Course(id="IS113", name="Web Application Development I")
    course_four= Course(id="IS210", name="Business Process Analysis & Solutioning")

    skill_one = Skill(id=1, name="Business Needs Analysis")
    skill_two = Skill(id=2, name="Business Requirement Management")
    skill_three = Skill(id=3, name="Process Improvement and Optimisation")
    skill_four = Skill(id=4, name="Project Management")
    skill_five = Skill(id=5, name="Software Testing")
    skill_six = Skill(id=6, name="Problem Management")

    role_one = Role(id=1, name="Business Analyst", 
                    desc='''An IT business analyst works across both business and IT 
                    to provide technology solutions. They analyse IT team capabilities
                    and the business' current processes, models and strategies, then help to design, 
                    build and implement new tech solutions.''', exp_level=1)
    role_two = Role(id=2, name="Data Analyst", 
                desc='''A Data Analyst interprets data and turns it into information which can offer 
                ways to improve a business, thus affecting business decisions..''', exp_level=1)
    role_three = Role(id=3, name="Software Engineer", 
                desc='''A Software Engineer needs to address the entire software development lifecycle 
                - to analyse the needs, and then design, test and develop software in order to meet those 
                needs.''', exp_level=1)
    
    keyword_one = Keyword(id=1, name="Tableau")
    keyword_two = Keyword(id=2, name="Data Structures Algorithms")
    keyword_three = Keyword(id=3, name="Diagramming")

    user_one = User(id=1,
                    full_name="Ben Ong Kai Wen",
                    faculty= "SCIS",
                    user_email="ben_ong.2022@scis.smu.edu.sg",
                    password="123")

    user_two = User(id=2,
                    full_name="Ariel Hannah Amal",
                    faculty= "SCIS",
                    user_email="ariel_amal.2021@scis.smu.edu.sg",
                    password="456")

    spec_one = Spec(id=1, name="Application Development")
    spec_two = Spec(id=2, name="Data & AI")
    salary_one = Salary(id= 1, amount = 3500, role_id = 1)
    salary_two = Salary(id= 2, amount = 3500, role_id = 1)
    salary_three = Salary(id= 3, amount = 3700, role_id = 2)
    salary_four = Salary(id= 4, amount = 3900, role_id = 2)


    course_one.mapped_skills.append(skill_five)
    course_two.mapped_skills.append(skill_one)
    course_two.mapped_skills.append(skill_two)
    course_four.mapped_skills.append(skill_one)
    course_four.mapped_skills.append(skill_two)
    course_four.mapped_skills.append(skill_three)
    course_four.mapped_skills.append(skill_six)

    role_one.mapped_keyw.append(keyword_three)
    role_two.mapped_keyw.append(keyword_one)
    role_two.mapped_keyw.append(keyword_two)
    role_three.mapped_keyw.append(keyword_two)

    role_one.mapped_skills.append(skill_one)
    role_one.mapped_skills.append(skill_two)
    role_one.mapped_skills.append(skill_three)
    role_one.mapped_skills.append(skill_six)
    role_two.mapped_skills.append(skill_six)
    role_three.mapped_skills.append(skill_five)
    role_three.mapped_skills.append(skill_six)

    spec_one.mapped_roles.append(role_one)
    spec_one.mapped_roles.append(role_three)
    spec_two.mapped_roles.append(role_two)

    user_one.mapped_courses.append(course_one)
    user_one.mapped_courses.append(course_two)
    user_two.mapped_courses.append(course_three)

    user_one.fav_roles.append(role_one)
    user_one.fav_roles.append(role_three)
    user_two.fav_roles.append(role_two)

    
    db.session.add_all([course_one, course_two, course_three, course_four])
    db.session.add_all([skill_one,skill_two,skill_three,skill_four,skill_five,skill_six])
    db.session.add_all([role_one,role_two, role_three])
    db.session.add_all([spec_one, spec_two])
    db.session.add_all([keyword_one, keyword_two,keyword_three])
    db.session.add_all([user_one, user_two])
    db.session.add_all([salary_one, salary_two, salary_three, salary_four])
    
    db.session.commit()
