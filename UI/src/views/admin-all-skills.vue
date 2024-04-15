<script setup>
import {ref, computed, onMounted} from "vue"
import {backend_url} from "../addresses"

const skillList = ref([]) // [{id, name}]
const filteredSkills = computed(() => skillList.value.filter((c) => c.name.toLowerCase().includes(search.value.toLowerCase())))
const search = ref("")
const newSkillName = ref("") // for add skill / update skill
const buttonLoading = ref(false) // for all buttons because it's unlikely for someone to have all of them up at the same time, and we probably rather they don't do that

// for adding course and role mappings for the skills
const courseList = ref([]) // [{id, name}]
const roleList = ref([]) // [{id, name}]
const selectProps = ({id, name}) => ({title: id, subtitle: name})
const courseListForAdding = (skill_id) => courseList.value.filter((course) => !skillCourseMappings.value[skill_id].some((mapping) => mapping.id === course.id))
const roleListForAdding = (skill_id) => roleList.value.filter((role) => !skillRoleMappings.value[skill_id].some((mapping) => mapping.id === role.id))

// using an object to make it easier to query when displaying on the UI
const skillCourseMappings = ref({}) // {id: [{id, name}]} --> skill_id --> course_id, course_name
const skillRoleMappings = ref({}) // {id: [{id, name}]} --> skill_id --> role_id, role_name

// arrays for adding mappings. Need name to add more easily on the frontend and reduce HTTP querying
const courses_toAdd = ref([]) // [{id, name}]
const roles_toAdd = ref([]) // [{id, name}]

// Idea: have deleted items in a select thing on the UI, and then when the "delete" button is pressed, we send the items to be all deleted at once (reducing HTTP query)
const courses_toDelete = ref([]) // [id]
const roles_toDelete = ref([]) // [id]


// retrieve on page mounting (loading)
onMounted(async () => {
	try {
		// retrieval of the skills
		const res_skill = await fetch(`${backend_url}/skill/get_all`)
		const data_skill = await res_skill.json()
		if (res_skill.status !== 200) throw new Error(data_skill.message)
		skillList.value = data_skill.content

		// retrieval of the courses for mappings
		const res_course = await fetch(`${backend_url}/course/get_all`)
		const data_course = await res_course.json()
		if (res_course.status !== 200) throw new Error(data_course.message)
		courseList.value = data_course.content

		// retieval of the roles for mappings
		const res_role = await fetch(`${backend_url}/role/get_all`)
		const data_role = await res_role.json()
		if (res_role.status !== 200) throw new Error(data_role.message)
		roleList.value = data_role.content

		// retrieving the skill-related mappings
		for (let skill of skillList.value) {
			// skill-course mappings
			const res_skillcourse = await fetch(`${backend_url}/skill/course_mapped/get/${skill.id}`)
			const data_skillcourse = await res_skillcourse.json()
			if (res_skillcourse.status === 200) skillCourseMappings.value[skill.id] = data_skillcourse.content
			else skillCourseMappings.value[skill.id] = [] // if there are no mappings found, set to an empty array

			// skill-role mappings
			const res_skillrole = await fetch(`${backend_url}/skill/roles_mapped/get/${skill.id}`)
			const data_skillrole = await res_skillrole.json()
			if (res_skillcourse.status === 200) skillRoleMappings.value[skill.id] = data_skillrole.content
			else skillRoleMappings.value[skill.id] = [] // if there are no mappings found, set to an empty array
		}
	} catch (err) {
		console.error(err)
	}
})

async function addSkill() {
	buttonLoading.value = true
	try {
		// adding the new skill thing
		const res_skill = await fetch(`${backend_url}/skill/create`, {
			method: "POST",
			mode: "cors",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({skill_name: newSkillName.value}), // auto-incremented ID in the DB
		})
		const data_skill = await res_skill.json()
		if (res_skill.status !== 201) throw new Error(data_skill.message)
		skillList.value.push({id: data_skill.skill_id, name: newSkillName.value}) // use returned skill_id & newSkillName, add to frontend

		// creating the new skill's skill-course mappings
		const res_course = await fetch(`${backend_url}/skill/course_mapped/create`, {
			method: "POST",
			mode: "cors",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({skill_id: data_skill.skill_id, course_id: courses_toAdd.value.map((c) => c.id)}),
		})
		const data_course = await res_course.json()
		if (res_course.status !== 201) throw new Error(data_course.message)
		skillCourseMappings.value[data_skill.skill_id] = courses_toAdd.value // setting courses_toAdd as the array for the new skill

		// creating the new skill's skill-role mappings
		const res_role = await fetch(`${backend_url}/skill/roles_mapped/create`, {
			method: "POST",
			mode: "cors",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({skill_id: data_skill.skill_id, role_id: roles_toAdd.value.map((r) => r.id)}),
		})
		const data_role = await res_role.json()
		if (res_role.status !== 201) throw new Error(data_role.message)
		skillRoleMappings.value[data_skill.skill_id] = roles_toAdd.value // setting roles_toAdd as the array for the new skill
	} catch (err) {
		console.error(err)
	}

	buttonLoading.value = false
	newSkillName.value = ""
	courses_toAdd.value = []
	roles_toAdd.value = []
	return
}

