<script setup>
import { onMounted, ref, watch } from "vue";
import axios, { all } from 'axios'; // Import Axios library
import { backend_url } from "../addresses";
import {useUserStore} from "../stores/user"
import {useRouter} from "vue-router"
import VueApexCharts from "vue3-apexcharts";

const store = useUserStore()
const router = useRouter()

const userId = store.userId;
const tab = ref(null);
const savedRoles = ref({});
const closeToCompletion = ref({});
const allSkillsCourses = ref({});
const top6skills = ref({})
const message = ref(null)
const isSuccessActive = ref(false)
const courseList = ref({})
const skillDict = ref({})
const courseDict = ref({})
const courseSkill = ref({})

onMounted(async () => {
	try {
		const getAllProgression = {
			method: 'POST',
			headers: {
        'Content-Type': 'application/json',
      },
			body: JSON.stringify({ "student_id": userId })
		}

		var progressionRes = await fetch(`${backend_url}/user/get_all_roles_progression`, getAllProgression)
		var progressionData = await progressionRes.json()
		// get roles that equal to or above 80% and sort by progression
		closeToCompletion.value = progressionData.data.all_roles_result
															.filter(({user_progression_level}) =>
															Number(user_progression_level) >= 80)
															.sort((a, b) => {
																const levelA = Number(a.user_progression_level);
																const levelB = Number(b.user_progression_level);
																return levelB - levelA;
															});

		var savedRolesRes = await fetch(`${backend_url}/user/get_fav_roles/` + userId)
		var savedRolesData = await savedRolesRes.json()
		savedRoles.value = progressionData.data.all_roles_result
												.filter(({name}) =>
												savedRolesData.content.map(item => item.name).includes(name))

		var coursesRes = await fetch(`${backend_url}/user/get_user_courses/` + userId)
		var coursesData = await coursesRes.json()
		// var courses = coursesData.content
		courseList.value = coursesData.content
		// console.log(courses)
		let tempSkillsCourse = {}

		for (let course of courseList.value) {
			let courseRes = await fetch(`${backend_url}/course/skills_mapped/get/` + course.id)
			let courseData = await courseRes.json()
			let courseSkillMapping = courseData.content
			let temp = []

			for (let skill of courseSkillMapping) {
				// if skill in object, object[skill] += 1, else 1
				tempSkillsCourse[skill.name] = (tempSkillsCourse[skill.name] ?? 0 ) + 1
				temp.push(skill.name)
			}
			temp = temp.sort()
			courseSkill.value[course.name] = temp
		}

		const skillsValueArray = Object.entries(tempSkillsCourse)

		skillsValueArray.sort((a, b) => b[1] - a[1])
		allSkillsCourses.value = Object.fromEntries(skillsValueArray)

		const top6Object = skillsValueArray.slice(0, 6)
		top6skills.value = Object.fromEntries(top6Object)

		const courseSkillResponse = await fetch(`${backend_url}/competency/course_skill`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ "user_id": userId })
		});

		var tempCourseDict = await courseSkillResponse.json();
		courseDict.value = tempCourseDict.content;
		// Process the data from 'competency/course_skill' as needed

		// Fetch data from 'competency/skill_course'
		const skillCourseResponse = await fetch(`${backend_url}/competency/skill_course`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ "user_id": userId })
		});

		var tempSkillDict = await skillCourseResponse.json();
		skillDict.value = tempSkillDict.content;

	} catch (err) {
		console.error(err)
	}
})

const roleProgressionChart = {
	chart: {
		type: 'radialBar',
	},
	plotOptions: {
	radialBar: {
		startAngle: -90,
		endAngle: 90,
		hollow: {
			size: '80%',
		},
		track: {
			margin: 1
		},
		dataLabels: {
			name: {
				show: false
			},
			value: {
				offsetY: 0,
				fontSize: 20
		}}}},
	labels: [],
	colors:["#106B13"],
	stroke: { lineCap: "round" },
}

