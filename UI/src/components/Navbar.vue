<script setup>
import {ref} from "vue"
import {useRouter} from "vue-router"
import {useUserStore} from "../stores/user"
import logo from "../assets/pathFinder-logo.png"

const rail = ref(true)
const router = useRouter()
const store = useUserStore()
// store.isAdmin = true // remove when not testing

function logout() {
	store.$reset()
	router.push("/login")
}
</script>

<template>
	<v-navigation-drawer app permanent color="primary" :rail="rail" elevation="10" v-if="store.userId">
		<v-list>
			<v-list-item :prepend-avatar="logo" class="text-white font-italic" title="Pathfinders" subtitle="For students, by students" @click="rail = !rail"></v-list-item>
			<v-divider></v-divider>
		</v-list>
		<v-list density="compact" nav>
			<!-- if admin, then Admin nav -->
			<template v-if="store.isAdmin">
				<v-list-item prepend-icon="mdi-account-multiple" title="All Roles" to="/admin-all-roles" class="icons">
					<v-tooltip activator="parent" location="end" :disabled="!rail">All Roles</v-tooltip>
				</v-list-item>
				<v-list-item prepend-icon="mdi-account-star" title="All Skills" to="/admin-all-skills" class="icons">
					<v-tooltip activator="parent" location="end" :disabled="!rail">All Skills</v-tooltip>
				</v-list-item>
				<v-list-item prepend-icon="mdi-file-multiple" title="All Courses" to="/admin-all-courses" class="icons">
					<v-tooltip activator="parent" location="end" :disabled="!rail">All Courses</v-tooltip>
				</v-list-item>
			</template>

			<!-- if not, student nav -->
			<template v-else>
				<v-list-item prepend-icon="mdi-account-multiple" title="Explore All Roles" to="/explore-role" class="icons">
					<v-tooltip activator="parent" location="end" :disabled="!rail">Explore All Roles</v-tooltip>
				</v-list-item>
				<v-list-item prepend-icon="mdi-file-arrow-up-down" title="Update my Courses" to="/update-my-courses" class="icons">
					<v-tooltip activator="parent" location="end" :disabled="!rail">Update my Courses</v-tooltip>
				</v-list-item>
				<v-list-item prepend-icon="mdi-monitor-dashboard" title="My Competencies" to="/competency-summary" class="icons">
					<v-tooltip activator="parent" location="end" :disabled="!rail">My Competencies</v-tooltip>
				</v-list-item>
				<v-list-item prepend-icon="mdi-account" title="My Profile" to="/user-profile" class="icons">
					<v-tooltip activator="parent" location="end" :disabled="!rail">My Profile</v-tooltip>
				</v-list-item>
				<!-- <v-list-item prepend-icon="mdi-account-group" title="Role Info View" to="/role-info" class="icons">
					<v-tooltip activator="parent" location="end" :disabled="!rail">Role Info</v-tooltip>
				</v-list-item> -->
				<!-- <v-list-item prepend-icon="mdi-ticket-confirmation" title="Confirm Courses" to="/confirm-courses" class="icons">
					<v-tooltip activator="parent" location="end" :disabled="!rail">Confirm Courses</v-tooltip>
				</v-list-item> -->
			</template>
		</v-list>

		<template v-slot:append>
			<v-list-item prepend-icon="mdi-logout-variant" title="Logout" @click="logout()" class="icons" v-if="store.isAuthenticated">
				<v-tooltip activator="parent" location="end" :disabled="!rail">Logout</v-tooltip>
			</v-list-item>
			<v-list-item prepend-icon="mdi-login-variant" title="Login" to="/login" class="icons" v-else>
				<v-tooltip activator="parent" location="end" :disabled="!rail">Login</v-tooltip>
			</v-list-item>
		</template>
	</v-navigation-drawer>
</template>

<style scoped>
	.icons{
		color: rgb(255, 255, 255, 0.6);
	}
</style>
