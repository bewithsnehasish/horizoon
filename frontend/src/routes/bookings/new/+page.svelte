<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import axios from 'axios';
	import { fly, fade, slide } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';

	import {
		Loader2,
		AlertTriangle,
		ChevronLeft,
		ChevronRight,
		Star,
		CalendarDays,
		MapPin,
		CheckCircle2,
		XCircle,
		KeyRound,
		PartyPopper
	} from 'lucide-svelte';
	import { getAuthToken } from '$lib/stores/auth';

	// Interfaces
	interface Vehicle {
		id: string;
		name: string;
		brand: string;
		model: string;
		vehicle_type: string;
		image_1: string;
		rating: number;
		price_per_day: number;
		price_per_hour: number;
		security_deposit: number;
		late_fee_per_hour: number;
	}

	interface BookingResponseData {
		order_id: string;
		otp: string;
		message: string;
	}

	// State Variables
	let currentStep = 1;
	const totalSteps = 2;

	let vehicle: Vehicle | null = null;
	let loadingVehicle = true;
	let errorVehicle: string | null = null;

	let pickupDatetime = '';
	let returnDatetime = '';
	let checkingAvailability = false;
	let availabilityError: string | null = null;
	let isAvailable: boolean | null = null;

	let pickupLocation = '';
	let dropoffLocation = '';

	let bookingLoading = false;
	let bookingError: string | null = null;
	let estimatedCost: number | null = null;
	let bookingResponse: BookingResponseData | null = null;

	let formErrors: { [key: string]: string } = {};

	const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://0.0.0.0:8000';
	const vehicleApiUrl = `${API_BASE_URL}/business/vehicle_details/`;
	const availabilityApiUrl = `${API_BASE_URL}/business/booking/availability/`;
	const bookingApiUrl = `${API_BASE_URL}/business/booking/`;

	const authToken = getAuthToken();

	$: vehicleId = $page.url.searchParams.get('vehicleId') || '';

	let minPickupDateString = '';
	function updateMinPickupDate() {
		minPickupDateString = new Date(new Date().getTime() + 30 * 60 * 1000)
			.toISOString()
			.slice(0, 16);
	}
	onMount(updateMinPickupDate);

	function getImageSource(image: string | null): string {
		if (!image) return 'https://via.placeholder.com/800x600?text=No+Image';
		if (image.startsWith('data:image')) return image;
		return image;
	}

	function formatNumber(num: number): string {
		return num.toLocaleString('en-IN', {
			style: 'currency',
			currency: 'INR',
			minimumFractionDigits: 0
		});
	}

	function validateStep1(): boolean {
		formErrors = {};
		const now = new Date();
		const pickup = pickupDatetime ? new Date(pickupDatetime) : null;
		const returnDate = returnDatetime ? new Date(returnDatetime) : null;
		const minPickup = new Date(now.getTime() + 29 * 60 * 1000);

		if (!pickupDatetime) formErrors.pickupDatetime = 'Pickup date and time are required.';
		else if (pickup && pickup < minPickup)
			formErrors.pickupDatetime = 'Pickup must be at least 30 minutes from now.';

		if (!returnDatetime) formErrors.returnDatetime = 'Return date and time are required.';
		else if (pickup && returnDate && returnDate <= pickup) {
			formErrors.returnDatetime = 'Return date must be after pickup date.';
		}

		if (Object.keys(formErrors).length > 0) {
			isAvailable = null;
			availabilityError = null;
			estimatedCost = null;
		}
		return Object.keys(formErrors).length === 0;
	}

	function validateStep2(): boolean {
		formErrors = {};
		if (!pickupLocation.trim()) formErrors.pickupLocation = 'Pickup location is required.';
		if (!dropoffLocation.trim()) formErrors.dropoffLocation = 'Dropoff location is required.';
		return Object.keys(formErrors).length === 0;
	}

	function calculateEstimatedCost(): void {
		if (!vehicle || !pickupDatetime || !returnDatetime || !isAvailable) {
			estimatedCost = null;
			return;
		}
		const pickup = new Date(pickupDatetime);
		const returnD = new Date(returnDatetime);
		const durationMs = returnD.getTime() - pickup.getTime();

		if (durationMs <= 0) {
			estimatedCost = null;
			return;
		}

		const durationHours = durationMs / (1000 * 60 * 60);
		const durationDays = Math.ceil(durationHours / 24);

		if (durationHours < 1) {
			estimatedCost = vehicle.price_per_hour;
		} else if (durationHours < 24) {
			estimatedCost = Math.ceil(durationHours) * vehicle.price_per_hour;
		} else {
			estimatedCost = durationDays * vehicle.price_per_day;
		}
	}

	async function fetchVehicleDetails() {
		if (!vehicleId) {
			errorVehicle = 'No vehicle ID specified.';
			loadingVehicle = false;
			return;
		}
		loadingVehicle = true;
		errorVehicle = null;
		try {
			const response = await axios.post(vehicleApiUrl, { vehicle_id: vehicleId });
			if (response.data && response.data.vehicle) {
				vehicle = response.data.vehicle;
			} else {
				errorVehicle = response.data.message || 'Vehicle details not found.';
			}
		} catch (err: any) {
			console.error('Error fetching vehicle:', err);
			errorVehicle = 'Could not load vehicle details. Please try again.';
		} finally {
			loadingVehicle = false;
		}
	}

	async function handleCheckAvailability() {
		if (!validateStep1() || !vehicleId) {
			isAvailable = null;
			availabilityError = 'Please ensure valid dates are selected.';
			estimatedCost = null;
			return;
		}
		checkingAvailability = true;
		availabilityError = null;
		isAvailable = null;
		estimatedCost = null;

		try {
			await tick();
			const response = await axios.post(availabilityApiUrl, {
				vehicle_id: vehicleId,
				pickup_datetime: pickupDatetime,
				return_datetime: returnDatetime
			});
			if (response.data && typeof response.data.available === 'boolean') {
				isAvailable = response.data.available;
				if (isAvailable) {
					calculateEstimatedCost();
				} else {
					availabilityError = response.data.message || 'Vehicle not available for these dates.';
				}
			} else {
				availabilityError = 'Invalid availability response from server.';
			}
		} catch (err: any) {
			console.error('Error checking availability:', err);
			availabilityError =
				err.response?.data?.message || 'Could not check availability. Server error.';
		} finally {
			checkingAvailability = false;
		}
	}

	$: if (pickupDatetime && returnDatetime && vehicle && currentStep === 1) {
		if (validateStep1()) {
			handleCheckAvailability();
		} else {
			isAvailable = null;
			availabilityError = null;
			estimatedCost = null;
		}
	} else if (vehicle && currentStep === 1) {
		isAvailable = null;
		availabilityError = null;
		estimatedCost = null;
	}

	async function submitBooking() {
		if (!validateStep2() || !isAvailable || !authToken) return;

		bookingLoading = true;
		bookingError = null;
		try {
			const response = await axios.post(bookingApiUrl, {
				authToken,
				vehicle_id: vehicleId,
				pickup_datetime: pickupDatetime,
				return_datetime: returnDatetime,
				pickup_location: pickupLocation,
				dropoff_location: dropoffLocation
			});

			if (response.data.success) {
				bookingResponse = response.data;
				currentStep = 3;
				handleBookingSuccessAndRedirect();
			} else {
				bookingError = response.data.message || 'Booking failed. Please try again.';
			}
		} catch (err: any) {
			console.error('Error creating booking:', err);
			bookingError = err.response?.data?.message || 'An unexpected error occurred during booking.';
		} finally {
			bookingLoading = false;
		}
	}

	function nextStep() {
		if (currentStep === 1) {
			if (validateStep1() && isAvailable) currentStep = 2;
			else if (validateStep1() && !isAvailable && !availabilityError && !checkingAvailability) {
				handleCheckAvailability().then(() => {
					if (isAvailable) currentStep = 2;
				});
			} else if (!isAvailable && availabilityError) {
				formErrors.global = availabilityError;
			}
		} else if (currentStep === 2) {
			if (validateStep2()) {
				submitBooking();
			}
		}
	}

	function prevStep() {
		if (currentStep > 1) currentStep -= 1;
	}

	function handleBookingSuccessAndRedirect() {
		setTimeout(() => {
			goto('/');
		}, 7000);
	}

	onMount(() => {
		fetchVehicleDetails();
	});
