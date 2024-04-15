from flask import jsonify, request, Flask
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
import sys 

sys.path.insert(0,'../..')
from ORM_globals import Spec_Role_Map


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
@app.route('/create_spec_role_map', methods=['POST'])
def create_spec_role_map():
    # Filter for non json requests
    if request.is_json:
        try:
            # Handle request
            request_obj = request.get_json()
            print("Spec Role Map received in: ", type(request_obj), 
                  request_obj)

            map_id = request_obj['map_id']
            spec_id = request_obj['spec_id']
            role_id = request_obj['role_id']
            spec_role_map = Spec_Role_Map(id=map_id, 
                                            role_id=role_id, 
                                            spec_id=spec_id)

            try:
                # Add Entry to DB
                db.session.add(spec_role_map)
                db.session.commit()

            except Exception as e:
                print(e)
                return jsonify({
                    "code": 401,
                    "message": "Duplicate mapping."
                }),401
            
            return jsonify({
                "code": 201, 
                "message": "Spec Role Map saved successfully."
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


@app.route('/get_mapped_role/<int:spec_id>', methods=["GET"])
def get_course_lib(spec_id):
    try:
        print(spec_id)
        mapping_saved = db.session.execute(
                    db.select(Spec_Role_Map).filter_by(id=spec_id)).scalar()
        roles_found_dict = mapping_saved.__dict__
        del roles_found_dict['_sa_instance_state']
        print(roles_found_dict)

        return jsonify(
            {"code":200, 
             "content": roles_found_dict
             }),200

    except Exception as e:
        print(e)
        return jsonify(
            {
            "code": 404,
            "message": "Spec Role Map not found"
             }), 404
        

@app.route('/update_spec_role', methods=["POST"])
def update_course():
    if request.is_json:
        
        try:
            # Handle request
            request_obj = request.get_json()
            print("Spec Role Map received in: ", 
                  type(request_obj), request_obj)
            
            spec_id = request_obj['spec_id']
            role_id = request_obj['role_id']

            # Query for existing entry
            try:
                mapping_saved = db.session.execute(
                    db.select(Spec_Role_Map).filter_by(spec_id=spec_id,
                                                          role_id=role_id, 
                                                          )).scalar_one()
            except Exception as e:
                print(e)
                return jsonify({
                    "code": 404,
                    "message": "Spec Role Map id not found in Database."
                }),404

            # Replace values and commit  
            try:
                mapping_saved.spec_id = spec_id
                mapping_saved.role_id = role_id
                db.session.commit()

            except Exception as e:
                print(e)
                return jsonify({
                    "code": 500,
                    "message": "Error saving mapping to database."
                }),500
            
            return jsonify({
                "code": 201, 
                "message": "Spec Role Map updated successfully."
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


@app.route('/delete_role_keyword_map/<spec_id>/<role_id>', methods=["DELETE"])
def delete_course(spec_id, role_id):
    # Query for existing entry
    try:
        mapping_saved = db.session.execute(
            db.select(Spec_Role_Map).filter_by(spec_id=spec_id, 
                                                  role_id=role_id)).scalar_one()
    except Exception as e:
        print(e)
        return jsonify({
            "code": 404,
            "message": "Mapping not found in Database."
        }),404

    # Delete   
    try:
        db.session.delete(mapping_saved)
        db.session.commit()

    except Exception as e:
        print(e)
        return jsonify({
            "code": 500,
            "message": "Error deleting mapping in database."
        }),500
    
    return jsonify({
        "code": 201, 
        "message": "Spec Role Map deleted successfully."
    }), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)