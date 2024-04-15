<script>
import axios from 'axios'; // Import Axios library
import {useUserStore} from '../stores/user'
import {useFileDialog} from "@vueuse/core"
import {ref} from "vue"
import {backend_url} from "../addresses"
import default_pic from "../assets/default_pic.png"
export default {
  data() {
    return {
			profileInfo: [],
			password:"",
			skillsInfo: [],
			firstThreeSkills: [],
			remainingSkills: [],
			coursesInfo: [],
			firstThreeCourses: [],
			remainingCourses: [],
			expandSkills: false,
			expandCourses: false,
			starredRoles: [],
			completedRoles: [],
			form_schools: ['SCIS', 'SOB', 'SOL', 'SOA', 'SOE', 'SOSS', 'CIS'],
			skills_expand: false,
			courses_expand: false,
			time: 0,
			profileImage: "", // profile picture image link to s3 bucket (image name should be randomized)
			// remove when redirects not needed
			change_password: "#",
			update_courses: "#2",
			old_password: '',
			new_password: '',
			message: "",
			updateSuccess: "",
			updateFailed: ""
    };
  },
  methods: {
    update_password(){

			console.log('old password',this.old_password)
			console.log('new password',this.new_password)
			console.log('cfm password',this.profileInfo.password)

			this.message = ''

			if (!this.old_password || !this.new_password || !this.profileInfo.password) {
				this.message = 'Please fill in all password fields.';
				return;
			} else if (this.new_password !== this.profileInfo.password) {
				this.message = 'New passwords do not match.';
				return;
			} else if (this.new_password === this.old_password) {
				this.message = 'New password must be different from the old password.';
				return;
			}
			else {
				// Perform your password update logic

				const userStore = useUserStore()
				console.log(userStore.userId)
				const password_update_details = {
					'user_id': userStore.userId,
					'user_password': this.profileInfo.password
				}
				axios.post(`${backend_url}/user/update_password`,password_update_details)
				.then(response => {
					console.log(response);
					//alert("Password Changed!");
					this.updateSuccess = 'Password changed successfully!'
					this.statusDialog = true
				})
				.catch(error => {
					console.error('Error fetching data:', error);
					//alert("Error changing password!")
					this.updateFailed = 'Error changing password!'
					this.statusDialog = true
				});

					// Clear the message on success
					this.message = '';
				}

    },
	updateParticulars(){

		console.log('ID', this.profileInfo.id)
		console.log('Full Name', this.profileInfo.full_name)
		console.log('School', this.profileInfo.faculty)
		console.log('User Email', this.profileInfo.user_email)

		this.updateFailed = ''

		if (!this.profileInfo.id || !this.profileInfo.full_name || !this.profileInfo.faculty || !this.profileInfo.user_email) {
			this.updateFailed = 'Please fill in all password fields.';
			this.statusDialog = true
			return;
		} else {
			const particulars_update_details = {
				'user_id': this.profileInfo.id,
				'user_faculty': this.profileInfo.faculty,
				'user_email' : this.profileInfo.user_email,
				'user_name': this.profileInfo.full_name
			}
					
			axios.post(`${backend_url}/user/update_particulars`,particulars_update_details)
			.then(response => {
				console.log(response);
				//alert("Password Changed!");
				this.updateSuccess = 'Particulars updated successfully!'
				this.statusDialog = true
			})
			.catch(error => {
				console.error('Error fetching data:', error);
				//alert("Error changing password!")
				this.updateFailed = 'Error updating particulars!'
				this.statusDialog = true
				
			});

		}


	},
  },
	setup() {
		// for profile file uploading
		const passwordDialog = ref(false);
		const statusDialog = ref(false)
		const profileLoading = ref(false)
		const store = useUserStore()
		const {open, onChange} = useFileDialog({accept: "image/*", multiple: false}) // accepting only a single image file
		onChange(async function(files) {
			profileLoading.value = true
			try {
				if (!files) throw new Error("No file input")
				const img_file = Array.from(files)[0]
				if (!img_file.type.includes("image/")) throw new Error("File input is not an image")

				const formData = new FormData()
				formData.append("img_file", img_file)
				formData.append("user_id", store.userId) // if not logged in, for testing can use a random number higher than 0

				// backend for user thingies doesn't seem to be added yet
				const res = await fetch(`${backend_url}/user/upload_profile_image`, { // ${backend_url}/user/upload_profile_image
					method: "POST",
					mode: "cors",
					body: formData,
				})
				const data = await res.json()
				console.log(data)
				if (res.status === 201) {
					this.profileImage = data.content
				}
				return
			} catch (err) {
				profileLoading.value = false
				console.error("error:", err) // should probably have some other error thing for users
				return
			}
		})
		return {
			passwordDialog,
			statusDialog,
			openFileDialog: open, // renaming "open" to "openFileDialog"
			profileLoading, // setting loading state
		}
	},
  created() {
	// In your script setup
    const userStore = useUserStore()
    console.log(userStore.userId)

    const requestData = {
      student_id: userStore.userId,
    };

    axios.post(`${backend_url}/user/view_account_information`, requestData)
      .then(response => {
        // this.accInfo = response.data.content;
        this.profileInfo = response.data.data.user_info_result
        this.skillsInfo = response.data.data.user_skills_result.content
        this.firstThreeSkills = this.skillsInfo.slice(0, 3);
        this.remainingSkills = this.skillsInfo.slice(3);
        this.coursesInfo = response.data.data.user_courses_result.content
        this.firstThreeCourses = this.coursesInfo.slice(0, 3);
        this.remainingCourses = this.coursesInfo.slice(3);
				this.profileImage = response.data.data?.profile_image || default_pic // profile picture

        console.log("profileInfo", this.profileInfo)
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });

    axios.post(`${backend_url}/user/get_completed_roles`, requestData) //! note: currently not in
      .then(response => {
        // this.accInfo = response.data.content;
        this.completedRoles = response.data.data.completed_roles

        console.log("completedRoles", this.completedRoles)

        if(this.completedRoles.length == 0){
					this.completedRoles.push({"name":"There are no starred roles at the moment"})
        }
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });

    axios.get(`${backend_url}/user/get_fav_roles/${requestData.student_id}`)
      .then(response => {
        this.starredRoles = response.data.content

        if(this.starredRoles.length == 0){
					this.starredRoles.push({"name":"There are no starred roles at the moment"})
        }

        console.log("starredRoles", this.starredRoles)
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  }
};
</script>

<template>
	<v-container class="mt-5">
		<v-card-title class="text-h5 font-weight-bold">My Profile</v-card-title>
		<v-divider></v-divider>
		<v-container>
			<v-col>
				<v-card align="center" class="elevation-14 rounded-lg py-10" id="my-profile">
					<!-- later change v-img src to :src="this.profileImage" (when done with profile picture thing) -->
					<v-img :src="profileImage" :width="175" aspect-ratio="16/9" class="pb-10 image-container">
						<!-- lower-right upload button camera icon -->
						<v-row class="fill-height" align="end" justify="end">
							<v-col cols="auto">
								<v-btn color="primary" icon="mdi-camera" @click="openFileDialog" :loading="profileLoading"></v-btn>
							</v-col>
						</v-row>
					</v-img>
					<v-form id='profile'>
						<v-text-field
							label='Name'
							placeholder='Name'
							v-model="profileInfo.full_name"
						></v-text-field>

						<v-select
							label="School"
							:items="form_schools"
							variant="underlined"
							v-model="profileInfo.faculty"
							class="ms-4"
						></v-select>

						<v-row>
							<v-col cols='4'>
								<v-text-field
									label='School ID'
									placeholder='School ID'
									v-model="profileInfo.id"
									class="ms-3"
									required
									disabled
								></v-text-field>
							</v-col>

							<v-col cols>
								<v-text-field
									label='Email'
									placeholder='Email'
									v-model='profileInfo.user_email'>
								</v-text-field>
							</v-col>
						</v-row>
						<v-row>
							<v-col>
							<!--
								<v-text-field
									label='Password'
									placeholder='Password'
									v-model="profileInfo.password"
									class="ms-3"
								></v-text-field>
							-->
							</v-col>
						</v-row>
						<v-row>
							<v-col cols="3">
								<v-btn
									class='float-right'
									text='Change Password'
									id='change_password_btn'
									@click="passwordDialog = true"
								></v-btn>
							</v-col>

							<v-col cols="3">
								<v-btn
									class="float-left"
									text='Update Transcript'
									id='update_transcript_btn'
									href="/upload-transcript"
								></v-btn>
							</v-col>

							<v-col cols class="d-flex justify-end">
								<v-btn
									text="Save"
									color='primary'
									class='text-right'
									@click="updateParticulars()"
								></v-btn>
							</v-col>
						</v-row>
					</v-form>
					
					<v-dialog v-model="passwordDialog" width="450">
						<v-card class="password-dialog-card">
							<v-card-text>
								<v-text-field
									label='Old Password'
									placeholder='Old Password'
									v-model="old_password"
									class="ms-3"
									type='password'
								></v-text-field>
								<v-text-field
									label='New Password'
									placeholder='New Password'
									v-model="new_password"
									class="ms-3"
									type='password'
								></v-text-field>
								<v-text-field
									label='Confirm New Password'
									placeholder='Confirm New Password'
									v-model="profileInfo.password"
									class="ms-3"
									type='password'
								></v-text-field>

								<!-- Display messages using v-alert -->
								<v-alert v-if="message" :value="true" type="error" class="mt-4">
								{{ message }}
								</v-alert>
							</v-card-text>


							<v-card-actions>
								<v-btn
									text='Confirm Password'
									id='confirm_password_btn'
									class="ms-7"
									@click="update_password();if (!message) passwordDialog = false"
								></v-btn>
								<!-- Button to close the dialog -->
								<v-btn					
									text='Close'
									id='close_dialog_btn'
									@click="passwordDialog = false"
								></v-btn>
							</v-card-actions>
						</v-card>
					</v-dialog> 

					<v-dialog v-model="statusDialog" max-width="600">
					<v-card>
						<v-card-title>Status Update</v-card-title>
						<v-card-text>
						<!-- Display the status information here -->
						<div v-if="updateSuccess">{{ updateSuccess }}</div>
						<div v-if="updateFailed">{{ updateFailed }}</div>
						</v-card-text>
						<v-card-actions>
						<v-btn @click="statusDialog = false">Close</v-btn>
						</v-card-actions>
					</v-card>
					</v-dialog>


				</v-card>
			</v-col>
		</v-container>
	</v-container>
</template>

<style scoped>
#my-profile {
	border-radius: 3px;
	border-color: #84704C;
}

#skills {
	background-color: #BAA26B;
	color: #FFFFFF;
	border-radius: 5px 5px 0px 0px;
}

