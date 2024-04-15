from flask import jsonify, request, Flask
from flask_cors import CORS, cross_origin
from werkzeug.datastructures import FileStorage
from pypdf import PdfReader
import requests
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

user_skill_url = "http://127.0.0.1:5010/get_user_skills/"
role_skill_url = "http://127.0.0.1:5004/get_role_skill/"
skill_course_url = "http://127.0.0.1:5006/get_course_mapped/"
course_skill_url = "http://127.0.0.1:5000/get_skills_mapped/"
get_all_skill_url = "http://127.0.0.1:5006/get_all_skills"

#---- Flask Endpoints ----
@app.route('/get_filter_skill', methods=['POST'])
def get_filter_skill():
    try:
        # Handle request
        response = request.get_json()
        user_id = response["user_id"]
        role_id = response["role_id"]

        try:
            user_skill_list = get_user_skill(user_id)
        except:
            return {
            "code": 500,
            "message": "Error when reading user."
        }

        try:
            role_skill_list = get_role_skill(role_id)
        except:
            return {
            "code": 500,
            "message": "Error when reading role."
        }

        user_skill_id_list = []
        role_skill_id_list = []

        for cur_dict in user_skill_list:
            cur_id = cur_dict["id"]
            user_skill_id_list.append(cur_id)

        for cur_dict in role_skill_list:
            cur_id = cur_dict["id"]
            role_skill_id_list.append(cur_id)

        user_skill_set = set(user_skill_id_list)
        role_skill_set = set(role_skill_id_list)

        unacquired_skill_set = role_skill_set - user_skill_set
        acquired_skill_list = list(role_skill_set - unacquired_skill_set)
        unacquired_skill_list = list(unacquired_skill_set)

        return jsonify({
            "code": 201,
            "acquired_skill":acquired_skill_list,
            "unacquired_skill":unacquired_skill_list
        }), 201

    except Exception as e:
        print(e)
        return jsonify({
            "code": 500,
            "message": "Error processing data."
        }), 500

def get_course_with_skill(unacquired_skill):
    course_dict = {}

    for cur_skill in unacquired_skill:
        cur_course_url = skill_course_url + str(cur_skill)
        cur_course_list = requests.get(cur_course_url).json()
        
        if 'content' in cur_course_list:
            cur_course_list = cur_course_list["content"]
            
            for cur_course in cur_course_list:
                cur_course_id = cur_course["id"]

                if course_dict.get(cur_course_id) is None:
                    cur_course_skill_url = course_skill_url + str(cur_course_id)
                    cur_course_skill_list = requests.get(cur_course_skill_url).json()
                    
                    if 'content' in cur_course_skill_list:
                        cur_course_skill_list = cur_course_skill_list["content"]
                        cur_course_skill_list = [cur_skill["id"] for cur_skill in cur_course_skill_list]
                        course_dict[cur_course_id] = cur_course_skill_list

    return course_dict

@app.route('/calculate_course_score', methods=['POST'])
def calculate_course_score_url():
    try:
        response = request.get_json()
        unacquired_skill = response["unacquired_skill"]
        sorted_course = calculate_course_with_skill(unacquired_skill)

        return jsonify({
            "code": 201,
            "content": sorted_course
        }), 201

    except Exception as e:
        print(e)
        return jsonify({
            "code": 500,
            "message": "Error processing data."
        }), 500
def calculate_course_with_skill(unacquired_skill):
    course_skill_dict = get_course_with_skill(unacquired_skill)

    all_skill_list = requests.get(get_all_skill_url).json()
    all_skill_list = all_skill_list["content"]
    skill_id_list = [skill["id"] for skill in all_skill_list]
    largest_id = max(skill_id_list)
    skill_id_limit = largest_id + 1

    # Create a binary vector for the user's desired skills
    user_skills_vector = [1 if skill_id in unacquired_skill else 0 for skill_id in range(0, skill_id_limit)]

    # Calculate cosine similarity for each course
    cosine_similarity_scores = []
    sorted_course =[]

    if course_skill_dict != None:
        for cur_course_id in course_skill_dict:
            cur_skill_list = course_skill_dict[cur_course_id]
            # Create a binary vector for the skills taught by the course
            course_skills_vector = [1 if skill_id in cur_skill_list else 0 for skill_id in range(0, skill_id_limit)]

            # Convert lists to NumPy arrays for cosine_similarity function
            user_skills_vector = np.array(user_skills_vector).reshape(1, -1)  # Reshape to a 2D array
            course_skills_vector = np.array(course_skills_vector).reshape(1, -1)

            # Calculate cosine similarity
            similarity_score = cosine_similarity(user_skills_vector, course_skills_vector)
            
            # Append the course ID and similarity score to the list
            cosine_similarity_scores.append({'course_id': cur_course_id, 'similarity_score': similarity_score[0][0]})

            # Rank the courses based on their similarity scores
            sorted_course = sorted(cosine_similarity_scores, key=lambda x: x['similarity_score'], reverse=True)
    return sorted_course

@app.route('/course_recommender', methods=['POST'])
def course_recommender():
    try:
        response = request.get_json()
        unacquired_skill = response["unacquired_skill"]
        course_list = []
        cur_length = len(course_list)
        prev_length = len(course_list)

        while len(unacquired_skill)!=0:
            print(unacquired_skill)
            prev_length = cur_length
            sorted_course = calculate_course_with_skill(unacquired_skill)

            for cur_course in sorted_course:
                cur_course = cur_course["course_id"]

                if cur_course not in course_list:
                    course_list.append(cur_course)

                    cur_course_skill_url = course_skill_url + str(cur_course)
                    cur_course_skill_list = requests.get(cur_course_skill_url).json()
                    cur_course_skill_list = cur_course_skill_list["content"]
                    cur_course_skill_list = [cur_skill["id"] for cur_skill in cur_course_skill_list]
                    unacquired_skill = [skill_id for skill_id in unacquired_skill if skill_id not in cur_course_skill_list]
                    print(unacquired_skill)
                    break
            cur_length = len(course_list)

            if cur_length == prev_length:
                break

        return jsonify({
            "code": 201,
            "content": course_list
        }), 201


    except Exception as e:
        print(e)
        return jsonify({
            "code": 500,
            "message": "Error processing data."
        }), 500

def get_user_skill(user_id):
    user_skills_result = requests.get(user_skill_url + str(user_id)).json()
    result_code = user_skills_result["code"]

    if result_code not in range(200, 300):
        return {
            "code": 500,
            "data": 
                {
                    "user_skills_result" : user_skills_result
                
                },
            "message": "There was an error in retrieving the user skills information"
        }
    return user_skills_result["content"]

def get_role_skill(role_id):
    role_skills_result = requests.get(role_skill_url + str(role_id)).json()
    result_code = role_skills_result["code"]

    if result_code not in range(200, 300):
        return {
            "code": 500,
            "data": 
                {
                    "user_skills_result" : role_skills_result
                
                },
            "message": "There was an error in retrieving the user skills information"
        }
    return role_skills_result["content"]



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5014, debug=True)
