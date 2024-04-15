<script>
export default {
	data: () => ({
	}),
	mounted() {
	},
}
</script>

<template>
	<v-container>
		<v-card-title>Test</v-card-title>
		<v-divider></v-divider>
		<v-card-text>Role ID: {{ this.$route.params.id }}</v-card-text>
	</v-container>
</template>

<style scoped></style>
