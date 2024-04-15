<script setup>
import {ref, onMounted, watch} from "vue"
import RoleSearchBar from "../components/RoleSearchBar.vue"
import {backend_url} from "../addresses"
import {useRouter} from "vue-router"
import {useUserStore} from "../stores/user"

const cards = ref([])
watch([cards], function() {
	cards.value.sort((a,b) => b["progression"] - a["progression"])
}, {deep: true})

const router = useRouter()
const store = useUserStore()

const selected = (e) => {
	router.push({path: "/role-info/", query: {id: e}})
}

onMounted(async () => {
	try {
		const res = await fetch(`${backend_url}/role/get_all`)
		const data = await res.json()
		cards.value = data.content

		cards.value.forEach(async (card, idx) => {
			const res_role_progression = await fetch(`${backend_url}/user/get_role_progression_level`, {
				method: "POST",
				mode: "cors",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify({role_id: card.id, student_id: store.userId}),
			})
			const data_role_progression = await res_role_progression.json()
			if (res_role_progression.status !== 201) throw new Error(data_role_progression.message)
			cards.value[idx]["progression"] = typeof(data_role_progression.data["role_progression_level"]) !== "number" ? 0 : data_role_progression.data["role_progression_level"]
		})
	} catch (err) {
		console.error(err)
	}
})
</script>

<template>
	<v-container class="mt-5">
			<v-card-title class="text-h5 font-weight-bold">Explore All Roles</v-card-title>
			<v-divider></v-divider>
			<v-container class="mt-6">
				<v-container id='search'>
					<RoleSearchBar></RoleSearchBar>
				</v-container>

				<v-container id='role-listing' class="mt-7">
					<v-row class="ms-2 mt-2 mb-5">
						<span class="font-weight-black text-h6">Discover NEW Roles!</span>
					</v-row>

					<v-row>
						<v-slide-group center-active show-arrows>
							<v-slide-group-item
								v-for="card in cards"
								:key="card"
								v-slot="{ isSelected, toggle }"
								>

								<v-card
									:color="isSelected ? 'primary' : 'white'"
									class="ma-2 rounded-lg"
									@click="toggle, selected(card.id)"
								>

									<v-card-title class="mt-1 font-weight-bold text-subtitle-1">
										{{card.name}}
									</v-card-title>

									<v-card-text class="text-left">
									{{card.desc}}
									</v-card-text>

									<v-row>
										<v-col cols>
											<v-card-text class="text-left font-weight-medium">
												Monthly Salary (Avg)
											</v-card-text>
										</v-col>
										<v-col cols="5">
											<v-card-text class="text-right font-weight-medium">
											${{(Math.floor(card.salary / 100) * 100 ).toLocaleString('en')}}
											</v-card-text>
										</v-col>
									</v-row>

								</v-card>

							</v-slide-group-item>
						</v-slide-group>
					</v-row>
				</v-container>
			</v-container>
	</v-container>
</template>

<style scoped>

	#click-here{
		color: #FFC424;
	}

	#click-here:hover{
		background-color: transparent;
		color: rgb(255, 196, 36, 0.5)
	}

	#role-listing{
		margin: 10px 10px 75px 10px;
	}

	.v-card{
		max-width: 29em;
	}

</style>
