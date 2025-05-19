<script lang="ts">
	import '../app.css';
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	// Optional: Mock authenticated user for development (comment out when not needed)
	onMount(() => {
		authStore.set({
			email: 'user@example.com',
			role: 'user', // Change to 'admin' to test admin routes
			token: 'mock-jwt-token'
		});
	});

	// Logout function to clear authStore and redirect to /intro
	const handleLogout = () => {
		authStore.set(null);
		goto('/intro');
	};
</script>

<div class="font-quicksand min-h-screen bg-black">
	{#if $authStore}
		<!-- Header for authenticated users -->
		<header class="flex items-center justify-between bg-gray-900 p-4 text-white">
			<h1 class="text-lg font-semibold">
				{$authStore.role === 'admin' ? 'Admin Dashboard' : 'Car Rental'}
			</h1>
			<button
				on:click={handleLogout}
				class="rounded-lg bg-red-500 px-4 py-2 font-semibold text-white hover:bg-red-600"
			>
				Logout
			</button>
		</header>
	{/if}

	<main class="mx-auto px-4 pb-4">
		<slot />
	</main>
</div>

<style>
	@font-face {
		font-family: 'Quicksand';
		src: url('https://fonts.googleapis.com/css2?family=Quicksand&display=swap');
	}

	.font-quicksand {
		font-family: 'Quicksand', sans-serif;
	}
</style>