const skillChart = ref({
	chart: {
		height: 400,
		type: 'radar',
		toolbar: { show: false },
		offsetY: 100,
	},
	plotOptions: {
		radar: {
			size: 150,
		}
	},
	title: {
	},
	xaxis: {
		categories: [],
		labels: {
			style: {
				colors: [..."000000"],
				fontWeight: 900,
				fontSize: 12,
			},
			offsetY: 0,
			offsetX: 0,
		}
	},
	fill: {
		colors: '#EBAF14', // area colour
		opacity: 0.4 // area opacity
	},
	stroke: { // doesnt work??
    width: 10, // border stroke
    colors: [...'#e342f5'], // border colour
  },
	markers: {
    size: 2,
		colors: '000000',	// fill colour
		strokeColors: '000000', // outline colour
  },
})

// get the line breaks for the spider chart. if a skill exceeded 17 char, it will broken into a few lines where needed
function getLineBreakForSpiderChart(s, char_limit) {
	if (s.length <= char_limit) {
		return s }

	const words = s.split(' ')
  const result = []
  let currentPiece = ''

  for (const word of words) {
    if (currentPiece.length + word.length <= char_limit) {
      currentPiece += (currentPiece.length > 0 ? ' ' : '') + word
    } else {
      result.push(currentPiece)
      currentPiece = word
    }
  }

  if (currentPiece.length > 0) {
    result.push(currentPiece)
  }

  return result;
}

// update the categories after onMounted
watch(() => top6skills.value, (newTop6skills) => {
	skillChart.value.xaxis.categories = Object.keys(newTop6skills).map(label => getLineBreakForSpiderChart(label, 17));
  skillChart.value = {
    ...skillChart.value,
    xaxis: {
			...skillChart.value.xaxis,
      categories: skillChart.value.xaxis.categories,
    },
  }
});

const viewRole = (roleId) => {
	router.push({path: "/role-info/", query: {id: roleId}})
}

function deleteRole(roleId) {
	let role = {
		user_id: userId,
		role_id: roleId
	}

	axios.post(`${backend_url}/user/delete_fav_role`, role)
	.then(response => {
		message.value = response.data.message
		isSuccessActive.value = true
	})
	.catch(error => {
			console.error('Error fetching data:', error);
	})
}

function deleteCourse(courseId) {
	let course = {
		user_id: userId,
		course_id: courseId
	}

	axios.post(`${backend_url}/user/delete_user_course`, course)
	.then(response => {
		message.value = response.data.message
		isSuccessActive.value = true
	})
	.catch(error => {
			console.error('Error fetching data:', error);
	})
}

function closeDialog() {
	isSuccessActive.value = false
	location.reload()
}

</script>


