<!-- src/routes/login/+page.svelte -->
<script lang="ts">
	import { goto } from '$app/navigation';
	import { Eye, EyeOff } from 'lucide-svelte';
	import { login } from '$lib/stores/auth';

	// Shadcn-svelte components
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import {
		Card,
		CardContent,
		CardDescription,
		CardFooter,
		CardHeader,
		CardTitle
	} from '$lib/components/ui/card';

	let showPassword = false;
	let loginEmail = '';
	let loginPassword = '';
	let errorMessage = '';
	let validationErrors: { [key: string]: string } = {};
	let isLoading = $state(false);

	// Validate form inputs
	const validateForm = () => {
		const errors: { [key: string]: string } = {};

		// Email validation
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!loginEmail || !emailRegex.test(loginEmail)) {
			errors.email = 'Please enter a valid email address';
		}

		// Password validation
		if (!loginPassword || loginPassword.length < 3) {
			errors.password = 'Password must be at least 6 characters long';
		}

		validationErrors = errors;
		return Object.keys(errors).length === 0;
	};

	// Handle login form submission
	const handleLogin = async () => {
		// Clear previous errors
		errorMessage = '';
		validationErrors = {};

		// Validate form
		if (!validateForm()) {
			return;
		}

		isLoading = true;
		try {
			const result = await login(loginEmail, loginPassword);
			if (result.success) {
				goto('/');
			} else {
				errorMessage = result.error || 'Login failed';
			}
		} catch (error) {
			console.error('Login error:', error);
			errorMessage = 'An error occurred. Please try again.';
		} finally {
			isLoading = false;
		}
	};

	const backgroundImageUrl =
		'https://images.unsplash.com/photo-1685729847171-7c7e631c2359?q=80&w=2126&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D';

	// Social providers for "Sign In"
	const socialProviders = [
		{
			label: 'Google',
			iconUrl: 'https://storage.googleapis.com/a1aa/image/29da2f80-2463-44b2-7766-8ab8f907eea7.jpg',
			href: '/auth/google'
		}
	];
</script>

<svelte:head>
	<title>Sign In</title>
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="" />
	<link
		href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div
	class="font-quicksand flex min-h-screen items-center justify-center bg-cover bg-center p-4 selection:bg-primary/30 selection:text-primary-foreground"
	style="background-image: url('{backgroundImageUrl}');"
>
	<!-- Gradient Overlay -->
	<div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-black/10"></div>

	<Card
		class="relative z-10 w-full max-w-md border-neutral-700 bg-neutral-900/70 text-white backdrop-blur-lg"
	>
		<CardHeader class="text-center">
			<CardTitle class="text-3xl font-semibold text-white">Welcome Back!</CardTitle>
			<CardDescription class="text-sm text-gray-300">
				Enter your credentials to access your account.
			</CardDescription>
		</CardHeader>

		<CardContent class="space-y-6">
			<!-- Login Form -->
			<form on:submit|preventDefault={handleLogin} class="space-y-4">
				<div>
					<Label for="login-email" class="font-semibold text-gray-200">Email</Label>
					<Input
						id="login-email"
						type="email"
						bind:value={loginEmail}
						placeholder="user@gmail.com"
						required
						class="mt-1 border-neutral-600 bg-neutral-800/50 text-white placeholder:text-neutral-400 focus:border-primary"
					/>
					{#if validationErrors.email}
						<p class="mt-1 text-sm text-red-500">{validationErrors.email}</p>
					{/if}
				</div>
				<div>
					<Label for="login-password" class="font-semibold text-gray-200">Password</Label>
					<div class="relative mt-1">
						<Input
							id="login-password"
							type={showPassword ? 'text' : 'password'}
							bind:value={loginPassword}
							placeholder="••••••••"
							required
							class="border-neutral-600 bg-neutral-800/50 text-white placeholder:text-neutral-400 focus:border-primary"
						/>
						<Button
							type="button"
							variant="ghost"
							size="icon"
							class="absolute inset-y-0 right-0 h-full px-3 text-gray-400 hover:bg-transparent hover:text-gray-200"
							on:click={() => (showPassword = !showPassword)}
							aria-label={showPassword ? 'Hide password' : 'Show password'}
						>
							{#if showPassword}
								<EyeOff class="h-5 w-5" />
							{:else}
								<Eye class="h-5 w-5" />
							{/if}
						</Button>
					</div>
					{#if validationErrors.password}
						<p class="mt-1 text-sm text-red-500">{validationErrors.password}</p>
					{/if}
					<div class="mt-2 text-right">
						<a href="/forgot-password" class="text-xs font-medium text-primary hover:underline">
							Forgot password?
						</a>
					</div>
				</div>
				{#if errorMessage}
					<p class="text-center text-sm text-red-500">{errorMessage}</p>
				{/if}
				<Button
					type="submit"
					disabled={isLoading}
					class="!mt-6 w-full rounded-md bg-blue-600 py-2 font-semibold text-white shadow-md transition-colors duration-200 hover:bg-blue-700 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
				>
					{#if isLoading}
						<span class="animate-pulse">Logging In...</span>
					{:else}
						Login
					{/if}
				</Button>
			</form>

			<!-- "Or sign in with" Separator -->
			<div class="relative my-6">
				<div class="absolute inset-0 flex items-center">
					<span class="w-full border-t border-neutral-700"></span>
				</div>
				<div class="relative flex justify-center text-xs uppercase">
					<span class="bg-neutral-900/70 px-2 text-gray-400">Or sign in with</span>
				</div>
			</div>

			<!-- Social Login Buttons -->
			<div class="space-y-3">
				{#each socialProviders as provider (provider.label)}
					<Button
						variant="outline"
						class="flex w-full items-center justify-center space-x-2 border-neutral-600 text-gray-200 hover:bg-neutral-700/50 hover:text-white"
						aria-label={`Sign in with ${provider.label}`}
						on:click={() => goto(provider.href)}
					>
						<img src={provider.iconUrl} alt="" class="h-5 w-5" />
						<span>{provider.label}</span>
					</Button>
				{/each}
			</div>
		</CardContent>

		<CardFooter class="flex justify-center pt-6">
			<p class="text-sm text-gray-400">
				Don't have an account?
				<a
					href="/signup"
					class="ml-1 font-semibold text-primary hover:underline focus:outline-none"
				>
					Sign Up
				</a>
			</p>
		</CardFooter>
	</Card>
</div>

<style>
	:global(.font-quicksand) {
		font-family: 'Quicksand', sans-serif;
	}
	:global(.backdrop-blur-lg) {
		backdrop-filter: blur(12px);
	}
</style>
