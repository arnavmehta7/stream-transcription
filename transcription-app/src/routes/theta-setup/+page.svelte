<script>
    const apiUrl = import.meta.env.VITE_API_URL;

    import { onMount, onDestroy } from "svelte";
    import axios from "axios";

    let saId = "";
    let saSecret = "";
    let streamName = "";
    let streamId = "";
    let ingestors = [];
    let selectedIngestorId = "";
    let streamServer = "";
    let streamKey = "";
    let message = "";
    let m3u8Url = "";
    let pollingInterval;
    async function createLivestream() {
        try {
            const response = await axios.post(
                "https://api.thetavideoapi.com/stream",
                { name: streamName },
                {
                    headers: {
                        "x-tva-sa-id": saId,
                        "x-tva-sa-secret": saSecret,
                        "Content-Type": "application/json",
                    },
                },
            );
            streamId = response.data.body.id;
            message = `Livestream created with ID: ${streamId}`;
            startPolling();
        } catch (error) {
            message = `Error creating livestream: ${error.response?.data?.message || error.message}`;
        }
    }

    async function listIngestors() {
        try {
            const response = await axios.get(
                "https://api.thetavideoapi.com/ingestor/filter",
                {
                    headers: {
                        "x-tva-sa-id": saId,
                        "x-tva-sa-secret": saSecret,
                    },
                },
            );
            ingestors = response.data.body.ingestors;
            message = "Ingestors listed successfully";
        } catch (error) {
            message = `Error listing ingestors: ${error.response?.data?.message || error.message}`;
        }
    }

    async function selectIngestor() {
        try {
            const response = await axios.put(
                `https://api.thetavideoapi.com/ingestor/${selectedIngestorId}/select`,
                { tva_stream: streamId },
                {
                    headers: {
                        "x-tva-sa-id": saId,
                        "x-tva-sa-secret": saSecret,
                        "Content-Type": "application/json",
                    },
                },
            );
            streamServer = response.data.body.stream_server;
            streamKey = response.data.body.stream_key;
            message = "Ingestor selected successfully";
        } catch (error) {
            message = `Error selecting ingestor: ${error.response?.data?.message || error.message}`;
        }
    }

    async function checkStreamStatus() {
        try {
            const response = await axios.get(
                `https://api.thetavideoapi.com/stream/${streamId}`,
                {
                    headers: {
                        "x-tva-sa-id": saId,
                        "x-tva-sa-secret": saSecret,
                    },
                },
            );
            const stream = response.data.body;
            if (stream.status === "on" && stream.playback_uri) {
                m3u8Url = stream.playback_uri;
                message = "Stream is live! M3U8 URL retrieved.";
                stopPolling();
            } else {
                message = `Stream status: ${stream.status}. Waiting for stream to go live...`;
            }
        } catch (error) {
            message = `Error checking stream status: ${error.response?.data?.message || error.message}`;
        }
    }

    function startPolling() {
        pollingInterval = setInterval(checkStreamStatus, 10000); // Check every 10 seconds
    }

    function stopPolling() {
        if (pollingInterval) {
            clearInterval(pollingInterval);
        }
    }

    onDestroy(() => {
        stopPolling();
    });
</script>

<main class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-4">Theta Video API Livestream Setup</h1>

    <div class="mb-4">
        <label for="saId" class="block mb-2">Service Account ID:</label>
        <input
            type="password"
            id="saId"
            bind:value={saId}
            class="w-full p-2 border rounded"
        />
    </div>

    <div class="mb-4">
        <label for="saSecret" class="block mb-2">Service Account Secret:</label>
        <input
            type="password"
            id="saSecret"
            bind:value={saSecret}
            class="w-full p-2 border rounded"
        />
    </div>

    <div class="mb-4">
        <label for="streamName" class="block mb-2">Stream Name:</label>
        <input
            type="text"
            id="streamName"
            bind:value={streamName}
            class="w-full p-2 border rounded"
        />
        <button
            on:click={createLivestream}
            class="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
            Create Livestream
        </button>
    </div>

    {#if streamId}
        <div class="mb-4">
            <p>Stream ID: {streamId}</p>
            <button
                on:click={listIngestors}
                class="mt-2 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
                List Available Ingestors
            </button>
        </div>
    {/if}

    {#if ingestors.length > 0}
        <div class="mb-4">
            <label for="ingestor" class="block mb-2">Select Ingestor:</label>
            <select
                id="ingestor"
                bind:value={selectedIngestorId}
                class="w-full p-2 border rounded"
            >
                {#each ingestors as ingestor}
                    <option value={ingestor.id}
                        >{ingestor.ip} - Stakes: {ingestor.stakes}</option
                    >
                {/each}
            </select>
            <button
                on:click={selectIngestor}
                class="mt-2 bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600"
            >
                Select Ingestor
            </button>
        </div>
    {/if}

    {#if streamServer && streamKey}
        <div class="mb-4">
            <h2 class="text-xl font-semibold mb-2">Stream Information:</h2>
            <p>Stream Server: {streamServer}</p>
            <p>Stream Key: {streamKey}</p>
        </div>
    {/if}

    {#if m3u8Url}
        <div class="mb-4">
            <h2 class="text-xl font-semibold mb-2">M3U8 URL:</h2>
            <p>{m3u8Url}</p>
        </div>
    {/if}

    {#if message}
        <div class="mt-4 p-4 bg-gray-100 rounded">
            <p>{message}</p>
        </div>
    {/if}
</main>

<style lang="postcss">
    @tailwind base;
    @tailwind components;
    @tailwind utilities;
</style>
