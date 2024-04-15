from flask import jsonify, request, Flask
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
import sys 

sys.path.insert(0,'../..')
from ORM_globals import Course_Skill_Map


#---- Set up connection to DB ----
db = SQLAlchemy()
app = Flask(__name__)

load_dotenv()

user_name = os.environ.get('USER')
password = os.environ.get('PASSWORD')
host_db = os.environ.get('HOSTDB')
database = os.environ.get('DATABASE')

app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql+pymysql://{user_name}:{password}@{host_db}:3306/{database}'

db.init_app(app)


with app.app_context():
    db.create_all()


#---- Flask Endpoints ----
@app.route('/create_course_skill_map', methods=['POST'])
def create_course_skill_map():
    # Filter for non json requests
    if request.is_json:
        try:
            # Handle request
            request_obj = request.get_json()
            print("Course Skill Map received in: ", type(request_obj), 
                  request_obj)

            map_id = request_obj['map_id']
            course_id = request_obj['course_id']
            skill_id = request_obj['skill_id']
            course_skill_map = Course_Skill_Map(id=map_id, 
                                                course_id=course_id, 
                                                skill_id=skill_id)

            try:
                # Add Entry to DB
                db.session.add(course_skill_map)
                db.session.commit()

            except Exception as e:
                print(e)
                return jsonify({
                    "code": 401,
                    "message": "Duplicate mapping or id."
                }),401
            
            return jsonify({
                "code": 201, 
                "message": "Course Skill Map saved successfully."
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


@app.route('/get_mapped_skills/<int:course_id>', methods=["GET"])
def get_course_lib(course_id):
    try:
        print(course_id)
        skill_saved = db.session.execute(
                    db.select(Course_Skill_Map).filter_by(course_id=course_id)).scalar()
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
            "message": "Course Skill Map not found"
             }), 404
        

@app.route('/update_course', methods=["POST"])
def update_course():
    if request.is_json:
        
        try:
            # Handle request
            request_obj = request.get_json()
            print("Course Skill Map received in: ", type(request_obj), 
                  request_obj)
            
            course_id = request_obj['course_id']
            skill_id = request_obj['skill_id']

            # Query for existing entry
            try:
                mapping_saved = db.session.execute(
                    db.select(Course_Skill_Map).filter_by(course_id=course_id, 
                                                          skill_id=skill_id)).scalar_one()
            except Exception as e:
                print(e)
                return jsonify({
                    "code": 404,
                    "message": "Course Skill Map id not found in Database."
                }),404

            # Replace values and commit  
            try:
                mapping_saved.course_id = course_id
                mapping_saved.skill_id = skill_id
                db.session.commit()

            except Exception as e:
                print(e)
                return jsonify({
                    "code": 500,
                    "message": "Error saving mapping to database."
                }),500
            
            return jsonify({
                "code": 201, 
                "message": "Course Skill Map updated successfully."
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


@app.route('/delete_course/<course_id>/<skill_id>', methods=["DELETE"])
def delete_course(course_id, skill_id):
    # Query for existing entry
    try:
        course_saved = db.session.execute(
            db.select(Course_Skill_Map).filter_by(course_id=course_id, 
                                                  skill_id=skill_id)).scalar_one()
    except Exception as e:
        print(e)
        return jsonify({
            "code": 404,
            "message": "Mapping not found in Database."
        }),404

    # Delete   
    try:
        db.session.delete(course_saved)
        db.session.commit()

    except Exception as e:
        print(e)
        return jsonify({
            "code": 500,
            "message": "Error deleting mapping from database."
        }),500
    
    return jsonify({
        "code": 201, 
        "message": "Course Skill Mapping deleted successfully."
    }), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)