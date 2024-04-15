from flask import jsonify, request, Flask
import os
import hashlib
import sys
# Get the absolute path to the directory containing ORM_globals.py
orm_globals_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add the directory containing ORM_globals.py to sys.path
sys.path.insert(0, orm_globals_directory)
from ORM_globals import User, Course, Role, db, app
from flask_cors import CORS
CORS(app)

def generate_salt(length=16):
    return os.urandom(length)

def hash_password(password, salt):
    salted_password = password.encode('utf-8') + salt
    sha512_hash = hashlib.sha512()
    sha512_hash.update(salted_password)
    hashed_password = sha512_hash.hexdigest()
    return hashed_password

def check_password(input_password,salt,hashed_password):
    input_password = hash_password(input_password,salt)
    return input_password==hashed_password
# -------------------------
# ---- User Auth ----
# -------------------------
@app.route('/user_auth', methods=['POST'])
def user_auth():
    # Filter for non json requests
    if request.is_json:
        try:
        # Handle request
            request_obj = request.get_json()
            print("User received in: ", type(request_obj), request_obj)
            user_id = request_obj['user_id']
            user_password = request_obj['password']

            try:
                user_saved = db.session.execute(
                    db.select(User).filter_by(id=user_id)).scalar_one()

                db_hpassword = user_saved.password
                db_salt = user_saved.salt

                if check_password(user_password, db_salt, db_hpassword):
                    return jsonify({
                    "user_id": user_id,
                    "is_admin": user_saved.is_admin,
                    "code": 200,
                    "message": f"User {user_id} is authenticated!"
                }),200

                else:
                    return jsonify({
                    "code": 403,
                    "message": "Password and username do not match"
                }),403

            except Exception as e:
                print(e)
                return jsonify({
                    "code": 404,
                    "message": "User not found"
                }),404

        except Exception as e:
            print(e)
            return jsonify({
                "code": 401,
                "message": "Invalid fields in request"
            }),401


    else:
        return jsonify({
            "code": 403,
            "message": "Invalid input"
        }), 403

# ---------------------------------
# ---- User Account Management ----
# ---------------------------------

@app.route('/create_user', methods=['POST'])
def create_user():
    # Filter for non json requests
    if request.is_json:
        try:
            # Handle request
            request_obj = request.get_json()
            print("User received in: ", type(request_obj), request_obj)

            salt = generate_salt()
            hashed_password = hash_password(request_obj['user_password'], salt)
            user_id = request_obj['user_id']
            user_password = hashed_password
            is_admin = False

            user = User(id=user_id, password = user_password, salt=salt, is_admin=is_admin)

            try:
                # Add Entry to DB
                db.session.add(user)
                db.session.commit()

            except Exception as e:
                print(e)
                return jsonify({
                    "code": 401,
                    "message": "Duplicate user or id."
                }),401

            return jsonify({
                "code": 201,
                "message": "User saved successfully."
            }), 201

        except Exception as e:
            print(e)
            return jsonify({
                "code": 500,
                "message": "Error saving user to database."
            }), 500

    else:
        return jsonify({
            "code": 403,
            "message": "Invalid input"
        }), 403


@app.route('/update_particulars', methods=['POST'])
def update_particulars():
    # Filter for non json requests
    if request.is_json:
        try:
            # Handle request
            request_obj = request.get_json()
            print("User received in: ", type(request_obj), request_obj)
            user_id = request_obj['user_id']
            user_faculty = request_obj['user_faculty']
            user_email = request_obj['user_email']
            user_name = request_obj['user_name']

            # Query for existing entry
            try:
                user_saved = db.session.execute(
                    db.select(User).filter_by(id=user_id)).scalar_one()
            except Exception as e:
                print(e)
                return jsonify({
                    "code": 404,
                    "message": "User id not found in Database."
                }),404

            # Replace values and commit
            try:
                user_saved.full_name = user_name
                user_saved.faculty = user_faculty
                user_saved.user_email = user_email
                db.session.commit()

            except Exception as e:
                print(e)
                return jsonify({
                    "code": 500,
                    "message": "Error saving user to database."
                }),500

            return jsonify({
                "code": 201,
                "message": "User particulars updated successfully."
            }), 201

        except Exception as e:
            print(e)
            return jsonify({
                "code": 500,
                "message": "Error saving user to database."
            }), 500

    else:
        return jsonify({
            "code": 403,
            "message": "Invalid input"
        }), 403


