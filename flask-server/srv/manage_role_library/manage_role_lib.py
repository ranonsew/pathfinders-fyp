from flask import jsonify, request
from dotenv import load_dotenv
import sys
from flask_cors import CORS
import heapq


import os
# Get the absolute path to the directory containing ORM_globals.py
orm_globals_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add the directory containing ORM_globals.py to sys.path
sys.path.insert(0, orm_globals_directory)
from ORM_globals import Role, Skill, Keyword, db, app
CORS(app)

# -------------------------
# ---- Flask Endpoints ----
# -------------------------

# ---- CRUD For Role Entity ----
@app.route('/create_role', methods=['POST'])
def create_role():
    # Filter for non json requests
    if request.is_json:
        try:
            # Handle request
            request_obj = request.get_json()
            print("Role received in: ", type(request_obj), request_obj)

            role_id = request_obj['role_id']
            role_name = request_obj['role_name']
            role_desc = request_obj['role_desc']
            role_exp_level = request_obj['exp_level']
            role = Role(id=role_id, name=role_name,
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


@app.route('/get_role/<int:role_id>', methods=["GET"])
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

@app.route('/get_all_roles', methods=["GET"])
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

@app.route('/update_role', methods=["POST"])
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


@app.route('/delete_role/<role_id>', methods=["DELETE"])
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
@app.route('/add_role_skill', methods=['POST'])
def add_role_skill():
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


@app.route('/add_role_keyw', methods=['POST'])
def add_role_keyw():
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

@app.route('/get_role_skill/<int:role_id>', methods=['GET'])
def get_role_skill(role_id):
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


@app.route('/get_role_keyw/<int:role_id>', methods=['GET'])
def get_role_keyw(role_id):
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


@app.route('/get_spec_mapped/<int:role_id>', methods=['GET'])
def get_spec_mapped(role_id):
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


@app.route('/delete_role_skill', methods=["POST"])
def delete_role_skill():
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


@app.route('/delete_role_keyw', methods=["POST"])
def delete_role_keyw():
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

@app.route('/get_role_salary/<int:role_id>', methods=['GET'])
def get_role_salary(role_id):
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


@app.route('/get_user_mapped/<int:role_id>', methods=['GET'])
def get_user_mapped(role_id):
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


@app.route('/get_role_popularity', methods=['GET'])
def get_role_popularity():
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
