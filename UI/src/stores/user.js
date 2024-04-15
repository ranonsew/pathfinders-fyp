import {defineStore, acceptHMRUpdate} from "pinia"

/**
 * To use, at the top of script, add "import {useAuthStore} from 'relative_path/stores/auth'"
 * Then in mounted, or setup, can add "const store = useAuthStore()". "store" is used to access everything here/
 * Current Pinia organization --> Options Store
 */
export const useUserStore = defineStore("user", {
	// retrieved as "store.id" for example
	state: () => ({
		isAuthenticated: false,
		isAdmin: false, // the only thing admin uses atm (26/9/23 -- 5.15pm)
		userId: 0,
		name: "",
		faculty: "",
		email: "",
		courses: [], // courses completed (student)
		skills: [], // skills obtained (student)
		roles: [], // roles obtained? (student)
	}),
	getters: {},
	actions: {},
	persist: {
		key: "user-related-data",
		storage: sessionStorage,
	},
})

if (import.meta.hot)
	import.meta.hot.accept(acceptHMRUpdate(useUserStore, import.meta.hot))
