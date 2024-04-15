<script setup>
import axios from 'axios'; // Import Axios library
import {ref, onMounted} from "vue"
import RoleSearchBar from "../components/RoleSearchBar.vue"
import {useSearchStore} from "../stores/search"
import {useUserStore} from "../stores/user"
import {storeToRefs} from "pinia"
import {backend_url} from "../addresses"
import {useRouter} from "vue-router"
import VueApexCharts from "vue3-apexcharts";

const store = useSearchStore()
const userStore = useUserStore()

const {search} = storeToRefs(store)
const userId = userStore.userId

const display_roles = ref([])

const router = useRouter();

const selected = (e) => {
	router.push({path: "/role-info/", query: {id: e}})
}

onMounted(async () => {
	try {
		if (search.value.specialization == null) {
			var res = await fetch(`${backend_url}/role/get_all`)
		} else {
			res = await fetch(`${backend_url}/spec/role_mapped/salary_range/get/${search.value.specialization}/${search.value.salary}`)
		}
		const data = await res.json()
		var temp = data.content

		if (search.value.keyword != null) {
			temp = temp.filter(({name}) => name.toLowerCase().includes(search.value.keyword.toLowerCase()))
		}

		display_roles.value = temp.filter(({salary}) => salary >= search.value.salary)

		for (let i = 0; i < display_roles.value.length; i++) {
			let requestData = {
        role_id: display_roles.value[i].id,
        student_id: userId
			};

			axios.post(`${backend_url}/user/get_role_progression_level`, requestData)
			.then(response => {
					display_roles.value[i]['progression'] = response.data.data['role_progression_level']
        })
        .catch(error => {
						display_roles.value[i]['progression'] = 0
            console.error('Error fetching data:', error);
        });
		}

	} catch (err) {
		console.error(err)
	}
})

const roleProgressionChart = {
	chart: {
		type: 'radialBar',
		offsetX: -10
	},
	plotOptions: {
	radialBar: {
		startAngle: -90,
		endAngle: 90,
		hollow: {
			size: '80%',
		},
		track: {
			margin: 1
		},
		dataLabels: {
			name: {
				offsetY: 25,
				fontSize: 12
				// show: false
			},
			value: {
				offsetY: -10,
				fontSize: 12
		}}}},
	labels: ["ROLE PROGRESSION"],
	colors:["#106B13"],
	stroke: { lineCap: "round" },
}

</script>

<template>
    <v-container class="mt-5">
			<v-btn prepend-icon="mdi-arrow-left-circle" variant="plain" id="back-button" class="mb-5" onclick="history.back()">
				Back
			</v-btn>

		<v-card-title class="text-h5 font-weight-bold">Searched Roles</v-card-title>
		<v-divider></v-divider>
        <v-container id='search'>
					<RoleSearchBar></RoleSearchBar>
        </v-container>
        <v-container class="ms-3" v-if="display_roles.length > 0">
            <v-card
						class="pa-2 mb-3"
						v-for="role in display_roles"
						:key="role"
						id="role-card">
                <div class="d-flex flex-no-wrap justify-space-between">
									<v-row style="max-width: 80%;">
                    <div>
                        <v-card-title class="text-h6 ms-4 mt-3">
                            {{ role.name }}
                        </v-card-title>

                        <v-card-text id="description" class="text-body-2 ms-4 mt-2">
                            {{ role.desc }}
                        </v-card-text>

                        <v-card-actions class="ms-4">
                            <v-btn variant="outlined" @click="selected(role.id)" id="view-info">View Info</v-btn>
                        </v-card-actions>

                    </div>
									</v-row>

									<v-row id="card_details" style="max-width: 20%;">

										<v-col>

											<v-row style="margin-bottom: 5px;">
												<!-- <v-progress-circular class="my-1 me-2" color="#106B13" model-value="100" :size="42">
												<span class="font-weight-black text-h6">%</span>
												</v-progress-circular>
												<span class="text-caption font-weight-medium me-5" id="completion">{{ role.progression }}<br>COMPLETED</span> -->
													<apexchart :options="roleProgressionChart" :series="[role.progression]" height="125px"></apexchart>
											</v-row>

											<v-row>
												<v-progress-circular class="my-1 me-2" color="#84704C" model-value="100" :size="42">
														<span class="font-weight-black text-h6">$</span>
												</v-progress-circular>
												<span class="text-caption font-weight-medium text-h6" id="salary">{{ Math.floor(role.salary / 100) * 100 }}<br>AVERAGE SALARY</span>
											</v-row>
										</v-col>
										</v-row>

                </div>
            </v-card>
        </v-container>
				<v-container v-else>
					No search results
				</v-container>
    </v-container>

</template>

<style scoped>
	#search {
		margin: 20px 10px 20px 10px;
		background: rgb(132, 112, 76, 0.38);
		border-radius: 10px;
		position: auto;
		font-weight: bold;
	}

    #description {
        text-align: justify;
    }

    #salary {
        color: #84704C
    }

    #completion {
        color: #106B13;
				text-align: center;
    }

    #view-info {
			background-color: RGB(21, 28, 85, 0.95);
			color: #FFFFFF;
			border-radius:5px;
			width: 130px;
			height: 36px;
			font-size: 14px;
    }

    #career-path {
        background-color: #84704C;
        color: white;
    }

    #career-path {
        border-radius: 19px;
        width: 110px;
    }

		#card_details{
			border-left: 2px solid #D7D7D7;
			padding-left: 15px;
			margin-bottom: 10px;
		}

		#role-card{
			margin-bottom: 10px;
			background-color: RGB(234, 234, 234, 0.95);
			padding: 15px;
		}

		#back-button {
        background: #151C55;
        color: #f4f4f4;
    }

</style>
