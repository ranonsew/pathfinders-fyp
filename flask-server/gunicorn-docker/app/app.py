import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlalchemy as sa
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import heapq
import hashlib
import json
from pypdf import PdfReader
import boto3 # for s3
from werkzeug.utils import secure_filename
import time

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

db = SQLAlchemy()
app = Flask(__name__)
CORS(app)

load_dotenv()

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
	id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
	name = sa.Column(sa.String(50), nullable=False, unique=True)
	desc = sa.Column(sa.String(500))
	exp_level = sa.Column(sa.Integer, nullable=False)
	mapped_skills = db.relationship("Skill", secondary=role_skill_map, backref='mapped_roles', cascade='all, delete')
	mapped_keyw = db.relationship("Keyword", secondary=role_keyword_map, backref='mapped_roles', cascade='all, delete')
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
	id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
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
	id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
	name = sa.Column(sa.String(50), nullable=False, unique=True)
	mapped_roles = db.relationship("Role", secondary=spec_role_map, backref='mapped_specs', cascade='all, delete')

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
	# profile_url = sa.Column(sa.String(255))
	mapped_skills = db.relationship("Skill", secondary=user_skill_map, backref='mapped_users', cascade='all, delete')
	mapped_courses = db.relationship("Course", secondary=user_course_map, backref='mapped_users', cascade='all, delete')
	fav_roles = db.relationship("Role", secondary=user_role_map, backref='mapped_users', cascade='all, delete')

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
	id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
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

# class Requisite(db.Model):
# 	__tablename__ = 'prerequisites'
# 	id = sa.Column(sa.String, primary_key=True, autoincrement=True)
# 	pre_req = db.relationship('Course', backref='requisite', cascade='all, delete')
# 	exclusive = sa.Column(sa.Integer, nullable=False)

