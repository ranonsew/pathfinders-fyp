<script setup>
import {ref, computed} from "vue"
import {useRouter} from "vue-router"
import {useDropZone, useFileDialog, useAsyncState} from "@vueuse/core"
import {useUserStore} from "../stores/user"
import {backend_url} from "../addresses"


const store = useUserStore()
const router = useRouter()

// file related reactive data thingy
const file = ref()
const fileDisplay = computed(() => {
	if (!file.value) return ""

	const name = file.value.name
	const size = file.value.size
	const len = size.toString().length

	// data size suffix changing (not sure if there is a better way or not hehe)
	if (len >= 4 && len <= 6) return `${name} (${(size / 1000).toFixed(3)} KB)`
	if (len >= 7 && len <= 9) return `${name} (${(size / 1000000).toFixed(3)} MB)`
	return `${name} (${size} B)`
})
const uploadError = ref(false)

// file drop zone related
const fileDropZone = ref() // drop zone template reference
const {isOverDropZone, files: dropZoneFiles} = useDropZone(fileDropZone, function(files) {
	uploadError.value = false
	if (!files) return
	if (files[0].type !== "application/pdf") {
		uploadError.value = true
		return
	}
	file.value = files[0] // Array --> get first index (one file only)
})

// file window thingy related
const {open, reset, onChange} = useFileDialog({accept: ".pdf", multiple: false}) // accepting only pdf files
onChange(function(files) {
	uploadError.value = false
	if (!files) return
	const inputFile = Array.from(files)[0] // FileList --> Array --> get first index (one file only)
	if (inputFile.type !== "application/pdf") {
		uploadError.value = true
		return
	}
	file.value = inputFile
})

// ensure things are reset properly
function clear() {
	reset()
	dropZoneFiles.value = null
	file.value = null
	uploadError.value = false
}

// isLoading sets the loading state; execute starts the fetching process
const {isLoading, execute} = useAsyncState(async () => {
	store.courses = [] // empty for the upload
	const formData = new FormData()
	formData.append("pdfFile", file.value)
	try {
		const res = await fetch(`${backend_url}/user/process_transcript`, {
			method: "POST",
			mode: "cors",
			body: formData,
		})
		console.log(res)
		const data = await res.json()
		console.log(data)
		if (data.code !== 201) throw new Error("PDF processing error.")
		for (let code in data.content) {
			console.log(code, data.content[code])
			if (!store.courses.some((c) => c.code === code)) {
				// placeholder terms (current processing does not include terms)
				store.courses.push({term: "202X-2Y Term Z", code, title: data.content[code]})
			}
		}
		router.push("/confirm-courses") // route to "confirm-courses" page
		return
	} catch (err) {
		uploadError.value = true
		console.error(err)
		return
	}
}, {}, {immediate: false, resetOnExecute: false})
</script>

<template>
	<v-container class="h-100">
		<v-btn prepend-icon="mdi-arrow-left-circle" variant="tonal" color="primary" @click="this.$router.back()">Back</v-btn>
		<v-container fluid class="d-flex justify-center mt-5 text-center">
			<v-card class="d-flex flex-column" :class="{'bg-white': isOverDropZone}" ref="fileDropZone" width="700" min-height="180" rounded="lg" variant="outlined">
				<v-card-title>Upload Transcript</v-card-title>
				<v-card-subtitle>
					<v-icon icon="mdi-folder-arrow-down" />
					Drop files here or choose from file directory
				</v-card-subtitle>

				<v-card-actions class="d-flex justify-center">
					<v-btn prepend-icon="mdi-folder-arrow-up" variant="tonal" color="info" @click="open()">Upload</v-btn>
					<v-btn prepend-icon="mdi-cloud-upload" variant="tonal" color="quarternary" @click="execute()" :disabled="!file" :loading="isLoading">Generate</v-btn>
					<v-btn prepend-icon="mdi-backspace" variant="tonal" color="warning" @click="clear()" :disabled="!file">Reset</v-btn>

					<!-- help modal thing -->
					<v-dialog	width="auto" max-width="800">
						<template v-slot:activator="{props}">
							<v-btn v-bind="props" variant="tonal" color="secondary" prepend-icon="mdi-help-circle">How to Obtain</v-btn>
						</template>
						<template v-slot:default="{isActive}">
							<v-card class="pa-3">
								<v-card-title>How to obtain Transcript</v-card-title>
								<v-card-text>
									<ol style="padding-left: 1rem;">
										<li>Navigate to <a href="https://smu.sharepoint.com/sites/oasis/" target="_blank">this</a> page and log in.</li>
										<li>Look for "Unofficial Transcript" under "All Apps"</li>
										<li>Click on the "Run Report" button and wait for a few minutes, after which it will present you with your PDF Transcript.</li>
										<li>Download the PDF, and you can now upload it generate the courses you have!</li>
									</ol>
								</v-card-text>
								<v-card-actions class="d-flex justify-end me-3">
									<v-btn color="primary" class="px-8" variant="tonal" @click="isActive.value = false">Close</v-btn>
								</v-card-actions>
							</v-card>
						</template>
					</v-dialog>
				</v-card-actions>

				<v-card-item v-if="file" color="primary" rounded="shaped" prepend-icon="mdi-file-document">
					<v-card-text>{{ fileDisplay }}</v-card-text>
				</v-card-item>

				<!-- Front end thing to tell users that they cannot input something that isn't a PDF -->
				<v-alert v-model="uploadError" closable>
					<v-alert-title>PDF Processing Error</v-alert-title>
					<v-card-text>An error occurred while processing the PDF.</v-card-text>
				</v-alert>
			</v-card>
		</v-container>
	</v-container>
</template>

<style scoped></style>
