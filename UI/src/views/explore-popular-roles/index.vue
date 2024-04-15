<script>
import { backend_url } from "../../addresses";
import axios from 'axios';

export default {
  data() {
    return {
			keyword_search: "",
			loading: false,
			filter_by_specialization: ['E-commerce', 'Technology', 'Consumer Products', 'Engineering'],
			specialization_selected: "",
			tickLabels: {0: "$3000", 1: "", 2: "", 3: "", 4: "", 5: "$8000+"},
			tickLabel_selected: 0,
			filter_by: ["'Role', 'Specialisation', 'Tech Stack','Company', 'Industry', 'Salary', 'Skills'"],
			roles: [
				{
					id: 1,
					name: "Data Engineer",
					description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla euismod, dui id facilisis mattis, neque felis bibendum velit, eu mollis nisi mi et nibh. Lorem ipsum dolor sit amet, consectetur",
					view_info: "#",
					career_path: "#2",
					percentage_completed: '60',
					avg_salary: '7,000',
				},
				{
					id: 2,
					name: "Senior Data Engineer",
					description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla euismod, dui id facilisis mattis, neque felis bibendum velit, eu mollis nisi mi et nibh. Lorem ipsum dolor sit amet, consectetur",
					view_info: "#",
					career_path: "#2",
					percentage_completed: '60',
					avg_salary: '7,000',
				},
			],
    };
  },
	computed: {
		filteredRoles() {
			return this.roles.filter((r) => {
				// filter matching title
				const titleMatch = r.name.toLowerCase().indexOf(this.keyword_search.toLowerCase()) !== -1

				// filter matching the salary
				// const salaryMatch = parseInt(r.avg_salary.slice(1)) >= parseInt(this.tickLabels[this.tickLabel_selected].slice(1))

				// filter matching the specialization
				// const specializationMatch = false

				// currently only returning the filter matching title
				return titleMatch
			})
		}
	},
	created() {
    const requestData = {
      student_id: 1
    };

    axios.post(`${backend_url}/user/get_all_roles_progression`, requestData)
      .then(response => {
        // this.accInfo = response.data.content;
        this.roles = response.data.data.all_roles_result

        console.log("this.roles", this.roles)

      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });

	}
}
</script>

<template>
  <v-container>
		<v-container id='explore_popular_title'>
			<h1 class='font-weight-bold'>Popular Job Roles</h1>
			<v-divider />
		</v-container>
		<v-container fluid>
			<v-row>
				<!--
				<v-col cols='3'>
					<v-data-table>
						<v-select label="Filter by" items="filter_by" multiple></v-select>
					</v-data-table>
				</v-col>
				-->
				<v-container id='search'>
					<v-form>
						<v-container fluid>
							<v-row>
								<v-col>
									<span class="text-h6 font-weight-bold">Role Search</span>
								</v-col>
							</v-row>

							<v-row>
								<v-col sm="3">
									<v-text-field v-model="keyword_search" label="Keyword" variant="underlined"></v-text-field>
								</v-col>

								<v-col sm="3">
									<v-select
										v-model="specialization_selected"
										label="Specialization"
										:items="filter_by_specialization"
										variant="underlined">
									</v-select>
								</v-col>

								<!-- <v-col sm="2">
									<v-select
										label="Faculty"
										:items="filter_by_faculty"
										variant="underlined">
									</v-select>
								</v-col> -->

								<v-col sm="4" class="ps-5">
									<div class="text-caption font-weight-medium">Salary</div>
									<v-slider
										v-model="tickLabel_selected"
										:ticks="tickLabels"
										:max="5"
										step="1"
										show-ticks="always"
										tick-size="4"
										class="text-caption"
										color="#24754d"
										track-color="black">
									</v-slider>
								</v-col>

								<v-col class="text-center" sm="2">
									<v-btn
										:loading="loading"
										width = "150px"
										type="submit"
										class="mt-2 ms-2"
										text="Submit"
										color='primary'
										to="/searched-roles">
									</v-btn>
								</v-col>
							</v-row>
						</v-container>
					</v-form>
				</v-container>

				<v-col>
					<v-card v-for="role in filteredRoles" :key="role">
						<v-row>
							<v-col cols='8'>
								<v-card-title class="ma-2 rounded-lg">
									<v-row>
										<v-col id='role_title'>{{role.name}}</v-col>

										<v-col>
											<v-btn
											:to="`/explore-popular-roles/${role.id}`"
											id='view_info_btn'>
												View Info
											</v-btn>
										</v-col>

										<v-col>
											<v-btn
											:href="role.career_path"
											id='career_path_btn'>
												Career Path
											</v-btn>
										</v-col>
									</v-row>
								</v-card-title>

								<v-card-text>{{role.desc}}</v-card-text>
							</v-col>

							<v-col cols='4' id='test'>
								<v-card-text id='percent_completed'>
									{{role.percentage_completed}}% COMPLETED
								</v-card-text>
								<v-card-text id='average_salary'>
									$7,000 AVERAGE SALARY
								</v-card-text>
							</v-col>
						</v-row>
					</v-card>
				</v-col>
			</v-row>
		</v-container>
	</v-container>
</template>

<style scoped>
.v-card {
	margin: 10px 10px 10px 10px;
	background: rgba(234, 234, 234, 0.3);
	box-shadow: 0px 4px 14px 1px rgba(0, 0, 0, 0.25);
	border-radius: 10px;
}

.v-btn{
	border-radius: 20px;
	font-weight: bold;
	color:white;
}


#role_title{
	font-weight: 400;
	font-size: 20px;
}

#career_path_btn{
	background-color: rgb(132, 112, 76);
	max-width: 870px;
}

#view_info_btn{
	background-color: rgb(21, 28, 85);
	max-width: 721px;
}

#test{
	border-left: 2px solid #D7D7D7;
}

#search{
  margin: 20px 10px 20px 10px;
  background: rgb(238, 225, 200, 0.8);
  border-radius: 10px;
  position: auto;
  font-weight: bold;
 }

</style>