</script>

<div class="font-quicksand min-h-screen bg-slate-950 text-gray-200 antialiased">
	<!-- Header -->
	<header class="sticky top-0 z-40 bg-slate-950/90 px-4 py-4 shadow-lg backdrop-blur-xl">
		<div class="mx-auto flex max-w-4xl items-center justify-between">
			{#if currentStep <= totalSteps}
				<button
					on:click={currentStep === 1 ? () => window.history.back() : prevStep}
					class="rounded-full p-2 transition-colors hover:bg-slate-800 active:bg-slate-700"
					aria-label="Go back"
				>
					<ChevronLeft class="h-6 w-6 text-slate-300" />
				</button>
			{:else}
				<div class="w-10"></div>
			{/if}
			<h1 class="truncate text-xl font-semibold text-gray-100 sm:text-2xl">
				{#if currentStep === 1}
					Choose Dates
				{:else if currentStep === 2}
					Location & Review
				{:else if currentStep === 3}
					Booking Confirmed!
				{:else}
					Book Your Ride
				{/if}
			</h1>
			<div class="w-10"></div>
		</div>
	</header>

	<main class="mx-auto max-w-4xl px-4 py-8 sm:px-6">
		{#if loadingVehicle}
			<div
				class="flex min-h-[70vh] flex-col items-center justify-center text-center"
				transition:fade={{ duration: 300 }}
			>
				<Loader2 class="mb-4 h-12 w-12 animate-spin text-teal-400" />
				<p class="text-lg font-medium text-slate-200">Loading Your Ride...</p>
				<p class="text-sm text-slate-400">Please wait a moment.</p>
			</div>
		{:else if errorVehicle}
			<div
				class="flex min-h-[70vh] flex-col items-center justify-center rounded-3xl bg-slate-900/80 p-8 text-center shadow-xl"
				transition:fade={{ duration: 300 }}
			>
				<AlertTriangle class="mb-4 h-16 w-16 text-red-400" />
				<h2 class="mb-2 text-xl font-semibold text-red-300">Error Loading Vehicle</h2>
				<p class="mb-6 max-w-md text-sm text-slate-400">{errorVehicle}</p>
				<button
					on:click={fetchVehicleDetails}
					class="rounded-full bg-gradient-to-r from-red-500 to-rose-600 px-6 py-2.5 font-semibold text-white shadow-md transition-transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-red-500/50"
				>
					Try Again
				</button>
			</div>
		{:else if vehicle}
			{#if currentStep <= totalSteps}
				<div
					class="mb-8 rounded-3xl bg-gradient-to-br from-slate-800/70 to-slate-900/50 p-6 shadow-lg"
					in:fade={{ delay: 100, duration: 400 }}
				>
					<div class="flex flex-col gap-4 sm:flex-row sm:items-center">
						<img
							src={getImageSource(vehicle.image_1)}
							alt="{vehicle.brand} {vehicle.name}"
							class="h-48 w-full rounded-2xl object-cover shadow-md sm:h-32 sm:w-48"
						/>
						<div class="flex-grow">
							<h2 class="text-2xl font-bold text-white sm:text-3xl">
								{vehicle.brand}
								{vehicle.name}
							</h2>
							<p class="text-sm text-slate-400">{vehicle.model} • {vehicle.vehicle_type}</p>
							<div class="mt-2 flex items-center gap-1.5">
								{#each { length: 5 } as _, i}
									<Star
										class="h-5 w-5 {i < Math.round(vehicle.rating)
											? 'fill-yellow-400 text-yellow-400'
											: 'text-slate-600'}"
									/>
								{/each}
								<span class="ml-2 text-sm font-medium text-slate-300"
									>{vehicle.rating.toFixed(1)}</span
								>
							</div>
						</div>
					</div>
				</div>
			{/if}

			<div class="relative">
				{#key currentStep}
					{#if currentStep === 1}
						<div
							class="space-y-6"
							in:fly={{ y: 30, duration: 400, easing: quintOut }}
							out:fly={{ y: -30, duration: 300 }}
						>
							<h3 class="text-xl font-semibold text-white">Select Your Dates</h3>
							<div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
								<div>
									<label for="pickupDatetime" class="mb-2 block text-sm font-medium text-slate-300"
										>Pickup Date & Time</label
									>
									<div class="relative">
										<CalendarDays
											class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-teal-400"
										/>
										<input
											type="datetime-local"
											id="pickupDatetime"
											bind:value={pickupDatetime}
											min={minPickupDateString}
											class="w-full rounded-xl border-2 border-slate-700 bg-slate-900/60 py-3 pl-10 pr-4 text-sm text-gray-100 placeholder-slate-500 transition-all focus:border-teal-400 focus:ring-2 focus:ring-teal-400/30"
											on:change={validateStep1}
											on:input={updateMinPickupDate}
										/>
									</div>
									{#if formErrors.pickupDatetime}
										<p class="mt-1 text-xs text-red-400">{formErrors.pickupDatetime}</p>
									{/if}
								</div>
								<div>
									<label for="returnDatetime" class="mb-2 block text-sm font-medium text-slate-300"
										>Return Date & Time</label
									>
									<div class="relative">
										<CalendarDays
											class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-teal-400"
										/>
										<input
											type="datetime-local"
											id="returnDatetime"
											bind:value={returnDatetime}
											min={pickupDatetime || minPickupDateString}
											class="w-full rounded-xl border-2 border-slate-700 bg-slate-900/60 py-3 pl-10 pr-4 text-sm text-gray-100 placeholder-slate-500 transition-all focus:border-teal-400 focus:ring-2 focus:ring-teal-400/30"
											on:change={validateStep1}
										/>
									</div>
									{#if formErrors.returnDatetime}
										<p class="mt-1 text-xs text-red-400">{formErrors.returnDatetime}</p>
									{/if}
								</div>
							</div>

							{#if pickupDatetime && returnDatetime}
								<div class="rounded-xl bg-slate-800/50 p-5" in:fade={{ duration: 300 }}>
									<h4 class="mb-3 text-sm font-semibold text-slate-200">Availability</h4>
									{#if checkingAvailability}
										<div class="flex items-center gap-2 text-sm text-slate-300">
											<Loader2 class="h-5 w-5 animate-spin text-teal-400" />
											Checking availability...
										</div>
									{:else if availabilityError && !isAvailable}
										<div class="flex items-center gap-2 text-sm text-red-400">
											<AlertTriangle class="h-5 w-5" />
											{availabilityError}
										</div>
									{:else if isAvailable === true}
										<div class="flex items-center gap-2 text-sm text-green-400">
											<CheckCircle2 class="h-5 w-5" />
											Vehicle is available!
										</div>
									{:else if isAvailable === false}
										<div class="flex items-center gap-2 text-sm text-red-400">
											<XCircle class="h-5 w-5" />
											Vehicle not available. Try different dates.
										</div>
									{:else if formErrors.pickupDatetime || formErrors.returnDatetime}
										<div class="flex items-center gap-2 text-sm text-yellow-400">
											<AlertTriangle class="h-5 w-5" />
											Please correct the errors above.
										</div>
									{:else}
										<p class="text-sm text-slate-400">Select dates to check availability.</p>
									{/if}
								</div>
							{/if}
						</div>

						<div class="mt-8 flex justify-end">
							<button
								on:click={nextStep}
								disabled={checkingAvailability ||
									!isAvailable ||
									Object.keys(formErrors).length > 0}
								class="flex items-center gap-2 rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-6 py-2.5 font-semibold text-white shadow-md transition-all hover:scale-105 focus:outline-none focus:ring-2 focus:ring-teal-400/50 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100"
							>
								Next
								<ChevronRight class="h-5 w-5" />
							</button>
						</div>
					{:else if currentStep === 2}
						<div
							class="space-y-6"
							in:fly={{ x: 30, duration: 400, easing: quintOut }}
							out:fly={{ x: -30, duration: 300 }}
						>
							<h3 class="text-xl font-semibold text-white">Pickup & Dropoff</h3>
							<div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
								<div>
									<label for="pickupLocation" class="mb-2 block text-sm font-medium text-slate-300"
										>Pickup Location</label
									>
									<div class="relative">
										<MapPin
											class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-teal-400"
										/>
										<input
											type="text"
											id="pickupLocation"
											bind:value={pickupLocation}
											placeholder="e.g., Airport Terminal 1"
											class="w-full rounded-xl border-2 border-slate-700 bg-slate-900/60 py-3 pl-10 pr-4 text-sm text-gray-100 placeholder-slate-500 transition-all focus:border-teal-400 focus:ring-2 focus:ring-teal-400/30"
											on:input={validateStep2}
										/>
									</div>
									{#if formErrors.pickupLocation}
										<p class="mt-1 text-xs text-red-400">{formErrors.pickupLocation}</p>
									{/if}
								</div>
								<div>
									<label for="dropoffLocation" class="mb-2 block text-sm font-medium text-slate-300"
										>Dropoff Location</label
									>
									<div class="relative">
										<MapPin
											class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-teal-400"
										/>
										<input
											type="text"
											id="dropoffLocation"
											bind:value={dropoffLocation}
											placeholder="e.g., Downtown Main Street"
											class="w-full rounded-xl border-2 border-slate-700 bg-slate-900/60 py-3 pl-10 pr-4 text-sm text-gray-100 placeholder-slate-500 transition-all focus:border-teal-400 focus:ring-2 focus:ring-teal-400/30"
											on:input={validateStep2}
										/>
									</div>
									{#if formErrors.dropoffLocation}
										<p class="mt-1 text-xs text-red-400">{formErrors.dropoffLocation}</p>
									{/if}
								</div>
							</div>

							{#if estimatedCost}
								<div class="rounded-xl bg-slate-900/50 p-5" in:fade={{ duration: 300 }}>
									<h4 class="mb-3 text-lg font-semibold text-white">Cost Summary</h4>
									<div class="space-y-2 text-sm">
										<div class="flex justify-between">
											<span class="text-slate-400"
												>Rental ({new Date(pickupDatetime).toLocaleDateString()} - {new Date(
													returnDatetime
												).toLocaleDateString()})</span
											>
											<span class="font-medium text-gray-100">{formatNumber(estimatedCost)}</span>
										</div>
										<div class="flex justify-between">
											<span class="text-slate-400">Security Deposit (Refundable)</span>
											<span class="font-medium text-gray-100"
												>{formatNumber(vehicle.security_deposit)}</span
											>
										</div>
										<hr class="my-2 border-slate-700" />
										<div class="flex justify-between text-base font-semibold">
											<span class="text-white">Total Payable</span>
											<span class="text-teal-400"
												>{formatNumber(estimatedCost + vehicle.security_deposit)}</span
											>
										</div>
									</div>
									<p class="mt-3 text-xs text-slate-500">
										Final charges may vary based on usage. Security deposit refunded post-trip.
									</p>
								</div>
							{/if}

							{#if bookingError}
								<div
									class="flex items-center gap-2 rounded-xl bg-red-600/20 p-4 text-sm text-red-300"
									transition:slide={{ duration: 300 }}
								>
									<AlertTriangle class="h-5 w-5" />
									{bookingError}
								</div>
							{/if}

							<div class="mt-8 flex items-center justify-between">
								<button
									on:click={prevStep}
									class="rounded-full bg-slate-700 px-6 py-2.5 text-sm font-semibold text-slate-200 transition-all hover:bg-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-500"
								>
									Back
								</button>
								<button
									on:click={submitBooking}
									disabled={bookingLoading ||
										Object.keys(formErrors).length > 0 ||
										!pickupLocation.trim() ||
										!dropoffLocation.trim()}
									class="flex items-center gap-2 rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-6 py-2.5 font-semibold text-white shadow-md transition-all hover:scale-105 focus:outline-none focus:ring-2 focus:ring-teal-400/50 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100"
								>
									{#if bookingLoading}
										<Loader2 class="h-5 w-5 animate-spin" />
										Processing...
									{:else}
										Confirm Booking
									{/if}
								</button>
							</div>
						</div>
					{:else if currentStep === 3 && bookingResponse}
						<div
							class="flex min-h-[60vh] flex-col items-center justify-center text-center"
							in:fly={{ y: 30, duration: 500, easing: quintOut }}
						>
							<PartyPopper class="mb-4 h-16 w-16 animate-bounce text-teal-400" />
							<h2
								class="mb-3 bg-gradient-to-r from-teal-400 to-cyan-500 bg-clip-text text-2xl font-bold text-transparent sm:text-3xl"
							>
								Booking Confirmed!
							</h2>
							<p class="mb-4 max-w-md text-sm text-slate-300">
								Your {vehicle.brand}
								{vehicle.name} is ready for your journey!
							</p>
							<p class="mb-6 text-sm text-slate-400">
								Order ID: <span class="font-mono text-slate-200">{bookingResponse.order_id}</span>
							</p>

							<div class="rounded-2xl border border-teal-500/20 bg-slate-900/60 p-6 shadow-lg">
								<p class="mb-2 text-lg font-semibold text-slate-200">Your OTP</p>
								<div class="my-3 flex items-center justify-center gap-2">
									<KeyRound class="h-6 w-6 text-teal-400" />
									<p
										class="rounded-lg bg-slate-900/50 px-4 py-2 text-3xl font-bold tracking-wider text-teal-300"
									>
										{bookingResponse.otp}
									</p>
								</div>
								<p class="mt-2 text-xs text-slate-500">Present this OTP for pickup verification.</p>
							</div>

							<p class="mt-6 text-sm text-slate-400">Redirecting to homepage in a few seconds...</p>
							<div class="mt-2 h-1 w-full max-w-sm overflow-hidden rounded-full bg-slate-700">
								<div class="animate-redirect-progress h-1 rounded-full bg-teal-400"></div>
							</div>
						</div>
					{/if}
				{/key}
			</div>
		{/if}
	</main>
</div>

<style>
	:global(.font-quicksand) {
		font-family: 'Quicksand', sans-serif;
	}
	input[type='datetime-local']::-webkit-calendar-picker-indicator {
		filter: invert(0.7) brightness(1.2) sepia(0.4) hue-rotate(140deg);
		cursor: pointer;
		opacity: 0.8;
	}
	input[type='datetime-local']::-webkit-calendar-picker-indicator:hover {
		opacity: 1;
	}

	@keyframes redirect-progress {
		0% {
			width: 0%;
		}
		100% {
			width: 100%;
		}
	}
	.animate-redirect-progress {
		animation: redirect-progress 7s linear forwards;
	}

	@keyframes bounce {
		0%,
		100% {
			transform: translateY(-8%);
			animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
		}
		50% {
			transform: translateY(0);
			animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
		}
	}
	.animate-bounce {
		animation: bounce 1.5s infinite;
	}
</style>
