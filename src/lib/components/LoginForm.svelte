<script lang="ts">
	import { login } from '$lib/stores/auth';
	import { goto } from '$app/navigation';

	let email = '';
	let password = '';
	let error = '';

	async function handleSubmit() {
		const result = await login(email, password);
		if (result.success) {
			goto('/home');
		} else {
			error = result.error || 'Login failed';
		}
	}
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-4">
	<div>
		<label for="email" class="block text-sm font-medium">Email</label>
		<input type="email" id="email" bind:value={email} class="w-full rounded border p-2" required />
	</div>
	<div>
		<label for="password" class="block text-sm font-medium">Password</label>
		<input
			type="password"
			id="password"
			bind:value={password}
			class="w-full rounded border p-2"
			required
		/>
	</div>
	{#if error}
		<p class="text-sm text-red-500">{error}</p>
	{/if}
	<button type="submit" class="w-full rounded bg-blue-600 p-2 text-white hover:bg-blue-700"
		>Login</button
	>
</form>
