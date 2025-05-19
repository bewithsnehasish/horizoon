<!-- src/routes/completeprofile/+page.svelte -->
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
	import { ArrowLeft } from 'lucide-svelte';
	import { getAuthToken } from '$lib/stores/auth';

	let name: string = '';
	let phoneNumber: string = '';
	let selectedGender: string | undefined = undefined;
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
		if (window.history.length > 1) {
			window.history.back();
		} else {
			goto('/');
		}
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
		if (!phoneNumber || !phoneRegex.test(phoneNumber)) {
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
		const authToken = getAuthToken();
		if (!authToken) {
			errorMessage = 'Authentication token not found. Please log in again.';
			goto('/login');
			return;
		}

		// Prepare payload with just the phone number
		const payload = {
			authToken,
			name,
			phone: phoneNumber, // Send only the phone number
			gender: selectedGender
		};

		isLoading = true;
		try {
			const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
			const response = await fetch(`${API_BASE_URL}/authentication/add-details/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});

			const data = await response.json();

			if (data.success) {
				console.log('Profile submission successful:', data.message);
				goto('/dashboard');
			} else {
				errorMessage = data.message || 'Failed to submit profile Please try again';
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
	<title>Complete Your Profile</title>
</svelte:head>

<div class="flex min-h-screen flex-col bg-white font-sans text-gray-800">
	<header class="sticky top-0 z-10 bg-white px-4 pb-2 pt-4">
		<Button
			variant="ghost"
			size="icon"
			class="rounded-full p-2 text-gray-700 hover:bg-gray-100"
			on:click={goBack}
			aria-label="Go back"
		>
			<ArrowLeft class="h-6 w-6" />
		</Button>
	</header>

	<main class="flex flex-grow flex-col items-center px-6 py-4">
		<div class="w-full max-w-sm space-y-8">
			<div>
				<h1 class="mt-16 text-center text-2xl font-semibold text-gray-900 md:text-3xl">
					Complete Your Profile
				</h1>
				<p class="mt-2 text-center text-sm text-gray-500">
					Don't worry, only you can see your personal data. No one else will be able to see it.
				</p>
			</div>

			<form on:submit|preventDefault={handleSubmitProfile} class="space-y-6">
				<div>
					<Label for="name" class="mb-1 block text-sm font-medium text-gray-700">Name</Label>
					<Input
						id="name"
						type="text"
						bind:value={name}
						placeholder="Ex: John Doe"
						class="focus:border-primary-500 border-gray-300 bg-gray-100 text-gray-800 placeholder-gray-400 focus:bg-white"
						required
					/>
					{#if validationErrors.name}
						<p class="mt-1 text-sm text-red-500">{validationErrors.name}</p>
					{/if}
				</div>

				<div>
					<Label for="phone" class="mb-1 block text-sm font-medium text-gray-700"
						>Phone Number</Label
					>
					<Input
						id="phone"
						type="number"
						bind:value={phoneNumber}
						placeholder="Enter the Phone Number"
						class="focus:border-primary-500 border-gray-300 bg-gray-100 text-gray-800 placeholder-gray-400 focus:bg-white"
						required
					/>
					{#if validationErrors.phone}
						<p class="mt-1 text-sm text-red-500">{validationErrors.phone}</p>
					{/if}
				</div>

				<div>
					<Label for="gender" class="mb-1 block text-sm font-medium text-gray-700">Gender</Label>
					<Select bind:selected={selectedGender}>
						<SelectTrigger
							id="gender"
							class="focus:ring-primary-500 focus:border-primary-500 w-full border-gray-300 bg-gray-100 text-gray-800 placeholder-gray-400 focus:bg-white focus:ring-1"
						>
							<SelectValue placeholder="Select" />
						</SelectTrigger>
						<SelectContent class="bg-white">
							<SelectGroup>
								{#each genders as gender (gender.value)}
									<SelectItem value={gender.value} class="text-gray-700">{gender.label}</SelectItem>
								{/each}
							</SelectGroup>
						</SelectContent>
					</Select>
					{#if validationErrors.gender}
						<p class="mt-1 text-sm text-red-500">{validationErrors.gender}</p>
					{/if}
				</div>

				{#if errorMessage}
					<p class="text-center text-sm text-red-500">{errorMessage}</p>
				{/if}

				<Button
					type="submit"
					disabled={isLoading}
					class="!mt-10 w-full rounded-xl bg-gray-600 py-3 text-base font-semibold text-white hover:bg-gray-700"
				>
					{#if isLoading}
						<span class="animate-pulse">Submitting...</span>
					{:else}
						Complete Profile
					{/if}
				</Button>
			</form>
		</div>
	</main>
</div>
