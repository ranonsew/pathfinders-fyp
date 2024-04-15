import {defineStore, acceptHMRUpdate} from "pinia"

export const useSearchStore = defineStore("search", {
	state: () => ({
		search: {
			keyword: null,
			specialization: null,
			salary: 0,
		},
	}),
	getters: {},
	actions: {},
	persist: {
		key: "role-search-data",
		storage: sessionStorage,
	},
})

if (import.meta.hot)
	import.meta.hot.accept(acceptHMRUpdate(useSearchStore, import.meta.hot))

