<script lang="ts">
	import { authStore } from '$lib/stores/auth';
</script>

<div class="text-center">
	<h1 class="mb-4 text-3xl font-bold">Admin Dashboard</h1>
	<p class="text-lg">Welcome, {$authStore?.email}! Manage vehicles and reports here.</p>
</div>
