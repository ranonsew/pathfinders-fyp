import requests
import csv

course_skill_dict = {}
role_skill_dict = {}
spec_role_dict = {}
role_keyw_dict = {}

course_skill_url = "http://127.0.0.1:5277/course/skills_mapped/create"
role_skill_url = "http://127.0.0.1:5277/role/skills_mapped/create"
role_keyw_url = "http://127.0.0.1:5277/role/keyws_mapped/create"
spec_role_url = "http://127.0.0.1:5277/spec/roles_mapped/create"

#--- Define Test data ---
with open("./sample_data/Course-skills.csv", "r") as file:
    csvreader = csv.reader(file)
    next(csvreader, None)
    for row in csvreader:
        course_id = row[0]
        skill_id = row[1]
        if course_id not in course_skill_dict:
            course_skill_dict[course_id] = [skill_id]
        else:
            course_skill_dict[course_id].append(skill_id)

print('course_skill_dict Created')
            
with open("./sample_data/Role-skills.csv", "r") as file:
    csvreader = csv.reader(file)
    next(csvreader, None)
    for row in csvreader:
        role_id = row[0]
        skill_id = row[1]
        if role_id not in role_skill_dict:
            role_skill_dict[role_id] = [skill_id]
        else:
            role_skill_dict[role_id].append(skill_id)
    
print('role_skill_dict Created')

with open("./sample_data/Role-keyw.csv", "r") as file:
    csvreader = csv.reader(file)
    next(csvreader, None)
    for row in csvreader:
        role_id = row[0]
        keyw_id = row[1]
        if role_id not in role_keyw_dict:
            role_keyw_dict[role_id] = [keyw_id]
        else:
            role_keyw_dict[role_id].append(keyw_id)
    
print('role_keyw_dict Created')

with open("./sample_data/Spec-Role.csv", "r") as file:
    csvreader = csv.reader(file)
    next(csvreader, None)
    for row in csvreader:
        spec_id = row[0]
        role_id = row[1]
        if spec_id not in spec_role_dict:
            spec_role_dict[spec_id] = [role_id]
        else:
            spec_role_dict[spec_id].append(role_id)
    
print('Spec_role_dict Created')

#--- Make requests to modules ---

for course in course_skill_dict.keys():
    course_code = course
    mapped_skills = course_skill_dict[course]
    course_obj = {
        'course_id' : course_code,
        'skill_id' : mapped_skills
    }
    x = requests.post(course_skill_url, json = course_obj)
    
    print(x.text)

print('Course_skill_mappings loaded')

for role in role_skill_dict.keys():
    role_id = role
    mapped_skills = role_skill_dict[role]
    course_obj = {
        'role_id' : role_id,
        'skill_id' : mapped_skills
    }
    x = requests.post(role_skill_url, json = course_obj)
    
    print(x.text)

print('Role_skill_mappings loaded')

for spec in spec_role_dict.keys():
    spec_id = spec
    mapped_roles = spec_role_dict[spec]
    course_obj = {
        'spec_id' : spec_id,
        'role_id' : mapped_roles
    }
    x = requests.post(spec_role_url, json = course_obj)
    
    print(x.text)

print('Spec_role_mappings loaded')


for role in role_keyw_dict.keys():
    role_id = role
    mapped_keyw = role_keyw_dict[role]
    course_obj = {
        'role_id' : role_id,
        'keyw_id' : mapped_keyw
    }
    x = requests.post(role_keyw_url, json = course_obj)
    
    print(x.text)

print('Role_keyw_mappings loaded')