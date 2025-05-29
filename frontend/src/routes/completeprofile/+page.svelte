<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import {
		ArrowLeft,
		Loader2,
		XCircle,
		AlertTriangle,
		User,
		Phone,
		CreditCard,
		Users
	} from 'lucide-svelte';
	import { getAuthToken } from '$lib/stores/auth';
	import { fade, scale, fly } from 'svelte/transition';

	let name: string = '';
	let phoneNumber: string = '';
	let aadhaarNumber: string = '';
	let selectedGender: string | undefined = undefined;
	let errorMessage: string = '';
	let validationErrors: { [key: string]: string } = {};
	let isLoading: boolean = false;

	const genders: any[] = [
		{ value: 'Male', label: 'Male' },
		{ value: 'Female', label: 'Female' },
		{ value: 'Other', label: 'Other' },
		{ value: 'Prefer not to say', label: 'Prefer not to say' }
	];

	function goBack() {
		if (typeof window !== 'undefined' && window.history.length > 1) {
			window.history.back();
		} else {
			goto('/');
		}
	}

	// Logout function to clear auth token and redirect
	function logout() {
		// Assuming there's a clearAuthToken function
		// clearAuthToken();
		goto('/intro');
	}

	// Format Aadhar number with spaces for display
	function formatAadharDisplay(value: string): string {
		const cleaned = value.replace(/\D/g, '');
		const match = cleaned.match(/^(\d{0,4})(\d{0,4})(\d{0,4})$/);
		if (match) {
			return [match[1], match[2], match[3]].filter(Boolean).join(' ');
		}
		return cleaned;
	}

	// Handle Aadhar input to allow only numbers and format
	function handleAadharInput(event: Event) {
		const target = event.target as HTMLInputElement;
		const value = target.value.replace(/\D/g, ''); // Remove non-digits
		if (value.length <= 12) {
			aadhaarNumber = value;
			target.value = formatAadharDisplay(value);
		}
	}

	// Validate form inputs
	const validateForm = () => {
		const errors: { [key: string]: string } = {};

		// Name validation
		if (!name || name.trim().length < 2) {
			errors.name = 'Name must be at least 2 characters long';
		} else if (name.trim().length > 50) {
			errors.name = 'Name must be less than 50 characters';
		} else if (!/^[a-zA-Z\s]+$/.test(name.trim())) {
			errors.name = 'Name can only contain letters and spaces';
		}

		// Phone number validation
		const phoneRegex = /^[0-9]{10}$/;
		if (!phoneNumber || !phoneRegex.test(phoneNumber.trim())) {
			errors.phone = 'Please enter a valid 10-digit phone number';
		}

		// Aadhar number validation
		const aadharRegex = /^[0-9]{12}$/;
		if (!aadhaarNumber || !aadharRegex.test(aadhaarNumber.trim())) {
			errors.aadhaar = 'Please enter a valid 12-digit Aadhar number';
		}

		// Gender validation
		if (!selectedGender) {
			errors.gender = 'Please select your gender';
		}

		validationErrors = errors;
		return Object.keys(errors).length === 0;
	};

	async function handleSubmitProfile() {
		// Clear previous errors
		errorMessage = '';
		validationErrors = {};

		// Validate form
		if (!validateForm()) {
			return;
		}

		// Get auth token
		const userAuthToken = getAuthToken();
		if (!userAuthToken) {
			errorMessage = 'Authentication token not found. Please log in again.';
			goto('/login');
			return;
		}

		// Prepare payload with aadhaar field
		const payload = {
			authToken: userAuthToken,
			name: name.trim(),
			phone: phoneNumber.trim(),
			aadhaar: aadhaarNumber.trim(), // Added aadhaar field
			gender: selectedGender
		};

		isLoading = true;
		try {
			const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
			const response = await fetch(`${API_BASE_URL}/authentication/add-details/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${userAuthToken}`
				},
				body: JSON.stringify(payload)
			});

			const data = await response.json();

			if (response.ok && data.success) {
				console.log('Profile submission successful:', data.message);
				goto('/');
			} else {
				// Handle specific error cases
				if (data.message === 'This Phone Number Already Registered') {
					errorMessage = 'This phone number is already registered with another account.';
				} else if (data.message === 'This Aadhar Number Already Registered') {
					errorMessage = 'This Aadhar number is already registered with another account.';
				} else if (
					data.error ===
					'Invalid authentication token provided: Client matching query does not exist.'
				) {
					errorMessage = 'Invalid authentication token. Logging out...';
					logout();
				} else {
					// Generic error handling
					let specificError = 'Failed to submit profile. Please try again.';
					if (data && data.message) {
						specificError = data.message;
					} else if (!response.ok) {
						specificError = `Server error (${response.status}). Please try again later.`;
					}
					errorMessage = specificError;
				}
			}
		} catch (error) {
			console.error('Profile submission error:', error);
			errorMessage = 'Network error. Please check your connection and try again.';
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Complete Profile | Horizoon</title>
	<meta name="description" content="Finalize your Horizoon profile to start your journey." />
</svelte:head>

<div
	class="font-inter min-h-screen bg-gradient-to-br from-gray-950 via-slate-900 to-gray-950 text-white antialiased"
>
	<!-- iOS Safe Area Background -->
	<div class="fixed left-0 right-0 top-0 z-50 h-[env(safe-area-inset-top)] bg-slate-900/95"></div>

	<!-- Animated Background Orbs -->
	<div class="pointer-events-none fixed inset-0 overflow-hidden">
		<div
			class="absolute -right-48 -top-48 h-96 w-96 animate-pulse rounded-full bg-gradient-to-br from-teal-500/20 to-cyan-500/10 blur-3xl"
		></div>
		<div
			class="absolute -bottom-48 -left-48 h-96 w-96 animate-pulse rounded-full bg-gradient-to-br from-purple-500/20 to-pink-500/10 blur-3xl"
			style="animation-delay: 2s;"
		></div>
	</div>

	<!-- Enhanced Header -->
	<header
		class="sticky top-0 z-40 border-b border-teal-500/20 bg-gradient-to-r from-slate-900/95 via-slate-800/95 to-slate-900/95 p-6 pt-[env(safe-area-inset-top)] shadow-2xl backdrop-blur-xl"
	>
		<Button
			variant="ghost"
			size="icon"
			class="rounded-2xl border border-slate-600/30 p-3 text-slate-300 transition-all duration-300 hover:scale-105 hover:bg-gradient-to-br hover:from-slate-700/50 hover:to-slate-600/50 hover:text-teal-400 focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
			on:click={goBack}
			aria-label="Go back"
		>
			<ArrowLeft class="h-6 w-6" />
		</Button>
	</header>

	<main class="flex flex-grow flex-col items-center justify-center px-6 py-8 sm:px-8 sm:py-12">
		<div class="w-full max-w-md space-y-8" in:fade={{ duration: 600 }}>
			<!-- Header Section -->
			<div class="mb-8 text-center" in:fly={{ y: -30, duration: 600, delay: 200 }}>
				<div
					class="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-teal-500 to-cyan-500 shadow-xl shadow-teal-500/25"
				>
					<User class="h-10 w-10 text-white" />
				</div>
				<h1
					class="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-3xl font-black tracking-tight text-transparent sm:text-4xl"
				>
					Complete Your Profile
				</h1>
				<p class="mt-3 text-base leading-relaxed text-slate-400">
					Just a few details to get you started on your <span
						class="bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text font-bold text-transparent"
						>Horizoon</span
					> journey
				</p>
			</div>

			<!-- Form Card -->
			<div
				class="rounded-3xl border border-slate-600/30 bg-gradient-to-br from-slate-800/80 to-slate-700/80 p-8 shadow-2xl backdrop-blur-lg"
				in:scale={{ duration: 600, delay: 400 }}
			>
				<form on:submit|preventDefault={handleSubmitProfile} class="space-y-6" novalidate>
					<!-- Name Field -->
					<div class="space-y-2" in:fly={{ x: -30, duration: 500, delay: 600 }}>
						<Label for="name" class="flex items-center gap-2 text-sm font-semibold text-slate-200">
							<User class="h-4 w-4 text-teal-400" />
							Full Name
						</Label>
						<Input
							id="name"
							type="text"
							bind:value={name}
							placeholder="Enter your full name"
							class="w-full rounded-2xl border-slate-600/50 bg-slate-700/50 px-4 py-4 text-base text-gray-100 placeholder-slate-400
								   transition-all duration-300 hover:border-slate-500 focus:border-teal-500 focus:bg-slate-700 focus:ring-2 focus:ring-teal-500/50"
							required
							aria-invalid={!!validationErrors.name}
							aria-describedby={validationErrors.name ? 'name-error' : undefined}
						/>
						{#if validationErrors.name}
							<p id="name-error" class="flex items-center text-sm text-red-400" transition:fade>
								<XCircle class="mr-2 h-4 w-4 shrink-0" />
								{validationErrors.name}
							</p>
						{/if}
					</div>

					<!-- Phone Field -->
					<div class="space-y-2" in:fly={{ x: -30, duration: 500, delay: 700 }}>
						<Label for="phone" class="flex items-center gap-2 text-sm font-semibold text-slate-200">
							<Phone class="h-4 w-4 text-green-400" />
							Phone Number
						</Label>
						<Input
							id="phone"
							type="tel"
							inputmode="numeric"
							maxlength="10"
							pattern="[0-9]{10}"
							bind:value={phoneNumber}
							placeholder="Enter 10-digit phone number"
							class="w-full rounded-2xl border-slate-600/50 bg-slate-700/50 px-4 py-4 text-base text-gray-100 placeholder-slate-400
								   transition-all duration-300 hover:border-slate-500 focus:border-green-500 focus:bg-slate-700 focus:ring-2 focus:ring-green-500/50"
							required
							aria-invalid={!!validationErrors.phone}
							aria-describedby={validationErrors.phone ? 'phone-error' : undefined}
						/>
						{#if validationErrors.phone}
							<p id="phone-error" class="flex items-center text-sm text-red-400" transition:fade>
								<XCircle class="mr-2 h-4 w-4 shrink-0" />
								{validationErrors.phone}
							</p>
						{/if}
					</div>

					<!-- Aadhar Field -->
					<div class="space-y-2" in:fly={{ x: -30, duration: 500, delay: 800 }}>
						<Label
							for="aadhaar"
							class="flex items-center gap-2 text-sm font-semibold text-slate-200"
						>
							<CreditCard class="h-4 w-4 text-blue-400" />
							Aadhar Number
						</Label>
						<input
							id="aadhaar"
							type="text"
							inputmode="numeric"
							maxlength="14"
							on:input={handleAadharInput}
							placeholder="Enter 12-digit Aadhar number"
							class="w-full rounded-2xl border border-slate-600/50 bg-slate-700/50 px-4 py-4 text-base text-gray-100 placeholder-slate-400
								   transition-all duration-300 hover:border-slate-500 focus:border-blue-500 focus:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
							required
							aria-invalid={!!validationErrors.aadhaar}
							aria-describedby={validationErrors.aadhaar ? 'aadhaar-error' : undefined}
						/>
						<p class="flex items-center gap-1 text-xs text-slate-500">
							<CreditCard class="h-3 w-3" />
							Your Aadhar information is secure and encrypted
						</p>
						{#if validationErrors.aadhaar}
							<p id="aadhaar-error" class="flex items-center text-sm text-red-400" transition:fade>
								<XCircle class="mr-2 h-4 w-4 shrink-0" />
								{validationErrors.aadhaar}
							</p>
						{/if}
					</div>

					<!-- Gender Field -->
					<div class="space-y-2" in:fly={{ x: -30, duration: 500, delay: 900 }}>
						<Label
							for="gender"
							class="flex items-center gap-2 text-sm font-semibold text-slate-200"
						>
							<Users class="h-4 w-4 text-purple-400" />
							Gender
						</Label>
						<select
							id="gender"
							bind:value={selectedGender}
							class="w-full rounded-2xl border border-slate-600/50 bg-slate-700/50 px-4 py-4 text-base text-gray-100 transition-all duration-300 hover:border-slate-500 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
							aria-invalid={!!validationErrors.gender}
							aria-describedby={validationErrors.gender ? 'gender-error' : undefined}
						>
							<option value="" disabled selected class="bg-slate-700">Select your gender</option>
							{#each genders as gender (gender.value)}
								<option value={gender.value} class="bg-slate-700">{gender.label}</option>
							{/each}
						</select>
						{#if validationErrors.gender}
							<p id="gender-error" class="flex items-center text-sm text-red-400" transition:fade>
								<XCircle class="mr-2 h-4 w-4 shrink-0" />
								{validationErrors.gender}
							</p>
						{/if}
					</div>

					<!-- Error Message -->
					{#if errorMessage}
						<div
							class="flex items-center justify-center rounded-2xl border border-red-500/30 bg-gradient-to-r from-red-500/20 to-orange-500/20 p-4 text-center backdrop-blur-lg"
							transition:fly={{ y: 20, duration: 400 }}
						>
							<AlertTriangle class="mr-3 h-5 w-5 shrink-0 text-red-400" />
							<span class="text-sm font-medium text-red-300">{errorMessage}</span>
						</div>
					{/if}

					<!-- Submit Button - Wrapped in div for transition -->
					<div in:fly={{ y: 30, duration: 500, delay: 1000 }}>
						<Button
							type="submit"
							disabled={isLoading}
							class="!mt-8 w-full transform rounded-2xl bg-gradient-to-r from-teal-500 to-cyan-600
			   px-6 py-4 text-base font-bold text-white shadow-xl transition-all duration-300
			   ease-out hover:scale-[1.02] hover:from-teal-600 hover:to-cyan-700
			   hover:shadow-teal-500/30 focus:outline-none focus-visible:ring-4 focus-visible:ring-teal-500/50 active:scale-[0.98] disabled:cursor-not-allowed
			   disabled:bg-slate-600 disabled:from-slate-600 disabled:to-slate-500 disabled:opacity-60 disabled:shadow-none disabled:hover:scale-100"
						>
							{#if isLoading}
								<div class="flex items-center justify-center">
									<Loader2 class="mr-3 h-5 w-5 animate-spin" />
									<span>Saving Profile...</span>
								</div>
							{:else}
								<span>Complete Profile</span>
							{/if}
						</Button>
					</div>
				</form>
			</div>

			<!-- Security Notice -->
			<div
				class="space-y-1 text-center text-xs text-slate-500"
				in:fade={{ duration: 600, delay: 1200 }}
			>
				<p>🔒 Your information is encrypted and secure</p>
				<p>© {new Date().getFullYear()} Horizoon. Your Adventure Awaits.</p>
			</div>
		</div>
	</main>
</div>

<style>
	:global(.font-inter) {
		font-family:
			'Inter',
			-apple-system,
			BlinkMacSystemFont,
			'Segoe UI',
			system-ui,
			sans-serif;
	}

	/* Custom styling for select dropdown */
	select option {
		background-color: rgb(51 65 85); /* slate-700 */
		color: rgb(241 245 249); /* slate-100 */
	}

	/* Remove number input spinners */
	input[type='number'] {
		-moz-appearance: textfield;
	}
	input::-webkit-outer-spin-button,
	input::-webkit-inner-spin-button {
		-webkit-appearance: none;
		margin: 0;
	}

	/* Touch improvements for mobile */
	:global(button),
	:global(input),
	:global(select) {
		-webkit-tap-highlight-color: transparent;
		touch-action: manipulation;
	}

	/* Safe area handling for iOS */
	@supports (padding: max(0px)) {
		.safe-top {
			padding-top: max(1rem, env(safe-area-inset-top));
		}
	}
</style>
