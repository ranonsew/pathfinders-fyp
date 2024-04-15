from flask import jsonify, request, Flask
from dotenv import load_dotenv
import sys 
from flask_cors import CORS

import os
# Get the absolute path to the directory containing ORM_globals.py
orm_globals_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add the directory containing ORM_globals.py to sys.path
sys.path.insert(0, orm_globals_directory)
from ORM_globals import Salary, app, db
CORS(app)

# -------------------------
# ---- Flask Endpoints ----
# -------------------------

# ---- CRUD For Skill Entity ----
@app.route('/create_salary', methods=['POST'])
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
        
        
@app.route('/get_all_salary', methods=["GET"])
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




@app.route('/delete_salary/<salary_id>', methods=["DELETE"])
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
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)