// import.meta.env.MODE --> "development" on npm run dev; "production" on npm run build
const dev_url = "http://127.0.0.1:5277"
const prod_url = "https://qrrequri26.execute-api.us-west-2.amazonaws.com" // Changes daily until I input an elastic IP
export const backend_url = import.meta.env.MODE === "development" ? dev_url : prod_url

// export const course_ms_address = import.meta.env.MODE === "development" ? "http://127.0.0.1:5000/": prod_url;
/*
COURSE ENDPOINTS
/course/create
/course/get_one/<string:course_id>
/course/get_all
/course/update
/course/delete
/course/skills_mapped/create
/course/skills_mapped/get/<string:course_id>
/course/skills_mapped/delete
*/
// export const keyw_ms_address = import.meta.env.MODE === "development" ? "http://127.0.0.1:5002/": prod_url;
/*
KEYWORDS ENDPOINTS
/keyword/create
/keyword/get_one/<int:keyword_id>
/keyword/get_all
/keyword/update
/keyword/delete/<int:keyword_id>
/keyword/roles_mapped/get/<int:keyw_id>
*/

// export const role_ms_address = import.meta.env.MODE === "development" ? "http://127.0.0.1:5004/" : prod_url;
/*
ROLES ENDPOINTS
/role/create
/role/get_one/<int:role_id>
/role/get_all
/role/update
/role/delete/<int:role_id>
/role/skills_mapped/create
/role/keyws_mapped/create
/role/skills_mapped/get/<int:role_id>
/role/keyws_mapped/get/<int:role_id>
/role/specs_mapped/get/<int:role_id>
/role/skills_mapped/delete
/role/keyws_mapped/delete
/role/salary_mapped/get/<int:role_id>
/role/get_user_mapped/<int:role_id>
/role/popular/get_top_3
/role/see_information
*/

/*
SALARY ENDPOINTS
/salary/create
/salary/get_all
/salary/delete/<int:salary_id>
*/

// export const skill_ms_address = import.meta.env.MODE === "development" ? "http://127.0.0.1:5006/" : prod_url;
/*
SKILL ENDPOINTS
/skill/get_all
/skill/create
/skill/get_one/<int:skill_id>
/skill/update
/skill/delete/<int:skill_id>
/skill/course_mapped/get/<int:skill_id>
/skill/roles_mapped/get/<int:skill_id>
*/

// export const spec_ms_address = import.meta.env.MODE === "development" ? "http://127.0.0.1:5007/" : prod_url;
/*
SPEC ENDPOINTS
/spec/create
/spec/get_one/<int:spec_id>
/spec/get_all
/spec/update
/spec/delete/<spec_id>
/spec/roles_mapped/create
/spec/role_mapped/salary_range/get/<int:spec_id>/<int:salary>
/spec/roles_mapped/delete
*/

// export const user_ms_address = import.meta.env.MODE === "development" ? "http://127.0.0.1:5010/" : prod_url;
// export const upload_ms_address = import.meta.env.MODE === "development" ? "http://127.0.0.1:5013/" : prod_url;
// export const view_account_address = import.meta.env.MODE === "development" ? "http://127.0.0.1:5012/" : prod_url;
// export const process_transcript_address = import.meta.env.MODE === "development" ? "http://127.0.0.1:5011/": prod_url
/*
USER ENDPOINTS
/user/auth
/user/process_transcript
/user/create
/user/update_particulars
/user/update_password
/user/get/<int:user_id>
/user/get_all
/user/delete/<int:user_id>
/user/add_user_course
/user/get_user_courses/<int:user_id>
/user/get_user_skills/<int:user_id>
/user/delete_user_course
/user/add_fav_role
/user/get_fav_roles/<int:user_id>
/user/delete_fav_role
/user/view_account_information
/user/get_filtered_courses
*/








