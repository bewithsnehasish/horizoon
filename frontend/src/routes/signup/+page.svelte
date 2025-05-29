<script lang="ts">
	import { goto } from '$app/navigation';
	import { Eye, EyeOff, Loader2 } from 'lucide-svelte';
	import { signup, loginWithGoogle } from '$lib/stores/auth';

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

	// SVELTE 5: Using $state for all reactive state
	let showPassword = $state(false);
	let showConfirmPassword = $state(false);
	let username = $state('');
	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let errorMessage = $state('');
	let validationErrors = $state<{ [key: string]: string }>({});
	let isLoading = $state(false);
	let isGoogleLoading = $state(false);

	// SVELTE 5: Reactive computations using $derived
	const isFormValid = $derived(() => {
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return (
			username.length >= 3 &&
			email &&
			emailRegex.test(email) &&
			password.length >= 6 &&
			password === confirmPassword
		);
	});

	const passwordsMatch = $derived(() => {
		return password === confirmPassword || confirmPassword === '';
	});

	// Validate form inputs
	const validateForm = () => {
		const errors: { [key: string]: string } = {};

		// Username validation
		if (!username || username.length < 3) {
			errors.username = 'Username must be at least 3 characters long';
		}

		// Email validation
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!email || !emailRegex.test(email)) {
			errors.email = 'Please enter a valid email address';
		}

		// Password validation
		if (!password || password.length < 6) {
			errors.password = 'Password must be at least 6 characters long';
		}

		// Confirm password validation
		if (password !== confirmPassword) {
			errors.confirmPassword = 'Passwords do not match';
		}

		validationErrors = errors;
		return Object.keys(errors).length === 0;
	};

	// Handle regular signup form submission
	const handleSignup = async () => {
		// Clear previous errors
		errorMessage = '';
		validationErrors = {};

		// Validate form
		if (!validateForm()) {
			return;
		}

		isLoading = true;
		try {
			const result = await signup(username, email, password);
			if (result.success) {
				goto('/completeprofile');
			} else {
				errorMessage = result.error || 'Registration failed';
			}
		} catch (error) {
			console.error('Signup error:', error);
			errorMessage = 'An error occurred. Please try again.';
		} finally {
			isLoading = false;
		}
	};

	// Handle Google Sign-Up
	const handleGoogleSignUp = async () => {
		errorMessage = '';
		isGoogleLoading = true;

		try {
			console.log('Initiating Google sign-up...');
			const result = await loginWithGoogle();

			if (result.success) {
				console.log('Google sign-up successful, redirecting...');
				goto('/completeprofile');
			} else {
				console.error('Google sign-up failed:', result.error);
				errorMessage = result.error || 'Google sign-up failed';
			}
		} catch (error) {
			console.error('Google sign-up error:', error);
			errorMessage = 'An error occurred during Google sign-up';
		} finally {
			isGoogleLoading = false;
		}
	};

	// SVELTE 5: Effects using $effect
	$effect(() => {
		// Clear validation errors when user types
		if (username || email || password || confirmPassword) {
			validationErrors = {};
			errorMessage = '';
		}
	});

	const backgroundImageUrl =
		'https://images.unsplash.com/photo-1685729847171-7c7e631c2359?q=80&w=2126&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D';
</script>

