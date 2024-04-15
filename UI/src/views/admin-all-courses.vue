<script setup>
import {ref, onMounted, computed} from "vue"
import { backend_url } from "../addresses";
import {useRouter} from "vue-router"
import axios from "axios"

var courses = ref([])
var search = ref('')

const router = useRouter()

const to_update = (e) => {
	router.push({path: "admin-update-course", query: {course_id: e.id}})
}

const to_add = () => {
	router.push({path: "admin-add-course"})
}

const filteredCourses = computed(() => {
	return courses.value.filter(course => course.name.toLowerCase().includes(search.value.toLowerCase()))
});

function deleteCourse(course_id) {
	axios.delete(`${backend_url}/course/delete/${course_id}`)
	.then(response => {
		// toast.info(response.data.message);
		location.reload();
	})
	.catch(error => {
		console.error('Error fetching data:', error);
	});
}

onMounted(async () => {
	try{
		var res = await fetch(`${backend_url}/course/get_all`)
		var data = await res.json()
		courses.value = data.content
	} catch (err) {
		console.error(err)
	}
})

</script>

<template>
	<v-container class="mt-5">
		<v-card-title class="text-h5 font-weight-bold">All Courses</v-card-title>
		<v-divider></v-divider>
		<v-container class="mt-5">
			<v-row>
				<v-col cols class="ms-11 me-5">
					<v-text-field
						v-model="search"
						label="Search Course by name"
						outlined clearable>
					</v-text-field>
				</v-col>
				<v-col cols="3" class="mt-2 d-flex justify-center">
					<v-btn class="elevation-0" id="new_courses" @click="to_add"> <!--link to new roles page to be added-->
						+ Add New Courses
					</v-btn>
				</v-col>
			</v-row>

			<v-table fixed-header>
				<thead>
					<tr>
						<th></th>
						<th class="text-left text-body-1 font-weight-black text-black">
							Course Code
						</th>
						<th class="text-left text-body-1 font-weight-black text-black">
							Course Name
						</th>
						<th></th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="course in filteredCourses" :key="course.name">
						<td></td>
						<td>
							{{ course.id }}
						</td>
						<td>
							{{ course.name }}
						</td>

						<td class="d-flex justify-end">
							<v-btn variant="plain" icon="mdi-pencil" color="#151C55" v-ripple="false" @click="to_update(course)"></v-btn>
							<v-dialog width="450">
								<template v-slot:activator="{ props }">
									<v-btn v-bind="props" variant="plain" icon="mdi-delete" color="#D94D36" v-ripple="false"></v-btn>
								</template>

								<template v-slot:default="{ isActive }">
									<v-card height="170" id="dialog">
										<v-card-title class="d-flex justify-center mt-7 font-weight-bold">
											Confirm Deletion of "{{ course.id }}"?
										</v-card-title>

										<v-card-text class="d-flex justify-center">
											<v-btn
											text="Cancel"
											@click="isActive.value = false"
											class="d-flex justify-center me-7 dialogCancelBtn dialogBtn elevation-0"
											></v-btn>

											<v-btn
											text="Delete"
											@click="isActive.value = false; deleteCourse(course.id)"
											class="d-flex justify-center dialogDeleteBtn dialogBtn elevation-4"
											></v-btn>

										</v-card-text>
									</v-card>
								</template>
							</v-dialog>
						</td>
					</tr>
				</tbody>
			</v-table>
		</v-container>
	</v-container>
</template>

<style scoped>
	#new_courses {
		background-color: #7F6B4A;
		color: #F9F9F9;
	}

	#dialog {
		border-radius: 10px;
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
