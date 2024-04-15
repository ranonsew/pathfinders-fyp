from flask import jsonify, request, Flask
from dotenv import load_dotenv
import sys 
from flask_cors import CORS

import os
# Get the absolute path to the directory containing ORM_globals.py
orm_globals_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add the directory containing ORM_globals.py to sys.path
sys.path.insert(0, orm_globals_directory)
from ORM_globals import Skill, app, db
CORS(app)

# -------------------------
# ---- Flask Endpoints ----
# -------------------------

# ---- CRUD For Skill Entity ----
@app.route('/create_skill', methods=['POST'])
def create_skill():
    # Filter for non json requests
    if request.is_json:
        try:
            # Handle request
            request_obj = request.get_json()
            print("Skill received in: ", type(request_obj), 
                  request_obj)

            skill_id = request_obj['skill_id']
            skill_name = request_obj['skill_name']
            skill = Skill(id=skill_id, name=skill_name)

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
                "message": "Skill saved successfully."
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


@app.route('/get_skill/<int:skill_id>', methods=["GET"])
def get_skill_lib(skill_id):
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
        
        
@app.route('/get_all_skills', methods=["GET"])
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

@app.route('/update_skill', methods=["POST"])
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


@app.route('/delete_skill/<skill_id>', methods=["DELETE"])
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

# Read mappings
@app.route('/get_course_mapped/<int:skill_id>', methods=["GET"])
def get_courses_mapped(skill_id):
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


@app.route('/get_roles_mapped/<int:skill_id>', methods=["GET"])
def get_roles_mapped(skill_id):
    try:
        print(skill_id)
        skill_saved= Skill.query.filter_by(id=skill_id).first()
        output_list = []
        for role in skill_saved.mapped_roles:
            role_found = role.to_dict()
            del role_found['mapped_skills']
            del role_found['mapped_keyw']
            output_list.append(role_found)
            

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
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)