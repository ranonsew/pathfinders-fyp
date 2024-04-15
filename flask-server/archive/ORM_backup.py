USER="admin"
PASSWORD="AforFYP+2023"
HOSTDB="db-path-finder.c8i66wx08e8k.ap-southeast-1.rds.amazonaws.com"
DATABASE="trial"

from flask import jsonify, request, Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa

db = SQLAlchemy()
app = Flask(__name__)


user_name = USER
password = PASSWORD
host_db = HOSTDB
database = DATABASE

app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql+pymysql://{user_name}:{password}@{host_db}:3306/{database}'
db.init_app(app)




#---- Define Association Tables ----
course_skill_map = db.Table('course_skill_map',
    db.Column('course_id', db.String(20), db.ForeignKey('course.id')),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id')))

role_keyword_map = db.Table('role_keyword_map',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('keyword_id', db.Integer, db.ForeignKey('keyword.id')))

user_skill_map = db.Table('user_skill_map',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id')))

user_course_map = db.Table('user_course_map',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('course_id', db.String(20), db.ForeignKey('course.id')))

spec_role_map = db.Table('spec_role_map',
    db.Column('spec_id', db.Integer, db.ForeignKey('spec.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')))

role_skill_map = db.Table('role_skill_map',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id')))


#---- Define Object Entities ----
class Course(db.Model):
    __tablename__ = 'course'
    id = sa.Column(sa.String(20), primary_key=True)
    name = sa.Column(sa.String(100), nullable=False)
    mapped_skills = db.relationship("Skill", secondary=course_skill_map, backref='mapped_course')

    def __repr__(self):
        return f'<Course: {self.name}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "mapped_skills": self.mapped_skills
            }

    
class Role(db.Model):
    __tablename__ = 'role'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False)
    desc = sa.Column(sa.String(80))
    exp_level = sa.Column(sa.Integer, nullable=False)
    mapped_skills = db.relationship("Skill", secondary=role_skill_map, backref='mapped_role')
    mapped_keyw = db.relationship("Keyword", secondary=role_keyword_map, backref='mapped_role')

    def __repr__(self):
        return f'<Role: {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "exp_level": self.exp_level,
            "mapped_skills": self.mapped_skills,
            "mapped_keyw": self.mapped_keyw 
        }

class Skill(db.Model):
    __tablename__ = 'skill'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Skill: {self.name}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "mapped_skills": self.mapped_skills
            }

class Keyword(db.Model):
    __tablename__ = 'keyword'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False)
    
    def __repr__(self):
        return f'<Keyword: {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
            }

class Spec(db.Model):
    __tablename__ = 'spec'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False)
    mapped_roles = db.relationship("Role", secondary=spec_role_map, backref='mapped_spec')

    def __repr__(self):
        return f'<Spec: {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "mapped_roles": self.mapped_roles
            }

class User(db.Model):
    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key=True)
    full_name = sa.Column(sa.String(50), nullable=False)
    faculty = sa.Column(sa.String(255), nullable=False)
    user_email = sa.Column(sa.String(255), nullable=False)
    password = sa.Column(sa.String(255), nullable=False)
    mapped_skills = db.relationship("Skill", secondary=user_skill_map, backref='mapped_user')
    mapped_courses = db.relationship("Course", secondary=user_course_map, backref='mapped_user')

    def __repr__(self):
        return f'<Spec: {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "faculty": self.faculty,
            "user_email": self.user_email,
            "password": self.password,
            "mapped_skills": self.mapped_skills,
            "mapped_courses": self.mapped_courses
            }


with app.app_context():
    db.create_all()
    print("Tables created")


# with app.app_context():

#     course_one = Course(id="IS111", name="Intro to Programming")
#     course_two = Course(id="IS112", name="Data Management")
#     course_three =  Course(id="IS113", name="Web Application Development I")
#     course_four= Course(id="IS210", name="Business Process Analysis & Solutioning")

