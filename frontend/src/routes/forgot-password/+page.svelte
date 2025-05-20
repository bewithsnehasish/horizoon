<!-- src/routes/forgot-password/+page.svelte -->
<script>
	async function handleSubmit(event) {
		event.preventDefault();
		const formData = new FormData(event.target);
		// Simulate API call
		console.log('Reset password for:', formData.get('email'));
	}
</script>

<h1>Forgot Password</h1>
<form on:submit={handleSubmit}>
	<label>
		Email:
		<input type="email" name="email" required />
	</label>
	<button type="submit">Reset Password</button>
</form>
