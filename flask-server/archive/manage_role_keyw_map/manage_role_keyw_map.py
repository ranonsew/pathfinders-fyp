from flask import jsonify, request, Flask
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
import sys 

sys.path.insert(0,'../..')
from ORM_globals import Role_Keyword_Map

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
@app.route('/create_role_keyword_map', methods=['POST'])
def create_role_keyword_map():
    # Filter for non json requests
    if request.is_json:
        try:
            # Handle request
            request_obj = request.get_json()
            print("Role Keyword Map received in: ", type(request_obj), 
                  request_obj)

            map_id = request_obj['map_id']
            role_id = request_obj['role_id']
            keyword_id = request_obj['keyword_id']
            role_keyword_map = Role_Keyword_Map(id=map_id, 
                                                role_id=role_id, 
                                                keyword_id=keyword_id)

            try:
                # Add Entry to DB
                db.session.add(role_keyword_map)
                db.session.commit()

            except Exception as e:
                print(e)
                return jsonify({
                    "code": 401,
                    "message": "Duplicate course or id."
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


@app.route('/get_mapped_keyword/<int:role_id>', methods=["GET"])
def get_course_lib(role_id):
    try:
        print(role_id)
        mapping_saved = db.session.execute(
                    db.select(Role_Keyword_Map).filter_by(id=role_id)).scalar()
        keywords_found_dict = mapping_saved.__dict__
        del keywords_found_dict['_sa_instance_state']
        print(keywords_found_dict)

        return jsonify(
            {"code":200, 
             "content": keywords_found_dict
             }),200

    except Exception as e:
        print(e)
        return jsonify(
            {
            "code": 404,
            "message": "Role Keyword Map not found"
             }), 404
        

@app.route('/update_course', methods=["POST"])
def update_course():
    if request.is_json:
        
        try:
            # Handle request
            request_obj = request.get_json()
            print("Role Keyword Map received in: ", 
                  type(request_obj), request_obj)
            
            role_id = request_obj['role_id']
            keyword_id = request_obj['keyword_id']

            # Query for existing entry
            try:
                mapping_saved = db.session.execute(
                    db.select(Role_Keyword_Map).filter_by(role_id=role_id, 
                                                          keyword_id=keyword_id)).scalar_one()
            except Exception as e:
                print(e)
                return jsonify({
                    "code": 404,
                    "message": "Role Keyword Map id not found in Database."
                }),404

            # Replace values and commit  
            try:
                mapping_saved.role_id = role_id
                mapping_saved.keyword_id = keyword_id
                db.session.commit()

            except Exception as e:
                print(e)
                return jsonify({
                    "code": 500,
                    "message": "Error saving mapping to database."
                }),500
            
            return jsonify({
                "code": 201, 
                "message": "Role Keyword Map updated successfully."
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


@app.route('/delete_role_keyword_map/<role_id>/<keyword_id>', methods=["DELETE"])
def delete_course(role_id, keyword_id):
    # Query for existing entry
    try:
        course_saved = db.session.execute(
            db.select(Role_Keyword_Map).filter_by(role_id=role_id, 
                                                  keyword_id=keyword_id)).scalar_one()
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
            "message": "Error deleting mapping in database."
        }),500
    
    return jsonify({
        "code": 201, 
        "message": "Role Keyword Map deleted successfully."
    }), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)