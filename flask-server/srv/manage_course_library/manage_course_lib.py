from flask import jsonify, request, Flask
import os
from flask_sqlalchemy import SQLAlchemy
import sys
from flask_cors import CORS


# Get the absolute path to the directory containing ORM_globals.py
orm_globals_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add the directory containing ORM_globals.py to sys.path
sys.path.insert(0, orm_globals_directory)
from ORM_globals import Course, Skill, db, app
CORS(app)

# -------------------------
# ---- Flask Endpoints ----
# -------------------------

# ---- CRUD For Course Entity ----
@app.route('/create_course', methods=['POST'])
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


@app.route('/get_course/<string:course_id>', methods=["GET"])
def get_course_lib(course_id):
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


@app.route('/get_all_courses', methods=["GET"])
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


@app.route('/update_course', methods=["POST"])
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


@app.route('/delete_course/<string:course_id>', methods=["DELETE"])
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
@app.route('/add_course_skill', methods=['POST'])
def create_course_skill():
    # Filter for non json requests
    if request.is_json:
        try:
            # Handle request
            request_obj = request.get_json()
            print("User Skill received in: ", type(request_obj), request_obj)

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



@app.route('/get_skills_mapped/<string:course_id>', methods=["GET"])
def get_skills_mapped(course_id):
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


@app.route('/delete_course_skill', methods=["POST"])
def delete_course_skill():
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
