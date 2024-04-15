<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import {backend_url} from "../addresses"
import axios from 'axios'; // Import Axios library

const route = useRoute();
const id = route.query.course_id;
const current_name = ref('')
const new_name = ref('')
const current_skills = ref([])
const skill_list = ref([])
const selected_skills = ref([])
const isSuccessActive = ref(false)
const popupMessage = ref([]);
var message = ref("");

onMounted(async () => {
	try{
		// get course name
		var res = await fetch(`${backend_url}/course/get_one/${id}`)
		var data = await res.json()
		current_name.value = data.content.name
		new_name.value = data.content.name

		// get course skills
		var res_2 = await fetch(`${backend_url}/course/skills_mapped/get/${id}`)
		var data_2 = await res_2.json()
		current_skills.value = data_2.content
		selected_skills.value = data_2.content.sort((a, b) => a.id < b.id ? -1 : 1)

		// get all skills
		var res3 = await fetch(`${backend_url}/skill/get_all`)
		var data3 = await res3.json()
		skill_list.value = data3.content
	} catch (err) {
		console.error(err)
	}
})

function getNewSkills() {
	var newSkills = []
	for (var i = 0; i < selected_skills.value.length; i++) {
		var selected_id = selected_skills.value[i].id
		if (current_skills.value.filter((skill) => skill.id == selected_id).length == 0) {
			newSkills.push(selected_skills.value[i].id)
		}
	}

	if (newSkills.length > 0) {
		return { course_id: id,
						skill_id: newSkills }
	} return null
}

function getDeleteSkills() {
	var deleteSkills = []

	for (var i = 0; i < current_skills.value.length; i++) {
		var current_skill_id = current_skills.value[i].id
		if (selected_skills.value.filter((skill) => skill.id == current_skill_id).length == 0) {
			deleteSkills.push(current_skills.value[i].id)
		}
	}

	if (deleteSkills.length > 0) {
		return { course_id: id,
						skill_id: deleteSkills }
	} return null
}

function checkNameChanged() {
	if (current_name.value == new_name.value) {
		return null
	}
	return { course_id: id,
					course_name: new_name.value}
}

async function updateCourse() {
	if (checkNameChanged() == null && getNewSkills() == null && getDeleteSkills() == null) {
		popupMessage.value.push('No changes made')
	}

	if (checkNameChanged()) {
		let updateCourseData = checkNameChanged()

		try {
			let response = await axios.post(`${backend_url}/course/update`, updateCourseData)
			popupMessage.value.push(response.data.message)
		} catch (error) {
			popupMessage.value.push(error);
		}
	}

	if (getNewSkills()) {
		let addCourseSkill = getNewSkills()

		try {
			let response = await axios.post(`${backend_url}/course/skills_mapped/create`, addCourseSkill)
			popupMessage.value.push(response.data.message)
		} catch (error) {
			popupMessage.value.push(error);
		}

	}

	if (getDeleteSkills()) {
		let deleteCourseSkill = getDeleteSkills()

		try {
			let response = await axios.post(`${backend_url}/course/skills_mapped/delete`, deleteCourseSkill)
			popupMessage.value.push(response.data.message)
		} catch (error) {
			popupMessage.value.push(error);
		}
	}

	current_skills.value = [...selected_skills.value]
	message.value = popupMessage.value.shift()
  isSuccessActive.value = true
}

async function closeDialog() {
	if (popupMessage.value.length >= 1) {
		isSuccessActive.value = true
		message.value = await popupMessage.value.shift();
	}
	else if (popupMessage.value.length == 0) {
		isSuccessActive.value = false
	}
}

</script>

<template>
    <v-container class="mt-5">
		<v-btn prepend-icon="mdi-arrow-left-circle" variant="plain" id="back-button" class="mb-5" onclick="history.back()">
			Back
		</v-btn>
		<v-card-title class="text-h5 font-weight-bold">Update Course</v-card-title>
		<v-divider></v-divider>
		<v-container class="mt-5">
            <v-card variant="tonal" min-width="500" min-height="150" rounded="lg">
                <v-card-text>
                    <!--insert form here of course ID, course name, Skill Name/ID attached to it, and button to add skills to the course-->
										<v-text-field label="Course Code" v-model=id disabled></v-text-field>
										<v-text-field label="Course Name" v-model=new_name></v-text-field>

										<v-row>
											<v-col cols="1"></v-col>
											<v-col class="font-weight-bold text-body-1">
												Skill ID
											</v-col>
											<v-col class="font-weight-bold text-body-1">
												Skill Name
											</v-col>
										</v-row>

										<v-row v-for="skill in selected_skills" :key="skill.id" >
											<v-col cols="1"></v-col>
											<v-col>{{ skill.id }}</v-col>
											<v-col>{{ skill.name }}</v-col>
										</v-row>

										<v-row>
											<v-col class="text-right">
												<v-dialog width="700">
													<template v-slot:activator="{ props }">
														<v-btn v-bind="props" variant="plain" v-ripple="false" id="add_skill">Add / Remove skill</v-btn>
													</template>

													<template v-slot:default="{ isActive }">
														<v-card height="186" id="dialog">

															<v-card-text class="d-flex justify-center mt-2">
																<v-select
																	v-model="selected_skills"
																	label="Skills"
																	:items="skill_list"
																	:item-value="skill => ({'id': skill.id, 'name': skill.name})"
																	item-title="name"
																	variant="underlined"
																	multiple chips>
																</v-select>
															</v-card-text>

															<v-card-actions>
																<v-spacer></v-spacer>
																<v-btn
																text="Close"
																@click="isActive.value = false"
																></v-btn>
															</v-card-actions>
														</v-card>
													</template>
												</v-dialog>
											</v-col>
										</v-row>
                </v-card-text>
								
                <v-card-actions>
									<v-col class="text-right">
											<v-btn @click="updateCourse()" id="update" variant="plain" v-ripple="false">
												Update
											</v-btn>
											<v-dialog v-model="isSuccessActive" width="450">
												<v-card  height="160" id="dialog">
													<v-card-title class="d-flex justify-center mt-7 font-weight-bold">
														{{ message }}
													</v-card-title>
													<v-card-text class="d-flex justify-center">
														<v-btn
														@click="closeDialog()"
														class="d-flex justify-center dialogConfirmBtn dialogBtn elevation-4">Close</v-btn>
													</v-card-text>
												</v-card>
											</v-dialog>
									</v-col>
                </v-card-actions>
            </v-card>
        </v-container>
    </v-container>
</template>

<style scoped>
	#back-button {
        background: #151C55;
        color: #f4f4f4;
    }

	#add_skill{
			background-color: #84704C;
			color: white;
	}

    #update{
        color: white;
        background-color: #151C55;
        border-radius:5px;
			width: 140px;
    }

	#dialog {
		border-radius: 10px;
	}

	.dialogBtn{
		border-radius:5px;
		width: 160px;
	}

	.dialogConfirmBtn{
		background-color: #3FB67C;
		color: #FFFFFF;
	}

</style>
