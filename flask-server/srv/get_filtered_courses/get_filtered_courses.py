from flask import jsonify, request, Flask
from flask_cors import CORS, cross_origin
import requests

app = Flask(__name__)
CORS(app)

get_skills_courses_url = "http://192.168.10.115:5006/get_course_mapped/"


#---- Flask Endpoints ----
@app.route('/get_filtered_courses', methods=['POST'])
def get_filter_courses():
    
    # JSON Request --> Skills List (List of skills unacquired by user)
    """
        {
            "unacquired_skill": [17,39]
        }
    """
    # Calls get-courses-map to get the list of courses for each skill
    # Returns List of Courses 
    """
        {
            "course_to_take" : [ 
                {
                    "skill_id": 17,
                    "courses": [] # all the courses required will be here
                },
                {
                    "skill_id": 39,
                    "courses": [] # all the courses required will be here
                }

            ]
        }
    """
    try:
        # Handle request
        response = request.get_json()
        unacquired_skill_list = response["unacquired_skill"]

        try:
            unacquired_courses_list = []

            for skill_id in unacquired_skill_list:

                temp_dict = {}
                skill_courses = get_skill_courses(skill_id)

                temp_dict['skill_id'] = skill_id
                temp_dict['courses'] = skill_courses
                unacquired_courses_list.append(temp_dict)  

            
            return jsonify({
                "code": 201,
                "unacquired_courses_list":unacquired_courses_list,
            }), 201

    
        except:
            return {
            "code": 500,
            "message": "Error when processing user's unacquired skills"
        }

    except Exception as e:
        print(e)
        return jsonify({
            "code": 500,
            "message": "Error processing data."
        }), 500



def get_skill_courses(skill_id):
    
    skill_courses_result = requests.get(get_skills_courses_url + str(skill_id)).json()

    result_code = skill_courses_result["code"]

    if result_code not in range(200, 300):
        return {
            "code": 500,
            "data": 
                {
                    "skills_courses_result" : skill_courses_result
                
                },
            "message": "There was an error in retrieving the courses for skill information"
        }
    return skill_courses_result["content"]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5015, debug=True)
