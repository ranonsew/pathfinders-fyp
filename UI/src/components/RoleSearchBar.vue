<script setup>
import {ref, onMounted} from "vue"
import {useRouter} from "vue-router"
import {useSearchStore} from "../stores/search"
import {backend_url} from "../addresses"
import {storeToRefs} from "pinia"

const router = useRouter()
const store = useSearchStore()
// direct store to ref for search. Updating stuff is done by directly putting the search.<x> into v-model.
const {search} = storeToRefs(store)

const loading = ref(false)
const specialization_list = ref([])
const min_salary = ref(3000)
const max_salary = ref(0)

function handleSearch() {
	loading.value = true
	if (location.href.includes("/searched-roles")) {
		location.reload()
	} else {
		router.push("/searched-roles")
	}
}

onMounted(async () => {
	try {
		// spec list
		const res = await fetch(`${backend_url}/spec/get_all`)
		const data = await res.json()
		specialization_list.value = data.content
		// salaries
		const res2 = await fetch(`${backend_url}/role/get_all`)
		const data2 = await res2.json()
		const salaries = data2.content.map(({salary}) => salary)
		// min_salary.value = 3000
		max_salary.value = Math.floor(Math.max(...salaries) / 1000) * 1000

	} catch (err) {
		console.error(err)
	}
})
</script>

<template>
		<v-form @submit.prevent="handleSearch">
				<v-container fluid>
						<v-row>
								<v-col>
										<span class="text-h6 font-weight-bold">Role Search</span>
								</v-col>
						</v-row>

						<v-row>
								<v-col sm="3">
										<v-text-field
												v-model="search.keyword"
												label="Keyword"
												variant="underlined">
										</v-text-field>
								</v-col>

								<v-col sm="3">
										<v-select
												v-model="search.specialization"
												label="Specialization"
												:items="specialization_list"
												item-value="id"
												item-title="name"
												variant="underlined"
												clearable>
										</v-select>
								</v-col>

								<v-col sm="4" class="ps-5">
										<div class="text-caption font-weight-medium">Salary ($)</div>
											<v-slider
												v-model="search.salary"
												thumb-label="always"
												:max="max_salary"
												:min="min_salary"
												:step="1"
												:ticks="[min_salary, max_salary]"
												show-ticks="always"
												tick-size="4"
												class="text-caption"
												color="#106B13"
											>
											</v-slider>
								</v-col>

								<v-col class="text-center" sm="2">
										<v-btn
												:loading="loading"
												width = "150px"
												type="submit"
												class="mt-2 ms-2"
												text="Submit"
												color='primary'>
										</v-btn>
								</v-col>

						</v-row>
				</v-container>
		</v-form>

	</template>

<style>

#search{
		margin: 10px 10px 10px 10px;
		background: rgb(132, 112, 76, 0.25);
		border-radius: 10px;
		position: auto;
		font-weight: bold;
	}

</style>
