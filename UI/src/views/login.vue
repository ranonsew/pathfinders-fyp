<!-- login to do later -->

<script setup>
import {ref, computed, watch} from "vue"
import {useRouter} from "vue-router"
import {backend_url} from "../addresses"
import {useUserStore} from "../stores/user"

// composables for use
const router = useRouter()
const store = useUserStore()

// UI related references
const tab = ref("") // "Login" | "Register"
watch(tab, function() {})
const form = ref()
const loginError = ref(false)
const registerError = ref({id_taken: false, pwd_not_matching: false}) // former for server returned err. latter for UI pwd check.
const errorContent = ref("")
const loading = ref(false)

// input fields and stuff
const user_id = ref("")
const password = ref("")
const confirm_password = ref("")

// showing password (via changing its field (and icon to show more easily))
const show_password = ref(false)
const show_cfm_password = ref(false)
const password_field_type = computed(() => show_password.value ? "text" : "password")
const cfm_pass_field_type = computed(() => show_cfm_password.value ? "text" : "password")
const show_password_icon = computed(() => show_password.value ? "mdi-eye-off-outline" : "mdi-eye-outline")
const show_cfm_password_icon = computed(() => show_cfm_password.value ? "mdi-eye-off-outline" : "mdi-eye-outline")

// form rules
const rules = ref([
	(v) => !!v || "This field is required.", // "required" rule
])

// login function on form submission
async function handleLogin() {
	// resetting error handle bits
	loginError.value = false
	loading.value = true

	try {
		// POST request to server
		const res = await fetch(`${backend_url}/user/auth`, {
			method: "POST",
			mode: "cors",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({user_id: parseInt(user_id.value), password: password.value}),
		})
		const data = await res.json()

		// server returns error
		if (res.status !== 200) {
			loginError.value = true
			errorContent.value = data.message
			loading.value = false
			return
		}

		// successful login
		store.isAuthenticated = true // confirm auth
		store.userId = user_id.value // confirm the userId (for later use)
		store.isAdmin = !!data.is_admin // is_admin check from the server/database (setting as a boolean)
		if (store.isAdmin) router.push("/admin-all-roles")
		else router.push("/explore-role") // go to "explore-role" route
	} catch (err) {
		// fetch errror
		loginError.value = true
		errorContent.value = err.message
		loading.value = false
		return
	}
}

// registration function on form submission
async function handleRegister() {
	// resetting error handle bits
	registerError.value.id_taken = false
	registerError.value.pwd_not_matching = false
	loading.value = true

	// UI check -- password matching
	if (password.value !== confirm_password.value) {
		registerError.value.pwd_not_matching = true
		loading.value = false
		return
	}

	try {
		// send POST request to server
		const res = await fetch(`${backend_url}/user/create`, {
			method: "POST",
			mode: "cors",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({user_id: user_id.value, user_password: password.value, is_admin:0}),
		})
		const data = await res.json()

		// server returns error
		if (res.status !== 201) {
			registerError.value.id_taken = true
			errorContent.value = data.message
			loading.value = false
			return
		}

		// successful login
		store.isAuthenticated = true // confirm registration auth
		store.userId = user_id.value // set userId for later use
		// can only register as student from the front end for security reasons -- we will use backend directly to intiailize new admins
		router.push("/particulars") // go to particulars -- continue setup
	} catch (err) {
		// fetch error
		registerError.value.id_taken = true
		errorContent.value = err.message
		loading.value = false
		return
	}
}
</script>

