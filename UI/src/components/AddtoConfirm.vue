<script setup>
import {ref, onMounted, watch} from "vue"
import {backend_url} from "../addresses.js"

defineProps({
  course_name: String,
  course_code: String,
	find_course: String,
})

const emits = defineEmits(['update:course_name', 'update:course_code', 'update:find_course'])

const listItems = ref([])
const selectedCourse = ref('');

watch(selectedCourse, (newValue) => {
  // Emit an event to update the parent component's prop when the selection changes
  emits('update:find_course', newValue);
});

onMounted(async () => {
	const res = await fetch(`${backend_url}/course/get_all`);
	const data = await res.json();
	console.log(data.content);
	listItems.value = data.content.map((course) => course.id +": "+ course.name);
})
</script>

<template>
	<v-card max-width="800">
		<v-toolbar>
			<v-toolbar-title class="font-weight-light">Add Courses</v-toolbar-title>
			<v-spacer></v-spacer>
		</v-toolbar>
		<v-card-text>

		<!--
			<v-text-field
				:value="course_code"
				@input="$emit('update:course_code', $event.target.value)"
				label="Course Code"
			></v-text-field>

			<v-text-field
				:value="course_name"
				@input="$emit('update:course_name', $event.target.value)"
				label="Course Name"
			></v-text-field>
		-->

			<v-autocomplete
				v-model="selectedCourse"
				label="Find Course"
				:items="listItems"
			></v-autocomplete>

		</v-card-text>
	</v-card>
</template>
