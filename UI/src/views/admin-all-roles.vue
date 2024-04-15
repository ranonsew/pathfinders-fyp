<script>
import axios from 'axios'; // Import Axios library
import {useUserStore} from '@/stores/user';
import {mapStores} from "pinia"
import {backend_url} from "../addresses"

export default {
	data() {
    return {
		roleList: [],
		skillList:[],
		searchQuery: '',
		addDialog: false,
		editDialog:false,
		addRoleID:"",
		addRoleName:"",
		addRoleDescription:"",
		addRoleExperience:null,
		addSkillList:[],
		editRoleID:"",
		editRoleName:"",
		editRoleDescription:"",
		editRoleExperience:null,
		editSkillList:[],
		editKeywordList:[],
		initialSkillList:[],
		initialKeywordList:[],
		keywordList:[]
    };
	},
	created() {
		this.getRole();
		this.getSkill();
		this.getKeyword();
	},
	computed: {
		...mapStores(useUserStore), // for pinia in the "export default" way -- (doesn't have vscode autocomplete, but does exist)
    filteredRoles() {
			return this.roleList.filter(role =>
				role.name.toLowerCase().includes(this.searchQuery.toLowerCase())
			);
    }
	},
	methods: {
		performSearch() {},
		deleteRole(k){
			axios.delete(`${backend_url}/role/delete/${k}`)
			.then(response => {
				if (response.status === 201) {
					this.getRole()
				}
			})
			.catch(error => {
				console.error('Error deleting data:', error)
			})
		},
		getSkill() {
			axios.get(`${backend_url}/skill/get_all`)
			.then(response => {
				this.skillList = response.data.content
			})
			.catch(error => {
				console.error('Error fetching data:', error)
			});
		},
		getRole() {
			axios.get(`${backend_url}/role/get_all`)
			.then(response => {
				this.roleList = response.data.content
			})
			.catch(error => {
				console.error('Error fetching data:', error)
			});
		},
		getKeyword() {
			axios.get(`${backend_url}/keyword/get_all`)
			.then(response => {
				this.keywordList = response.data.content
			})
			.catch(error => {
				console.error('Error fetching data:', error)
			});
		},
		addRole() {
			const requestData = {
				role_id:this.addRoleID,
				role_name:this.addRoleName,
				role_desc:this.addRoleDescription,
				exp_level:this.addRoleExperience,
			};
			axios.post(`${backend_url}/role/create`,requestData)
			.then(response => {
				console.log(response.data);
				this.getRole();
				this.addDialog = false;

				const requestData2 = {role_id:this.addRoleID,
									skill_id:this.addSkillList}
			axios.post(`${backend_url}/role/skills_mapped/create`,requestData2)
			.then(response => {
				console.log(response.data);
				this.getRole();
				this.addDialog = false;
			})
			.catch(error => {
				console.error('Error fetching data:', error)
				console.log(error)
			});
			})
			.catch(error => {
				console.error('Error fetching data:', error)
			});
		},
		openEditDialog(curRole) {
			this.editRoleID = curRole.id;
			this.editRoleName = curRole.name;
			this.editRoleDescription = curRole.desc;
			this.editRoleExperience = curRole.exp_level.toString();

			axios.get(`${backend_url}/role/skills_mapped/get/${curRole.id}`)
			.then(response => {
				this.editSkillList = response.data.content
				this.initialSkillList = response.data.content
			})
			.catch(error => {
				console.error('Error fetching data:', error)
			});

			axios.get(`${backend_url}/role/keyws_mapped/get/${curRole.id}`)
			.then(response => {
				this.editKeywordList = response.data.content
				this.initialKeywordList = response.data.content
			})
			.catch(error => {
				console.error('Error fetching data:', error)
			});

			this.editDialog = true;
		},
		editRole() {
			const requestData = {
				role_id:this.editRoleID,
				role_name:this.editRoleName,
				role_desc:this.editRoleDescription,
				exp_level:this.editRoleExperience,
			};
			axios.post(`${backend_url}/role/update`,requestData)
			.then(response => {
				console.log(response.data);
			})
			.catch(error => {
				console.error('Error fetching data:', error)
			});

			const addedSkill = this.editSkillList.filter(skill => !this.initialSkillList.some(initialSkill => initialSkill.id === skill.id));
			const removedSkill = this.initialSkillList
								.filter(initialSkill => !this.editSkillList.some(editSkill => editSkill.id === initialSkill.id))
								.map(skill => skill.id);

			const addSkillData = {role_id:this.editRoleID,
									skill_id:addedSkill}
			axios.post(`${backend_url}/role/skills_mapped/create`,addSkillData)
			.then(response => {
				console.log(response.data);
			})
			.catch(error => {
				console.error('Error fetching data:', error)
			});

			const deleteSkillData = {role_id:this.editRoleID,
									skill_id:removedSkill}
			axios.post(`${backend_url}/role/skills_mapped/delete`,deleteSkillData)
			.then(response => {
				console.log(response.data);
			})
			.catch(error => {
				console.error('Error fetching data:', error)
			});

			const addedKeyword = this.editKeywordList.filter(keyword => !this.initialKeywordList.some(initialKeyword => initialKeyword.id === keyword.id));
			const removedKeyword = this.initialKeywordList
								.filter(initialKeyword => !this.editKeywordList.some(editKeyword => editKeyword.id === initialKeyword.id))
								.map(keyword => keyword.id);

			const addKeywordData = {role_id:this.editRoleID,
									keyw_id:addedKeyword}
			axios.post(`${backend_url}/role/keyws_mapped/create`,addKeywordData)
			.then(response => {
				console.log(response.data);
			})
			.catch(error => {
				console.error('Error fetching data:', error)
			});

			const deleteKeywordData = {role_id:this.editRoleID,
									keyw_id:removedKeyword}
			axios.post(`${backend_url}/role/keyws_mapped/delete`,deleteKeywordData)
			.then(response => {
				console.log(response.data);
				this.getRole();
			})
			.catch(error => {
				console.error('Error fetching data:', error)
			});
			this.editDialog = false;
		},
	},
}
</script>

