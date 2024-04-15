<script setup>
import { onMounted, ref } from "vue";
import axios from 'axios'; // Import Axios library
import { backend_url } from "../addresses";
import {useRouter} from "vue-router"

var course_id = ref('')
var course_name = ref('')
const router = useRouter()
const skill_list = ref([])
const selected_skills = ref([])
const isSuccessActive = ref(false)
const popupMessage = ref([]);
var message = ref("");

async function addSkills(addCourseSkill) {
	try {
		let response = await axios.post(`${backend_url}/course/skills_mapped/create`, addCourseSkill)
		popupMessage.value.push(response.data.message)
		console.log(response.data.message)
		console.log(1)

	} catch (error) {
			popupMessage.value.push(error);
	}
}

async function addCourse() {
	if (course_id.value == '' || course_name.value == '') {
		message.value = 'Course code and/or course name cannot be empty'
		isSuccessActive.value = true
		return
	}

	const addCourseData = {
		course_id: course_id.value,
    course_name: course_name.value
	}

	const addCourseSkill = {
		course_id: course_id.value,
		skill_id: selected_skills.value
	}

	try {
		let response = await axios.post(`${backend_url}/course/create` ,addCourseData)
			console.log(2)
			console.log(response)
			popupMessage.value.push(response.data.message)
			addSkills(addCourseSkill)
	} catch (error) {
			console.log(3)
			console.log(error.data.message)

			popupMessage.value.push(error);
	}

	message.value = popupMessage.value.shift()
  isSuccessActive.value = true
}

async function closeDialog() {
	if (popupMessage.value.length >= 1) {
		isSuccessActive.value = true
		message.value = await popupMessage.value.shift();
	}
	else if (popupMessage.value.length == 0 & message.value != 'Course code and/or course name cannot be empty') {
		isSuccessActive.value = false
		router.push("/admin-all-courses")
	} else {
		isSuccessActive.value = false
	}
}

onMounted(async () => {
	try {
		var res = await fetch(`${backend_url}/skill/get_all`)
		var data = await res.json()
		skill_list.value = data.content
	} catch (err) {
		console.error(err)
	}
})

</script>

<template>
	<v-container class="mt-5">
		<v-btn prepend-icon="mdi-arrow-left-circle" variant="plain" id="back-button" class="mb-5" onclick="history.back()">
			Back
		</v-btn>
		<v-card-title class="text-h5 font-weight-bold">Add Course</v-card-title>
		<v-divider></v-divider>
		<v-container class="mt-5">
			<v-card class="px-4 py-3">
				<v-text-field
					v-model="course_id"
					label="Course Course">
				</v-text-field>

				<v-text-field
					v-model="course_name"
					label="Course Name">
				</v-text-field>

				<v-select
					v-model="selected_skills"
					label="Skills"
					:items="skill_list"
					item-value="id"
					item-title="name"
					variant="outlined"
					multiple chips clearable>
				</v-select>

				<v-card-actions>
					<v-col class="text-right">
						<v-btn @click="addCourse()" id="add_course" variant="plain" v-ripple="false">
							Add Course
						</v-btn>
						<v-dialog v-model="isSuccessActive" width="450">
							<v-card height="170" id="dialog">
								<v-card-title class="text-wrap text-center d-flex justify-center mt-7 font-weight-bold">
									{{ message }}
								</v-card-title>
								<v-card-text class="d-flex justify-center">
									<v-btn
									@click="closeDialog()"
									class="d-flex justify-center dialogConfirmBtn dialogBtn elevation-4 mt-2">Close</v-btn>
								</v-card-text>
							</v-card>
						</v-dialog>
					</v-col>
				</v-card-actions>

			</v-card>
		</v-container>
	</v-container>
</template>

<style>
	#add_course{
		background-color: #151C55;
		color: white;
	}

	#back-button {
			background: #151C55;
			color: #f4f4f4;
	}

	#dialog {
		border-radius: 10px;
	}

	.dialogBtn{
		border-radius:5px;
		width: 160px;
	}

	.dialogConfirmBtn{
		color: grey;
		border-color: grey;
		border-width: 2px;
	}

</style>
