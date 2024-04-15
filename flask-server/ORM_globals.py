from flask import jsonify, request, Flask
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa

db = SQLAlchemy()
app = Flask(__name__)

load_dotenv()

if os.environ.get('TESTING') == '1':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    db.init_app(app)
else:
    user_name = os.environ.get('DBUSER')
    password = os.environ.get('PASSWORD')
    host_db = os.environ.get('HOSTDB')
    database = os.environ.get('DATABASE')

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
    db.Column('user_id', db.String(20), db.ForeignKey('user.id')),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id')))

user_course_map = db.Table('user_course_map',
    db.Column('user_id', db.String(20), db.ForeignKey('user.id')),
    db.Column('course_id', db.String(20), db.ForeignKey('course.id')))

user_role_map = db.Table('user_role_map',
    db.Column('user_id', db.String(20), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')))

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
    name = sa.Column(sa.String(100), nullable=False,unique=True)
    mapped_skills = db.relationship("Skill", secondary=course_skill_map, backref='mapped_courses')

    def __repr__(self):
        return f'<Course: {self.name}'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "mapped_skills": self.mapped_skills
            }
    
class Role(db.Model):
    __tablename__ = 'role'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False, unique=True)
    desc = sa.Column(sa.String(500))
    exp_level = sa.Column(sa.Integer, nullable=False)
    mapped_skills = db.relationship("Skill", secondary=role_skill_map, backref='mapped_roles')
    mapped_keyw = db.relationship("Keyword", secondary=role_keyword_map, backref='mapped_roles')
    salary = db.relationship('Salary', backref='role')

    def __repr__(self):
        return f'<Role: {self.name}'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "exp_level": self.exp_level,
            "mapped_skills": self.mapped_skills,
            "mapped_keyw": self.mapped_keyw,
            "salary": self.salary
        }

class Skill(db.Model):
    __tablename__ = 'skill'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(100), nullable=False, unique=True)
    
    def __repr__(self):
        return f'<Skill: {self.name}'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            }

class Keyword(db.Model):
    __tablename__ = 'keyword'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False, unique=True)
    
    def __repr__(self):
        return f'<Keyword: {self.name}'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
            }

class Spec(db.Model):
    __tablename__ = 'spec'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False, unique=True)
    mapped_roles = db.relationship("Role", secondary=spec_role_map, backref='mapped_specs')

    def __repr__(self):
        return f'<Spec: {self.name}'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "mapped_roles": self.mapped_roles
            }

class User(db.Model):
    __tablename__ = 'user'
    id = sa.Column(sa.String(20), primary_key=True)
    password = sa.Column(sa.String(255), nullable=False)
    salt = sa.Column(sa.LargeBinary, nullable=False)
    full_name = sa.Column(sa.String(50))
    faculty = sa.Column(sa.String(255))
    user_email = sa.Column(sa.String(255))
    is_admin = sa.Column(sa.Boolean, nullable=False)
    mapped_skills = db.relationship("Skill", secondary=user_skill_map, backref='mapped_users')
    mapped_courses = db.relationship("Course", secondary=user_course_map, backref='mapped_users')
    fav_roles = db.relationship("Role", secondary=user_role_map, backref='mapped_users')

    def __repr__(self):
        return f'<User: {self.full_name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "faculty": self.faculty,
            "user_email": self.user_email,
            "password": self.password,
            "mapped_skills": self.mapped_skills,
            "mapped_courses": self.mapped_courses,
            "fav_roles": self.fav_roles
            }
    
class Salary(db.Model):
    __tablename__ = 'salary'
    id = sa.Column(sa.Integer, primary_key=True)
    amount = sa.Column(sa.Integer, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __repr__(self):
        return f'<Role_id: {self.role_id}, Salary: {self.amount}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "role_id": self.role_id
            }



with app.app_context():
    db.create_all()
    print("Tables created")

db.close_all_sessions()