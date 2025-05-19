<script lang="ts">
	import '../app.css';
	import { authStore } from '$lib/stores/auth';
</script>

<div class="min-h-screen bg-black">
	{#if $authStore}{/if}
	<main class=" mx-auto">
		<slot />
	</main>
</div>
