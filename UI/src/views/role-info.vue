<script>
import axios from 'axios'; // Import Axios library
import {useUserStore} from "../stores/user"
import {backend_url} from "../addresses"
import VueApexCharts from "vue3-apexcharts";

export default {
  data() {
    return {
        availableCourseDict:{},
        courseRecommenderDialog:false,
        availableCourseDialog:false,
        courseList: [],
        courseDict: {},
        acquiredSkill: [],
        unacquiredSkill: [],
        userId : "",
        roleInfo: [],
        roleKeywordsInfo: [{id: 1, name: "Test 1"}, {id: 2, name: "Test 2"}, {id: 3, name: "Test 3"}, {id: 4, name: "Test 4"}],
        roleSkillsInfo: [],
        userRoleSkills: [],
        roleProgressionLevel: 0,
			salaries: [],
			favourite: false,
			icon: "",
			iconColour: "",
			message: null,
			isSuccessActive: false,
			barChart: {
					chart: {
						type: "bar",
						toolbar: {show: false, enabled: false}
					},
					plotOptions: {
						bar: {
							distributed: true,
							dataLabels: {position: 'top'},
						},
					},
					legend: { show: false },
          xaxis: {
            categories: [],
						title: {text: "Salary"},
						},
					yaxis: {
						labels: {
							formatter: function (val) {
								return val.toFixed(0);
							},
						},
						title: {text: "Counts"}
					},
					dataLabels: {
						enabled: false,
					},
					colors: [],
					annotations: {
						xaxis: [{
							x: "",
							label: {
								text: "Average",
								orientation: "horizontal",
								offsetY: -15,
								style: {
									fontSize: "90%",
									},
								},
							borderColor: "transparent"
					}]
				}
			},
			series: [{
				name: "Number of people with this salary",
				data: []
			}],
			roleProgressionChart: {
				chart: {
					type: 'radialBar',
				},
				plotOptions: {
        radialBar: {
          startAngle: -90,
          endAngle: 90,
          hollow: {
            size: '70%',
					},
					track: {
						margin: 1
					},
					dataLabels: {
						name: {
							show: false
						},
						value: {
							offsetY: 0,
							fontSize: 20
						}
					}
        }
      },
			colors:["#106B13"],
            stroke: { lineCap: "round" },
      labels: [""],
			grid: {padding: {top: -20}},
			},
    };
  },
	components: {
		apexchart: VueApexCharts,
	},
	computed: {
		roleId() {
			return this.$route.query.id;
		}
	},
	methods: {
		objectToArray(obj) {
      return Object.keys(obj).reduce((arr, key) => {
        const value = obj[key];
        const repeatedKeys = Array.from({ length: value }, () => key);
        return arr.concat(repeatedKeys);
      }, []).map(Number);
    },
		percentile() {
			let salary_expanded = this.objectToArray(this.salaries)
			let ten_percentile = salary_expanded[Math.floor(0.1 * salary_expanded.length)]
			let twentyFive_quantile = salary_expanded[Math.floor(0.25 * salary_expanded.length)]
			let fifty_percentile = salary_expanded[Math.floor(0.5 * salary_expanded.length)]
			let seventyFive_percentile = salary_expanded[Math.floor(0.75 * salary_expanded.length)]
			let ninty_percentile = salary_expanded[Math.floor(0.9 * salary_expanded.length)]
			return [ten_percentile, twentyFive_quantile, fifty_percentile, seventyFive_percentile, ninty_percentile]
		},
		getChartData() {
			let salary_expanded = this.objectToArray(this.salaries)
			let avg = salary_expanded.reduce((x, y) => {return x + y;}, 0) / salary_expanded.length
			let percentile_arr = this.percentile()

			for (let i = 0; i < percentile_arr.length; i++) {
				let current = percentile_arr[i];
				let prev = percentile_arr[i-1]

				if (avg > prev && avg < current) {
					this.barChart.colors.push("#48bf91")
					this.barChart.annotations.xaxis[0].x = "$" + current

				} else {
					this.barChart.colors.push("#b1e0ce")
				}

				if (i == 0) {
					this.barChart.xaxis.categories.push("<=$" + current)
					this.series[0].data.push(salary_expanded.filter((salary) => (salary <= current )).length)
				}

				else if (i == percentile_arr.length-1) {
					this.barChart.xaxis.categories.push(">$" + prev)
					this.series[0].data.push(salary_expanded.filter((salary) => (salary > prev)).length)
				}

				else {
					this.barChart.xaxis.categories.push("$" + current)
					this.series[0].data.push(salary_expanded.filter((salary) => (salary > prev && salary <= current)).length)
				}
			}
		},
		updateFav() {
			let role = {
					user_id: useUserStore().userId,
					role_id: this.roleId
			}

			if (this.favourite === false) {
				this.icon = 'mdi-star'
				this.iconColour = 'secondary'
				this.favourite = true
				axios.post(`${backend_url}/user/add_fav_role`, role)
				.then(response => {
					this.message = response.data.message
					this.isSuccessActive = true
				})
				.catch(error => {
					this.message = ('Error fetching data: ' + error)
					this.isSuccessActive = true
        })

			} else {
				this.icon = 'mdi-star-outline'
				this.iconColour = 'black'
				this.favourite = false
				axios.post(`${backend_url}/user/delete_fav_role`, role)
				.then(response => {
					this.message = response.data.message
					this.isSuccessActive = true
				})
				.catch(error => {
					this.message = ('Error fetching data: ' + error);
					this.isSuccessActive = true
        })
			}
		},

        courseRecommender()
        {
            const curRoleId = this.$route.query.id;
            const requestData = {
                role_id: parseInt(curRoleId),
                user_id: parseInt(this.userId)
            };

            axios.post(`${backend_url}/course_recommender/course_recommender`, requestData)
            .then(response => {
                this.courseDict = response.data.content;
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
        },

        getAvailableCourse()
        {
            const curRoleId = this.$route.query.id;
            const requestData = {
                role_id: parseInt(curRoleId),
                user_id: parseInt(this.userId)
            };

            axios.post(`${backend_url}/course_recommender/all_course_available`, requestData)
            .then(response => {
                this.availableCourseDict = response.data.content;
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
        },

        openCourseRecommender() {
        this.courseRecommenderDialog = true;
        },
        closeCourseRecommender() {
        this.courseRecommenderDialog = false;
        },

        openAvailableCourse() {
        this.availableCourseDialog = true;
        },
        closeAvailableCourse() {
        this.availableCourseDialog = false;
        },

		closeDialog() {
			this.isSuccessActive = false
		},

	},
	created() {
		const id = this.roleId;
		const store = useUserStore();
		const userId = store.userId;
        this.userId = store.userId;

        this.courseRecommender();
        this.getAvailableCourse();

    const requestData1 = {
        role_id: id
    };

    axios.post(`${backend_url}/role/see_information`, requestData1)
        .then(response => {
            this.roleInfo = response.data.data['role_info_result'];
            this.roleKeywordsInfo = response.data.data['role_keywords_result'];
            this.roleSkillsInfo = response.data.data['role_skills_result'];
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });

    const requestData2 = {
        role_id: id,
        student_id: userId
    };

    axios.post(`${backend_url}/user/get_role_progression_level`, requestData2)
        .then(response => {
            this.roleProgressionLevel = response.data.data['role_progression_level']
           // this.$set(this, 'roleProgressionLevel', response.data.data['role_progression_level']);
            console.log("Role Progression Level: ", this.roleProgressionLevel)

            if (typeof this.roleProgressionLevel === 'number') {
            // It's a numeric value
                console.log('roleProgressionLevel is a number:', this.roleProgressionLevel);
            } else {
                // It's not a numeric value
                console.log('roleProgressionLevel is not a number:', this.roleProgressionLevel);
            }

            this.userRoleSkills = response.data.data['role_user_skills_result']
            console.log('User Role Skills', this.userRoleSkills)
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });

    axios.get(`${backend_url}/role/salary_mapped/get/` + id)
    .then(response => {
				this.salaries = response.data.content.breakdown
				this.getChartData()
				this.percentile()
    })
    .catch(error => {
        console.error('Error fetching data:', error);
    });

		axios.get(`${backend_url}/user/get_fav_roles/` + userId)
		.then(response => {
			let fav_roles = response.data.content.map(item => item.id);
			this.favourite = fav_roles.includes(Number(id))
			this.icon = (this.favourite === true ? 'mdi-star' : 'mdi-star-outline')
			this.iconColour = (this.favourite === true ? 'secondary' : 'black');
		})
		.catch(error => {
			console.error('Error fetching data:', error);
		})
	}
}
</script>

<template>
    <v-container class="mt-5">
        <v-btn prepend-icon="mdi-arrow-left-circle" variant="plain" id="back-button" class="mb-5" onclick="history.back()">
            Back
        </v-btn>
        <v-card-title class="text-h5 font-weight-bold">
            <v-btn variant="plain" id='favButton' @click="updateFav()" :icon="icon" :color="iconColour"></v-btn>
            {{ roleInfo.name }}
        </v-card-title>

				<v-dialog v-model="isSuccessActive" width="450">
					<v-card  height="160" id="dialog">
						<v-card-title class="d-flex justify-center mt-7 font-weight-bold">
							{{ message }}
						</v-card-title>
						<v-card-text class="d-flex justify-center">
							<v-btn
							@click="closeDialog()"
							class="d-flex justify-center closeDialogBtn elevation-4">Close</v-btn>
						</v-card-text>
					</v-card>
				</v-dialog>

        <v-divider></v-divider>
        <v-container class="text-h6">
            {{ roleInfo.desc }}
        </v-container>
        <v-container>
            <v-row style="max-height: 370px;">
                <v-col cols="8">
                    <v-card id="monthly-wages" class="elevation-6 rounded-lg px-10 py-5" >
                        <v-card-title class="text-h6 font-weight-medium ps-1">Wages (Monthly)</v-card-title>
                        <apexchart height="120%" :options="barChart" :series="series"></apexchart>
										</v-card>
                </v-col>
                <v-col cols="4">
                    <v-card id="completion" class="elevation-3 rounded-lg pt-2">
                        <v-card-title class="text-h6 font-weight-medium ps-6">
                        Completed Skills
                        <span>
                            <v-icon class="icon-smaller">
                                mdi-information-outline
                            </v-icon>
                        <v-tooltip activator="parent" location="top">The number of skills that you have out of the total number of skills required <br> for the role, which are measured from the courses you have completed.</v-tooltip>
                        </span>
                        </v-card-title>
                            <div class="text-center mt-1">
                                    <apexchart height="130%" :options="roleProgressionChart" :series="[roleProgressionLevel]" ></apexchart>
                            </div>
                    </v-card>

                    <v-card id="buzzwords" class="elevation-3 rounded-lg pt-2 mt-5" >
                        <v-card-title class="text-h6 font-weight-medium ps-6">Buzzwords</v-card-title>
												<v-virtual-scroll :items="roleKeywordsInfo" class="ps-11" height="80">
														<template v-slot:default="{item}">
																<li class="font-weight-bold" :key="item.id">{{ item.name }}</li>
														</template>
												</v-virtual-scroll>
                        <!-- <ul class="ps-11" v-for="buzzword in roleKeywordsInfo" :key="buzzword.id">
                            <li class="font-weight-bold">{{buzzword.name}}</li>
                        </ul> -->
                    </v-card>
                </v-col>
            </v-row>

            <v-row class="pt-2">
                <v-col id="hard-skills">
                    <div class="text-h6 font-weight-medium mb-4 ms-5">
                        Skills
                        <span>
                            <v-icon class="icon-smaller">
                                mdi-information-outline
                            </v-icon>
                        <v-tooltip activator="parent" location="right">
                            Skills are specific abilities, capabilities and skill sets that an individual <br> can possess and demonstrate in a measured way.</v-tooltip>
                        </span>
                        <span class="ms-16"></span><span class="ms-16"></span><span class="ms-16"></span><span class="ms-16"></span>
                        <span class="ms-16"></span><span class="ms-16"></span><span class="ms-16"></span><span class="ms-16"></span>
                        <span class="ms-6"></span>

                        <v-btn @click="openCourseRecommender" class="text-right recommendBtn">Recommended Courses</v-btn>

                        <v-dialog v-model="courseRecommenderDialog" max-width="620">
                        <v-card class="pa-1">
                            <v-card-title>
                                <v-row class="ms-3 mt-1">
                                    <v-col cols="8" class="font-weight-bold">
                                        Recommended Courses
                                        <v-icon class="icon-smaller">
                                            mdi-information-outline
                                        </v-icon>
                                        <v-tooltip activator="parent" location="top">
                                            This is the recommended list of courses that will allow
                                            <br> you to clear all the skills required for {{ roleInfo.name }}.
                                        </v-tooltip>
                                    </v-col>
                                    <v-col cols class="d-flex justify-end">
                                        <v-btn icon="mdi-close" variant="plain" density="comfortable" class="closeBtn" @click="closeCourseRecommender">
                                        </v-btn>
                                    </v-col>
                                </v-row>
                            <v-spacer></v-spacer>
                            </v-card-title>

                            <v-card-text class="scrollable-card">
                            <v-list>
                                <v-list-item v-for="(name, id) in courseDict" :key="id">
                                <v-list-item-title>{{id}} {{ name }}</v-list-item-title>
                                </v-list-item>
                            </v-list>
                            </v-card-text>
                        </v-card>
                        </v-dialog>

                        <v-btn @click="openAvailableCourse" class="text-right ms-3 comprehensiveBtn">Comprehensive List</v-btn>
                        <v-dialog v-model="availableCourseDialog" max-width="620">
                        <v-card class="pa-1">
                            <v-card-title>
                                <v-row class="ms-3 mt-1">
                                    <v-col cols="8" class="font-weight-bold mt-1">
                                        Comprehensive Course List
                                        <v-icon class="icon-smaller">
                                            mdi-information-outline
                                        </v-icon>
                                        <v-tooltip activator="parent" location="top">
                                            This is a comprehensive list of all the courses that allow you to clear all the skills required
                                            for <br> {{ roleInfo.name }} and are arranged with the course teaching the most unacquired skills first.
                                        </v-tooltip>
                                    </v-col>
                                    <v-col cols class="d-flex justify-end">
                                        <v-btn icon="mdi-close" variant="plain" density="comfortable" class="closeBtn" @click="closeAvailableCourse">
                                        </v-btn>
                                    </v-col>
                                </v-row>
                            <v-spacer></v-spacer>
                            </v-card-title>

                            <v-card-text class="scrollable-card">
                            <v-list>
                                <v-list-item v-for="(name, id) in availableCourseDict" :key="id">
                                <v-list-item-title>{{id}} {{ name }}</v-list-item-title>
                                </v-list-item>
                            </v-list>
                            </v-card-text>
                        </v-card>
                        </v-dialog>
                    </div>
                    <v-expansion-panels>
                        <v-expansion-panel v-for="skill in roleSkillsInfo"
                                            :key="skill.id">
                            <v-expansion-panel-title disable-icon-rotate  >
                                {{ skill.name }}
                                <template v-slot:actions>
                                    <v-icon v-if='userRoleSkills.includes(skill.id)' icon="mdi-check-circle" color="#106B13">  <!--color of icon will depend on if they are completed ornot-->
                                    </v-icon>
                                    <v-icon v-else icon="mdi-alert-circle" color="#C31F1F">  <!--color of icon will depend on if they are completed ornot-->
                                    </v-icon>
                                </template>
                                </v-expansion-panel-title>
                                <v-expansion-panel-text class="description">
                                    <v-table fixed-header height="220px">
                                        <thead>
                                            <tr>
                                                <th class="text-left" style="font-weight:bold">
                                                    Course Name
                                                </th>
                                                <th class="text-left" style="font-weight:bold">
                                                    Course Code
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr v-for="course in skill.courses" :key="course.id">
                                                <td>{{ course.name }}</td>
                                                <td>{{ course.id }}</td>
                                            </tr>
                                        </tbody>
                                    </v-table>
                                </v-expansion-panel-text>
                        </v-expansion-panel>
                    </v-expansion-panels>
                </v-col>
            </v-row>
        </v-container>
    </v-container>

</template>


<style scoped>

    .icon-smaller {
    font-size: 18px; /* Adjust the font-size as needed to make the icon smaller */
    padding-bottom: 15px;
    color: #000000;
    }

    #back-button {
        background: #151C55;
        color: #f4f4f4;
    }

    #monthly-wages {
        border-width: 2px;
        border-color: rgb(132, 112, 76, 0.6);
    }

    #completion {
        border-width: 2px;
        border-color: rgb(21, 28, 85, 0.6);
				max-height: 40%;
				margin: auto;
    }

    #buzzwords {
        border-width: 2px;
        min-height: 145px;
        border-color: rgb(255, 54, 54, 0.5);
        color: rgb(255, 54, 54);
    }

    .description{
        font-size: 15px;
    }

	#favButton {
        width: 0px;
        height: 0px;
        margin-bottom: 28px;
        margin-right: 12px;
    }

    .scrollable-card {
    max-height: 500px; /* Set the maximum height as needed */
    overflow-y: auto;
    }

    .recommendBtn{
        background-color: RGB(132, 112, 76, 0.8);
        color: white;
    }

    .comprehensiveBtn{
        background-color: RGB(21, 28, 85, 0.8);
        color: white;
    }

    .closeBtn{
        color: RGB(195, 31, 31, 0.8);
    }

    .closeDialogBtn{
        border-width: 2px;
        border-color: grey;
        color: grey;
    }
</style>
