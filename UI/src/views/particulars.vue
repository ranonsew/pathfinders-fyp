<script setup>
import {ref, watch} from "vue"
import {useRouter} from "vue-router"
import {useUserStore} from "../stores/user"
import {backend_url} from "../addresses"

const router = useRouter()
const store = useUserStore()

const form = ref()
const loading = ref(false)

const name = ref("")

const faculty = ref()
const faculty_list = ref(["SCIS", "SOSS", "Accountancy", "Business", "Law", "Economics", "CIS"]) // for students creating an account

const email = ref("")
watch(email, () => {
	email.value = email.value.toLowerCase()
})

const rules = ref([
	(v) => !!v || "This field is required.",
])

async function handleSubmit() {
	loading.value = true

	try {
		// POST request to server
		const res =  await fetch(`${backend_url}/user/update_particulars`, {
			method: "POST",
			mode: "cors",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({
				user_id: store.userId,
				user_name: name.value,
				user_faculty: faculty.value,
				user_email: email.value
			})
		})
		const data = await res.json()

		if (res.status !== 201) {
			console.error(data.message)
			return
		}

		// successful update
		store.name = name.value
		store.faculty = faculty.value
		store.email = email.value
		router.push("/update-my-courses")
	} catch (err) {
		console.error(err)
	}
}
</script>

<template>
	<v-container fluid class="text-center d-flex justify-center mt-10">
		<v-card class="px-6 py-8" width="444">
			<v-card-title>Personal Particulars</v-card-title>
			<v-form v-model="form" @submit.prevent="handleSubmit">
				<v-spacer></v-spacer>
				<v-text-field
					v-model="name"
					:rules="rules"
					class="mb-2"
					clearable
					label="Full Name"
				></v-text-field>
				<v-select
					clearable
					:items="faculty_list"
					v-model="faculty"
					:rules="rules"
					class="mb-2"
					label="Faculty"
					variant="outlined"
				></v-select>
				<v-text-field
					v-model="email"
					:rules="rules"
					class="mb-2"
					clearable
					type="email"
					label="Email Address"
					placeholder="name.2020@scis.smu.edu.sg"
				></v-text-field>
				<v-spacer />
				<v-btn
					:disabled="!form"
					:loading="loading"
					block
					color="indigo-darken-4"
					size="large"
					type="submit"
					variant="elevated"
				>
					Save
				</v-btn>
			</v-form>
		</v-card>
	</v-container>
</template>