<template>
	<v-container class="d-flex align-center justify-center">
		<span class="hero"></span>
		<v-card width="500px" height="380px" class="loginCard py-3 px-3">
			<v-tabs v-model="tab" align-tabs="center" fixed-tabs class="bothTabs">
				<v-tab value="Login" color="#151C55" variant="elevated" class="tabs">Login</v-tab>
				<v-tab value="Register" color="#84704C" variant="elevated" class="tabs">Sign Up</v-tab>
			</v-tabs>
			<v-card-text>
				<v-window v-model="tab">
					<v-window-item value="Login" class="mt-10">
						<v-form v-model="form" @submit.prevent="handleLogin">
							<v-text-field
								v-model="user_id"
								:readonly="loading"
								:rules="rules"
								class="mb-2"
								clearable
								label="User ID"
								placeholder="Enter your user ID"
							></v-text-field>

							<v-text-field
								v-model="password"
								:readonly="loading"
								:rules="rules"
								class="mb-5"
								clearable
								:type="password_field_type"
								:append-icon="show_password_icon"
								@click:append="show_password = !show_password"
								label="Password"
								placeholder="Enter your password"
							></v-text-field>

							<v-spacer />

							<v-row>
								<v-col>
									<!-- <v-btn variant="text" :ripple="false" class="text-decoration-underline adminBtn">
										Admin? Click Here
									</v-btn> -->
								</v-col>
								<v-col>
									<v-btn
									:disabled="!form"
									:loading="loading"
									block
									color="#151C55"
									type="submit"
									variant="elevated"
									class="	text-white">
										Login
									</v-btn>
								</v-col>
							</v-row>
						</v-form>

						<v-dialog v-model="loginError" width="auto" max-width="600">
							<v-card>
								<v-card-title>Login Error</v-card-title>
								<v-card-text>{{ errorContent }}</v-card-text>
								<v-card-actions>
									<v-btn color="primary" @click="loginError = false">Close</v-btn>
								</v-card-actions>
							</v-card>
						</v-dialog>
					</v-window-item>

					<v-window-item value="Register">
						<v-form v-model="form" @submit.prevent="handleRegister">
							<v-text-field
								v-model="user_id"
								:readonly="loading"
								:rules="rules"
								class="mb-2"
								clearable
								label="User ID"
								placeholder="Enter your user ID"
							></v-text-field>

							<v-text-field
								v-model="password"
								:readonly="loading"
								:rules="rules"
								clearable
								label="Password"
								:type="password_field_type"
								:append-icon="show_password_icon"
								@click:append="show_password = !show_password"
								placeholder="Enter your password"
							></v-text-field>

							<v-text-field
								v-model="confirm_password"
								:readonly="loading"
								:rules="rules"
								clearable
								:type="cfm_pass_field_type"
								:append-icon="show_cfm_password_icon"
								@click:append="show_cfm_password = !show_cfm_password"
								label="Confirm your password"
							></v-text-field>

							<v-spacer />
							<v-row>
								<v-col>
								</v-col>
								<v-col>
									<v-btn
									:disabled="!form"
									:loading="loading"
									block
									color="#84704C"
									type="submit"
									variant="elevated"
									class="	text-white">
										Sign Up
									</v-btn>
								</v-col>
							</v-row>
						</v-form>

						<!-- ID taken (error by server) -->
						<v-dialog v-model="registerError.id_taken" width="auto" max-width="600">
							<v-card>
								<v-card-title>Registration Error</v-card-title>
								<v-card-text>{{ errorContent }}</v-card-text>
								<v-card-actions>
									<v-btn color="primary" @click="registerError.id_taken = false">Close</v-btn>
								</v-card-actions>
							</v-card>
						</v-dialog>

						<!-- Password & Confirm not matching (UI check) -->
						<v-dialog v-model="registerError.pwd_not_matching" width="auto" max-width="600">
							<v-card>
								<v-card-title>Registration Error</v-card-title>
								<v-card-text>"Password" & "Confirm Password" do not match.</v-card-text>
								<v-card-actions>
									<v-btn color="primary" @click="registerError.pwd_not_matching = false">Close</v-btn>
								</v-card-actions>
							</v-card>
						</v-dialog>
					</v-window-item>
				</v-window>
			</v-card-text>
		</v-card>
	</v-container>

</template>

<style scoped>
	.hero{
		background: url('../assets/bg2.jpg');
		/* background-repeat: repeat; */
		background-size: cover;
		opacity: 0.5;
		position: absolute;
    top: 0;
    left: 0;
		height: 100%;
		width: 100%;
	}

	.loginCard{
		border-radius: 10px;
	}

	.tabs{
		opacity: 90%;
		border-radius: 5px;
	}

	.adminBtn:hover{
		color: RGB(0, 0, 0, 0.5);
	}
</style>