<svelte:head>
	<title>Sign Up - Horizoon</title>
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
			<CardTitle class="text-3xl font-semibold text-white">Create Account</CardTitle>
			<CardDescription class="text-sm text-gray-300">
				Fill in your details to register.
			</CardDescription>
		</CardHeader>

		<CardContent class="space-y-6">
			<!-- Signup Form -->
			<form on:submit|preventDefault={handleSignup} class="space-y-4">
				<div>
					<Label for="username" class="font-semibold text-gray-200">Username</Label>
					<Input
						id="username"
						type="text"
						bind:value={username}
						placeholder="user"
						required
						class="mt-1 border-neutral-600 bg-neutral-800/50 text-white placeholder:text-neutral-400 focus:border-primary"
					/>
					{#if validationErrors.username}
						<p class="mt-1 text-sm text-red-500">{validationErrors.username}</p>
					{/if}
				</div>
				<div>
					<Label for="email" class="font-semibold text-gray-200">Email</Label>
					<Input
						id="email"
						type="email"
						bind:value={email}
						placeholder="user@gmail.com"
						required
						class="mt-1 border-neutral-600 bg-neutral-800/50 text-white placeholder:text-neutral-400 focus:border-primary"
					/>
					{#if validationErrors.email}
						<p class="mt-1 text-sm text-red-500">{validationErrors.email}</p>
					{/if}
				</div>
				<div>
					<Label for="password" class="font-semibold text-gray-200">Password</Label>
					<div class="relative mt-1">
						<Input
							id="password"
							type={showPassword ? 'text' : 'password'}
							bind:value={password}
							placeholder="••••••••"
							required
							class="border-neutral-600 bg-neutral-800/50 text-white placeholder:text-neutral-400 focus:border-primary"
						/>
						<Button
							type="button"
							variant="ghost"
							size="icon"
							class="absolute inset-y-0 right-0 h-full px-3 text-gray-400 hover:bg-transparent hover:text-gray-200"
							onclick={() => (showPassword = !showPassword)}
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
				</div>
				<div>
					<Label for="confirm-password" class="font-semibold text-gray-200">Confirm Password</Label>
					<div class="relative mt-1">
						<Input
							id="confirm-password"
							type={showConfirmPassword ? 'text' : 'password'}
							bind:value={confirmPassword}
							placeholder="••••••••"
							required
							class="border-neutral-600 bg-neutral-800/50 text-white placeholder:text-neutral-400 focus:border-primary {!passwordsMatch
								? 'border-red-500'
								: ''}"
						/>
						<Button
							type="button"
							variant="ghost"
							size="icon"
							class="absolute inset-y-0 right-0 h-full px-3 text-gray-400 hover:bg-transparent hover:text-gray-200"
							onclick={() => (showConfirmPassword = !showConfirmPassword)}
							aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
						>
							{#if showConfirmPassword}
								<EyeOff class="h-5 w-5" />
							{:else}
								<Eye class="h-5 w-5" />
							{/if}
						</Button>
					</div>
					{#if validationErrors.confirmPassword}
						<p class="mt-1 text-sm text-red-500">{validationErrors.confirmPassword}</p>
					{:else if !passwordsMatch}
						<p class="mt-1 text-sm text-yellow-500">Passwords do not match</p>
					{/if}
				</div>
				{#if errorMessage}
					<p class="text-center text-sm text-red-500">{errorMessage}</p>
				{/if}
				<Button
					type="submit"
					disabled={isLoading || isGoogleLoading || !isFormValid}
					class="!mt-6 w-full rounded-md bg-blue-600 py-2 font-semibold text-white shadow-md transition-colors duration-200 hover:bg-blue-700 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
				>
					{#if isLoading}
						<div class="flex items-center justify-center gap-2">
							<Loader2 class="h-4 w-4 animate-spin" />
							<span>Signing Up...</span>
						</div>
					{:else}
						Sign Up
					{/if}
				</Button>
			</form>

			<!-- "Or sign up with" Separator -->
			<div class="relative my-6">
				<div class="absolute inset-0 flex items-center">
					<span class="w-full border-t border-neutral-700"></span>
				</div>
				<div class="relative flex justify-center text-xs uppercase">
					<span class="bg-neutral-900/70 px-2 text-gray-400">Or sign up with</span>
				</div>
			</div>

			<!-- Enhanced Google Signup Button -->
			<div class="space-y-3">
				<Button
					variant="outline"
					disabled={isLoading || isGoogleLoading}
					class="flex w-full items-center justify-center space-x-2 border-neutral-600 text-gray-200 transition-all duration-200 hover:bg-neutral-700/50 hover:text-white disabled:opacity-50"
					aria-label="Sign up with Google"
					onclick={handleGoogleSignUp}
				>
					{#if isGoogleLoading}
						<Loader2 class="h-5 w-5 animate-spin" />
						<span>Signing up...</span>
					{:else}
						<img
							src="https://storage.googleapis.com/a1aa/image/29da2f80-2463-44b2-7766-8ab8f907eea7.jpg"
							alt="Google"
							class="h-5 w-5"
						/>
						<span>Continue with Google</span>
					{/if}
				</Button>
			</div>
		</CardContent>

		<CardFooter class="flex justify-center pt-6">
			<p class="text-sm text-gray-400">
				Already have an account?
				<a
					href="/signin"
					class="ml-1 font-semibold text-primary hover:underline focus:outline-none"
				>
					Sign In
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
