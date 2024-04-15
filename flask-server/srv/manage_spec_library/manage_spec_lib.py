from flask import jsonify, request, Flask
import os
import sys 
from flask_cors import CORS



# Get the absolute path to the directory containing ORM_globals.py
orm_globals_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add the directory containing ORM_globals.py to sys.path
sys.path.insert(0, orm_globals_directory)
from ORM_globals import Spec, Role, db, app
CORS(app)
# -------------------------
# ---- Flask Endpoints ----
# -------------------------


# ---- CRUD For Spec Entity ----
@app.route('/create_spec', methods=['POST'])
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


@app.route('/get_spec/<int:spec_id>', methods=["GET"])
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


@app.route('/get_all_specs', methods=["GET"])
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

@app.route('/update_spec', methods=["POST"])
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


@app.route('/delete_spec/<spec_id>', methods=["DELETE"])
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
@app.route('/add_spec_role', methods=['POST'])
def add_spec_role():
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


@app.route('/search_spec_role_sal/<int:spec_id>/<int:salary>', methods=['GET'])
def get_spec_role(spec_id, salary):
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


@app.route('/delete_spec_role', methods=["POST"])
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)