from flask import jsonify, request, Flask
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
import sys 

sys.path.insert(0,'../..')
from ORM_globals import User_Skill_Map
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


#---- Flask Endpoints ----
@app.route('/create_user_skill_map', methods=['POST'])
def create_user_skill_map():
    # Filter for non json requests
    if request.is_json:
        try:
            # Handle request
            request_obj = request.get_json()
            print("Role Keyword Map received in: ", type(request_obj), 
                  request_obj)

            map_id = request_obj['map_id']
            user_id = request_obj['user_id']
            skill_id = request_obj['skill_id']
            user_skill_map = User_Skill_Map(
                id=map_id, user_id=user_id, skill_id=skill_id)

            try:
                # Add Entry to DB
                db.session.add(user_skill_map)
                db.session.commit()

            except Exception as e:
                print(e)
                return jsonify({
                    "code": 401,
                    "message": "Duplicate mapping."
                }),401
            
            return jsonify({
                "code": 201, 
                "message": "User Skill Map saved successfully."
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


@app.route('/get_user_skill/<int:user_id>', methods=["GET"])
def get_user_skill(user_id):
    try:
        print(user_id)
        mapping_saved = db.session.execute(
                    db.select(User_Skill_Map).filter_by(
                        user_id=user_id)).scalar()
        
        skill_found_dict = mapping_saved.__dict__
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
            "message": "No user courses not found"
             }), 404
        

@app.route('/update_user_courses', methods=["POST"])
def update_course():
    if request.is_json:
        
        try:
            # Handle request
            request_obj = request.get_json()
            print("Role Skill Map received in: ", type(request_obj), 
                  request_obj)
            user_id = request_obj['user_id']
            skill_id = request_obj['skill_id']

            # Query for existing entry
            try:
                mapping_saved = db.session.execute(
                    db.select(User_Skill_Map).filter_by(
                    user_id=user_id, skill_id=skill_id)).scalar_one()
            except Exception as e:
                print(e)
                return jsonify({
                    "code": 404,
                    "message": "User skill not found in Database."
                }),404

            # Replace values and commit  
            try:
                mapping_saved.user_id = user_id
                mapping_saved.skill_id = skill_id
                db.session.commit()

            except Exception as e:
                print(e)
                return jsonify({
                    "code": 500,
                    "message": "Error saving entry to database."
                }),500
            
            return jsonify({
                "code": 201, 
                "message": "User skill bank updated successfully."
            }), 201
        
        except Exception as e:
            print(e)
            return jsonify({
                "code": 500,
                "message": "Error saving entry to database."
            }), 500

    else:
        return jsonify({
            "code": 403,
            "message": "Invalid input"
        }), 403


@app.route('/delete_user_skill_map/<user_id>/<skill_id>', methods=["DELETE"])
def delete_course(user_id, skill_id):
    # Query for existing entry
    try:
        mapping_saved = db.session.execute(
            db.select(User_Skill_Map).filter_by(
                user_id=user_id, skill_id=skill_id)).scalar_one()
    except Exception as e:
        print(e)
        return jsonify({
            "code": 404,
            "message": "User skill not found in Database."
        }),404

    # Delete   
    try:
        db.session.delete(mapping_saved)
        db.session.commit()

    except Exception as e:
        print(e)
        return jsonify({
            "code": 500,
            "message": "Error deleting entry in database."
        }),500
    
    return jsonify({
        "code": 201, 
        "message": "User skill deleted successfully."
    }), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)