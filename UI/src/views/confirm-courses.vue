<script setup>
// import AddtoConfirm from '../components/AddtoConfirm.vue';
import {backend_url} from "../addresses.js"
import {ref, onMounted} from "vue"
import {useRouter} from "vue-router"
import {useUserStore} from "../stores/user"
// import axios from 'axios'; // Import Axios library

const store = useUserStore()
const router = useRouter()

const showCourses = ref(true)
// const course_name = ref("")
// const course_code = ref("")
// const find_course = ref("")
// const course_term = ref("")
const courses = ref([])
const courseProps = ({id, name}) => ({title: id, subtitle: name})
const courses_selected = ref([])

onMounted(async () => {
	const res = await fetch(`${backend_url}/course/get_all`) // retrieve possible courses from db
	const data = await res.json()
	console.log(data.content)
	courses.value = data.content
})

function UploadAgain() {
	store.courses = []
	router.push("/upload-transcript")
}

function addCourse() {
	showCourses.value = false
}

function confirmAddCourse() {
	for (let course of courses_selected.value) {
		console.log(course.id, course.name)
		if (!store.courses.some((c) => c.code === course.id)) {
			// placeholder terms (current processing does not include terms)
			store.courses.push({term: "202X-2Y Term Z", code: course.id, title: course.name})
		}
	}
	showCourses.value = !showCourses.value
	courses_selected.value = []
}

function cancelAdd() {
	showCourses.value = !showCourses.value
}

function deleteCourse(course) {
	store.courses = store.courses.filter((item) => item !== course)
	console.log(course.title + " deleted")
}


async function onConfirmation() {
	try {
		const res = await fetch(`${backend_url}/user/add_user_course`, {
			method: "POST",
			mode: "cors",
			headers: {"Content-Type": "application/json"}, // need for JSON passing
			body: JSON.stringify({user_id: store.userId, course_id: Array.from(store.courses, ({code}) => code)})
		})
		const data = await res.json()
		console.log(data)
		router.push("/user-profile")
		return
	} catch (err) {
		console.error(err)
	}
}


</script>

<template>
	<v-container fluid>
		<!-- Display response from upload courses -->
		<v-container fluid v-if="showCourses">
			<v-card-title class="text-h5 font-weight-bold mt-5">Confirm Courses</v-card-title>
			<v-divider class="mb-5"></v-divider>
			<v-container class="text-center">
				<v-row>
					<v-col cols="1"></v-col>
					<v-col cols='2' class="font-weight-bold text-left">
						Code
					</v-col>
					<v-col cols='6' class="font-weight-bold text-left">
						Title
					</v-col>
					<v-col></v-col>
				</v-row>
				<v-row v-for="(course, idx) in store.courses" :key="idx+'-'+course.code">
					<v-col cols="1"></v-col>
					<v-col cols='2' class="text-left">
						{{course.code}}
					</v-col>
					<v-col cols='6' class="text-left">
						{{course.title}}
					</v-col>
					<v-col class="text-right">
						<v-btn density="compact" variant="plain" icon="mdi-delete" color="#D94D36" class="pb-1" @click="deleteCourse(course)">
						</v-btn>
					</v-col>
				</v-row>
				<v-row class="mt-7">
					<v-col class="text-right" >
						<v-btn @click="UploadAgain" class='action_buttons' style='background: RGB(195, 31, 31, 0.88)'>
							Upload Again
						</v-btn>
						<v-btn @click="addCourse" class='action_buttons' style='background: RGB(21, 28, 85, 0.85)'>
							Add courses
						</v-btn>
						<v-btn @click="onConfirmation" class='action_buttons' style='background: RGB(16, 107, 19)'>
							Confirm
						</v-btn>
					</v-col>
				</v-row>
			</v-container>
		</v-container>
		<v-container fluid class="d-flex flex-column align-center" v-else>
			<v-card max-width="800" min-width="550">
				<v-toolbar>
					<v-toolbar-title class="font-weight-bold">Add Courses</v-toolbar-title>
					<v-spacer></v-spacer>
				</v-toolbar>
				<v-card-text>
					<v-autocomplete
						clearable multiple chips
						:items="courses" :item-props="courseProps"
						v-model="courses_selected" label="Courses" variant="underlined"
					></v-autocomplete>
				</v-card-text>
			</v-card>
			<v-row class="mx-auto mt-2 d-flex align-center">
				<v-btn @click="confirmAddCourse" class='action_buttons mt-2' style='background-color: RGB(16, 107, 19, 0.98)'>
						Confirm
				</v-btn>
				<v-btn @click="cancelAdd" class='action_buttons mt-2' style='background-color: RGB(195, 31, 31, 0.8)'>
						Cancel
				</v-btn>
			</v-row>
		</v-container>
	</v-container>
</template>

<style scoped>
.action_buttons{
	border-radius: 5px;
	text-align: center;
	width: 720;
	height: 44;
	margin: 10px 10px 2px 2px;
	color: white;
}
</style>
