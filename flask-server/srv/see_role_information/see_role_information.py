from flask import jsonify, request, Flask
import os, sys
import requests
import json
from flask_cors import CORS

#---- Set up connection to DB ----
app = Flask(__name__)
CORS(app)

role_info_url = "http://127.0.0.1:5004/get_role/"
role_skills_url = "http://127.0.0.1:5004/get_role_skill/"
role_courses_url = "http://127.0.0.1:5006/get_course_mapped/"
role_keywords_url = "http://127.0.0.1:5004/get_role_keyw/"


#---- Flask Endpoints ----
@app.route('/see_role_information', methods=['POST'])
def see_role_information():
    
    if request.is_json:
            try:
                response = request.get_json()
                print("\nReceived a role id in JSON:", response)

                # do the actual work
                # 1. Send student id to user microservice to obtain profile information
                result = obtain_role_info(response['role_id'])
                print('\n------------------------')
                print('\nresult: ', result)
                return jsonify(result), result["code"]


            except Exception as e:
                # Unexpected error in code
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
                print(ex_str)

                return jsonify({
                    "code": 500,
                    "message": "see_account_information.py internal error: " + ex_str
                }), 500


    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def obtain_role_info(role_id):
   
    print('\n----- Obtaining Role Information -----')
    role_info_result = requests.get(role_info_url + str(role_id)).json()
    print('role_info_result:', role_info_result)


    # Check the user result - Error Handling; 
    code = role_info_result["code"]
    print("code", code)
    # message = json.dumps(user_result)

    if code not in range(200, 300):

        return {
            "code": 500,
            "data": {"role_info_result": role_info_result},
            "message": "There was an error in retrieving the user information"
        }

    print('\n\n----- Obtaining Roles Skills -----')    
    
    role_skills_result = requests.get(role_skills_url + str(role_id)).json()
    print("role_skills_result:", role_skills_result, '\n')


    # Check the user courses result - Error Handling;
    code = role_skills_result["code"]
    print("code", code)
    # message = json.dumps(user_result)

    if code not in range(200, 300):

        return {
            "code": 500,
            "data": 
                {
                    "role_info_result": role_info_result,
                    "role_skills_result" : role_skills_result
                
                },
            "message": "There was an error in retrieving the user courses information"
        }
    
    print('\n\n----- Obtaining Roles Courses-----')    

    for role_skills in role_skills_result['content']:
        role_skills["courses"] = []
    
    for role_skills in role_skills_result['content']:
        role_courses_result = requests.get(role_courses_url + str(role_skills['id'])).json()
        print("role_courses_result:", role_courses_result, '\n')

        # Check the role courses result - Error Handling;
        code = role_courses_result["code"]
        print("code", code)
        # message = json.dumps(user_result)

        # If code == 400 (no mapped courses found)
        if code == 404:
            role_skills["courses"].append(role_courses_result["message"])
        
        # If code not in 200-300 (error retrieving in the user skills information)
        elif code not in range(200, 300):
            role_skills["courses"].append("Error retrieving courses for this skill")
        # If code in 200-300 (add courses to a skill)
        else:
            role_skills["courses"] = role_courses_result["content"]

    print('\n\n----- Obtaining Roles Keyword-----')    

    role_keywords_result = requests.get(role_keywords_url + str(role_id)).json()
    print("role_keywords_result:", role_keywords_result, '\n')


    # Check the user courses result - Error Handling;
    code = role_keywords_result["code"]
    print("code", code)
    # message = json.dumps(user_result)

    if code not in range(200, 300):

        return {
            "code": 500,
            "data": 
                {
                    "role_info_result": role_info_result,
                    "role_skills_result" : role_skills_result,
                    "role_keywords_result": role_keywords_result
                
                },
            "message": "There was an error in retrieving the user courses information"
        }


    # Consolidated Return User Information
    return {
        "code": 201,
        "data": {
            "role_info_result": role_info_result["content"],
            "role_skills_result": role_skills_result["content"],
            "role_keywords_result": role_keywords_result["content"]
        }
    }



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5014, debug=True)