async function updateSkill(id) {
	buttonLoading.value = true
	try {
		// updating the skill name
		const res_skill = await fetch(`${backend_url}/skill/update`, {
			method: "POST",
			mode: "cors",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({skill_id:id, skill_name: newSkillName.value}),
		})
		const data_skill = await res_skill.json()
		if (res_skill.status !== 201) throw new Error(data_skill.message)
		const idx = skillList.value.findIndex((e) => e.id === id)
		skillList.value[idx] = {id, name: newSkillName.value}


		// adding skill-course mappings
		const res_course_add = await fetch(`${backend_url}/skill/course_mapped/create`, {
			method: "POST",
			mode: "cors",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({skill_id: id, course_id: courses_toAdd.value.map((c) => c.id)}),
		})
		const data_course_add = await res_course_add.json()
		if (res_course_add.status !== 201) throw new Error(data_course_add.message)
		skillCourseMappings.value[id] = [...skillCourseMappings.value[id], ...courses_toAdd.value] // updating the array

		// deleting skill-course mappings
		const res_course_delete = await fetch(`${backend_url}/skill/course_mapped/delete`, {
			method: "POST",
			mode: "cors",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({skill_id: id, course_id: courses_toDelete.value}),
		})
		const data_course_delete = await res_course_delete.json()
		if (res_course_delete.status !== 201) throw new Error(data_course_delete.message)
		const idx_course = skillCourseMappings.value[id].findIndex((e) => e.id === id) // find on frontend
		skillCourseMappings.value[id].splice(idx_course, 1) // remove the 1 item at index "idx" on the frontend


		// adding skill-role mappings
		const res_role_add = await fetch(`${backend_url}/skill/roles_mapped/create`, {
			method: "POST",
			mode: "cors",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({skill_id: id, role_id: roles_toAdd.value.map((r) => r.id)}),
		})
		const data_role_add = await res_role_add.json()
		if (res_role_add.status !== 201) throw new Error(data_role_add.message)
		skillRoleMappings.value[id] = [...skillRoleMappings.value[id], ...roles_toAdd.value] // updating the array

		// deleting skill-role mappings
		const res_role_delete = await fetch(`${backend_url}/skill/roles_mapped/delete`, {
			method: "POST",
			mode: "cors",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({skill_id: id, role_id: roles_toDelete.value}),
		})
		const data_role_delete = await res_role_delete.json()
		if (res_role_delete.status !== 201) throw new Error(data_role_delete.message)
		const idx_role = skillRoleMappings.value[id].findIndex((e) => e.id === id) // find on frontend
		skillRoleMappings.value[id].splice(idx_role, 1) // remove the 1 item at index "idx" on the frontend
	} catch (err) {
		console.error(err)
	}

	buttonLoading.value = false
	newSkillName.value = ""
	courses_toAdd.value = []
	roles_toAdd.value = []
	return
}

async function deleteSkill(id) {
	buttonLoading.value = true
	try {
		const res = await fetch(`${backend_url}/skill/delete/${id}`, {method: "DELETE", mode: "cors"})
		const data = await res.json()
		if (res.status !== 201) throw new Error(data.message)
		const idx = skillList.value.findIndex((e) => e.id === id) // find on frontend
		skillList.value.splice(idx, 1) // remove the 1 item at index "idx" on the frontend
	} catch (err) {
		console.error(err)
	}

	buttonLoading.value = false
	return
}
</script>