#     skill_one = Skill(id=1, name="Business Needs Analysis")
#     skill_two = Skill(id=2, name="Business Requirement Management")
#     skill_three = Skill(id=3, name="Process Improvement and Optimisation")
#     skill_four = Skill(id=4, name="Project Management")
#     skill_five = Skill(id=5, name="Software Testing")
#     skill_six = Skill(id=6, name="Problem Management")

#     role_one = Role(id=1, name="Business Analyst", 
#                     desc='''An IT business analyst works across both business and IT 
#                     to provide technology solutions. They analyse IT team capabilities
#                     and the business' current processes, models and strategies, then help to design, 
#                     build and implement new tech solutions.''', exp_level=1)
#     role_two = Role(id=2, name="Data Analyst", 
#                 desc='''A Data Analyst interprets data and turns it into information which can offer 
#                 ways to improve a business, thus affecting business decisions..''', exp_level=1)
#     role_three = Role(id=3, name="Software Engineer", 
#                 desc='''A Software Engineer needs to address the entire software development lifecycle 
#                 - to analyse the needs, and then design, test and develop software in order to meet those 
#                 needs.''', exp_level=1)
    
#     keyword_one = Keyword(id=1, name="Tableau")
#     keyword_two = Keyword(id=2, name="Data Structures Algorithms")
#     keyword_three = Keyword(id=3, name="Diagramming")

#     user_one = User(id=1,
#                     full_name="Ben Ong Kai Wen",
#                     faculty= "SCIS",
#                     user_email="ben_ong.2022@scis.smu.edu.sg",
#                     password="123")

#     user_two = User(id=2,
#                     full_name="Ariel Hannah Amal",
#                     faculty= "SCIS",
#                     user_email="ariel_amal.2021@scis.smu.edu.sg",
#                     password="456")

#     spec_one = Spec(id=1, name="Application Development")
#     spec_two = Spec(id=2, name="Data & AI")

#     course_one.mapped_skills.append(skill_five)
#     course_two.mapped_skills.append(skill_one)
#     course_two.mapped_skills.append(skill_two)
#     course_four.mapped_skills.append(skill_one)
#     course_four.mapped_skills.append(skill_two)
#     course_four.mapped_skills.append(skill_three)
#     course_four.mapped_skills.append(skill_six)

#     role_one.mapped_keyw.append(keyword_three)
#     role_two.mapped_keyw.append(keyword_one)
#     role_two.mapped_keyw.append(keyword_two)
#     role_three.mapped_keyw.append(keyword_two)

#     role_one.mapped_skills.append(skill_one)
#     role_one.mapped_skills.append(skill_two)
#     role_one.mapped_skills.append(skill_three)
#     role_one.mapped_skills.append(skill_six)
#     role_two.mapped_skills.append(skill_six)
#     role_three.mapped_skills.append(skill_five)
#     role_three.mapped_skills.append(skill_six)

#     spec_one.mapped_roles.append(role_one)
#     spec_one.mapped_roles.append(role_three)
#     spec_two.mapped_roles.append(role_two)

#     user_one.mapped_courses.append(course_one)
#     user_one.mapped_courses.append(course_two)
#     user_two.mapped_courses.append(course_three)
    
#     db.session.add_all([course_one, course_two, course_three, course_four])
#     db.session.add_all([skill_one,skill_two,skill_three,skill_four,skill_five,skill_six])
#     db.session.add_all([role_one,role_two, role_three])
#     db.session.add_all([spec_one, spec_two])
#     db.session.add_all([keyword_one, keyword_two,keyword_three])
#     db.session.add_all([user_one, user_two])
#     db.session.commit()
with app.app_context():
    user_one = User.query.filter_by(id=1).first()
    skill_one = Skill.query.filter_by(id=1).first()
    course_one = Course.query.filter_by(id='IS111').first()

    print('user one')
    print(user_one.mapped_skills)
    print(user_one.mapped_courses)
    print('skill one')
    print(skill_one.mapped_course)
    print(skill_one.mapped_role)

    print('course one')
    print(course_one.mapped_skills)
    
    print('user_skills')
    for course in user_one.mapped_courses:
        print(course.mapped_skills)


    

    
    


    

    
    

    
    
    
    


    


    
