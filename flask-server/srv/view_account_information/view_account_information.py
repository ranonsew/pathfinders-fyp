from flask import jsonify, request, Flask
import os, sys
import requests
import json
from flask_cors import CORS

#---- Init Flask App ----
app = Flask(__name__)
CORS(app)

user_info_url = "http://127.0.0.1:5010/get_user/"
user_courses_url = "http://127.0.0.1:5010/get_user_courses/"
user_skills_url = "http://127.0.0.1:5010/get_user_skills/"

#---- Flask Endpoints ----
@app.route('/view_account_information', methods=['POST'])
def view_account_information():
    
    if request.is_json:
            try:
                response = request.get_json()
                print("\nReceived a student id in JSON:", response)

                # do the actual work
                # 1. Send student id to user microservice to obtain profile information
                result = obtain_account_info(response['student_id'])
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

def obtain_account_info(student_id):
   
    print('\n----- Obtaining User Information -----')
    user_info_result = requests.get(user_info_url + str(student_id)).json()
    print('user_result:', user_info_result)


    # Check the user result - Error Handling; 
    code = user_info_result["code"]
    print("code", code)
    # message = json.dumps(user_result)

    if code not in range(200, 300):

        return {
            "code": 500,
            "data": {"user_info_result": user_info_result},
            "message": "There was an error in retrieving the user information"
        }

    print('\n\n----- Obtaining User Courses -----')    
    
    # shipping_result = invoke_http(
    #     shipping_record_URL, method="POST", json=order_result['data'])
    user_courses_result = requests.get(user_courses_url + str(student_id)).json()
    print("user_courses_result:", user_courses_result, '\n')


    # Check the user courses result - Error Handling;
    code = user_courses_result["code"]
    print("code", code)
    # message = json.dumps(user_result)

    if code not in range(200, 300):

        return {
            "code": 500,
            "data": 
                {
                    "user_info_result": user_info_result,
                    "user_courses_result" : user_courses_result
                
                },
            "message": "There was an error in retrieving the user courses information"
        }
    
    print('\n\n----- Obtaining User Skills-----')    
    
    user_skills_result = requests.get(user_skills_url + str(student_id)).json()
    print("user_skills_result:", user_skills_result, '\n')


    # Check the user skills result - Error Handling;
    code = user_skills_result["code"]
    print("code", code)
    # message = json.dumps(user_result)

    if code not in range(200, 300):

        return {
            "code": 500,
            "data": 
                {
                    "user_info_result": user_info_result,
                    "user_courses_result" : user_courses_result,
                    "user_skills_result": user_skills_result
                
                },
            "message": "There was an error in retrieving the user skills information"
        }



    # Consolidated Return User Information
    return {
        "code": 201,
        "data": {
            "user_info_result": user_info_result["content"],
            "user_courses_result": user_courses_result,
            "user_skills_result": user_skills_result
        }
    }



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5012, debug=True)
