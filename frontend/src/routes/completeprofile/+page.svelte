<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { ArrowLeft, Loader2, XCircle, AlertTriangle } from 'lucide-svelte';
	import { getAuthToken } from '$lib/stores/auth'; // Added clearAuthToken

	let name: string = '';
	let phoneNumber: string = '';
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
		logout(); // Clear the auth token from store
		goto('/intro');
	}

	// Validate form inputs
	const validateForm = () => {
		const errors: { [key: string]: string } = {};

		// Name validation
		if (!name || name.trim().length < 2) {
			errors.name = 'Name must be at least 2 characters long';
		}

		// Phone number validation
		const phoneRegex = /^[0-9]{10}$/;
		if (!phoneNumber || !phoneRegex.test(phoneNumber.trim())) {
			errors.phone = 'Please enter a valid 10-digit phone number';
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

		// Prepare payload
		const payload = {
			authToken: userAuthToken,
			name: name.trim(),
			phone: phoneNumber.trim(),
			gender: selectedGender
		};

		isLoading = true;
		try {
			const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'; // Adjusted to match API endpoint
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
				// Success case: { "success": true, "message": "Client details updated successfully" }
				console.log('Profile submission successful:', data.message);
				goto('/');
			} else {
				// Handle specific error cases
				if (data.message === 'This Phone Number Already Registered') {
					errorMessage = data.message;
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
			errorMessage = 'An error occurred. Please try again.';
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Complete Profile | Horizoon</title>
	<meta name="description" content="Finalize your Horizoon profile to start your journey." />
</svelte:head>

<div class="font-quicksand flex min-h-screen flex-col bg-slate-950 text-gray-300 antialiased">
	<header class="sticky top-0 z-20 bg-slate-900/70 p-4 shadow-md backdrop-blur-lg">
		<Button
			variant="ghost"
			size="icon"
			class="rounded-full p-2 text-slate-300 transition-colors hover:bg-slate-700/50 hover:text-teal-400 focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
			on:click={goBack}
			aria-label="Go back"
		>
			<ArrowLeft class="h-6 w-6" />
		</Button>
	</header>

	<main class="flex flex-grow flex-col items-center justify-center px-4 py-10 sm:px-6 sm:py-12">
		<div class="w-full max-w-md space-y-8 rounded-3xl bg-slate-900 p-6 shadow-2xl sm:p-10">
			<div class="text-center">
				<h1 class="text-3xl font-bold tracking-tight text-white sm:text-4xl">Just a Few Details</h1>
				<p class="mt-2.5 text-sm leading-relaxed text-slate-400">
					Complete your profile to enhance your <span class="font-semibold text-teal-400"
						>Horizoon</span
					> experience.
				</p>
			</div>

			<form
				on:submit|preventDefault={handleSubmitProfile}
				class="space-y-6 sm:space-y-7"
				novalidate
			>
				<div>
					<Label for="name" class="mb-2 block text-sm font-medium text-slate-300">Full Name</Label>
					<Input
						id="name"
						type="text"
						bind:value={name}
						placeholder="e.g., Alex Rider"
						class="w-full rounded-xl border-slate-700/80 bg-slate-800/60 px-4 py-3.5 text-gray-100 placeholder-slate-500
							   transition-all duration-150 focus:border-teal-500 focus:bg-slate-800 focus:ring-2 focus:ring-teal-500"
						required
						aria-invalid={!!validationErrors.name}
						aria-describedby={validationErrors.name ? 'name-error' : undefined}
					/>
					{#if validationErrors.name}
						<p id="name-error" class="mt-2 flex items-center text-xs text-red-400">
							<XCircle class="mr-1.5 h-3.5 w-3.5 shrink-0" />
							{validationErrors.name}
						</p>
					{/if}
				</div>

				<div>
					<Label for="phone" class="mb-2 block text-sm font-medium text-slate-300"
						>Phone Number (10-digit)</Label
					>
					<Input
						id="phone"
						type="tel"
						inputmode="numeric"
						maxlength="10"
						pattern="[0-9]{10}"
						bind:value={phoneNumber}
						placeholder="e.g., 9876543210"
						class="w-full rounded-xl border-slate-700/80 bg-slate-800/60 px-4 py-3.5 text-gray-100 placeholder-slate-500
							   transition-all duration-150 focus:border-teal-500 focus:bg-slate-800 focus:ring-2 focus:ring-teal-500"
						required
						aria-invalid={!!validationErrors.phone}
						aria-describedby={validationErrors.phone ? 'phone-error' : undefined}
					/>
					{#if validationErrors.phone}
						<p id="phone-error" class="mt-2 flex items-center text-xs text-red-400">
							<XCircle class="mr-1.5 h-3.5 w-3.5 shrink-0" />
							{validationErrors.phone}
						</p>
					{/if}
				</div>

				<div>
					<Label for="gender" class="mb-2 block text-sm font-medium text-slate-300">Gender</Label>
					<select
						id="gender"
						bind:value={selectedGender}
						class="w-full rounded-xl border border-slate-700/80 bg-slate-800/60 px-4 py-3.5 text-gray-100 transition-all duration-150 focus:border-teal-500 focus:ring-2 focus:ring-teal-500"
						aria-invalid={!!validationErrors.gender}
						aria-describedby={validationErrors.gender ? 'gender-error' : undefined}
					>
						<option value="" disabled selected>Select your gender</option>
						{#each genders as gender (gender.value)}
							<option value={gender.value}>{gender.label}</option>
						{/each}
					</select>
					{#if validationErrors.gender}
						<p id="gender-error" class="mt-2 flex items-center text-xs text-red-400">
							<XCircle class="mr-1.5 h-3.5 w-3.5 shrink-0" />
							{validationErrors.gender}
						</p>
					{/if}
				</div>

				{#if errorMessage}
					<p
						class="flex items-center justify-center rounded-xl border border-red-700/50 bg-red-900/30 p-3.5 text-center text-sm text-red-400"
					>
						<AlertTriangle class="mr-2.5 h-5 w-5 shrink-0 text-red-400" />
						{errorMessage}
					</p>
				{/if}

				<Button
					type="submit"
					disabled={isLoading}
					class="!mt-10 w-full transform rounded-xl bg-gradient-to-r from-teal-500 to-cyan-600
						   px-6 py-3.5 text-base font-semibold text-white shadow-lg transition-all duration-300
						   ease-out hover:scale-[1.03] hover:from-teal-600
						   hover:to-cyan-700 focus:outline-none focus-visible:ring-4 focus-visible:ring-teal-500/50 active:scale-100 disabled:cursor-not-allowed
						   disabled:bg-slate-600 disabled:from-slate-600 disabled:to-slate-500 disabled:opacity-60 disabled:hover:scale-100 sm:py-4"
				>
					{#if isLoading}
						<Loader2 class="mr-2.5 inline h-5 w-5 animate-spin align-middle" />
						<span class="align-middle">Saving...</span>
					{:else}
						<span class="align-middle">Complete Profile</span>
					{/if}
				</Button>
			</form>
		</div>
	</main>
	<footer class="py-8 text-center text-xs text-slate-500">
		© {new Date().getFullYear()} Horizoon. Your Adventure Awaits.
	</footer>
</div>

<style>
	:global(body.font-quicksand) {
		font-family: 'Quicksand', sans-serif;
	}
	.font-quicksand {
		font-family: 'Quicksand', sans-serif;
	}

	input[type='number'] {
		-moz-appearance: textfield;
	}
	input::-webkit-outer-spin-button,
	input::-webkit-inner-spin-button {
		-webkit-appearance: none;
		margin: 0;
	}
</style>
