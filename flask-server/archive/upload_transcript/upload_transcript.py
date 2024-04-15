from flask import jsonify, request, Flask
import os, sys
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
import requests
import json
from flask_cors import CORS


#---- Set up connection to DB ----
db = SQLAlchemy()
app = Flask(__name__)
CORS(app)

load_dotenv()

user_name = os.environ.get('USER')
password = os.environ.get('PASSWORD')
host_db = os.environ.get('HOSTDB')
database = os.environ.get('DATABASE')

app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql+pymysql://{user_name}:{password}@{host_db}:3306/{database}'

db.init_app(app)

add_user_courses_url = "http://192.168.10.115:5010/add_user_course"

#---- Flask Endpoints ----
@app.route('/upload_transcript', methods=['POST'])
def upload_transcript():
    
    if request.is_json:
            try:
                response = request.get_json()
                print("\nReceived a student id in JSON:", response)

                # do the actual work
                # 1. Send student id to user microservice to obtain profile information
                result = store_user_information(response)
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

def store_user_information(student_info):
   
    print('\n----- Storing User Courses and Skills Information -----')
    # user_info_result = requests.get(user_info_url + str(student_id)).json()
    # print('user_result:', user_info_result)


    # # Check the user result - Error Handling; 
    # code = user_info_result["code"]
    # print("code", code)
    # # message = json.dumps(user_result)

    # if code not in range(200, 300):

    #     return {
    #         "code": 500,
    #         "data": {"user_info_result": user_info_result},
    #         "message": "There was an error in retrieving the user information"
    #     }

    # print('\n\n----- Obtaining User Courses -----')    
    
    # shipping_result = invoke_http(
    #     shipping_record_URL, method="POST", json=order_result['data'])
    add_user_courses_result = requests.post(add_user_courses_url,json=student_info).json()
    print("user_courses_result:", add_user_courses_result, '\n')


    # Check the user courses result - Error Handling;
    code = add_user_courses_result["code"]
    print("code", code)
    # message = json.dumps(user_result)

    if code not in range(200, 300):

        return {
            "code": 500,
            "data": 
                {
                    "add_user_courses_result": add_user_courses_result
                },
            "message": "There was an error in storing the user courses information"
        }
    
    # print('\n\n----- Obtaining User Skills-----')    
    
    # user_skills_result = requests.get(user_skills_url + str(student_id)).json()
    # print("user_skills_result:", user_skills_result, '\n')


    # # Check the user skills result - Error Handling;
    # code = user_skills_result["code"]
    # print("code", code)
    # # message = json.dumps(user_result)

    # if code not in range(200, 300):

    #     return {
    #         "code": 500,
    #         "data": 
    #             {
    #                 "user_info_result": user_info_result,
    #                 "user_courses_result" : user_courses_result,
    #                 "user_skills_result": user_skills_result
                
    #             },
    #         "message": "There was an error in retrieving the user skills information"
    #     }



    # Consolidated Return User Information
    return {
        "code": 201,
        "data": {
            "add_user_courses_result": add_user_courses_result
        }
    }



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5013, debug=True)
