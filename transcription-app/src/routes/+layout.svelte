<div class="app">
	
	<Header></Header>

	<main>
		<slot></slot>
	</main>

	<footer>
		<!-- <p>visit <a href="https://kit.svelte.dev">kit.svelte.dev</a> to learn SvelteKit</p> -->
		<p>{text}</p>
	</footer>
</div>


<script>import Header from "./Header.svelte";
import "../app.css";
let text = "Theta2024 hackathon, made by Arnav with <3"
</script><style>
	.app {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}
	p {
		font-size: large;
	}

	main {
		flex: 1;
		display: flex;
		flex-direction: column;
		padding: 1rem;
		width: 100%;
		max-width: 64rem;
		margin: 0 auto;
		box-sizing: border-box;
	}

	footer {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		padding: 12px;
	}

	footer a {
		font-weight: bold;
	}

	@media (min-width: 480px) {
		footer {
			padding: 12px 0;
		}
	}
</style>