<script setup></script>

<template>
	<v-container class="h-100">
		<v-card-title class="text-h5 font-weight-bold">Update My Courses</v-card-title>
		<v-divider class="mb-16"></v-divider>
		<v-container class="d-flex justify-center text-center pt-3">
			<v-card class="d-flex flex-column pa-5" variant="outlined" color="secondary" min-width="500" min-height="150" rounded="lg">
				<v-card-title class="text-black text-h6 text-start ms-3">Upload Transcript</v-card-title>
				<v-card-item id="transcript-setup-main">
					<v-btn variant="tonal" class="bg-primary text-white btn" @click="this.$router.push('/upload-transcript')">
						Browse Files
					</v-btn>
					<div class="pa-5 rounded-circle d-inline-block text-body-2 text-black font-weight-medium">OR</div>
					<v-btn variant="tonal" class="bg-secondary text-white btn" @click="this.$router.push('/manual-setup')">
						Create Manually
					</v-btn>
				</v-card-item>
				<v-card-subtitle class="text-black ma-2 text-left">
					<b>NOTE: The transcript will be used to generate all the courses you have taken, <br> which will populate your skills bank in competency summary. The results <br> in your transcript will NOT be stored.</b>
				</v-card-subtitle>
			</v-card>
		</v-container>
	</v-container>
</template>

<style scoped>
.btn{
	width: 180px;
}
</style>
