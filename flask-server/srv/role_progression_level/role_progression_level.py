from flask import jsonify, request, Flask
import json
import os, sys

import requests
from flask_cors import CORS

#---- Init Flask ----
app = Flask(__name__)
CORS(app)

role_skills_url = "http://127.0.0.1:5004/get_role_skill/"
user_skills_url = "http://127.0.0.1:5010/get_user_skills/"
all_roles_url = "http://127.0.0.1:5004/get_all_roles"

#---- Flask Endpoints ----
@app.route('/get_role_progression_level', methods=['POST'])
def get_role_progression_level():
    
    if request.is_json:
            try:
                response = request.get_json()
                print("\nReceived student and role id in JSON:", response)

                # do the actual work
                # 1. Send student id to user microservice to obtain profile information
                result = obtain_progression_level(response)
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
                    "message": "view_account_information.py internal error: " + ex_str
                }), 500


    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def obtain_progression_level(json_request):

    print(json_request['role_id'])
   
    print('\n----- Obtaining Role Skills -----')
    role_skills_result = requests.get(role_skills_url + str(json_request['role_id'])).json()
    print('role_skills_result:', role_skills_result)


    # Check the role skills result - Error Handling; 
    code = role_skills_result["code"]
    print("code", code)

    if code not in range(200, 300):

        return {
            "code": 500,
            "data": {"role_skills_result": role_skills_result},
            "message": "There was an error in retrieving the role skills information"
        }

    print('\n\n----- Obtaining User Skills -----')    
    
    user_skills_result = requests.get(user_skills_url + str(json_request['student_id'])).json()
    print("user_skills_result:", user_skills_result, '\n')


    # Check the user skills result - Error Handling;
    code = user_skills_result["code"]
    print("code", code)

    if code not in range(200, 300):

        return {
            "code": 500,
            "data": 
                {
                    "role_skills_result": role_skills_result,
                    "user_skills_result" : user_skills_result
                
                },
            "message": "There was an error in retrieving the user skills information"
        }
    
    # Compute role progression level

   
    # only skills of the role
    role_skills_id_list = []
    # Get user_skills that fulfills role requirement
    role_user_skills_id_list = []

    for skill in role_skills_result['content']:
        role_skills_id_list.append(skill['id'])

    for skill in user_skills_result['content']:
        if skill["id"] in role_skills_id_list:
            role_user_skills_id_list.append(skill["id"])

    if len(role_skills_id_list) != 0:
        role_progression_level = round(len(role_user_skills_id_list)/len(role_skills_id_list) * 100, 0)

    else:
        role_progression_level = "No skills mapped to the role currently"




    # Consolidated Return Information
    return {
        "code": 201,
        "data": {
            "role_skills_result": role_skills_result['content'],
            "user_skills_result" : user_skills_result['content'],
            "role_progression_level": role_progression_level
                
        }
    }

# Get Progression Level of all Roles
@app.route('/get_all_roles_progression', methods=['POST'])
def get_all_roles_progression():
    
    if request.is_json:
            try:
                response = request.get_json()
                print("\nReceived student in JSON:", response)

                # do the actual work
                # 1. Send student id to user microservice to obtain profile information
                result = obtain_all_progression(response)
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
                    "message": "role_progression_level.py internal error: " + ex_str
                }), 500


    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def obtain_all_progression(json_request):

    print("Student ID from obtain_all_progression",json_request['student_id'])
   
    # print('\n\n----- Obtaining User Skills -----')    
    
    # user_skills_result = requests.get(user_skills_url + str(json_request['student_id'])).json()
    # print("user_skills_result:", user_skills_result, '\n')

    print('\n\n----- Obtaining User Skills -----')    
    
    user_skills_result = requests.get(user_skills_url + str(json_request['student_id'])).json()
    print("user_skills_result:", user_skills_result, '\n')


    # Check the user skills result - Error Handling;
    code = user_skills_result["code"]
    print("code", code)

    if code not in range(200, 300):

        return {
            "code": 500,
            "data": 
                {
                    "user_skills_result" : user_skills_result
                
                },
            "message": "There was an error in retrieving the user skills information"
        }
    
   
    print('\n----- Obtaining All Roles -----')
    all_roles_result = requests.get(all_roles_url).json()
    # print('all_roles_result', all_roles_result) ## List of Dictionary


    # Check the role skills result - Error Handling; 
    code =  all_roles_result["code"]
    print("code", code)

    if code not in range(200, 300):

        return {
            "code": 500,
            "data": {"all_roles_result":  all_roles_result},
            "message": "There was an error in retrieving the role skills information"
        }


    # Compute role progression level

    for role in all_roles_result["content"]:
        role["role_skills"] = []
        role["user_progression_level"] = 0
    
    for role in all_roles_result["content"]:
        role_skills_result = requests.get(role_skills_url + str(role["id"])).json()
        # print('role_skills_result:', role_skills_result)


        # Check the role skills result - Error Handling; 
        code = role_skills_result["code"]
        print("code", code)

        if code not in range(200, 300):

            return {
                "code": 500,
                "data": {"role_skills_result": role_skills_result},
                "message": "There was an error in retrieving the role skills information for Role ID: " + role["id"]
            }
        
        role["role_skills"].append(role_skills_result["content"])

        # # Assign a list to store all role skills ID (for checking whether user has them or not)
        role_skills_id_list = []
        for role_skills in role_skills_result["content"]:
            role_skills_id_list.append(role_skills["id"])
        
        print(role_skills_id_list)

        # Assign a list to store all user skills ID that fulfills the role requirement
        role_user_skills_id_list = []

        # Loop trough every user_skill and if exist in role_skill, add into the list
        for user_skill in user_skills_result['content']:
            if user_skill["id"] in role_skills_id_list:
               role_user_skills_id_list.append(user_skill["id"])
        
        if len(role_skills_id_list) != 0:
            role["user_progression_level"] = len(role_user_skills_id_list)/len(role_skills_id_list) * 100
        else:
            role["user_progression_level"] = "No skills mapped to the role currently"




    print("Skills of all roles", all_roles_result)
  


    return {
        "code": 201,
        "data": {
            "user_skills_result" : user_skills_result['content'],
            "all_roles_result": all_roles_result["content"]
                
        }
    }

# Get Completed Roles for a User
@app.route('/get_completed_roles', methods=['POST'])
def get_completed_roles():
    
    if request.is_json:
            try:
                response = request.get_json()
                print("\nReceived student_id in JSON:", response)


                result = obtain_all_progression(response)
                print('\n------------------------')
                print('\nresult: ', result)

                all_roles_progression = result["data"]["all_roles_result"]

                completed_roles = []

                for roles in all_roles_progression:
                    if roles["user_progression_level"] == 100:
                        completed_roles.append(roles)
                
                print("completed_roles", completed_roles)

                # return jsonify(completed_roles), result["code"]
                # # return all_roles_progression

                return {
                    "code": 201,
                    "data": {
                        "completed_roles" : completed_roles                
                    }
                }


            except Exception as e:
                # Unexpected error in code
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
                print(ex_str)

                return jsonify({
                    "code": 500,
                    "message": "role_progression_level.py internal error: " + ex_str
                }), 500


    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5015, debug=True)