<template>
	<v-container class="mt-5">
		<v-card-title class="text-h5 font-weight-bold">All Skills</v-card-title>
		<v-divider></v-divider>
		<v-container class="mt-5">
			<v-row>
				<v-col cols class="ms-11 me-5">
					<v-text-field
						v-model="search"
						label="Search skill by name"
						outlined clearable
					></v-text-field>
				</v-col>
				<v-col cols="3" class="mt-2 d-flex justify-center">

					<!-- Add Skill Button & Modal -->
					<v-dialog max-width="900" min-width="450" min-height="300">
						<template v-slot:activator="{props}">
							<v-btn v-bind="props" @click="newSkillName = ''" class="elevation-0" id="new_skills">+ Add New Skill</v-btn>
						</template>
						<template v-slot:default="{isActive}">
							<v-card id="dialog">
								<v-card-title class="font-weight-bold ms-4 mt-3">Add new skill</v-card-title>
								<v-card-text>
									<v-text-field
										v-model="newSkillName"
										label="New skill name"
										outlined clearable
										class="mt-1"
									></v-text-field>
									<!-- New skill course mappings (add) -->
									<v-autocomplete
										clearable	multiple chips
										:items="courseList" :item-props="selectProps"
										v-model="courses_toAdd" label="Related courses" variant="underlined"
										class="mt-1"
									></v-autocomplete>
									<!-- New skill role mappings (add) -->
									<v-autocomplete
										clearable	multiple chips
										:items="roleList" :item-props="selectProps"
										v-model="roles_toAdd" label="Related roles" variant="underlined"
										class="mt-1"
									></v-autocomplete>
								</v-card-text>
								<v-card-actions class="d-flex justify-center">
									<v-btn
										@click="isActive.value = false"
										class="d-flex justify-center me-7 dialogCancelBtn dialogBtn elevation-0"
									>Cancel</v-btn>
									<v-btn
										:loading="buttonLoading"
										@click="async () => {
											await addSkill()
											isActive.value = false
										}"
										class="d-flex justify-center dialogDeleteBtn dialogBtn elevation-4"
									>Add</v-btn>
								</v-card-actions>
							</v-card>
						</template>
					</v-dialog>
				</v-col>
			</v-row>
		</v-container>

		<v-list class="bg-transparent">
			<v-list-item v-for="skill in filteredSkills" :key="skill.id">
				<v-card class="skillCardClass ms-4">
					<v-row>
						<v-col cols="12" sm="9">
							<v-card-title>{{ skill.name }}</v-card-title>
							<v-card-actions class="mt-1">
								<!-- View Skill Modal & Button -->
								<v-dialog max-width="900" min-width="450" min-height="300">
									<template v-slot:activator="{props}">
										<v-btn v-bind="props" class="viewBtn">View Skill</v-btn>
									</template>
									<template v-slot:default="{isActive}">
										<v-card id="dialog">
											<v-card-title class="font-weight-bold ms-4 mt-3">{{ skill.name }}</v-card-title>
											<v-card-text>
												<v-row>
													<v-col>
														<v-list density="compact">
															<v-list-subheader>Courses</v-list-subheader>
															<v-list-item
																v-for="course in skillCourseMappings[skill.id]"
																:key="course.id"
																:title="course.name"
																prepend-icon="mdi-human-male-board-poll"
															></v-list-item>
														</v-list>
													</v-col>
													<v-col>
														<v-list density="compact">
															<v-list-subheader>Roles</v-list-subheader>
															<v-list-item
																v-for="role in skillRoleMappings[skill.id]"
																:key="role.id"
																:title="role.name"
																prepend-icon="mdi-badge-account-horizontal"
															></v-list-item>
														</v-list>
													</v-col>
												</v-row>
											</v-card-text>
											<v-card-actions class="d-flex justify-end">
												<v-btn
													@click="isActive.value = false"
													class="d-flex justify-center me-7 dialogCancelBtn dialogBtn elevation-0"
												>Close</v-btn>
											</v-card-actions>
										</v-card>
									</template>
								</v-dialog>

								<!-- Edit/Update Skill Modal & Button -->
								<v-dialog max-width="900" min-width="450" min-height="300">
									<template v-slot:activator="{props}">
										<!-- function to also move the new skill name in -->
										<v-btn v-bind="props" @click="newSkillName = skill.name" class="editBtn">Edit Skill</v-btn>
									</template>
									<template v-slot:default="{isActive}">
										<v-card id="dialog">
											<v-card-title class="font-weight-bold ms-4 mt-3">Edit skill: {{ skill.name }}</v-card-title>
											<v-card-text>
												<v-text-field
													v-model="newSkillName"
													label="Update skill name"
													outlined clearable
													class="mt-1"
												></v-text-field>
												<!-- Existing skill course mappings (add) -->
												<v-autocomplete
													clearable	multiple chips
													:items="courseListForAdding(skill.id)" :item-props="selectProps"
													v-model="courses_toAdd" label="Courses to add" variant="underlined"
													class="mt-1"
												></v-autocomplete>
												<!-- Existing skill course mappings (delete) -->
												<v-autocomplete
													clearable	multiple chips
													:items="skillCourseMappings[skill.id]" :item-props="selectProps"
													v-model="courses_toDelete" label="Courses to delete" variant="underlined"
													class="mt-1"
												></v-autocomplete>
												<!-- Existing skill role mappings (add) -->
												<v-autocomplete
													clearable	multiple chips
													:items="roleListForAdding(skill.id)" :item-props="selectProps"
													v-model="roles_toAdd" label="Roles to add" variant="underlined"
													class="mt-1"
												></v-autocomplete>
												<!-- Existing skill role mappings (delete) -->
												<v-autocomplete
													clearable	multiple chips
													:items="skillRoleMappings[skill.id]" :item-props="selectProps"
													v-model="roles_toDelete" label="Roles to delete" variant="underlined"
													class="mt-1"
												></v-autocomplete>
											</v-card-text>
											<v-card-actions class="d-flex justify-center">
												<v-btn
													@click="isActive.value = false"
													class="d-flex justify-center me-7 dialogCancelBtn dialogBtn elevation-0"
												>Cancel</v-btn>
												<v-btn
													:loading="buttonLoading"
													@click="async () => {
														await updateSkill(skill.id)
														isActive.value = false
													}"
													class="d-flex justify-center dialogDeleteBtn dialogBtn elevation-4"
												>Update</v-btn>
											</v-card-actions>
										</v-card>
									</template>
								</v-dialog>

								<!-- Delete Skill Modal & Button -->
								<v-dialog max-width="600" min-width="300" min-height="180">
									<template v-slot:activator="{props}">
										<v-btn v-bind="props" class="deleteBtn">Delete Skill</v-btn>
									</template>
									<template v-slot:default="{isActive}">
										<v-card id="dialog">
											<v-card-title class="d-flex justify-center mt-7 font-weight-bold">
												Confirm Deletion of {{ skill.name }}?
											</v-card-title>
											<v-card-actions class="d-flex justify-center">
												<v-btn
													@click="isActive.value = false"
													class="d-flex justify-center me-7 dialogCancelBtn dialogBtn elevation-0"
												>Cancel</v-btn>
												<v-btn
													:loading="buttonLoading"
													@click="async () => {
														await deleteSkill(skill.id)
														isActive.value = false
													}"
													class="d-flex justify-center dialogDeleteBtn dialogBtn elevation-4"
												>Delete</v-btn>
											</v-card-actions>
										</v-card>
									</template>
								</v-dialog>
							</v-card-actions>
						</v-col>
					</v-row>
				</v-card>
			</v-list-item>
		</v-list>
	</v-container>
</template>

<style scoped>
	#new_skills {
		background-color: #7F6B4A;
		color: #F9F9F9;
	}

	.salary{
		color: #7F6B4A;
	}

	.skillCardClass {
		background-color: RGB(234, 234, 234, 0.95);
		padding: 15px;
	}
	.viewBtn{
		background-color: RGB(136, 130, 115, 0.95);
		color: #FFFFFF;
		width: 130px;
	}

	.deleteBtn{
		background-color: RGB(195, 31, 31, 0.8);
		color: #FFFFFF;
		border-radius:5px;
		width: 130px;
	}

	.editBtn{
		background-color: RGB(21, 28, 85, 0.95);
		color: #FFFFFF;
		border-radius:17px;
		width: 130px;
	}

	#dialog {
		border-radius: 10px;
		padding: 15px;
	}

	.dialogBtn{
		border-radius:5px;
		width: 160px;
	}

	.dialogDeleteBtn{
		background-color: RGB(195, 31, 31);
		color: #FFFFFF;
	}

	.dialogCancelBtn{
		color: grey;
		border-color: grey;
		border-width: 2px;
	}
</style>

<!-- Need this here for the Router to detect that this is an Admin Only file -->
<route lang="yaml">
meta:
  requiresAdmin: true
</route>
