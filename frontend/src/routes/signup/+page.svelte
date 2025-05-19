<script lang="ts">
	import { goto } from '$app/navigation';
	import { Eye, EyeOff } from 'lucide-svelte';

	// Assuming shadcn-svelte components are in $lib/components/ui
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Checkbox } from '$lib/components/ui/checkbox';
	import {
		Card,
		CardContent,
		CardDescription,
		CardFooter,
		CardHeader,
		CardTitle
	} from '$lib/components/ui/card';

	// This component still retains the ability to show either form.
	// For a dedicated signup page, showLogin would typically be false initially.
	let showLogin = false; // Default to showing Sign Up form
	let showPassword = false;
	let name = '';
	let email = '';
	let password = '';
	let agreeTerms = false;
	let loginEmail = '';
	let loginPassword = '';

	// Handle signup form submission
	const handleSignup = async () => {
		if (!agreeTerms) {
			alert('Please agree to the Terms & Conditions');
			return;
		}
		const response = await fetch('/signup', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ name, email, password })
		});
		const data = await response.json();
		if (response.ok) {
			goto('/dashboard');
		} else {
			alert(data.error || 'Signup failed');
		}
	};

	// Handle login form submission (if login form is shown on this page)
	const handleLogin = async () => {
		const response = await fetch('/login', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ email: loginEmail, password: loginPassword })
		});
		const data = await response.json();
		if (response.ok) {
			goto('/dashboard');
		} else {
			alert(data.error || 'Login failed');
		}
	};

	const backgroundImageUrl =
		'https://images.unsplash.com/photo-1685729847171-7c7e631c2359?q=80&w=2126&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D';

	const socialProviders = [
		{
			label: 'Google',
			iconUrl: 'https://storage.googleapis.com/a1aa/image/29da2f80-2463-44b2-7766-8ab8f907eea7.jpg',
			href: '/auth/google'
		}
		// Add Apple and Facebook back if needed for signup
		// { label: 'Apple',   iconUrl: "https://storage.googleapis.com/a1aa/image/7a39ff8e-37f7-411b-66e6-8a1244dbf4a4.jpg",    href: '/auth/apple' },
		// { label: 'Facebook',iconUrl: "https://storage.googleapis.com/a1aa/image/4dd686bb-21e2-4571-95d2-258ba41795b3.jpg", href: '/auth/facebook' }
	];
</script>

<svelte:head>
	<title>{showLogin ? 'Sign In' : 'Create Account'}</title>
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
			<CardTitle class="text-3xl font-semibold text-white">
				{showLogin ? 'Welcome Back!' : 'Create an Account'}
			</CardTitle>
			<CardDescription class="text-sm text-gray-300">
				{showLogin
					? 'Enter your credentials to access your account.'
					: 'Join us! Fill in your details below to get started.'}
			</CardDescription>
		</CardHeader>

		<CardContent class="space-y-6">
			{#if showLogin}
				<!-- Login Form -->
				<form on:submit|preventDefault={handleLogin} class="space-y-4">
					<div>
						<Label for="login-email" class="font-semibold text-gray-200">Email</Label>
						<Input
							id="login-email"
							type="email"
							bind:value={loginEmail}
							placeholder="you@example.com"
							required
							class="mt-1 border-neutral-600 bg-neutral-800/50 text-white placeholder:text-neutral-400 focus:border-primary"
						/>
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
						<div class="mt-2 text-right">
							<a href="/forgot-password" class="text-xs font-medium text-primary hover:underline">
								Forgot password?
							</a>
						</div>
					</div>
					<Button type="submit" class="!mt-6 w-full">Login</Button>
				</form>
			{:else}
				<!-- Signup Form -->
				<form on:submit|preventDefault={handleSignup} class="space-y-4">
					<div>
						<Label for="name" class="font-semibold text-gray-200">Name</Label>
						<Input
							id="name"
							type="text"
							bind:value={name}
							placeholder="John Doe"
							required
							class="mt-1 border-neutral-600 bg-neutral-800/50 text-white placeholder:text-neutral-400 focus:border-primary"
						/>
					</div>
					<div>
						<Label for="signup-email" class="font-semibold text-gray-200">Email</Label>
						<Input
							id="signup-email"
							type="email"
							bind:value={email}
							placeholder="you@example.com"
							required
							class="mt-1 border-neutral-600 bg-neutral-800/50 text-white placeholder:text-neutral-400 focus:border-primary"
						/>
					</div>
					<div>
						<Label for="signup-password" class="font-semibold text-gray-200">Password</Label>
						<div class="relative mt-1">
							<Input
								id="signup-password"
								type={showPassword ? 'text' : 'password'}
								bind:value={password}
								placeholder="Choose a strong password"
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
					</div>
					<div class="flex items-center space-x-2 pt-2">
						<Checkbox
							id="agree"
							bind:checked={agreeTerms}
							class="border-neutral-500 data-[state=checked]:border-primary data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground"
						/>
						<Label for="agree" class="select-none text-xs font-normal text-gray-400">
							I agree to the
							<a href="/terms" class="font-medium text-primary hover:underline"
								>Terms & Conditions</a
							>
						</Label>
					</div>
					<Button type="submit" class="!mt-6 w-full bg-blue-600 text-white hover:bg-blue-700"
						>Create Account</Button
					>
				</form>

				<!-- Social Login Buttons - Shown only for Signup Form -->
				<div class="relative my-6">
					<div class="absolute inset-0 flex items-center">
						<span class="w-full border-t border-neutral-700"></span>
					</div>
					<div class="relative flex justify-center text-xs uppercase">
						<span class="bg-neutral-900/70 px-2 text-gray-400">Or sign up with</span>
					</div>
				</div>

				<div class="space-y-3">
					{#each socialProviders as provider (provider.label)}
						<Button
							variant="outline"
							class="flex w-full items-center justify-center space-x-2 border-neutral-600 text-gray-200 hover:bg-neutral-700/50 hover:text-white"
							aria-label={`Sign up with ${provider.label}`}
							on:click={() => goto(provider.href)}
						>
							<img src={provider.iconUrl} alt="{provider.label} logo" class="h-5 w-5" />
							<!-- Added alt text -->
							<span>{provider.label}</span>
						</Button>
					{/each}
				</div>
			{/if}
			<!-- End of {#if showLogin} ... {:else} ... {/if} for form content -->
		</CardContent>

		<CardFooter class="flex justify-center pt-6">
			<p class="text-sm text-gray-400">
				{#if showLogin}
					Don't have an account?
					<button
						on:click={() => {
							showLogin = false; // Switch to Sign Up form on this page
						}}
						class="ml-1 font-semibold text-primary hover:underline focus:outline-none"
					>
						Sign Up
					</button>
				{:else}
					Already have an account?
					<button
						on:click={() => goto('/signin')}
						class="ml-1 font-semibold text-primary hover:underline focus:outline-none"
					>
						Sign In
					</button>
				{/if}
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
	:global(body.dark .bg-neutral-900\/70) {
		/* background-color: hsl(var(--background) / 0.7); */
	}
	:global(body.dark .border-neutral-700) {
		/* border-color: hsl(var(--border)); */
	}
</style>