<template>
    <div>
		<v-container class="mt-5">
        <v-card-title class="text-h5 font-weight-bold">
            My Competencies
        </v-card-title>
        <v-divider></v-divider>
        <v-container>
            <v-card variant="text" class="mt-5">
                <v-tabs v-model="tab" background-color="white" color="#84704C">
										<v-tab value="one">My Saved Roles</v-tab>
                    <v-tab value="two">Roles Close to Completion</v-tab>
										<v-tab value="three">Courses taken</v-tab>
										<v-tab value="four">Skills obtained by courses</v-tab>
                </v-tabs>

                <v-card-text>
                    <v-window v-model="tab">
                        <v-window-item value="one">
                            <!--populate with skills that are saved-->
                            <v-sheet class="mx-auto" elevation="8" max-width="2000">
                                <v-slide-group v-if="savedRoles.length > 0" v-model="savedRoles" class="pa-4" selected-class="bg-success" show-arrows>
                                    <v-slide-group-item v-for="role in savedRoles" :key="role">
                                        <v-card class="ma-2 elevation-4" height="200" width="220">
																					<v-card-text style="height:100px; max-height:100px;">
																						<apexchart :options="roleProgressionChart" :series="[role.user_progression_level.toFixed(0)]" height="175px"></apexchart>
																					</v-card-text>
																					<v-card-title class="text-center">
																						{{ role.name }}
																					</v-card-title>
																					<v-divider></v-divider>
																					<v-card-actions class="d-flex justify-center">
																						<v-btn @click="viewRole(role.id)" color="#84704C" class="roleBtn">
																							More Info
																						</v-btn>
																						<v-btn @click="deleteRole(role.id)" color="#C31F1F" class="roleBtn">
																							Remove
																						</v-btn>

																						<v-dialog v-model="isSuccessActive" width="450">
																							<v-card  height="160" id="dialog">
																								<v-card-title class="d-flex justify-center mt-7 font-weight-bold">
																									{{ message }}
																								</v-card-title>
																								<v-card-text class="d-flex justify-center">
																									<v-btn
																									@click="closeDialog()"
																									class="d-flex justify-center closeDialogBtn elevation-4">Close</v-btn>
																								</v-card-text>
																							</v-card>
																						</v-dialog>
																					</v-card-actions>
                                        </v-card>
                                    </v-slide-group-item>
                                </v-slide-group>
																<v-container v-else style="padding: 0px">
																	No favourite roles.
																</v-container>
                            </v-sheet>
                        </v-window-item>

                        <v-window-item value="two">
                            <!--populate with skills that are close to completion-->
                            <v-sheet class="mx-auto" elevation="8" max-width="2000">
                                <v-slide-group v-if="closeToCompletion.length > 0" v-model="closeToCompletion" class="pa-4" selected-class="bg-success" show-arrows>
                                    <v-slide-group-item v-for="role in closeToCompletion" :key="role">
                                        <v-card class="ma-2 elevation-4" height="200" width="220">
																					<v-card-text style="height:100px; max-height:100px;">
																						<apexchart :options="roleProgressionChart" :series="[role.user_progression_level.toFixed(0)]" height="175px"></apexchart>
																					</v-card-text>
																					<v-card-title class="text-center">
																						{{ role.name }}
																					</v-card-title>
																					<v-divider></v-divider>
																					<v-card-actions class="d-flex justify-center">
																						<v-btn @click="viewRole(role.id)" color="#84704C" width="200px">
																							More Info
																						</v-btn>
																					</v-card-actions>
                                        </v-card>
                                    </v-slide-group-item>
                                </v-slide-group>
																<v-container v-else style="padding: 0px">
																	No roles are close to completion.
																</v-container>
                            </v-sheet>
                        </v-window-item>

												<v-window-item value="three">
                            <v-sheet class="mx-auto" elevation="8" max-width="2000">
																<v-table v-if="courseList.length > 0">
																	<thead>
																		<tr>
																			<th class="font-weight-bold">Course Code</th>
																			<th class="font-weight-bold">Course Name</th>
																			<th></th>
																		</tr>
																	</thead>
																	<tbody>
																		<tr v-for="course in courseList" :key="course.id">
																			<td>{{ course.id }}</td>
																			<td>{{ course.name }}</td>
																			<td>
																				<v-btn variant="plain" icon="mdi-delete" color="#D94D36" v-ripple="false" @click="deleteCourse(course.id)"></v-btn>
																				<v-dialog v-model="isSuccessActive" width="450">
																					<v-card  height="160" id="dialog">
																						<v-card-title class="d-flex justify-center mt-7 font-weight-bold">
																							{{ message }}
																						</v-card-title>
																						<v-card-text class="d-flex justify-center">
																							<v-btn
																							@click="closeDialog()"
																							class="d-flex justify-center closeDialogBtn elevation-4">Close</v-btn>
																						</v-card-text>
																					</v-card>
																				</v-dialog>
																			</td>
																		</tr>
																		<tr>
																			<td colspan="3">
																				<v-btn
																					class="float-right"
																					text='Update Courses'
																					id='update_courses_btn'
																					href="/update-my-courses"
																				></v-btn>
																			</td>
																		</tr>
																	</tbody>
																</v-table>

																<v-container v-else style="padding: 0px; min-height: 500px">
																	No courses taken. Please upload your transcript here.
																	<v-btn
																		text='Update Courses'
																		id='update_courses_btn'
																		href="/update-my-courses"
																		style="position: absolute; right: 0; bottom: 0;"
																	></v-btn>
																</v-container>
                            </v-sheet>
                        </v-window-item>

												<v-window-item value="four">
                            <v-sheet class="mx-auto" elevation="8" max-width="2000">
															<v-table v-if="courseList.length > 0">
																<thead>
																	<tr>
																		<th class="font-weight-bold">Course Name</th>
																		<th class="font-weight-bold">Course Skills</th>
																	</tr>
																</thead>
																<tbody>
																	<tr v-for="course in Object.keys(courseSkill).sort()" :key="course" style="padding-bottom: 5px;">
																		<td colspan="{{ courseSkill[course].length }}">{{ course }}</td>
																		<td>
																			<div style="max-height: 65px; overflow: auto; list-style-position: inside;">
																				<ol>
																					<li v-for="skill in courseSkill[course]" :key="skill">{{ skill }}</li>
																				</ol>
																			</div>
																		</td>
																	</tr>

																</tbody>
															</v-table>

																<v-container v-else style="padding: 0px; min-height: 500px">
																	No skills obtained.
																</v-container>
                            </v-sheet>
                        </v-window-item>

                    </v-window>
                </v-card-text>
            </v-card>
        </v-container>
    </v-container>
    <v-divider>
    </v-divider>

		<v-container class="mb-10" v-if=" courseList.length > 0">
			<div class="text-h6 font-weight-bold ms-5 mt-5">Skills Obtained</div>
			<v-row>
				<v-col class="align-start">
				<apexchart
					:options="skillChart"
					:series="[{
					name: 'Count',
					data: Object.values(top6skills),
					}]">
				</apexchart>
				</v-col>
				<v-col>
					<v-container>
						<!-- First row for the header and description -->
						<v-row>
							<v-col>
							<span class="text-body-1 font-weight-bold ms-3">Top Skills with Familiarity Scores
								<v-icon size="x-small" class="pb-3">
									mdi-information-outline
								</v-icon>
								<v-tooltip activator="parent" location="top">
									The familiarity score is derived from the number of
								<br> courses completed that teach you the skills.
								</v-tooltip>
							</span>
							</v-col>
						</v-row>

						<!-- Second row for the expansion panels -->
						<v-row class="scrollable-table">
							<v-col>
							<v-expansion-panels multiple>
								<!-- Iterate through skills -->
								<v-expansion-panel v-for="skill in Object.keys(allSkillsCourses)" :key="skill">
								<v-expansion-panel-title>
									<!-- Skill name -->
									{{ skill }} &nbsp;<span v-pre>(</span>{{ allSkillsCourses[skill] }}<span v-pre> )</span>
								</v-expansion-panel-title>
								<v-expansion-panel-text class="scrollable-panel">
									<!-- Your code to populate related courses goes here -->
									<!-- Your content here -->
									<v-table>
									<tbody>
										<!-- Iterate through courses for the current skill -->
										<tr v-for="curDict in skillDict[skill]" :key="curDict.course_id">
										<td>{{ curDict["course_id"] }}</td>
										<td>{{ curDict["course_name"] }}</td>
										</tr>
									</tbody>
									</v-table>
								</v-expansion-panel-text>
								</v-expansion-panel>
							</v-expansion-panels>
							</v-col>
						</v-row>
						</v-container>
				</v-col>
			</v-row>
		</v-container>
	</div>
</template>

<style>
	.roleBtn{
		width: 100px;
	}

	.iconSmaller{
		font-size: 15px; /* Adjust the font-size as needed to make the icon smaller */
		padding-bottom: 10px;
		color: #000000;
	}

	.closeDialogBtn{
		border-color: grey;
		border-width: 2px;
		color: grey;
	}

	#update_courses_btn{
		background-color: #151C55;
		opacity: 80%;
		color: #FFFFFF;
		margin-top: 20px;
	}

	#skillTable{
		border: 1px black;
		height:"500px";
	}

	.scrollable-panel {
		max-height: 175px;
		overflow-y: auto;
	}

	.scrollable-table {
		max-height: 13.5cm;
		overflow-y: auto;
	}
</style>
