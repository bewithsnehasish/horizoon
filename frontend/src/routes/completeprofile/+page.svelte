<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import {
		Select,
		SelectContent,
		SelectGroup,
		SelectItem,
		SelectTrigger,
		SelectValue
	} from '$lib/components/ui/select';
	import { ArrowLeft, Loader2 } from 'lucide-svelte';
	import { getAuthToken } from '$lib/stores/auth'; // Ensure this store and function are correctly set up

	let name: string = '';
	let phoneNumber: string = '';
	let selectedGender: string | undefined = undefined; // Make sure your Select component handles undefined initial value correctly or provide a default
	let errorMessage: string = '';
	let validationErrors: { [key: string]: string } = {};
	let isLoading: boolean = false;

	const genders = [
		{ value: 'Male', label: 'Male' },
		{ value: 'Female', label: 'Female' },
		{ value: 'Other', label: 'Other' },
		{ value: 'Prefer not to say', label: 'Prefer not to say' }
	];

	function goBack() {
		if (typeof window !== 'undefined' && window.history.length > 1) {
			window.history.back();
		} else {
			goto('/'); // Fallback to home page
		}
	}

	// Validate form inputs
	const validateForm = () => {
		const errors: { [key: string]: string } = {};

		if (!name || name.trim().length < 2) {
			errors.name = 'Full name must be at least 2 characters.';
		}

		// A more common international phone number regex, allowing optional '+' and digits
		const phoneRegex = /^\+?[0-9]{7,15}$/; // Allows 7-15 digits after optional +
		if (!phoneNumber || !phoneRegex.test(phoneNumber.trim())) {
			errors.phone = 'Please enter a valid phone number (e.g., +1 123 456 7890).';
		}

		if (!selectedGender) {
			errors.gender = 'Please select your gender.';
		}

		validationErrors = errors;
		return Object.keys(errors).length === 0;
	};

	async function handleSubmitProfile() {
		errorMessage = '';
		validationErrors = {};

		if (!validateForm()) {
			return;
		}

		const authToken = getAuthToken();
		if (!authToken) {
			errorMessage = 'Authentication required. Please log in again.';
			goto('/login'); // Ensure you have a login route
			return;
		}

		const payload = {
			name: name.trim(),
			phone: phoneNumber.trim(),
			gender: selectedGender
		};

		isLoading = true;
		try {
			// Ensure VITE_API_BASE_URL is set in your .env file
			const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'; // Provide a sensible fallback
			const response = await fetch(`${API_BASE_URL}/authentication/add-details/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${authToken}` // Standard way to send token
				},
				body: JSON.stringify(payload)
			});

			const data = await response.json();

			if (response.ok && data.success) {
				console.log('Profile submission successful:', data.message);
				goto('/dashboard'); // Or desired next page, e.g., user dashboard
			} else {
				let specificError = 'Failed to submit profile. Please try again.';
				if (data && data.message) {
					specificError = data.message;
				} else if (!response.ok) {
					specificError = `Server error (${response.status}). Please try again later.`;
				}
				errorMessage = specificError;
			}
		} catch (error) {
			console.error('Profile submission error:', error);
			errorMessage = 'A network error occurred. Please check your connection and try again.';
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Complete Your Profile | Horizoon</title>
	<meta
		name="description"
		content="Complete your profile to personalize your Horizoon car rental experience."
	/>
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
		<div
			class="w-full max-w-md transform space-y-8 rounded-3xl bg-slate-900 p-6 shadow-2xl transition-all duration-500 ease-out sm:p-10"
		>
			<div class="text-center">
				<h1 class="text-3xl font-bold tracking-tight text-white sm:text-4xl">Almost There!</h1>
				<p class="mt-2.5 text-sm leading-relaxed text-slate-400">
					Tell us a bit more about yourself to personalize your <span
						class="font-semibold text-teal-400">Horizoon</span
					> experience.
				</p>
			</div>

			<form on:submit|preventDefault={handleSubmitProfile} class="space-y-6 sm:space-y-7">
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
						>Phone Number</Label
					>
					<Input
						id="phone"
						type="tel"
						bind:value={phoneNumber}
						placeholder="e.g., +1 123 456 7890"
						class="w-full rounded-xl border-slate-700/80 bg-slate-800/60 px-4 py-3.5 text-gray-100 placeholder-slate-500
							   transition-all duration-150 focus:border-teal-500 focus:bg-slate-800 focus:ring-2 focus:ring-teal-500"
						required
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
					<Select bind:value={selectedGender}>
						<SelectTrigger
							id="gender"
							class="w-full rounded-xl border-slate-700/80 bg-slate-800/60 px-4 py-3.5 text-gray-100
								   transition-all duration-150 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 data-[placeholder]:text-slate-500"
							aria-describedby={validationErrors.gender ? 'gender-error' : undefined}
						>
							<SelectValue placeholder="Choose your gender" />
						</SelectTrigger>
						<SelectContent
							class="z-50 rounded-xl border-slate-700 bg-slate-800 p-1.5 text-gray-200 shadow-xl"
						>
							<SelectGroup>
								{#each genders as gender (gender.value)}
									<SelectItem
										value={gender.value}
										class="rounded-lg px-3 py-2 hover:bg-teal-500/20 focus:bg-teal-500/30 data-[state=checked]:bg-teal-600/25 data-[state=checked]:text-teal-300"
									>
										{gender.label}
									</SelectItem>
								{/each}
							</SelectGroup>
						</SelectContent>
					</Select>
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
						   ease-out hover:scale-105 hover:from-teal-600
						   hover:to-cyan-700 focus:outline-none focus-visible:ring-4 focus-visible:ring-teal-500/50 active:scale-100 disabled:cursor-not-allowed
						   disabled:bg-slate-600 disabled:from-slate-600 disabled:to-slate-500 disabled:opacity-60 disabled:hover:scale-100 sm:py-4"
				>
					{#if isLoading}
						<Loader2 class="mr-2.5 inline h-5 w-5 animate-spin" />
						<span>Saving Profile...</span>
					{:else}
						Complete Profile & Drive
					{/if}
				</Button>
			</form>
		</div>
	</main>
	<footer class="py-8 text-center text-xs text-slate-500">
		© {new Date().getFullYear()} Horizoon Car Rentals. Drive Your Dreams.
	</footer>
</div>

<style>
	:global(.font-quicksand) {
		font-family: 'Quicksand', sans-serif;
	}
	:global(.backdrop-blur-lg) {
		/* If not already globally defined by Tailwind */
		backdrop-filter: blur(12px);
	}

	/* For Firefox to remove number input spinners - if you use type=number specifically */
	input[type='number'] {
		-moz-appearance: textfield;
	}
	/* For Chrome, Safari, Edge, Opera - if you use type=number specifically */
	input::-webkit-outer-spin-button,
	input::-webkit-inner-spin-button {
		-webkit-appearance: none;
		margin: 0;
	}
</style>