@app.route('/update_password', methods=["POST"])
def update_password():
    if request.is_json:

        try:
            # Handle request
            request_obj = request.get_json()
            print("User received in: ", type(request_obj), request_obj)
            user_id = request_obj['user_id']
            salt = generate_salt()
            hashed_password = hash_password(request_obj['user_password'], salt)
            user_password = hashed_password[:41]

            # Query for existing entry
            try:
                user_saved = User.query.filter_by(id=user_id).first()
                print(user_saved.to_dict())
            except Exception as e:
                print(e)
                return jsonify({
                    "code": 404,
                    "message": "User id not found in Database."
                }),404

            # Replace values and commit
            try:
                user_saved.password = user_password
                user_saved.salt = salt
                print(user_saved.to_dict())
                db.session.commit()

            except Exception as e:
                print(e)
                return jsonify({
                    "code": 500,
                    "message": "Error saving user to database."
                }),500

            return jsonify({
                "code": 201,
                "message": "User updated successfully."
            }), 201

        except Exception as e:
            print(e)
            return jsonify({
                "code": 500,
                "message": "Error saving user to database."
            }), 500

    else:
        return jsonify({
            "code": 403,
            "message": "Invalid input"
        }), 403


# ----------------------------------
# ---- Admin Account Management ----
# ----------------------------------

@app.route('/get_user/<int:user_id>', methods=["GET"])
def get_user_lib(user_id):
    try:
        print(user_id)
        user_saved = db.session.execute(
                    db.select(User).filter_by(id=user_id)).scalar_one()
        user_found_dict = user_saved.__dict__
        del user_found_dict['_sa_instance_state']
        del user_found_dict['password']
        print(user_found_dict)
        del user_found_dict['salt']

        return jsonify(
            {"code":200,
             "content": user_found_dict
             }),200

    except Exception as e:
        print(e)
        return jsonify(
            {
            "code": 404,
            "message": "User not found"
             }), 404


@app.route('/get_all_users', methods=["GET"])
def get_all_users():
    try:

        user_saved = User.query.all()
        user_found_dict = []
        for user in user_saved:
            user_found = user.to_dict()
            del user_found['mapped_courses']
            del user_found['fav_roles']
            user_found_dict.append(user_found)
            print(user_found_dict)

        return jsonify(
            {"code":200,
             "content": user_found_dict
             }),200

    except Exception as e:
        print(e)
        return jsonify(
            {
            "code": 404,
            "message": "Users not found"
             }), 404


@app.route('/delete_user/<int:user_id>', methods=["DELETE"])
def delete_user(user_id):
    # Query for existing entry
    try:
        user_saved = db.session.execute(
            db.select(User).filter_by(id=user_id)).scalar_one()
    except Exception as e:
        print(e)
        return jsonify({
            "code": 404,
            "message": "No user id not found in Database."
        }),404

    # Delete
    try:
        db.session.delete(user_saved)
        db.session.commit()

    except Exception as e:
        print(e)
        return jsonify({
            "code": 500,
            "message": "Error deleting user in database."
        }),500

    return jsonify({
        "code": 201,
        "message": "User deleted successfully."
    }), 201


# ---- Create, Read and Delete Mappings ----
@app.route('/add_user_course', methods=['POST'])
def add_user_course():
    # Filter for non json requests
    if request.is_json:
        try:
            # Handle request
            request_obj = request.get_json()
            print("User Skill received in: ", type(request_obj), request_obj)

            user_id = request_obj['user_id']
            course_id = request_obj['course_id'] # List

            user_saved= User.query.filter_by(id=user_id).first()
            for course in course_id:
                course_select= Course.query.filter_by(id=course).first()
                if course_select not in user_saved.mapped_courses:
                    user_saved.mapped_courses.append(course_select)

            try:
                db.session.commit()

            except Exception as e:
                print(e)
                return jsonify({
                    "code": 500,
                    "message": "User courses not saved successfully."
                }),401

            return jsonify({
                "code": 201,
                "message": "User saved successfully."
            }), 201

        except Exception as e:
            print(e)
            return jsonify({
                "code": 500,
                "message": "Error saving user to database."
            }), 500

    else:
        return jsonify({
            "code": 403,
            "message": "Invalid input"
        }), 403


@app.route('/get_user_courses/<int:user_id>', methods=['GET'])
def get_user_course(user_id):
    try:
        print(user_id)
        user_saved = User.query.filter_by(id=user_id).first()
        user_courses = user_saved.mapped_courses
        print(user_courses)
        courses_found_list = []
        for course in user_courses:
            mapping = course.to_dict()
            del mapping['mapped_skills']
            courses_found_list.append(mapping)
        print(courses_found_list)
        return jsonify(
            {"code":200,
             "content": courses_found_list
             }),200

    except Exception as e:
        print(e)
        return jsonify(
            {
            "code": 404,
            "message": "User not found"
             }), 404