def create_app():
	#============== SKILLS ==============
	@app.route("/skill/")
	def index():
		return "hello skills!"

	@app.route("/skill/get_all")
	def get_all_skills():
		try:

			skill_saved = Skill.query.all()
			skill_found_dict = [skill.to_dict() for skill in skill_saved]

			return jsonify(
				{"code":200,
				"content": skill_found_dict
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "Skills not found"
				}), 404

	@app.route('/skill/create', methods=['POST'])
	def create_skill():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()

				skill_name = request_obj['skill_name']
				skill = Skill(name=skill_name)

				try:
					# Add Entry to DB
					db.session.add(skill)
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 401,
						"message": "Duplicate skill or id."
					}),401

				return jsonify({
					"code": 201,
					"message": "Skill saved successfully.",
					"skill_id": skill.id # return skill id
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving skill to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/skill/get_one/<int:skill_id>', methods=["GET"])
	def get_one_skill(skill_id):
		try:
			print(skill_id)
			skill_saved = db.session.execute(
						db.select(Skill).filter_by(id=skill_id)).scalar_one()
			skill_found_dict = skill_saved.__dict__
			del skill_found_dict['_sa_instance_state']
			print(skill_found_dict)

			return jsonify(
				{"code":200,
				"content": skill_found_dict
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "Skill not found"
				}), 404

	@app.route('/skill/update', methods=["POST"])
	def update_skill():
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("Skill received in: ", type(request_obj),
					request_obj)
				skill_id = request_obj['skill_id']
				skill_name = request_obj['skill_name']

				# Query for existing entry
				try:
					skill_saved = db.session.execute(
						db.select(Skill).filter_by(id=skill_id)).scalar_one()
				except Exception as e:
					print(e)
					return jsonify({
						"code": 404,
						"message": "Skill id not found in Database."
					}),404

				# Replace values and commit
				try:
					skill_saved.name = skill_name
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "Error saving skill to database."
					}),500

				return jsonify({
					"code": 201,
					"message": "Skill updated successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving skill to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/skill/delete/<int:skill_id>', methods=["DELETE"])
	def delete_skill(skill_id):
		# Query for existing entry
		try:
			skill_saved = db.session.execute(
				db.select(Skill).filter_by(id=skill_id)).scalar_one()
		except Exception as e:
			print(e)
			return jsonify({
				"code": 404,
				"message": "No skill id not found in Database."
			}),404

		# Delete
		try:
			db.session.delete(skill_saved)
			db.session.commit()

		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error deleting skill in database."
			}),500

		return jsonify({
			"code": 201,
			"message": "Skill deleted successfully."
		}), 201

	@app.route('/skill/course_mapped/get/<int:skill_id>', methods=["GET"])
	def get_skill_courses_mapped(skill_id):
		try:
			print(skill_id)
			skill_saved= Skill.query.filter_by(id=skill_id).first()
			print(skill_saved.mapped_courses)
			output_list = []
			for course in skill_saved.mapped_courses:
				course_mapped = course.to_dict()
				del course_mapped['mapped_skills']
				output_list.append(course_mapped)

			print(course_mapped)
			return jsonify(
				{"code":200,
				"content": output_list
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "No mapped course found"
				}), 404

	@app.route('/skill/course_mapped/create', methods=['POST'])
	def create_skill_courses_mapped():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("Skill course received in: ", type(request_obj), request_obj)

				skill_id = request_obj['skill_id']
				course_id = request_obj['course_id'] # List

				skill_saved = Skill.query.filter_by(id=skill_id).first()
				for course in course_id:
					course_select= Course.query.filter_by(id=course).first()
					if course_select not in skill_saved.mapped_courses:
						skill_saved.mapped_courses.append(course_select)

				try:
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "role courses not saved successfully."
					}),401

				return jsonify({
					"code": 201,
					"message": "role saved successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving role to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/skill/course_mapped/delete', methods=["POST"])
	def delete_skill_courses_mapped():
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("Skill course received in: ", type(request_obj), request_obj)
				skill_id = request_obj['skill_id']
				course_id = request_obj['course_id'] # List

				# Query for Specific course
				with app.app_context():
					skill_saved = Skill.query.filter_by(id=skill_id).first()
					course_skill = skill_saved.mapped_courses
					for course in course_skill:
						if course.id in course_id:
							skill_saved.mapped_courses.remove(course)
							print(f'{course.name} removed from skill mapping with {skill_saved.name}')

					try:
						db.session.commit()

					except Exception as e:
						print(e)
						return jsonify({
							"code": 500,
							"message": "Error deleting course skill map."
						}),401

				return jsonify({
					"code": 201,
					"message": "Mapping deleted successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error Handling request"
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/skill/roles_mapped/get/<int:skill_id>', methods=["GET"])
	def get_skill_roles_mapped(skill_id):
		try:
			print(skill_id)
			skill_saved= Skill.query.filter_by(id=skill_id).first()
			output_list = []
			for role in skill_saved.mapped_roles:
				role_found = role.to_dict()
				del role_found['mapped_skills']
				del role_found['mapped_keyw']

				salary_list = [salary.amount for salary in role_found['salary']]
				if len(salary_list) == 0:
					role_found['salary'] = 0
				else:
					average_salary = sum(salary_list) / len(salary_list)
					role_found['salary'] = round(average_salary,0)
				print(role_found)
				output_list.append(role_found)


			print(output_list)
			return jsonify(
				{"code":200,
				"content": output_list
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "No mapped roles found"
				}), 404

	@app.route('/skill/roles_mapped/create', methods=['POST'])
	def create_skill_roles_mapped():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("Skill role received in: ", type(request_obj), request_obj)

				skill_id = request_obj['skill_id']
				role_id = request_obj['role_id'] # List

				skill_saved = Skill.query.filter_by(id=skill_id).first()
				for role in role_id:
					role_select = Role.query.filter_by(id=role).first()
					if role_select not in skill_saved.mapped_roles:
						skill_saved.mapped_roles.append(role_select)

				try:
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "skill roles not saved successfully."
					}),401

				return jsonify({
					"code": 201,
					"message": "skill roles saved successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving skill roles to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/skill/roles_mapped/delete', methods=["POST"])
	def delete_skill_roles_mapped():
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("Role Skill received in: ", type(request_obj), request_obj)
				skill_id = request_obj['skill_id']
				role_id = request_obj['role_id'] # List

				# Query for Specific role
				with app.app_context():
					skill_saved = Skill.query.filter_by(id=skill_id).first()
					role_skill = skill_saved.mapped_roles
					for role in role_skill:
						if role.id in role_id:
							skill_saved.mapped_roles.remove(role)
							print(f'{role.name} removed from Skill mapping with {skill_saved.name}')

					try:
						db.session.commit()

					except Exception as e:
						print(e)
						return jsonify({
							"code": 500,
							"message": "Error deleting role skill map."
						}),401

				return jsonify({
					"code": 201,
					"message": "Mapping deleted successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error Handling request"
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	#============== COURSES ==============
	@app.route('/course/create', methods=['POST'])
	def create_course():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("Course received in: ", type(request_obj), request_obj)

				course_id = request_obj['course_id']
				course_name = request_obj['course_name']
				course = Course(id=course_id, name=course_name)

				try:
					# Add Entry to DB
					db.session.add(course)
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 401,
						"message": "Duplicate course or id."
					}),401

				return jsonify({
					"code": 201,
					"message": "Course saved successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving course to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/course/get_one/<string:course_id>', methods=["GET"])
	def get_one_course(course_id):
		try:
			print(course_id)
			course_saved = db.session.execute(
						db.select(Course).filter_by(id=course_id)).scalar_one()
			course_found_dict = course_saved.__dict__
			del course_found_dict['_sa_instance_state']
			print(course_found_dict)

			return jsonify(
				{"code":200,
				"content": course_found_dict
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "Course not found"
				}), 404

	@app.route('/course/get_all', methods=["GET"])
	def get_all_courses():
		try:

			course_saved = Course.query.all()
			course_found_dict = []
			for course in course_saved:
				course_found = course.to_dict()
				del course_found['mapped_skills']
				course_found_dict.append(course_found)
				print(course_found_dict)

			return jsonify(
				{"code":200,
				"content": course_found_dict
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "Courses not found"
				}), 404

	@app.route('/course/update', methods=["POST"])
	def update_course():
		if request.is_json:

			try:
				# Handle request
				request_obj = request.get_json()
				print("Course received in: ", type(request_obj), request_obj)
				course_id = request_obj['course_id']
				course_name = request_obj['course_name']

				# Query for existing entry
				try:
					course_saved = db.session.execute(
						db.select(Course).filter_by(id=course_id)).scalar_one()
				except Exception as e:
					print(e)
					return jsonify({
						"code": 404,
						"message": "Course id not found in Database."
					}),404

				# Replace values and commit
				try:
					course_saved.name = course_name
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "Error saving course to database."
					}),500

				return jsonify({
					"code": 201,
					"message": "Course updated successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving course to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/course/delete/<string:course_id>', methods=["DELETE"])
	def delete_course(course_id):
		# Query for existing entry
		try:
			course_saved = db.session.execute(
				db.select(Course).filter_by(id=course_id)).scalar_one()
		except Exception as e:
			print(e)
			return jsonify({
				"code": 404,
				"message": "No course id not found in Database."
			}),404

		# Delete
		try:
			db.session.delete(course_saved)
			db.session.commit()

		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error deleting course in database."
			}),500

		return jsonify({
			"code": 201,
			"message": "Course deleted successfully."
		}), 201

	# Create, Read and Delete Mappings
	@app.route('/course/skills_mapped/create', methods=['POST'])
	def create_course_skills_mapped():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("Course Skill received in: ", type(request_obj), request_obj)

				course_id = request_obj['course_id']
				skill_id = request_obj['skill_id'] # List

				course_saved= Course.query.filter_by(id=course_id).first()
				for skill in skill_id:
					skill_select= Skill.query.filter_by(id=skill).first()
					if skill_select not in course_saved.mapped_skills:
						course_saved.mapped_skills.append(skill_select)

				try:
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "Course skills mapping not saved successfully."
					}),401

				return jsonify({
					"code": 201,
					"message": "Course skills mapping saved successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving course skills to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/course/skills_mapped/get/<string:course_id>', methods=["GET"])
	def get_course_skills_mapped(course_id):
		try:
			print(course_id)
			course_saved= Course.query.filter_by(id=course_id).first()
			print(course_saved)
			skills_mapped = [skill.to_dict() for skill in course_saved.mapped_skills]

			return jsonify(
				{"code":200,
				"content": skills_mapped
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "Course not found"
				}), 404

	@app.route('/course/skills_mapped/delete', methods=["POST"])
	def delete_course_skills_mapped():
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("Course Skill received in: ", type(request_obj), request_obj)
				course_id = request_obj['course_id']
				skill_id = request_obj['skill_id'] # List

				# Query for Specific course
				with app.app_context():
					course_saved= Course.query.filter_by(id=course_id).first()
					course_skill = course_saved.mapped_skills
					for skill in course_skill:
						if skill.id in skill_id:
							course_saved.mapped_skills.remove(skill)
							print(f'{skill.name} removed from course mapping with {course_saved.name}')

					try:
						db.session.commit()

					except Exception as e:
						print(e)
						return jsonify({
							"code": 500,
							"message": "Error deleting course skill map."
						}),401

				return jsonify({
					"code": 201,
					"message": "Mapping deleted successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error Handling request"
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403


	#============== KEYWORDS ==============
	@app.route('/keyword/create', methods=['POST'])
	def create_keyword():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("Keyword received in: ", type(request_obj), request_obj)

				keyword_id = request_obj['keyword_id']
				keyword_name = request_obj['keyword_name']
				keyword = Keyword(id=keyword_id, name=keyword_name)

				try:
					# Add Entry to DB
					db.session.add(keyword)
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 401,
						"message": "Duplicate keyword or id."
					}),401

				return jsonify({
					"code": 201,
					"message": "Keyword saved successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving keyword to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/keyword/get_one/<int:keyword_id>', methods=["GET"])
	def get_one_keyword(keyword_id):
		try:
			print(keyword_id)
			keyword_saved = db.session.execute(
						db.select(Keyword).filter_by(id=keyword_id)).scalar_one()
			keyword_found_dict = keyword_saved.__dict__
			del keyword_found_dict['_sa_instance_state']
			print(keyword_found_dict)

			return jsonify(
				{"code":200,
				"content": keyword_found_dict
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "Keyword not found"
				}), 404

	@app.route('/keyword/get_all', methods=["GET"])
	def get_all_keywords():
		try:

			keyword_saved = Keyword.query.all()
			keyword_found_dict = [keyword.to_dict() for keyword in keyword_saved]

			return jsonify(
				{"code":200,
				"content": keyword_found_dict
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "keywords not found"
				}), 404

	@app.route('/keyword/update', methods=["POST"])
	def update_keyword():
		if request.is_json:

			try:
				# Handle request
				request_obj = request.get_json()
				print("Keyword received in: ", type(request_obj), request_obj)
				keyword_id = request_obj['keyword_id']
				keyword_name = request_obj['keyword_name']

				# Query for existing entry
				try:
					keyword_saved = db.session.execute(
						db.select(Keyword).filter_by(id=keyword_id)).scalar_one()
				except Exception as e:
					print(e)
					return jsonify({
						"code": 404,
						"message": "Keyword id not found in Database."
					}),404

				# Replace values and commit
				try:
					keyword_saved.name = keyword_name
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "Error saving keyword to database."
					}),500

				return jsonify({
					"code": 201,
					"message": "Keyword updated successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving keyword to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/keyword/delete/<int:keyword_id>', methods=["DELETE"])
	def delete_keyword(keyword_id):
		# Query for existing entry
		try:
			keyword_saved = db.session.execute(
				db.select(Keyword).filter_by(id=keyword_id)).scalar_one()
		except Exception as e:
			print(e)
			return jsonify({
				"code": 404,
				"message": "No keyword id not found in Database."
			}),404

		# Delete
		try:
			db.session.delete(keyword_saved)
			db.session.commit()

		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error deleting keyword in database."
			}),500

		return jsonify({
			"code": 201,
			"message": "Keyword deleted successfully."
		}), 201

	@app.route('/keyword/roles_mapped/get/<int:keyw_id>', methods=['GET'])
	def get_keyw_roles_mapped(keyw_id):
		try:
			print(keyw_id)
			keyw_saved = Keyword.query.filter_by(id=keyw_id).first()
			mapped_role = []
			for role in keyw_saved.mapped_roles:
				role_found = role.to_dict()
				del role_found['mapped_skills']
				del role_found['mapped_keyw']
				mapped_role.append(role_found)

			return jsonify(
				{
				"code":200,
				"content": mapped_role
			}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "No mapped roles found"
				}), 404

	#============== ROLES ==============
	@app.route('/role/create', methods=['POST'])
	def create_role():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("Role received in: ", type(request_obj), request_obj)

				role_name = request_obj['role_name']
				role_desc = request_obj['role_desc']
				role_exp_level = request_obj['exp_level']
				role = Role( name=role_name,
							desc=role_desc,
							exp_level=role_exp_level)

				try:
					# Add Entry to DB
					db.session.add(role)
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 401,
						"message": "Duplicate role or id."
					}),401

				return jsonify({
					"code": 201,
					"message": "Role saved successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving role to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/role/get_one/<int:role_id>', methods=["GET"])
	def get_role_lib(role_id):
		try:
			print(role_id)
			role_saved = db.session.execute(
						db.select(Role).filter_by(id=role_id)).scalar_one()
			role_found = role_saved.to_dict()
			del role_found['mapped_skills']
			del role_found['mapped_keyw']

			salary_list = [salary.amount for salary in role_found['salary']]
			if len(salary_list) == 0:
				role_found['salary'] = 0
			else:
				average_salary = sum(salary_list) / len(salary_list)
				role_found['salary'] = round(average_salary,0)
			print(role_found)

			return jsonify(
				{"code":200,
				"content": role_found
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "Role not found"
				}), 404

	@app.route('/role/get_all', methods=["GET"])
	def get_all_roles():
		try:

			role_saved = Role.query.all()
			role_found_dict = []
			for role in role_saved:
				role_found = role.to_dict()
				del role_found['mapped_skills']
				del role_found['mapped_keyw']
				# Compute for average salary
				salary_list = [salary.amount for salary in role_found['salary']]
				if len(salary_list) == 0:
					role_found['salary'] = 0
				else:
					average_salary = sum(salary_list) / len(salary_list)
					role_found['salary'] = round(average_salary,0)
				role_found_dict.append(role_found)
				print(role_found_dict)

			return jsonify(
				{"code":200,
				"content": role_found_dict
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "Role not found"
				}), 404

	@app.route('/role/update', methods=["POST"])
	def update_role():
		if request.is_json:

			try:
				# Handle request
				request_obj = request.get_json()
				print("Role received in: ", type(request_obj), request_obj)
				role_id = request_obj['role_id']
				role_name = request_obj['role_name']
				role_desc = request_obj['role_desc']
				role_exp_level = request_obj['exp_level']

				# Query for existing entry
				try:
					role_saved = db.session.execute(
						db.select(Role).filter_by(id=role_id)).scalar_one()
				except Exception as e:
					print(e)
					return jsonify({
						"code": 404,
						"message": "Role id not found in Database."
					}),404

				# Replace values and commit
				try:
					role_saved.name = role_name
					role_saved.desc = role_desc
					role_saved.exp_level = role_exp_level
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "Error saving role to database."
					}),500

				return jsonify({
					"code": 201,
					"message": "Role updated successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving role to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/role/delete/<int:role_id>', methods=["DELETE"])
	def delete_role(role_id):
		# Query for existing entry
		try:
			role_saved = db.session.execute(
				db.select(Role).filter_by(id=role_id)).scalar_one()
		except Exception as e:
			print(e)
			return jsonify({
				"code": 404,
				"message": "No role id not found in Database."
			}),404

		# Delete
		try:
			db.session.delete(role_saved)
			db.session.commit()

		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error deleting role in database."
			}),500

		return jsonify({
			"code": 201,
			"message": "Role deleted successfully."
		}), 201

	# ---- Create, Read and Delete Mappings ----
	@app.route('/role/skills_mapped/create', methods=['POST'])
	def create_role_skills_mapped():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("role Skill received in: ", type(request_obj), request_obj)

				role_id = request_obj['role_id']
				skill_id = request_obj['skill_id'] # List

				role_saved= Role.query.filter_by(id=role_id).first()
				for skill in skill_id:
					skill_select= Skill.query.filter_by(id=skill).first()
					if skill_select not in role_saved.mapped_skills:
						role_saved.mapped_skills.append(skill_select)

				try:
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "role skills not saved successfully."
					}),401

				return jsonify({
					"code": 201,
					"message": "role skills saved successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving role skills to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/role/keyws_mapped/create', methods=['POST'])
	def create_role_keyws_mapped():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("Role Keyword received in: ", type(request_obj), request_obj)

				role_id = request_obj['role_id']
				keyw_id = request_obj['keyw_id'] # List

				role_saved= Role.query.filter_by(id=role_id).first()
				for keyw in keyw_id:
					keyw_select= Keyword.query.filter_by(id=keyw).first()
					if keyw_select not in role_saved.mapped_keyw:
						role_saved.mapped_keyw.append(keyw_select)

				try:
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "Role Keyword not saved successfully."
					}),401

				return jsonify({
					"code": 201,
					"message": "Role keyword saved successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving role to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/role/skills_mapped/get/<int:role_id>', methods=['GET'])
	def get_role_skills_mapped(role_id):
		try:
			print(role_id)
			role_saved = Role.query.filter_by(id=role_id).first()
			role_skills = role_saved.mapped_skills
			print(role_skills)
			skill_found_list = [skill.to_dict() for skill in role_skills]
			print(skill_found_list)
			return jsonify(
				{"code":200,
				"content": skill_found_list
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "role not found"
				}), 404

	@app.route('/role/keyws_mapped/get/<int:role_id>', methods=['GET'])
	def get_role_keyws_mapped(role_id):
		try:
			role_saved = Role.query.filter_by(id=role_id).first()
			role_keyws = role_saved.mapped_keyw
			keyword_found_list = [keyw.to_dict() for keyw in role_keyws]
			print(keyword_found_list)

			return jsonify(
				{
				"code":200,
				"content": keyword_found_list
			}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "role not found"
				}), 404

	@app.route('/role/specs_mapped/get/<int:role_id>', methods=['GET'])
	def get_role_specs_mapped(role_id):
		try:
			print(role_id)
			role_saved = Role.query.filter_by(id=role_id).first()
			mapped_spec = []
			for spec in role_saved.mapped_specs:
				spec_found = spec.to_dict()
				del spec_found['mapped_roles']
				mapped_spec.append(spec_found)

			return jsonify(
				{
				"code":200,
				"content": mapped_spec
			}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "role not found"
				}), 404

	@app.route('/role/skills_mapped/delete', methods=["POST"])
	def delete_role_skills_mapped():
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("Role Skill received in: ", type(request_obj), request_obj)
				role_id = request_obj['role_id']
				skill_id = request_obj['skill_id'] # List

				# Query for Specific role
				with app.app_context():
					role_saved= Role.query.filter_by(id=role_id).first()
					role_skill = role_saved.mapped_skills
					for skill in role_skill:
						if skill.id in skill_id:
							role_saved.mapped_skills.remove(skill)
							print(f'{skill.name} removed from Role mapping with {role_saved.name}')

					try:
						db.session.commit()

					except Exception as e:
						print(e)
						return jsonify({
							"code": 500,
							"message": "Error deleting role skill map."
						}),401

				return jsonify({
					"code": 201,
					"message": "Mapping deleted successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error Handling request"
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/role/keyws_mapped/delete', methods=["POST"])
	def delete_role_keyws_mapped():
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("Role Keyword received in: ", type(request_obj), request_obj)
				role_id = request_obj['role_id']
				keyw_id = request_obj['keyw_id'] # List

				# Query for Specific role
				with app.app_context():
					role_saved= Role.query.filter_by(id=role_id).first()
					role_keyw = role_saved.mapped_keyw
					for keyw in role_keyw:
						if keyw.id in keyw_id:
							role_saved.mapped_keyw.remove(keyw)
							print(f'{keyw.name} removed from keyw Bank of {role_saved.name}')

					try:
						db.session.commit()

					except Exception as e:
						print(e)
						return jsonify({
							"code": 500,
							"message": "Error deleting role keyw."
						}),401

				return jsonify({
					"code": 201,
					"message": "Role Keyword deleted successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving role to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/role/salary_mapped/get/<int:role_id>', methods=['GET'])
	def get_role_salary_mapped(role_id):
		try:
			role_saved = Role.query.filter_by(id=role_id).first()
			role_salaries = [sal.amount for sal in role_saved.salary]
			average_salary = sum(role_salaries) / len(role_salaries)
			print(average_salary)
			sal_breakdown = {}
			for sal in role_salaries:
				if sal in sal_breakdown:
					sal_breakdown[sal] += 1
				else:
					sal_breakdown[sal] = 1

			return jsonify(
				{
				"code":200,
				"content": {
					"id": role_id,
					"average": round(average_salary,0),
					"breakdown": sal_breakdown
				}
			}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "role not found"
				}), 404

	@app.route('/role/get_user_mapped/<int:role_id>', methods=['GET'])
	def get_role_users_mapped(role_id):
		try:
			role_saved = Role.query.filter_by(id=role_id).first()
			user_mapped = role_saved.mapped_users
			print(user_mapped)
			user_found_list = []
			for user in user_mapped:
				user_dict = user.to_dict()
				del user_dict['mapped_skills']
				del user_dict['mapped_courses']
				del user_dict['fav_roles']
				user_found_list.append(user_dict)

			return jsonify(
				{"code":200,
				"content": user_found_list
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "role not found"
				}), 404

	@app.route('/role/popular/get_top_3', methods=['GET'])
	def get_role_popular_top3():
		try:
			role_saved = Role.query.all()
			pop_ranking_dict = {}

			for role in role_saved:
				fav_number = len(role.mapped_users)
				pop_ranking_dict[role.id] = fav_number

			top_3_list = heapq.nlargest(3, pop_ranking_dict, key=pop_ranking_dict.get)
			return jsonify(
				{"code":200,
				"content": {
					"ranking": pop_ranking_dict,
					"top_3": top_3_list
				}
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "role not found"
				}), 404

	@app.route('/role/see_information', methods=['POST'])
	def see_role_information():

		if request.is_json:
				try:
					response = request.get_json()
					print("\nReceived a role id in JSON:", response)

					# do the actual work
					# 1. Send student id to user microservice to obtain profile information
					result = obtain_role_info(response['role_id'])
					print('\n------------------------')
					print('\nresult: ', result)
					return jsonify(result), result["code"]


				except Exception as e:
					# Unexpected error in code
					exc_type, exc_obj, exc_tb = sys.exc_info()
					fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
					ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
					print(ex_str)

					return jsonify({
						"code": 500,
						"message": "see_account_information.py internal error: " + ex_str
					}), 500


		# if reached here, not a JSON request.
		return jsonify({
			"code": 400,
			"message": "Invalid JSON input: " + str(request.get_data())
		}), 400
	# Helper function for see_role_information
	def obtain_role_info(role_id):

		print('\n----- Obtaining Role Information -----')
		role_info_result = get_role_lib(str(role_id))[0].json
		print('role_info_result:', role_info_result)

		# Check the user result - Error Handling;
		code = role_info_result["code"]
		print("code", code)

		if code not in range(200, 300):
			return {
				"code": 500,
				"data": {"role_info_result": role_info_result},
				"message": "There was an error in retrieving the user information"
			}
		print('\n\n----- Obtaining Roles Skills -----')

		role_skills_result = get_role_skills_mapped(str(role_id))[0].json
		print("role_skills_result:", role_skills_result, '\n')

		# Check the user courses result - Error Handling;
		code = role_skills_result["code"]
		print("code", code)

		if code not in range(200, 300):

			return {
				"code": 500,
				"data":
					{
						"role_info_result": role_info_result,
						"role_skills_result" : role_skills_result

					},
				"message": "There was an error in retrieving the user courses information"
			}

		print('\n\n----- Obtaining Roles Courses-----')

		for role_skills in role_skills_result['content']:
			role_skills["courses"] = []

		for role_skills in role_skills_result['content']:
			role_courses_result = get_skill_courses_mapped(str(role_skills['id']))[0].json
			print("role_courses_result:", role_courses_result, '\n')

			# Check the role courses result - Error Handling;
			code = role_courses_result["code"]
			print("code", code)

			# If code == 400 (no mapped courses found)
			if code == 404:
				role_skills["courses"].append(role_courses_result["message"])

			# If code not in 200-300 (error retrieving in the user skills information)
			elif code not in range(200, 300):
				role_skills["courses"].append("Error retrieving courses for this skill")
			# If code in 200-300 (add courses to a skill)
			else:
				role_skills["courses"] = role_courses_result["content"]

		print('\n\n----- Obtaining Roles Keyword-----')

		role_keywords_result = get_role_keyws_mapped(str(role_id))[0].json
		print("role_keywords_result:", role_keywords_result, '\n')


		# Check the user courses result - Error Handling;
		code = role_keywords_result["code"]
		print("code", code)
		# message = json.dumps(user_result)

		if code not in range(200, 300):

			return {
				"code": 500,
				"data":
					{
						"role_info_result": role_info_result,
						"role_skills_result" : role_skills_result,
						"role_keywords_result": role_keywords_result

					},
				"message": "There was an error in retrieving the user courses information"
			}


		# Consolidated Return User Information
		return {
			"code": 201,
			"data": {
				"role_info_result": role_info_result["content"],
				"role_skills_result": role_skills_result["content"],
				"role_keywords_result": role_keywords_result["content"]
			}
		}

	#============== SALARY ==============
	@app.route('/salary/create', methods=['POST'])
	def create_salary():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("salary received in: ", type(request_obj),
					request_obj)

				salary_id = request_obj['salary_id']
				salary_amount = request_obj['amount']
				role_id = request_obj['role_id'] # Single

				salary = Salary(id=salary_id, amount=salary_amount, role_id=role_id)

				try:
					# Add Entry to DB
					db.session.add(salary)
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 401,
						"message": "Duplicate salary or id."
					}),401

				return jsonify({
					"code": 201,
					"message": "salary saved successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving salary to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/salary/get_all', methods=["GET"])
	def get_all_salary():
		try:

			salary_saved = Salary.query.all()
			salary_found_dict = [salary.to_dict() for salary in salary_saved]

			return jsonify(
				{"code":200,
				"content": salary_found_dict
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "salaries not found"
				}), 404

	@app.route('/salary/delete/<int:salary_id>', methods=["DELETE"])
	def delete_salary(salary_id):
		# Query for existing entry
		try:
			salary_saved = db.session.execute(
				db.select(Salary).filter_by(id=salary_id)).scalar_one()
		except Exception as e:
			print(e)
			return jsonify({
				"code": 404,
				"message": "No salary id not found in Database."
			}),404

		# Delete
		try:
			db.session.delete(salary_saved)
			db.session.commit()

		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error deleting salary in database."
			}),500

		return jsonify({
			"code": 201,
			"message": "Salary deleted successfully."
		}), 201

	#============== SPECIALISATION ==============
	@app.route('/spec/create', methods=['POST'])
	def create_spec():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("spec received in: ", type(request_obj), request_obj)

				spec_id = request_obj['spec_id']
				spec_name = request_obj['spec_name']
				spec = Spec(id=spec_id, name=spec_name)

				try:
					# Add Entry to DB
					db.session.add(spec)
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 401,
						"message": "Duplicate specialisation or id."
					}),401

				return jsonify({
					"code": 201,
					"message": "Specialisation saved successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving specialisation to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/spec/get_one/<int:spec_id>', methods=["GET"])
	def get_spec_lib(spec_id):
		try:
			print(spec_id)
			spec_saved = db.session.execute(
						db.select(Spec).filter_by(
				id=spec_id)).scalar_one()

			spec_found_dict = spec_saved.__dict__
			del spec_found_dict['_sa_instance_state']
			print(spec_found_dict)

			return jsonify(
				{"code":200,
				"content": spec_found_dict
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "Specialisation not found"
				}), 404

	@app.route('/spec/get_all', methods=["GET"])
	def get_all_specs():
		try:

			spec_saved = Spec.query.all()
			spec_found_dict = []
			for spec in spec_saved:
				spec_found = spec.to_dict()
				role_ids = [role.id for role in spec_found['mapped_roles']]
				spec_found['mapped_roles'] = role_ids
				spec_found_dict.append(spec_found)
				print(spec_found_dict)

			return jsonify(
				{"code":200,
				"content": spec_found_dict
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "Specs not found"
				}), 404

	@app.route('/spec/update', methods=["POST"])
	def update_spec():
		if request.is_json:

			try:
				# Handle request
				request_obj = request.get_json()
				print("spec received in: ", type(request_obj),
					request_obj)
				spec_id = request_obj['spec_id']
				spec_name = request_obj['spec_name']

				# Query for existing entry
				try:
					spec_saved = db.session.execute(
						db.select(Spec).filter_by(
							id=spec_id)).scalar_one()
				except Exception as e:
					print(e)
					return jsonify({
						"code": 404,
						"message": "Specialisation id not found in Database."
					}),404

				# Replace values and commit
				try:
					spec_saved.name = spec_name
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "Error saving specialisation to database."
					}),500

				return jsonify({
					"code": 201,
					"message": "Specialisation updated successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving specialisation to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/spec/delete/<spec_id>', methods=["DELETE"])
	def delete_spec(spec_id):
		# Query for existing entry
		try:
			spec_saved = db.session.execute(
				db.select(Spec).filter_by(
					id=spec_id)).scalar_one()
		except Exception as e:
			print(e)
			return jsonify({
				"code": 404,
				"message": "No specialisation id not found in Database."
			}),404

		# Delete
		try:
			db.session.delete(spec_saved)
			db.session.commit()

		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error deleting specialisation in database."
			}),500

		return jsonify({
			"code": 201,
			"message": "Specialisation deleted successfully."
		}), 201

	# ---- Create Read and delete mappings ----
	@app.route('/spec/roles_mapped/create', methods=['POST'])
	def create_spec_roles_mapped():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("User Skill received in: ", type(request_obj), request_obj)

				spec_id = request_obj['spec_id']
				role_id = request_obj['role_id'] # List

				spec_saved= Spec.query.filter_by(id=spec_id).first()
				for role in role_id:
					role_select= Role.query.filter_by(id=role).first()
					if role_select not in spec_saved.mapped_roles:
						spec_saved.mapped_roles.append(role_select)

				try:
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "Spec roles not saved successfully."
					}),401

				return jsonify({
					"code": 201,
					"message": "Mapping saved successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving mapping to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/spec/role_mapped/salary_range/get/<int:spec_id>/<int:salary>', methods=['GET'])
	def get_spec_role_mapped_salary_range(spec_id, salary):
		try:
			spec_saved = Spec.query.filter_by(id=spec_id).first()
			output_data = []
			for role in spec_saved.mapped_roles:
				role_found = role.to_dict()
				print(role_found)
				del role_found['mapped_skills']
				del role_found['mapped_keyw']
				# Compute for average salary
				salary_list = [salary.amount for salary in role_found['salary']]
				if len(salary_list) == 0:
					role_found['salary'] = 0
				else:
					average_salary = sum(salary_list) / len(salary_list)
					role_found['salary'] = average_salary
				print(role_found)
				output_data.append(role_found)

			output_data = [role for role in output_data if role['salary'] >= salary]

			print(output_data)

			return jsonify(
				{
				"code":200,
				"content": output_data
			}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "Spec Role mapping not found"
				}), 404

	@app.route('/spec/roles_mapped/delete', methods=["POST"])
	def delete_spec_role():
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("User Skill received in: ", type(request_obj), request_obj)
				spec_id = request_obj['spec_id']
				role_id = request_obj['role_id'] # List

				# Query for Spec
				with app.app_context():
					spec_saved= Spec.query.filter_by(id=spec_id).first()
					spec_roles = spec_saved.mapped_roles
					for role in spec_roles:
						if role.id in role_id:
							spec_saved.mapped_roles.remove(role)
							print(f'{role.name} removed from Specialisation of {spec_saved.name}')

					try:
						db.session.commit()

					except Exception as e:
						print(e)
						return jsonify({
							"code": 500,
							"message": "Error deleting mapping."
						}),401

				return jsonify({
					"code": 201,
					"message": "Mapping deleted successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving mapping to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	#============== USER ==============
	# -------------------------
	# ---- User Auth ----
	# -------------------------
	# Helper functions for the auth process
	def generate_salt(length=16):
		return os.urandom(length)

	def hash_password(password, salt):
		salted_password = password.encode('utf-8') + salt
		sha512_hash = hashlib.sha512()
		sha512_hash.update(salted_password)
		hashed_password = sha512_hash.hexdigest()
		return hashed_password

	def check_password(input_password,salt,hashed_password):
		input_password = hash_password(input_password,salt)
		return input_password==hashed_password

	@app.route('/user/auth', methods=['POST'])
	def user_auth():
		# Filter for non json requests
		if request.is_json:
			try:
			# Handle request
				request_obj = request.get_json()
				print("User received in: ", type(request_obj), request_obj['user_id'])
				user_id = request_obj['user_id']
				user_password = request_obj['password']

				try:
					user_saved = db.session.execute(
						db.select(User).filter_by(id=user_id)).scalar_one()

					db_hpassword = user_saved.password
					db_salt = user_saved.salt

					if check_password(user_password, db_salt, db_hpassword):
						return jsonify({
						"user_id": user_id,
						"is_admin": user_saved.is_admin,
						"code": 200,
						"message": f"User {user_id} is authenticated!"
					}),200

					else:
						return jsonify({
						"code": 403,
						"message": "Password and username do not match"
					}),403

				except Exception as e:
					print(e)
					return jsonify({
						"code": 404,
						"message": "User not found"
					}),404

			except Exception as e:
				print(e)
				return jsonify({
					"code": 401,
					"message": "Invalid fields in request"
				}),401


		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/user/process_transcript', methods=['POST'])
	def process_transcript():
		# Take in PDF file itself. The PDF file should be of DataFile type.
		try:
			# Handle request
			uploaded_file = request.files.get('pdfFile')
			print("PDF file received. Processing.")

			#Read pdf file and split into individual line
			reader = PdfReader(uploaded_file)

			page=[]
			#Split line into individual sections (like course title, grade, cu)
			for i in range(len(reader.pages)):
				page.append(reader.pages[i])
				page[i] = page[i].extract_text().split("\n")

				for j in range(len(page[i])):
					page[i][j] = page[i][j].split("   ")

			courses_result = json.loads(get_all_courses()[0].get_data(as_text=True))
			print('Course result:', courses_result)
			course_dict = dict((course['name'], course['id']) for course in courses_result['content'])

			final_dict = {}

			for cur_page in page:
				for cur_list in cur_page:
					if len(cur_list)>=2:
						if cur_list[1] != "1.0 / 0.0 IP":
							if course_dict.get(cur_list[0]):
								final_dict[course_dict[cur_list[0]]] = cur_list[0]

			return jsonify({
				"code": 201,
				"message": "Course extracted successfully.",
				"content": final_dict
			}), 201

		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error processing PDF file."
			}), 500

	# ---------------------------------
	# ---- User Account Management ----
	# ---------------------------------

	@app.route('/user/create', methods=['POST'])
	def create_user():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("User received in: ", type(request_obj), request_obj)

				salt = generate_salt()
				hashed_password = hash_password(request_obj['user_password'], salt)
				user_id = request_obj['user_id']
				user_password = hashed_password
				if request_obj['is_admin'] == 0:
					is_admin = False	
				elif request_obj['is_admin'] == 1:
					is_admin = True
				
				user = User(id=user_id, password = user_password, salt=salt, is_admin=is_admin)

				try:
					# Add Entry to DB
					db.session.add(user)
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 401,
						"message": "Duplicate user or id."
					}),401

				return jsonify({
					"code": 201,
					"message": "User saved successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving user to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/user/update_particulars', methods=['POST'])
	def update_particulars():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("User received in: ", type(request_obj), request_obj)
				user_id = request_obj['user_id']
				user_faculty = request_obj['user_faculty']
				user_email = request_obj['user_email']
				user_name = request_obj['user_name']

				# Query for existing entry
				try:
					user_saved = db.session.execute(
						db.select(User).filter_by(id=user_id)).scalar_one()
				except Exception as e:
					print(e)
					return jsonify({
						"code": 404,
						"message": "User id not found in Database."
					}),404

				# Replace values and commit
				try:
					user_saved.full_name = user_name
					user_saved.faculty = user_faculty
					user_saved.user_email = user_email
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "Error saving user to database."
					}),500

				return jsonify({
					"code": 201,
					"message": "User particulars updated successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving user to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/user/update_password', methods=["POST"])
	def update_password():
		if request.is_json:

			try:
				# Handle request
				request_obj = request.get_json()
				print("User received in: ", type(request_obj), request_obj)
				user_id = request_obj['user_id']
				salt = generate_salt()
				hashed_password = hash_password(request_obj['user_password'], salt)
				user_password = hashed_password

				# Query for existing entry
				try:
					user_saved = User.query.filter_by(id=user_id).first()
					print(user_saved.to_dict())
				except Exception as e:
					print(e)
					return jsonify({
						"code": 404,
						"message": "User id not found in Database."
					}),404

				# Replace values and commit
				try:
					user_saved.password = user_password
					user_saved.salt = salt
					print(user_saved.to_dict())
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "Error saving user to database."
					}),500

				return jsonify({
					"code": 201,
					"message": "User updated successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving user to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403
    
	@app.route('/user/upload_profile_pic', methods=['POST'])
	def upload_profile_picture():
		try:
			# Handle request
			uploaded_file = request.files['file']
			s3_client = boto3.client('s3')
			if uploaded_file.filename != '':
				filename = uploaded_file.filename
				s3_bucket = 'pathfinders-frontend'
				response = s3_client.upload_file(uploaded_file,s3_bucket,filename)
				print(response)
				
		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "User not found"
				}), 404
	# ----------------------------------
	# ---- Admin Account Management ----
	# ----------------------------------
	
	@app.route('/user/get/<string:user_id>', methods=["GET"])
	def get_one_user(user_id):
		try:
			print(user_id)
			user_saved = db.session.execute(
						db.select(User).filter_by(id=user_id)).scalar_one()
			user_found_dict = user_saved.__dict__
			del user_found_dict['_sa_instance_state']
			del user_found_dict['password']
			print(user_found_dict)
			del user_found_dict['salt']

			return jsonify(
				{"code":200,
				"content": user_found_dict
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "User not found"
				}), 404

	@app.route('/user/get_all', methods=["GET"])
	def get_all_users():
		try:

			user_saved = User.query.all()
			user_found_dict = []
			for user in user_saved:
				user_found = user.to_dict()
				del user_found['mapped_courses']
				del user_found['fav_roles']
				user_found_dict.append(user_found)
				print(user_found_dict)

			return jsonify(
				{"code":200,
				"content": user_found_dict
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "Users not found"
				}), 404

	@app.route('/user/delete/<string:user_id>', methods=["DELETE"])
	def delete_user(user_id):
		# Query for existing entry
		try:
			user_saved = db.session.execute(
				db.select(User).filter_by(id=user_id)).scalar_one()
		except Exception as e:
			print(e)
			return jsonify({
				"code": 404,
				"message": "No user id not found in Database."
			}),404

		# Delete
		try:
			db.session.delete(user_saved)
			db.session.commit()

		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error deleting user in database."
			}),500

		return jsonify({
			"code": 201,
			"message": "User deleted successfully."
		}), 201

	# ---- Create, Read and Delete Mappings ----
	@app.route('/user/add_user_course', methods=['POST'])
	def add_user_course():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("User Skill received in: ", type(request_obj), request_obj)

				user_id = request_obj['user_id']
				course_id = request_obj['course_id'] # List

				user_saved= User.query.filter_by(id=user_id).first()
				for course in course_id:
					course_select= Course.query.filter_by(id=course).first()
					if course_select not in user_saved.mapped_courses:
						user_saved.mapped_courses.append(course_select)

				try:
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "User courses not saved successfully."
					}),401

				return jsonify({
					"code": 201,
					"message": "User saved successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving user to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/user/get_user_courses/<string:user_id>', methods=['GET'])
	def get_user_course(user_id):
		try:
			print(user_id)
			user_saved = User.query.filter_by(id=user_id).first()
			user_courses = user_saved.mapped_courses
			print(user_courses)
			courses_found_list = []
			for course in user_courses:
				mapping = course.to_dict()
				del mapping['mapped_skills']
				courses_found_list.append(mapping)
			print(courses_found_list)
			return jsonify(
				{"code":200,
				"content": courses_found_list
				}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "User not found"
				}), 404

	@app.route('/user/get_user_skills/<string:user_id>', methods=['GET'])
	def get_user_skills(user_id):
		try:
			user_saved = User.query.filter_by(id=user_id).first()
			user_courses = user_saved.mapped_courses
			user_skills = []
			for course in user_courses:
				mapped_skills = course.mapped_skills
				for skill in mapped_skills:
					if skill.to_dict() not in user_skills:
						user_skills.append(skill.to_dict())

			print(user_skills)

			return jsonify(
				{
				"code":200,
				"content": user_skills
			}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "User not found"
				}), 404

	@app.route('/user/delete_user_course', methods=["POST"])
	def delete_user_course():
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("User Course received in: ", type(request_obj), request_obj)
				user_id = request_obj['user_id']
				course_id = request_obj['course_id'] # List

				# Query for Specific user
				with app.app_context():
					user_saved= User.query.filter_by(id=user_id).first()
					print(user_saved)
					user_courses = user_saved.mapped_courses
					print(user_courses)
					for course in user_courses:
						if course.id in course_id:
							user_saved.mapped_courses.remove(course)
							print(f'{course.name} removed from Course Bank of {user_saved.full_name}')

					try:
						db.session.commit()

					except Exception as e:
						print(e)
						return jsonify({
							"code": 500,
							"message": "Error deleting user course."
						}),401

				return jsonify({
					"code": 201,
					"message": "Course removed successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving user to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/user/add_fav_role', methods=['POST'])
	def add_user_fav_role():
		# Filter for non json requests
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("User Skill received in: ", type(request_obj), request_obj)

				user_id = request_obj['user_id']
				role_id = request_obj['role_id'] # List

				user_saved= User.query.filter_by(id=user_id).first()
				print(user_saved)
				for role in role_id:
					role_select= Role.query.filter_by(id=role).first()
					if role_select not in user_saved.fav_roles:
						user_saved.fav_roles.append(role_select)

				try:
					db.session.commit()

				except Exception as e:
					print(e)
					return jsonify({
						"code": 500,
						"message": "Fav roles not saved successfully."
					}),401

				return jsonify({
					"code": 201,
					"message": "Fav roles saved successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving user to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/user/get_fav_roles/<string:user_id>', methods=['GET'])
	def get_user_fav_roles(user_id):
		try:
			user_saved = User.query.filter_by(id=user_id).first()
			fav_roles = user_saved.fav_roles
			user_fav = []
			for roles in fav_roles:
				mapped_roles = roles.to_dict()
				del mapped_roles['mapped_skills']
				del mapped_roles['mapped_keyw']
				del mapped_roles['salary']
				user_fav.append(mapped_roles)

			return jsonify(
				{
				"code":200,
				"content": user_fav
			}),200

		except Exception as e:
			print(e)
			return jsonify(
				{
				"code": 404,
				"message": "Favourite roles not found"
				}), 404

	@app.route('/user/delete_fav_role', methods=["POST"])
	def delete_user_fav_role():
		if request.is_json:
			try:
				# Handle request
				request_obj = request.get_json()
				print("User Course received in: ", type(request_obj), request_obj)
				user_id = request_obj['user_id']
				role_id = request_obj['role_id']

				# Query for Specific user
				with app.app_context():
					user_saved= User.query.filter_by(id=user_id).first()
					print(user_saved)
					fav_roles = user_saved.fav_roles
					print(f"{fav_roles=}")
					for role in fav_roles:
						if int(role_id) == role.id:
							user_saved.fav_roles.remove(role)
							print(f'{role.name} removed from fav list of {user_saved.full_name}')

					try:
						db.session.commit()

					except Exception as e:
						print(e)
						return jsonify({
							"code": 500,
							"message": "Error removing user fav role."
						}),401

				return jsonify({
					"code": 201,
					"message": "Fav role removed successfully."
				}), 201

			except Exception as e:
				print(e)
				return jsonify({
					"code": 500,
					"message": "Error saving user changes to database."
				}), 500

		else:
			return jsonify({
				"code": 403,
				"message": "Invalid input"
			}), 403

	@app.route('/user/view_account_information', methods=['POST'])
	def view_account_information():

		if request.is_json:
				try:
					response = request.get_json()
					print("\nReceived a student id in JSON:", response)

					# do the actual work
					# 1. Send student id to user microservice to obtain profile information
					result = obtain_account_info(response['student_id'])
					print('\n------------------------')
					print('\nresult: ', result)
					return jsonify(result), result["code"]


				except Exception as e:
					# Unexpected error in code
					exc_type, exc_obj, exc_tb = sys.exc_info()
					fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
					ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
					print(ex_str)

					return jsonify({
						"code": 500,
						"message": "view_account_information.py internal error: " + ex_str
					}), 500


		# if reached here, not a JSON request.
		return jsonify({
			"code": 400,
			"message": "Invalid JSON input: " + str(request.get_data())
		}), 400
	# Helper function for view account information
	def obtain_account_info(student_id):

		print('\n----- Obtaining User Information -----')
		user_info_result = get_one_user(str(student_id))[0].json
		print('user_result:', user_info_result)


		# Check the user result - Error Handling;
		code = user_info_result["code"]
		print("code", code)

		if code not in range(200, 300):

			return {
				"code": 500,
				"data": {"user_info_result": user_info_result},
				"message": "There was an error in retrieving the user information"
			}

		print('\n\n----- Obtaining User Courses -----')

		user_courses_result = get_user_course(str(student_id))[0].json
		print("user_courses_result:", user_courses_result, '\n')


		# Check the user courses result - Error Handling;
		code = user_courses_result["code"]
		print("code", code)
		# message = json.dumps(user_result)

		if code not in range(200, 300):

			return {
				"code": 500,
				"data":
					{
						"user_info_result": user_info_result,
						"user_courses_result" : user_courses_result

					},
				"message": "There was an error in retrieving the user courses information"
			}

		print('\n\n----- Obtaining User Skills-----')

		user_skills_result = get_user_skills(str(student_id))[0].json
		print("user_skills_result:", user_skills_result, '\n')

		# Check the user skills result - Error Handling;
		code = user_skills_result["code"]
		print("code", code)
		# message = json.dumps(user_result)

		if code not in range(200, 300):

			return {
				"code": 500,
				"data":
					{
						"user_info_result": user_info_result,
						"user_courses_result" : user_courses_result,
						"user_skills_result": user_skills_result

					},
				"message": "There was an error in retrieving the user skills information"
			}

		# Consolidated Return User Information
		return {
			"code": 201,
			"data": {
				"user_info_result": user_info_result["content"],
				"user_courses_result": user_courses_result,
				"user_skills_result": user_skills_result
			}
		}

	# upload user profile picture (should return in /user/view_account_information)
	@app.route('/user/upload_profile_image', methods=['POST'])
	def upload_profile_image():
		print("uploading profile image...")
		try:
			img_file = request.files.get("img_file")
			user_id = request.form.get("user_id")
			img_filename = f"{time.time_ns()}-{user_id}-{secure_filename(img_file.filename)}"
			print(img_filename)
			# raise Exception("Test stops here") // for testing until the db side
			try:
				user_saved = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one()
			except Exception as err:
				print(err)
				return jsonify({"code": 404, "error": err}), 404
			AWS_REGION = os.environ.get("AWS_REGION")
			AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
			AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
			AWS_IMG_S3 = os.environ.get("AWS_IMG_S3")
			s3 = boto3.client(
				"s3",
				region_name=AWS_REGION,
				aws_access_key_id=AWS_ACCESS_KEY,
				aws_secret_access_key=AWS_SECRET_KEY,
			)
			s3.upload_fileobj(img_file, AWS_IMG_S3, img_filename)
			file_url = f"https://{AWS_IMG_S3}.s3.amazonaws.com/{img_filename}"
			try:
				user_saved.profile_image = file_url # need to add a column called "profile_image" to the user table
				db.session.commit()
			except Exception as err:
				print(err)
				return jsonify({"code": 500, "message": f"Error: {err}"}), 500
			return jsonify({"code": 201, "file_url": file_url}), 201
		except Exception as err:
			print(err)
			return jsonify({"code": 500, "message": f"Error: {err}"}), 500
		return jsonify({"code": 400, "message": "Error: img_file and user_id must be valid"}), 400

	@app.route('/user/get_filtered_courses', methods=['POST'])
	def get_filter_courses():

		# JSON Request --> Skills List (List of skills unacquired by user)
		"""
			{
				"unacquired_skill": [17,39]
			}
		"""
		# Calls get-courses-map to get the list of courses for each skill
		# Returns List of Courses
		"""
			{
				"course_to_take" : [
					{
						"skill_id": 17,
						"courses": [] # all the courses required will be here
					},
					{
						"skill_id": 39,
						"courses": [] # all the courses required will be here
					}

				]
			}
		"""
		try:
			# Handle request
			response = request.get_json()
			unacquired_skill_list = response["unacquired_skill"]

			try:
				unacquired_courses_list = []

				for skill_id in unacquired_skill_list:

					temp_dict = {}
					skill_courses = get_skill_courses(skill_id)

					temp_dict['skill_id'] = skill_id
					temp_dict['courses'] = skill_courses
					unacquired_courses_list.append(temp_dict)


				return jsonify({
					"code": 201,
					"unacquired_courses_list":unacquired_courses_list,
				}), 201


			except:
				return {
				"code": 500,
				"message": "Error when processing user's unacquired skills"
			}

		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error processing data."
			}), 500
	# helper function for get_filter_skill
	def get_skill_courses(skill_id):

		skill_courses_result = get_skill_courses_mapped(str(skill_id))[0].json
		result_code = skill_courses_result["code"]

		if result_code not in range(200, 300):
			return {
				"code": 500,
				"data":
					{
						"skills_courses_result" : skill_courses_result

					},
				"message": "There was an error in retrieving the courses for skill information"
			}
		return skill_courses_result["content"]

	@app.route('/user/get_filter_skill', methods=['POST'])
	def get_filter_skill():
	# Take in PDF file itself. The PDF file should be of DataFile type.

		try:
			# Handle request
			response = request.get_json()
			user_id = response["user_id"]
			role_id = response["role_id"]

			try:
				user_skill_list = get_user_skill(user_id)
			except:
				return {
				"code": 500,
				"message": "Error when reading user."
			}

			try:
				role_skill_list = get_role_skill(role_id)
			except:
				return {
				"code": 500,
				"message": "Error when reading role."
			}

			user_skill_id_list = []
			role_skill_id_list = []

			for cur_dict in user_skill_list:
				cur_id = cur_dict["id"]
				user_skill_id_list.append(cur_id)

			for cur_dict in role_skill_list:
				cur_id = cur_dict["id"]
				role_skill_id_list.append(cur_id)

			user_skill_set = set(user_skill_id_list)
			role_skill_set = set(role_skill_id_list)

			unacquired_skill_set = role_skill_set - user_skill_set
			acquired_skill_list = list(role_skill_set - unacquired_skill_set)
			unacquired_skill_list = list(unacquired_skill_set)

			return jsonify({
				"code": 201,
				"acquired_skill":acquired_skill_list,
				"unacquired_skill":unacquired_skill_list
			}), 201

		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error processing data."
			}), 500
	# helper function for get_filter_skill
	def get_user_skill(user_id):
		user_skills_result = get_user_skills(str(user_id))[0].json
		result_code = user_skills_result["code"]

		if result_code not in range(200, 300):
			return {
				"code": 500,
				"data":
					{
						"user_skills_result" : user_skills_result

					},
				"message": "There was an error in retrieving the user skills information"
			}
		return user_skills_result["content"]
	# helper function for get_filter_skill
	def get_role_skill(role_id):
		role_skills_result = get_role_skills_mapped(str(role_id))[0].json
		result_code = role_skills_result["code"]

		if result_code not in range(200, 300):
			return {
				"code": 500,
				"data":
					{
						"user_skills_result" : role_skills_result

					},
				"message": "There was an error in retrieving the user skills information"
			}
		return role_skills_result["content"]

	@app.route('/user/get_role_progression_level', methods=['POST'])
	def get_role_progression_level():
		if request.is_json:
				try:
					response = request.get_json()
					print("\nReceived student and role id in JSON:", response)

					# do the actual work
					result = obtain_progression_level(response) # obtain profile information
					print('\n------------------------')
					print('\nresult: ', result)
					return jsonify(result), result["code"]


				except Exception as e:
					# Unexpected error in code
					exc_type, exc_obj, exc_tb = sys.exc_info()
					fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
					ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
					print(ex_str)

					return jsonify({
						"code": 500,
						"message": "view_account_information.py internal error: " + ex_str
					}), 500


		# if reached here, not a JSON request.
		return jsonify({
			"code": 400,
			"message": "Invalid JSON input: " + str(request.get_data())
		}), 400

	def obtain_progression_level(json_request):

		print(json_request['role_id'])
		print('\n----- Obtaining Role Skills -----')
		role_skills_call = get_role_skills_mapped(str(json_request['role_id']))
		role_skills_result = role_skills_call[0].json
		print('role_skills_result:', role_skills_result)

		# Check the role skills result - Error Handling;
		code = role_skills_result["code"]
		print("code", code)

		if code not in range(200, 300):
			return {
				"code": 500,
				"data": {"role_skills_result": role_skills_result},
				"message": "There was an error in retrieving the role skills information"
			}
		print('\n\n----- Obtaining User Skills -----')
		# user_skills_call = get_role_skills_mapped(str(json_request['student_id']))
		# user_skills_result = user_skills_call[0].json
		user_skills_call = get_user_skills(str(json_request['student_id']))
		user_skills_result = user_skills_call[0].json
		print("user_skills_result:", user_skills_result, '\n')


		# Check the user skills result - Error Handling;
		code = user_skills_result["code"]
		print("code", code)
		if code not in range(200, 300):

			return {
				"code": 500,
				"data":
					{
						"role_skills_result": role_skills_result,
						"user_skills_result" : user_skills_result
					},
				"message": "There was an error in retrieving the user skills information"
			}

		# Compute role progression level
		# only skills of the role
		role_skills_id_list = []
		# Get user_skills that fulfills role requirement
		role_user_skills_id_list = []

		# Get user_skills that they need to take
		skills_required_id_list = []

		#Skills to be displayed
		sorted_skills_list = []

		for skill in role_skills_result['content']:
			role_skills_id_list.append(skill['id'])

		for skill in user_skills_result['content']:
			if skill["id"] in role_skills_id_list:
				role_user_skills_id_list.append(skill["id"])

		if len(role_skills_id_list) != 0:
			role_progression_level = round(len(role_user_skills_id_list)/len(role_skills_id_list) * 100, 0)

		else:
			role_progression_level = "No skills mapped to the role currently"
		
		# Get the skills that user need to fulfil the role
		for skill in role_skills_id_list:
			if skill not in role_user_skills_id_list:
				skills_required_id_list.append(skill)
		
		sorted_skills_list = skills_required_id_list + role_user_skills_id_list
		sorted_skills_result = []

		for skill in sorted_skills_list:
			temp_dict = {}

			skill_info_call = get_one_skill(skill)
			skill_info_result = skill_info_call[0].json['content']

			temp_dict['id'] = skill_info_result['id']
			temp_dict['name'] = skill_info_result['name']

			sorted_skills_result.append(temp_dict)

		

		# Consolidated Return Information
		return {
			"code": 201,
			"data": {
				"role_skills_result": role_skills_result['content'],
				"user_skills_result" : user_skills_result['content'],
				"role_progression_level": role_progression_level,
				"role_user_skills_result":role_user_skills_id_list,
				"sorted_skills_result": sorted_skills_result

			}
		}

	# Get Progression Level of all Roles
	@app.route('/user/get_all_roles_progression', methods=['POST'])
	def get_all_roles_progression():

		if request.is_json:
				try:
					response = request.get_json()
					print("\nReceived student in JSON:", response)

					# do the actual work
					# 1. Send student id to user microservice to obtain profile information
					result = obtain_all_progression(response)
					print('\n------------------------')
					print('\nresult: ', result)
					return jsonify(result), result["code"]


				except Exception as e:
					# Unexpected error in code
					exc_type, exc_obj, exc_tb = sys.exc_info()
					fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
					ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
					print(ex_str)

					return jsonify({
						"code": 500,
						"message": "role_progression_level.py internal error: " + ex_str
					}), 500


		# if reached here, not a JSON request.
		return jsonify({
			"code": 400,
			"message": "Invalid JSON input: " + str(request.get_data())
		}), 400

	def obtain_all_progression(json_request):

		print("Student ID from obtain_all_progression",json_request['student_id'])

		# print('\n\n----- Obtaining User Skills -----')

		# user_skills_result = requests.get(user_skills_url + str(json_request['student_id'])).json()
		# print("user_skills_result:", user_skills_result, '\n')

		print('\n\n----- Obtaining User Skills -----')

		user_skills_result = get_user_skills(str(json_request['student_id']))[0].json
		print("user_skills_result:", user_skills_result, '\n')


		# Check the user skills result - Error Handling;
		code = user_skills_result["code"]
		print("code", code)

		if code not in range(200, 300):

			return {
				"code": 500,
				"data":
					{
						"user_skills_result" : user_skills_result

					},
				"message": "There was an error in retrieving the user skills information"
			}


		print('\n----- Obtaining All Roles -----')
		all_roles_result = get_all_roles()[0].json
		print('all_roles_result', all_roles_result) ## List of Dictionary


		# Check the role skills result - Error Handling;
		code =  all_roles_result["code"]
		print("code", code)

		if code not in range(200, 300):

			return {
				"code": 500,
				"data": {"all_roles_result":  all_roles_result},
				"message": "There was an error in retrieving the role skills information"
			}


		# Compute role progression level

		for role in all_roles_result["content"]:
			role["role_skills"] = []
			role["user_progression_level"] = 0

		for role in all_roles_result["content"]:
			role_skills_result = get_role_skills_mapped(str(role["id"]))[0].json
			print('role_skills_result:', role_skills_result)


			# Check the role skills result - Error Handling;
			code = role_skills_result["code"]
			print("code", code)

			if code not in range(200, 300):

				return {
					"code": 500,
					"data": {"role_skills_result": role_skills_result},
					"message": "There was an error in retrieving the role skills information for Role ID: " + str(role["id"])
				}

			role["role_skills"].append(role_skills_result["content"])

			# # Assign a list to store all role skills ID (for checking whether user has them or not)
			role_skills_id_list = []
			for role_skills in role_skills_result["content"]:
				role_skills_id_list.append(role_skills["id"])

			print(role_skills_id_list)

			# Assign a list to store all user skills ID that fulfills the role requirement
			role_user_skills_id_list = []

			# Loop trough every user_skill and if exist in role_skill, add into the list
			for user_skill in user_skills_result['content']:
				if user_skill["id"] in role_skills_id_list:
					role_user_skills_id_list.append(user_skill["id"])

			if len(role_skills_id_list) != 0:
				role["user_progression_level"] = len(role_user_skills_id_list)/len(role_skills_id_list) * 100
			else:
				role["user_progression_level"] = "No skills mapped to the role currently"




		print("Skills of all roles", all_roles_result)



		return {
			"code": 201,
			"data": {
				"user_skills_result" : user_skills_result['content'],
				"all_roles_result": all_roles_result["content"]

			}
		}

	# Get Completed Roles for a User
	@app.route('/user/get_completed_roles', methods=['POST'])
	def get_completed_roles():

		if request.is_json:
				try:
					response = request.get_json()
					print("\nReceived student_id in JSON:", response)


					result = obtain_all_progression(response)
					print('\n------------------------')
					print('\nresult: ', result)

					all_roles_progression = result["data"]["all_roles_result"]

					completed_roles = []

					for roles in all_roles_progression:
						if roles["user_progression_level"] == 100:
							completed_roles.append(roles)

					print("completed_roles", completed_roles)

					# return jsonify(completed_roles), result["code"]
					# # return all_roles_progression

					return {
						"code": 201,
						"data": {
							"completed_roles" : completed_roles
						}
					}


				except Exception as e:
					# Unexpected error in code
					exc_type, exc_obj, exc_tb = sys.exc_info()
					fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
					ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
					print(ex_str)

					return jsonify({
						"code": 500,
						"message": "role_progression_level.py internal error: " + ex_str
					}), 500


		# if reached here, not a JSON request.
		return jsonify({
			"code": 400,
			"message": "Invalid JSON input: " + str(request.get_data())
		}), 400

	def get_course_with_skill(unacquired_skill):
		course_dict = {}

		for cur_skill in unacquired_skill:
			cur_course_list = get_skill_courses_mapped(int(cur_skill))[0].json

			if 'content' in cur_course_list:
				cur_course_list = cur_course_list["content"]

				for cur_course in cur_course_list:
					cur_course_id = cur_course["id"]

					if course_dict.get(cur_course_id) is None:
						cur_course_skill_list = get_course_skills_mapped(str(cur_course_id))[0].json

						if 'content' in cur_course_skill_list:
							cur_course_skill_list = cur_course_skill_list["content"]
							cur_course_skill_list = [cur_skill["id"] for cur_skill in cur_course_skill_list]
							course_dict[cur_course_id] = cur_course_skill_list

		return course_dict
	@app.route('/course_recommender/calculate_course_score', methods=['POST'])
	def calculate_course_score_url():
		try:
			response = request.get_json()
			unacquired_skill = response["unacquired_skill"]
			sorted_course = calculate_course_with_skill(unacquired_skill)

			return jsonify({
				"code": 201,
				"content": sorted_course
			}), 201

		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error processing data."
			}), 500

	def calculate_course_with_skill(unacquired_skill):
		course_skill_dict = get_course_with_skill(unacquired_skill)

		all_skill_list = get_all_skills()[0].json
		all_skill_list = all_skill_list["content"]
		skill_id_list = [skill["id"] for skill in all_skill_list]
		largest_id = max(skill_id_list)
		skill_id_limit = largest_id + 1

		# Create a binary vector for the user's desired skills
		user_skills_vector = [1 if skill_id in unacquired_skill else 0 for skill_id in range(0, skill_id_limit)]

		# Calculate cosine similarity for each course
		cosine_similarity_scores = []
		sorted_course =[]

		if course_skill_dict != None:
			for cur_course_id in course_skill_dict:
				cur_skill_list = course_skill_dict[cur_course_id]
				# Create a binary vector for the skills taught by the course
				course_skills_vector = [1 if skill_id in cur_skill_list else 0 for skill_id in range(0, skill_id_limit)]

				# Convert lists to NumPy arrays for cosine_similarity function
				user_skills_vector = np.array(user_skills_vector).reshape(1, -1)  # Reshape to a 2D array
				course_skills_vector = np.array(course_skills_vector).reshape(1, -1)

				# Calculate cosine similarity
				similarity_score = cosine_similarity(user_skills_vector, course_skills_vector)

				# Append the course ID and similarity score to the list
				cosine_similarity_scores.append({'course_id': cur_course_id, 'similarity_score': similarity_score[0][0]})

				# Rank the courses based on their similarity scores
				sorted_course = sorted(cosine_similarity_scores, key=lambda x: x['similarity_score'], reverse=True)
		return sorted_course

	@app.route('/course_recommender/course_recommender', methods=['POST'])
	def course_recommender():
		try:
			response = request.get_json()
			role_id = response["role_id"]
			user_id = response["user_id"]
			try:
				user_skill_list = get_user_skill(user_id)
				role_skill_list = get_role_skill(role_id)
			except:
				return {
				"code": 500,
				"message": "Error when reading user and role."
			}
			user_skill_id_list = []
			role_skill_id_list = []

			for cur_dict in user_skill_list:
				cur_id = cur_dict["id"]
				user_skill_id_list.append(cur_id)

			for cur_dict in role_skill_list:
				cur_id = cur_dict["id"]
				role_skill_id_list.append(cur_id)

			user_skill_set = set(user_skill_id_list)
			role_skill_set = set(role_skill_id_list)

			unacquired_skill_set = role_skill_set - user_skill_set
			unacquired_skill = list(unacquired_skill_set)

			course_list = []
			cur_length = len(course_list)
			prev_length = len(course_list)

			while len(unacquired_skill)!=0:
				print(unacquired_skill)
				prev_length = cur_length
				sorted_course = calculate_course_with_skill(unacquired_skill)

				for cur_course in sorted_course:
					cur_course = cur_course["course_id"]

					if cur_course not in course_list:
						course_list.append(cur_course)

						cur_course_skill_list = get_course_skills_mapped(str(cur_course))[0].json
						cur_course_skill_list = cur_course_skill_list["content"]
						cur_course_skill_list = [cur_skill["id"] for cur_skill in cur_course_skill_list]
						unacquired_skill = [skill_id for skill_id in unacquired_skill if skill_id not in cur_course_skill_list]
						break
				cur_length = len(course_list)

				if cur_length == prev_length:
					break

			course_dict = {}

			for cur_course in course_list:
				course_saved = db.session.execute(
							db.select(Course).filter_by(id=cur_course)).scalar_one()
				cur_course_info = course_saved.__dict__
				course_dict[cur_course_info["id"]] = cur_course_info["name"]

			return jsonify({
				"code": 201,
				"content": course_dict
			}), 201


		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error processing data."
			}), 500

	@app.route('/course_recommender/all_course_available', methods=['POST'])
	def all_course_available():
		try:
			response = request.get_json()
			role_id = response["role_id"]
			user_id = response["user_id"]
			try:
				user_skill_list = get_user_skill(user_id)
				role_skill_list = get_role_skill(role_id)
			except:
				return {
				"code": 500,
				"message": "Error when reading user and role."
			}
			user_skill_id_list = []
			role_skill_id_list = []

			for cur_dict in user_skill_list:
				cur_id = cur_dict["id"]
				user_skill_id_list.append(cur_id)

			for cur_dict in role_skill_list:
				cur_id = cur_dict["id"]
				role_skill_id_list.append(cur_id)

			user_skill_set = set(user_skill_id_list)
			role_skill_set = set(role_skill_id_list)

			unacquired_skill_set = role_skill_set - user_skill_set
			unacquired_skill = list(unacquired_skill_set)

			course_list = []
			cur_length = len(course_list)
			prev_length = len(course_list)
			sorted_course = calculate_course_with_skill(unacquired_skill)
			course_list = []

			for cur_course in sorted_course:
				cur_course = cur_course["course_id"]
				course_list.append(cur_course)

			course_dict = {}

			for cur_course in course_list:
				course_saved = db.session.execute(
							db.select(Course).filter_by(id=cur_course)).scalar_one()
				cur_course_info = course_saved.__dict__
				course_dict[cur_course_info["id"]] = cur_course_info["name"]

			return jsonify({
				"code": 201,
				"content": course_dict
			}), 201


		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error processing data."
			}), 500


	@app.route('/competency/skill_course', methods=['POST'])
	def competency_skill_course_mapping():
		try:
			response = request.get_json()
			user_id = response["user_id"]
			try:
				user_skill_list = get_user_skill(user_id)
				user_course_list = get_user_course(user_id)[0].json
			except:
				return {
				"code": 500,
				"message": "Error when reading user and role."
			}

			user_course_id_list = []
			final_dict = {}
			user_course_list = user_course_list["content"]

			for cur_dict in user_course_list:
				cur_id = cur_dict["id"]
				user_course_id_list.append(cur_id)

			for cur_dict in user_skill_list:
				cur_name = cur_dict["name"]
				final_dict[cur_name] = []

			for cur_dict in user_skill_list:
				cur_id = cur_dict["id"]
				cur_name = cur_dict["name"]
				skill_saved= Skill.query.filter_by(id=cur_id).first()
				cur_course_list = []
				for course in skill_saved.mapped_courses:
					course_mapped = course.to_dict()
					del course_mapped['mapped_skills']
					cur_course_list.append(course_mapped)

				for cur_course in cur_course_list:
					if cur_course["id"] in user_course_id_list:
						cur_skill_course_dict = {"skill_id":cur_id,
												"course_id":cur_course["id"],
												"course_name":cur_course["name"]}
						final_dict[cur_name].append(cur_skill_course_dict)

			return jsonify({
				"code": 201,
				"content": final_dict
			}), 201

		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error processing data."
			}), 500

	@app.route('/competency/course_skill', methods=['POST'])
	def competency_course_skill_mapping():
		try:
			response = request.get_json()
			user_id = response["user_id"]
			try:
				user_skill_list = get_user_skill(user_id)
				user_course_list = get_user_course(user_id)[0].json
			except:
				return {
				"code": 500,
				"message": "Error when reading user and role."
			}

			user_skill_id_list = []
			final_dict = {}
			user_course_list = user_course_list["content"]

			for cur_dict in user_skill_list:
				cur_id = cur_dict["id"]
				user_skill_id_list.append(cur_id)

			for cur_dict in user_course_list:
				cur_name = cur_dict["name"]
				final_dict[cur_name] = []

			for cur_dict in user_course_list:
				cur_id = cur_dict["id"]
				cur_name = cur_dict["name"]
				course_saved= Course.query.filter_by(id=cur_id).first()
				cur_skill_list = [skill.to_dict() for skill in course_saved.mapped_skills]

				for cur_course in cur_skill_list:
					if cur_course["id"] in user_skill_id_list:
						cur_skill_course_dict = {"course_id":cur_id,
												"skill_id":cur_course["id"],
												"skill_name":cur_course["name"]}
						final_dict[cur_name].append(cur_skill_course_dict)

			return jsonify({
				"code": 201,
				"content": final_dict
			}), 201

		except Exception as e:
			print(e)
			return jsonify({
				"code": 500,
				"message": "Error processing data."
			}), 500
		
	
	return app