<template>
	<v-container class="mt-5">
		<v-card-title class="text-h5 font-weight-bold">All Roles</v-card-title>
		<v-divider></v-divider>
		<v-container class="mt-5">
			<v-row>
				<v-col cols class="ms-11 me-5">
					<v-text-field v-model="searchQuery" label="Search Role by name"
					outlined clearable @input="performSearch"></v-text-field>
				</v-col>
				<v-col cols="3" class="mt-2 d-flex justify-center">
					<div class="text-center">
					<v-btn class="elevation-0" id="new_roles">
						+ Add New Roles
						<v-dialog
							v-model="addDialog"
							activator="parent"
							>
							<v-card>
								<v-card-text>
									<v-row>
										<v-col>
											<v-text-field v-model="addRoleName" label="Role Name" outlined></v-text-field>
										</v-col>
									</v-row>
									<v-textarea v-model="addRoleDescription" label="Role Description" outlined ></v-textarea>
									Role Experience
									<v-radio-group v-model="addRoleExperience" inline>
										<v-radio label="Experience Level 1" value="1"></v-radio>
										<v-radio label="Experience Level 2" value="2"></v-radio>
										<v-radio label="Experience Level 3" value="3"></v-radio>
										<v-radio label="Experience Level 4" value="4"></v-radio>
									</v-radio-group>
									<v-autocomplete
									v-model="addSkillList"
									:items="skillList"
									item-title="name"
									item-value="id"
									label="Select skills"
									clearable multiple></v-autocomplete>
								</v-card-text>
								<v-card-actions>
									<v-row>
										<v-col>
											<v-btn block @click="addRole()">Add Role</v-btn>
										</v-col>
										<v-col>
											<v-btn color="red" block @click="addDialog = false">Close</v-btn>
										</v-col>
									</v-row>
								</v-card-actions>
							</v-card>
						</v-dialog>
					</v-btn>
				</div>
				</v-col>
			</v-row>
		</v-container>

		<div>
			<v-dialog
				v-model="editDialog"
				activator="parent"
				>
				<v-card>
					<v-card-text>
						<v-row>
							<v-col>
								<v-text-field v-model="editRoleName" label="Role Name" outlined></v-text-field>
							</v-col>
						</v-row>
						<v-textarea v-model="editRoleDescription" label="Role Description" outlined></v-textarea>
						Role Experience
						<v-radio-group v-model="editRoleExperience" inline>
							<v-radio label="Experience Level 1" value="1"></v-radio>
							<v-radio label="Experience Level 2" value="2"></v-radio>
							<v-radio label="Experience Level 3" value="3"></v-radio>
							<v-radio label="Experience Level 4" value="4"></v-radio>
						</v-radio-group>
						<v-autocomplete
									v-model="editSkillList"
									:items="skillList"
									item-title="name"
									item-value="id"
									label="Select skills"
									clearable multiple></v-autocomplete>
						<v-autocomplete
									v-model="editKeywordList"
									:items="keywordList"
									item-title="name"
									item-value="id"
									label="Select keywords"
									clearable multiple></v-autocomplete>
					</v-card-text>
					<v-card-actions>
						<v-row>
							<v-col>
								<v-btn block @click="editRole()">Edit Role</v-btn>
							</v-col>
							<v-col>
								<v-btn color="red" block @click="editDialog = false">Close</v-btn>
							</v-col>
						</v-row>
				</v-card-actions>
				</v-card>
			</v-dialog>
		</div>


		<!--if search bar empty-->
		<div v-if="searchQuery===''">
		<v-list class="bg-transparent">
            <v-list-item
                v-for="role in roleList"
                :key="role.id">
				<v-card class="roleCardClass ms-4">
					<v-card-title>{{ role.name }}</v-card-title>
					<v-card-text>{{ role.desc }}</v-card-text>
					<v-card-actions class="ms-2">
						<v-btn class="editBtn" @click="openEditDialog(role)">Edit Role</v-btn>
						<v-dialog width="450">
							<template v-slot:activator="{ props }">
								<v-btn v-bind="props" text="Delete Role" class="deleteBtn"></v-btn>
							</template>

							<template v-slot:default="{ isActive }">
								<v-card height="160" id="dialog">
									<v-card-title class="d-flex justify-center mt-7 font-weight-bold">
										Confirm Deletion of {{ role.name }}?
									</v-card-title>

									<v-card-text class="d-flex justify-center">
										<v-btn
										text="Cancel"
										@click="isActive.value = false"
										class="d-flex justify-center me-7 dialogCancelBtn dialogBtn elevation-0"
										></v-btn>

										<v-btn
										text="Delete"
										@click="deleteRole(role.id)"
										class="d-flex justify-center dialogDeleteBtn dialogBtn elevation-4"
										></v-btn>
									</v-card-text>
								</v-card>
							</template>
						</v-dialog>
					</v-card-actions>
				</v-card>
            </v-list-item>
        </v-list>
		</div>

		<!--if search bar has fields-->
		<div v-else>
		<v-list class="bg-transparent">
            <v-list-item
                v-for="role in filteredRoles"
                :key="role.id">
				<v-card class="roleCardClass ms-4">
					<v-card-title>{{ role.name }}</v-card-title>
					<v-card-text>{{ role.desc }}</v-card-text>
					<v-card-actions class="ms-2">
						<v-btn class="editBtn" @click="openEditDialog(role)">Edit Role</v-btn>
						<v-dialog width="450">
							<template v-slot:activator="{ props }">
								<v-btn v-bind="props" text="Delete Role" class="deleteBtn"></v-btn>
							</template>

							<template v-slot:default="{ isActive }">
								<v-card height="170" id="dialog">
									<v-card-title class="d-flex justify-center mt-7 font-weight-bold">
										Confirm Deletion of {{ role.name }}?
									</v-card-title>

									<v-card-text class="d-flex justify-center">
										<v-btn
										text="Cancel"
										@click="isActive.value = false"
										class="d-flex justify-center me-7 dialogCancelBtn dialogBtn elevation-0"
										></v-btn>

										<v-btn
										text="Delete"
										@click="deleteRole(role.id)"
										class="d-flex justify-center dialogDeleteBtn dialogBtn elevation-4"
										></v-btn>
									</v-card-text>
								</v-card>
							</template>
						</v-dialog>
					</v-card-actions>
				</v-card>
            </v-list-item>
        </v-list>
		</div>
	</v-container>
</template>

<style scoped>
	#new_roles {
		background-color: #7F6B4A;
		color: #F9F9F9;
	}

	.salary{
		color: #7F6B4A;
	}

	.roleCardClass {
		background-color: RGB(234, 234, 234, 0.95);
		padding: 15px;
	}

	.deleteBtn{
		background-color: RGB(195, 31, 31, 0.8);
		color: #FFFFFF;
		border-radius:5px;
		width: 130px;
	}

	.editBtn{
		background-color: RGB(21, 28, 85, 0.95);
		color: #FFFFFF;
		border-radius:5px;
		width: 130px;
	}

	#dialog {
		border-radius: 10px;
	}

	.dialogBtn{
		border-radius:5px;
		width: 160px;
	}

	.dialogDeleteBtn{
		background-color: RGB(195, 31, 31);
		color: #FFFFFF;
	}

	.dialogCancelBtn{
		color: grey;
		border-color: grey;
		border-width: 2px;
	}
</style>

<!-- Need this here for the Router to detect that this is an Admin Only file -->
<route lang="yaml">
meta:
  requiresAdmin: true
</route>