#courses{
	/* background-color: #D1B971; */
	background-color: #BAA26B;
	color: #FFFFFF;
	border-radius: 5px 5px 0px 0px;
}

.roles{
	background-color: #F7F3EC;
}

#profile {
	margin: 20px;
}

.image-container {
  position: relative;
  width: 100%;
  /* Set a specific height or use aspect-ratio */
  height: 300px;
}

.image-container .v-image__image {
  object-fit: cover;
}

#update_transcript_btn, #password_update_details{
	/*background-color: #6E6893;*/
	background-color: #151C55;
	opacity: 80%;
	color: #FFFFFF;
}

#change_password_btn{
	background-color: #6E6893;
	color: #FFFFFF;
}

#confirm_password_btn{
	background-color: #106B13;
	color: #FFFFFF;
}

#close_dialog_btn{
	border-width: 2px;
	border-color: grey;
	color: grey;
}


.password-dialog-card {
    border: 2px solid #ffffff; /* White border */
    padding: 15px; /* Adjust padding as needed */
}

/*
#update_transcript_btn{
	background-color: #151C55;
	opacity: 80%;
	color: #FFFFFF;
}
*/

.scrollable {
	height: 200px;
	overflow-y:overlay;
}

::-webkit-scrollbar {
	background:  #D1B971;
	border-radius: 10px;
}

::-webkit-scrollbar-thumb {
	background: #87784a;
	border-radius: 20px;
}

.text-wrap {
	word-wrap: break-word;
}
</style>


