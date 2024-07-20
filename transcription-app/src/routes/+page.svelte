<script>
	import axios from "axios";
	import Hls from "hls.js";

	let m3u8Url = "";
	let taskId = "";
	let transcript = "";
	let videoElement;

	const apiUrl = import.meta.env.VITE_API_URL;
	let targetLanguages = [
		{ code: "en", name: "English", selected: false },
		{ code: "es", name: "Spanish", selected: false },
		{ code: "fr", name: "French", selected: false },
		{ code: "de", name: "German", selected: false },
	];

	async function startTranscription() {
		const selectedLanguages = targetLanguages
			.filter((lang) => lang.selected)
			.map((lang) => lang.code);

		try {
			let res = await axios.post(
				`${apiUrl}/start_task`,
				{
					//   task_id: taskId,
					m3u8_url: m3u8Url,
				},
				{
					headers: {
						"Content-Type": "application/json",
						Accept: "application/json",
					},
				},
			);

			console.log("res is: ", res);
			taskId = res.data.task_id;
			console.log("taskId is: ", taskId);
			// Start streaming the transcript
			streamTranscript();

			// Load the video
			loadVideo();
		} catch (error) {
			console.error("Error starting transcription:", error);
		}
	}

	async function streamTranscript() {
		// await new Promise((resolve) => setTimeout(resolve, 5000));
		async function pollForTranscript() {
			let response = await fetch(`${apiUrl}/transcript/${taskId}`, {
				method: "GET",
				headers: {
					"Content-Type": "application/json",
				},
			});
			var reader = response.body?.getReader();
			let decoder = new TextDecoder();
			while (true) {
				const { done, value } = await reader.read();
				console.log("done is: ", done);
				console.log("value is: ", value);
				// if (done) break;
				try {
					let chunk = decoder.decode(value);
					transcript += chunk;
					console.log("chunk is: ", chunk);
				} catch (error) {
					console.error("Error reading stream:", error);
				}
			}
		}
		pollForTranscript();
	}

	async function loadVideo() {
		while (!transcript) {
			await new Promise((resolve) => setTimeout(resolve, 1000));
			console.log("Waiting for transcript...");
		}
		if (Hls.isSupported()) {
			var video = videoElement;
			var hls = new Hls();
			hls.loadSource(m3u8Url);
			console.log("hls", hls);
			hls.attachMedia(video);
			hls.on(Hls.Events.MANIFEST_PARSED, function () {
				video.play();
			});
		} else if (video.canPlayType("application/vnd.apple.mpegurl")) {
			video.src = m3u8Url;
			video.addEventListener("canplay", function () {
				video.play();
			});
		}
	}
</script>

<svelte:head>
	<title>Theta Streaming</title>
</svelte:head>

<main class="container mx-auto p-4">
	<h1 class="text-3xl font-bold mb-4">Live Stream Transcription with ThetaCloud</h1>

	<div class="mb-4">
		<label for="m3u8Url" class="block mb-2">M3U8 URL running on theta:</label>
		<input
			type="text"
			id="m3u8Url"
			bind:value={m3u8Url}
			class="w-full p-2 border rounded"
			placeholder="Enter M3U8 URL"
		/>
	</div>

	<button
		on:click={startTranscription}
		class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
	>
		Start Transcription
	</button>

	<div class="mt-4 flex">
		{#if m3u8Url}
			<div class="w-1/2 pr-2">
				<h2 class="text-xl font-semibold mb-2">Live Stream:</h2>
				<video
					bind:this={videoElement}
					controls
					class="w-full aspect-video"
				></video>
			</div>
		{/if}

		<div class="w-1/2 pl-2">
			<h2 class="text-xl font-semibold mb-2">Live Transcript:</h2>
			<pre
				class="bg-gray-100 p-4 rounded h-[400px] overflow-y-auto whitespace-pre-wrap">{transcript}</pre>
		</div>
	</div>

	<div class="my-4">
		Task Id: {taskId}
	</div>
</main>
