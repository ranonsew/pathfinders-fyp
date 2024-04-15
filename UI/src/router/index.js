import { createRouter, createWebHistory } from 'vue-router/auto'
import {useUserStore} from "../stores/user" // used in prod
import NProgress from "nprogress"

// route configuration with file-based routing
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
	scrollBehavior() {
		return {top: 0}
	},
})

// Progress bar configuration
NProgress.configure({
	minimum: 0.1,
	easing: 'ease',
	speed: 800,
	showSpinner: false,
})

// eslint-disable-next-line
router.beforeEach((to, from) => {
	NProgress.start() // progress bar start

	// prod only
	if (import.meta.env.MODE === "production") {
		const store = useUserStore() // need to have inside here to prevent error
		if (!store.isAuthenticated && to.name !== "/login") return "/login" // must log in to do stuff
		if (store.isAuthenticated && to.name === "/login" && store.isAdmin) return "/admin-all-roles" // cannot access login if already logged in admin
		if (store.isAuthenticated && to.name === "/login" && !store.isAdmin) return "/explore-role" // cannot access login page if already logged in
		if (!store.isAdmin && to.meta.requiresAdmin) return false // cannot access admin pages if not admin
	}
})

// eslint-disable-next-line
router.afterEach((to, from) => {
	document.title = `Pathfinders | ${to.name.slice(1) || "Home"}` // dynamic title changing -- only after user loads into page
	NProgress.done() // progress bar complete
})

export default router