@app.route('/get_user_skills/<int:user_id>', methods=['GET'])
def get_user_skills(user_id):
    try:
        user_saved = User.query.filter_by(id=user_id).first()
        user_courses = user_saved.mapped_courses
        user_skills = []
        for course in user_courses:
            mapped_skills = course.mapped_skills
            for skill in mapped_skills:
                if skill.to_dict() not in user_skills:
                    user_skills.append(skill.to_dict())

        print(user_skills)

        return jsonify(
            {
            "code":200,
            "content": user_skills
        }),200

    except Exception as e:
        print(e)
        return jsonify(
            {
            "code": 404,
            "message": "User not found"
             }), 404


@app.route('/delete_user_course', methods=["POST"])
def delete_user_course():
    if request.is_json:
        try:
            # Handle request
            request_obj = request.get_json()
            print("User Course received in: ", type(request_obj), request_obj)
            user_id = request_obj['user_id']
            course_id = request_obj['course_id'] # List

            # Query for Specific user
            with app.app_context():
                user_saved= User.query.filter_by(id=user_id).first()
                print(user_saved)
                user_courses = user_saved.mapped_courses
                print(user_courses)
                for course in user_courses:
                    if course.id in course_id:
                        user_saved.mapped_courses.remove(course)
                        print(f'{course.name} removed from Course Bank of {user_saved.full_name}')

                try:
                    db.session.commit()

                except Exception as e:
                    print(e)
                    return jsonify({
                        "code": 500,
                        "message": "Error deleting user course."
                    }),401

            return jsonify({
                "code": 201,
                "message": "User deleted successfully."
            }), 201

        except Exception as e:
            print(e)
            return jsonify({
                "code": 500,
                "message": "Error saving user to database."
            }), 500

    else:
        return jsonify({
            "code": 403,
            "message": "Invalid input"
        }), 403


@app.route('/add_fav_role', methods=['POST'])
def add_fav_role():
    # Filter for non json requests
    if request.is_json:
        try:
            # Handle request
            request_obj = request.get_json()
            print("User Skill received in: ", type(request_obj), request_obj)

            user_id = request_obj['user_id']
            role_id = request_obj['role_id'] # List

            user_saved= User.query.filter_by(id=user_id).first()
            print(user_saved)
            for role in role_id:
                role_select= Role.query.filter_by(id=role).first()
                if role_select not in user_saved.fav_roles:
                    user_saved.fav_roles.append(role_select)

            try:
                db.session.commit()

            except Exception as e:
                print(e)
                return jsonify({
                    "code": 500,
                    "message": "Fav roles not saved successfully."
                }),401

            return jsonify({
                "code": 201,
                "message": "Fav roles saved successfully."
            }), 201

        except Exception as e:
            print(e)
            return jsonify({
                "code": 500,
                "message": "Error saving user to database."
            }), 500

    else:
        return jsonify({
            "code": 403,
            "message": "Invalid input"
        }), 403


@app.route('/get_fav_roles/<int:user_id>', methods=['GET'])
def get_fav_roles(user_id):
    try:
        user_saved = User.query.filter_by(id=user_id).first()
        fav_roles = user_saved.fav_roles
        user_fav = []
        for roles in fav_roles:
            mapped_roles = roles.to_dict()
            del mapped_roles['mapped_skills']
            del mapped_roles['mapped_keyw']
            del mapped_roles['salary']
            user_fav.append(mapped_roles)

        return jsonify(
            {
            "code":200,
            "content": user_fav
        }),200

    except Exception as e:
        print(e)
        return jsonify(
            {
            "code": 404,
            "message": "Favourite roles not found"
             }), 404


@app.route('/delete_fav_role', methods=["POST"])
def delete_fav_role():
    if request.is_json:
        try:
            # Handle request
            request_obj = request.get_json()
            print("User Course received in: ", type(request_obj), request_obj)
            user_id = request_obj['user_id']
            role_id = request_obj['role_id'] # List

            # Query for Specific user
            with app.app_context():
                user_saved= User.query.filter_by(id=user_id).first()
                print(user_saved)
                fav_roles = user_saved.fav_roles
                print(fav_roles)
                for role in fav_roles:
                    if role.id in role_id:
                        user_saved.fav_roles.remove(role)
                        print(f'{role.name} removed from fav list of {user_saved.full_name}')

                try:
                    db.session.commit()

                except Exception as e:
                    print(e)
                    return jsonify({
                        "code": 500,
                        "message": "Error deleting user fav role."
                    }),401

            return jsonify({
                "code": 201,
                "message": "Fav role deleted successfully."
            }), 201

        except Exception as e:
            print(e)
            return jsonify({
                "code": 500,
                "message": "Error saving user changes to database."
            }), 500

    else:
        return jsonify({
            "code": 403,
            "message": "Invalid input"
        }), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)
