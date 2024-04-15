from flask import jsonify, request, Flask
from flask_sqlalchemy import SQLAlchemy
import sys
from flask_cors import CORS

import os
# Get the absolute path to the directory containing ORM_globals.py
orm_globals_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add the directory containing ORM_globals.py to sys.path
sys.path.insert(0, orm_globals_directory)
from ORM_globals import Keyword, db, app
CORS(app)

# -------------------------
# ---- Flask Endpoints ----
# -------------------------

# ---- CRUD For Keyword Entity ----
@app.route('/create_keyword', methods=['POST'])
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


@app.route('/get_keyword/<int:keyword_id>', methods=["GET"])
def get_keyword_lib(keyword_id):
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


@app.route('/get_all_keywords', methods=["GET"])
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


@app.route('/update_keyword', methods=["POST"])
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


@app.route('/delete_keyword/<int:keyword_id>', methods=["DELETE"])
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


@app.route('/get_roles_mapped/<int:keyw_id>', methods=['GET'])
def get_mapped_roles(keyw_id):
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
