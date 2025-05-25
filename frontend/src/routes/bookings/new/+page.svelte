<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';
	import axios from 'axios';
	import { fly, fade, slide, scale, blur } from 'svelte/transition';
	import { quintOut, backOut, elasticOut } from 'svelte/easing';
	import LocationPicker from '$lib/components/LocationPicker.svelte';

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
		PartyPopper,
		Clock,
		Fuel,
		Users,
		Shield,
		CreditCard,
		Navigation,
		Sparkles,
		Car,
		Zap,
		Info,
		AlertCircle,
		Check,
		ArrowRight,
		Calendar,
		Timer,
		DollarSign,
		Award,
		Target,
		Plus,
		Minus
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
		seating_capacity?: number;
		fuel_type?: string;
		transmission?: string;
	}

	interface BookingResponseData {
		order_id: string;
		otp: string;
		message: string;
	}

	interface LocationData {
		lat: number;
		lng: number;
		address: string;
		name?: string;
	}

	// State Variables
	let currentStep = 1;
	const totalSteps = 3;

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
	let pickupLocationData: LocationData | null = null;
	let dropoffLocationData: LocationData | null = null;

	let bookingLoading = false;
	let bookingError: string | null = null;
	let estimatedCost: number | null = null;
	let bookingResponse: BookingResponseData | null = null;

	let formErrors: { [key: string]: string } = {};
	let slideDirection = 1; // 1 for forward, -1 for backward

	let vehicleId = '';
	let showSuccessAnimation = false;
	let progressWidth = 0;

	// Location picker state
	let showLocationPicker = false;
	let locationPickerType: 'pickup' | 'dropoff' = 'pickup';

	const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://0.0.0.0:8000';
	const vehicleApiUrl = `${API_BASE_URL}/business/vehicle_details/`;
	const availabilityApiUrl = `${API_BASE_URL}/business/booking/availability/`;
	const bookingApiUrl = `https://horizoon.onrender.com/business/booking/`;

	const authToken = getAuthToken();

	// Extract vehicleId only in browser context
	$: if (browser) {
		vehicleId = $page.url.searchParams.get('vehicleId') || '';
		console.log('Extracted vehicleId:', vehicleId);
	}

	// Progress calculation
	$: progressWidth = (currentStep / totalSteps) * 100;

	// Redirect if no auth token
	onMount(() => {
		if (!authToken) {
			console.log('No auth token found, redirecting to /intro');
			goto('/intro', { replaceState: true });
			return;
		}
		fetchVehicleDetails();
	});

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

	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			weekday: 'short',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function calculateDuration(): string {
		if (!pickupDatetime || !returnDatetime) return '';
		const pickup = new Date(pickupDatetime);
		const returnD = new Date(returnDatetime);
		const durationMs = returnD.getTime() - pickup.getTime();
		const hours = Math.floor(durationMs / (1000 * 60 * 60));
		const days = Math.floor(hours / 24);
		const remainingHours = hours % 24;

		if (days > 0) {
			return `${days}d ${remainingHours}h`;
		}
		return `${hours}h`;
	}

	// Location Handlers
	function openLocationPicker(type: 'pickup' | 'dropoff') {
		locationPickerType = type;
		showLocationPicker = true;
	}

	function handleLocationSelected(event: CustomEvent<LocationData>) {
		const locationData = event.detail;

		if (locationPickerType === 'pickup') {
			pickupLocationData = locationData;
			pickupLocation = locationData.address;
		} else {
			dropoffLocationData = locationData;
			dropoffLocation = locationData.address;
		}

		showLocationPicker = false;
		validateStep2();
	}

	function handleLocationCleared() {
		if (locationPickerType === 'pickup') {
			pickupLocationData = null;
			pickupLocation = '';
		} else {
			dropoffLocationData = null;
			dropoffLocation = '';
		}

		showLocationPicker = false;
		validateStep2();
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

	// Create datetime format for API
	function createDateTime(date: string, time: string): string {
		return `${date}T${time}:00`;
	}

	async function submitBooking() {
		if (!validateStep2() || !isAvailable || !authToken) {
			if (!authToken) {
				bookingError = 'Authentication required. Please log in.';
				setTimeout(() => goto('/intro'), 1000);
			}
			return;
		}

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
				showSuccessAnimation = true;
				setTimeout(() => {
					currentStep = 3;
				}, 1500);
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
			if (validateStep1() && isAvailable) {
				slideDirection = 1;
				currentStep = 2;
			} else if (validateStep1() && !isAvailable && !availabilityError && !checkingAvailability) {
				handleCheckAvailability().then(() => {
					if (isAvailable) {
						slideDirection = 1;
						currentStep = 2;
					}
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
		if (currentStep > 1) {
			slideDirection = -1;
			currentStep -= 1;
		}
	}

	function handleBookingSuccessAndRedirect() {
		setTimeout(() => {
			goto('/bookings');
		}, 7000);
	}

	// Step configurations
	const stepConfig = [
		{
			title: 'Choose Dates',
			subtitle: 'When do you need the car?',
			icon: Calendar,
			color: 'text-sky-400',
			bg: 'bg-sky-500/20'
		},
		{
			title: 'Location & Review',
			subtitle: 'Where will you pick it up?',
			icon: MapPin,
			color: 'text-emerald-400',
			bg: 'bg-emerald-500/20'
		},
		{
			title: 'Booking Complete',
			subtitle: 'Your ride is confirmed!',
			icon: CheckCircle2,
			color: 'text-teal-400',
			bg: 'bg-teal-500/20'
		}
	];

	const vehicleFeatures = [
		{ icon: Users, label: 'Seats', value: vehicle?.seating_capacity || '4' },
		{ icon: Fuel, label: 'Fuel', value: vehicle?.fuel_type || 'Petrol' },
		{ icon: Zap, label: 'Type', value: vehicle?.transmission || 'Manual' }
	];
</script>

<!-- Global Location Picker Modal -->
{#if showLocationPicker}
	<div class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm">
		<div class="flex h-full items-center justify-center p-4">
			<div class="w-full max-w-4xl">
				<LocationPicker
					label="{locationPickerType === 'pickup' ? 'Pickup' : 'Drop-off'} Location"
					placeholder="Select {locationPickerType} location..."
					initialLocation={locationPickerType === 'pickup' ? pickupLocation : dropoffLocation}
					on:locationSelected={handleLocationSelected}
					on:locationCleared={handleLocationCleared}
				/>
				<div class="mt-4 flex justify-center">
					<button
						on:click={() => (showLocationPicker = false)}
						class="rounded-xl bg-slate-700 px-6 py-3 font-medium text-slate-300 transition-all duration-200 hover:bg-slate-600"
					>
						Cancel
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<div class="font-quicksand min-h-screen bg-slate-950 text-gray-200 antialiased">
	<!-- Enhanced Mobile Header -->
	<header
		class="sticky top-0 z-40 border-b border-slate-700/50 bg-gradient-to-r from-slate-900/95 to-slate-800/95 backdrop-blur-xl"
	>
		<div class="px-4 py-3">
			<!-- Top Row -->
			<div class="mb-3 flex items-center justify-between">
				<button
					on:click={currentStep === 1 ? () => window.history.back() : prevStep}
					class="rounded-full bg-slate-800/60 p-2.5 text-slate-300 transition-all duration-200 hover:bg-slate-700 hover:text-teal-400"
					aria-label="Go back"
				>
					<ChevronLeft class="h-5 w-5" />
				</button>

				<div class="flex-1 text-center">
					<h1 class="text-xl font-bold text-gray-100">
						{stepConfig[currentStep - 1]?.title || 'Book Your Ride'}
					</h1>
					<p class="text-sm text-slate-400">
						{stepConfig[currentStep - 1]?.subtitle || ''}
					</p>
				</div>

				<div class="flex w-10 justify-end">
					{#if currentStep <= totalSteps}
						<div class="rounded-full bg-slate-800/60 px-3 py-1 text-sm font-medium text-slate-300">
							{currentStep}/{totalSteps}
						</div>
					{/if}
				</div>
			</div>

			<!-- Enhanced Progress Bar -->
			<div class="relative">
				<div class="h-2 overflow-hidden rounded-full bg-slate-800">
					<div
						class="h-full rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 transition-all duration-700 ease-out"
						style="width: {progressWidth}%"
					></div>
				</div>
				<!-- Step indicators -->
				<div class="mt-2 flex justify-between">
					{#each stepConfig as step, index}
						<div class="flex flex-col items-center">
							<div
								class="flex h-8 w-8 items-center justify-center rounded-full border-2 transition-all duration-300 {index +
									1 <=
								currentStep
									? 'border-teal-500 bg-gradient-to-r from-teal-500 to-cyan-600 text-white'
									: 'border-slate-600 text-slate-500'}"
							>
								<svelte:component this={step.icon} class="h-4 w-4" />
							</div>
						</div>
					{/each}
				</div>
			</div>
		</div>
	</header>

	<main class="px-4 py-6">
		{#if loadingVehicle}
			<div
				class="flex min-h-[70vh] flex-col items-center justify-center text-center"
				transition:fade={{ duration: 300 }}
			>
				<div class="relative mb-6">
					<div
						class="h-20 w-20 animate-pulse rounded-full bg-gradient-to-r from-teal-500 to-cyan-600"
					></div>
					<Loader2 class="absolute inset-0 m-auto h-8 w-8 animate-spin text-white" />
				</div>
				<p class="mb-2 text-lg font-medium text-slate-200">Loading Your Ride...</p>
				<p class="text-sm text-slate-400">Setting up your booking experience</p>
			</div>
		{:else if errorVehicle}
			<div
				class="flex min-h-[70vh] flex-col items-center justify-center rounded-3xl border border-slate-700/50 bg-slate-900/80 p-8 text-center shadow-xl backdrop-blur-sm"
				transition:fade={{ duration: 300 }}
			>
				<div class="mb-6 rounded-full bg-red-500/20 p-4">
					<AlertTriangle class="h-12 w-12 text-red-400" />
				</div>
				<h2 class="mb-2 text-xl font-semibold text-red-300">Error Loading Vehicle</h2>
				<p class="mb-6 max-w-md text-sm leading-relaxed text-slate-400">{errorVehicle}</p>
				<button
					on:click={fetchVehicleDetails}
					class="rounded-2xl bg-gradient-to-r from-red-500 to-rose-600 px-8 py-3 font-semibold text-white shadow-lg transition-all duration-200 hover:scale-105 hover:shadow-xl"
				>
					Try Again
				</button>
			</div>
		{:else if vehicle}
			<!-- Enhanced Vehicle Display Card -->
			{#if currentStep <= 2}
				<section
					class="mb-6 overflow-hidden rounded-3xl border border-slate-700/50 bg-gradient-to-br from-slate-800/80 to-slate-900/80 shadow-2xl backdrop-blur-sm"
					in:fade={{ delay: 100, duration: 400 }}
				>
					<div class="relative">
						<!-- Background Effects -->
						<div
							class="absolute -right-20 -top-16 h-40 w-40 rounded-full bg-teal-600/20 opacity-70 blur-3xl"
						></div>
						<div
							class="absolute -bottom-10 -left-16 h-48 w-48 rounded-full bg-cyan-600/10 opacity-60 blur-3xl"
						></div>

						<div class="relative z-10 p-6">
							<div class="flex flex-col gap-6 sm:flex-row">
								<!-- Vehicle Image -->
								<div class="relative flex-shrink-0">
									<img
										src={getImageSource(vehicle.image_1)}
										alt="{vehicle.brand} {vehicle.name}"
										class="h-40 w-full rounded-2xl border border-slate-700/50 object-cover shadow-lg sm:h-32 sm:w-48"
									/>
									<div class="absolute left-3 top-3">
										<div
											class="flex items-center gap-1 rounded-full bg-slate-900/80 px-3 py-1 backdrop-blur-sm"
										>
											<Star class="h-4 w-4 fill-yellow-400 text-yellow-400" />
											<span class="text-sm font-medium text-white">{vehicle.rating.toFixed(1)}</span
											>
										</div>
									</div>
								</div>

								<!-- Vehicle Details -->
								<div class="flex-1">
									<div class="mb-4">
										<h2
											class="mb-1 bg-gradient-to-r from-gray-100 to-slate-300 bg-clip-text text-2xl font-bold text-transparent"
										>
											{vehicle.brand}
											{vehicle.name}
										</h2>
										<p class="mb-3 text-sm text-slate-400">
											{vehicle.model} • {vehicle.vehicle_type}
										</p>

										<!-- Vehicle Features Grid -->
										<div class="grid grid-cols-3 gap-3">
											{#each vehicleFeatures as feature}
												<div
													class="rounded-xl border border-slate-700/30 bg-slate-900/50 p-3 text-center"
												>
													<div class="mb-1 flex items-center justify-center">
														<svelte:component this={feature.icon} class="h-4 w-4 text-teal-400" />
													</div>
													<p class="mb-1 text-xs text-slate-400">{feature.label}</p>
													<p class="text-sm font-semibold text-gray-200">{feature.value}</p>
												</div>
											{/each}
										</div>
									</div>

									<!-- Pricing Display -->
									<div
										class="flex items-center justify-between rounded-2xl border border-slate-700/30 bg-slate-900/30 p-4"
									>
										<div>
											<p class="mb-1 text-xs text-slate-400">Starting from</p>
											<p class="text-xl font-bold text-teal-400">
												{formatNumber(vehicle.price_per_day)}
											</p>
											<p class="text-xs text-slate-500">per day</p>
										</div>
										<div class="text-right">
											<p class="mb-1 text-xs text-slate-400">Hourly rate</p>
											<p class="text-sm font-semibold text-gray-200">
												{formatNumber(vehicle.price_per_hour)}
											</p>
											<p class="text-xs text-slate-500">per hour</p>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</section>
			{/if}

			<!-- Step Content with Enhanced Animations -->
			<div class="relative min-h-[400px]">
				{#key currentStep}
					{#if currentStep === 1}
						<!-- Step 1: Date Selection -->
						<div
							class="space-y-6"
							in:fly={{
								x: slideDirection * 300,
								duration: 500,
								easing: quintOut
							}}
							out:fly={{
								x: slideDirection * -300,
								duration: 300,
								easing: quintOut
							}}
						>
							<div class="mb-6 text-center">
								<div
									class="mx-auto mb-4 h-16 w-16 rounded-full border border-sky-500/30 bg-sky-500/20 p-4"
								>
									<Calendar class="mx-auto h-8 w-8 text-sky-400" />
								</div>
								<h3 class="mb-2 text-2xl font-bold text-white">When do you need it?</h3>
								<p class="text-slate-400">Select your pickup and return dates</p>
							</div>

							<!-- Enhanced Date Inputs -->
							<div class="space-y-4">
								<!-- Pickup Date -->
								<div
									class="rounded-2xl border border-slate-700/50 bg-slate-800/50 p-5 backdrop-blur-sm"
								>
									<label
										for="pickupDatetime"
										class="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-300"
									>
										<div class="rounded-full bg-green-500/20 p-1">
											<Navigation class="h-4 w-4 text-green-400" />
										</div>
										Pickup Date & Time
									</label>
									<div class="relative">
										<CalendarDays
											class="absolute left-4 top-1/2 z-10 h-5 w-5 -translate-y-1/2 text-teal-400"
										/>
										<input
											type="datetime-local"
											id="pickupDatetime"
											bind:value={pickupDatetime}
											min={minPickupDateString}
											class="w-full rounded-xl border-2 border-slate-700 bg-slate-900/60 py-4 pl-12 pr-4 text-gray-100 placeholder-slate-500 transition-all duration-200 hover:border-slate-600 focus:border-teal-400 focus:ring-2 focus:ring-teal-400/30"
											on:change={validateStep1}
											on:input={updateMinPickupDate}
										/>
									</div>
									{#if formErrors.pickupDatetime}
										<p
											class="mt-2 flex items-center gap-1 text-sm text-red-400"
											transition:slide={{ duration: 200 }}
										>
											<AlertCircle class="h-4 w-4" />
											{formErrors.pickupDatetime}
										</p>
									{/if}
								</div>

								<!-- Return Date -->
								<div
									class="rounded-2xl border border-slate-700/50 bg-slate-800/50 p-5 backdrop-blur-sm"
								>
									<label
										for="returnDatetime"
										class="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-300"
									>
										<div class="rounded-full bg-red-500/20 p-1">
											<MapPin class="h-4 w-4 text-red-400" />
										</div>
										Return Date & Time
									</label>
									<div class="relative">
										<CalendarDays
											class="absolute left-4 top-1/2 z-10 h-5 w-5 -translate-y-1/2 text-teal-400"
										/>
										<input
											type="datetime-local"
											id="returnDatetime"
											bind:value={returnDatetime}
											min={pickupDatetime || minPickupDateString}
											class="w-full rounded-xl border-2 border-slate-700 bg-slate-900/60 py-4 pl-12 pr-4 text-gray-100 placeholder-slate-500 transition-all duration-200 hover:border-slate-600 focus:border-teal-400 focus:ring-2 focus:ring-teal-400/30"
											on:change={validateStep1}
										/>
									</div>
									{#if formErrors.returnDatetime}
										<p
											class="mt-2 flex items-center gap-1 text-sm text-red-400"
											transition:slide={{ duration: 200 }}
										>
											<AlertCircle class="h-4 w-4" />
											{formErrors.returnDatetime}
										</p>
									{/if}
								</div>

								<!-- Duration Display -->
								{#if pickupDatetime && returnDatetime && !formErrors.pickupDatetime && !formErrors.returnDatetime}
									<div
										class="rounded-2xl border border-teal-500/30 bg-gradient-to-r from-teal-500/10 to-cyan-500/10 p-4"
										in:scale={{ duration: 300, easing: backOut }}
									>
										<div class="flex items-center justify-between">
											<div class="flex items-center gap-2">
												<Timer class="h-5 w-5 text-teal-400" />
												<span class="text-sm font-medium text-slate-300">Duration</span>
											</div>
											<span class="text-lg font-bold text-teal-400">{calculateDuration()}</span>
										</div>
										<div class="mt-2 text-xs text-slate-400">
											From {formatDate(pickupDatetime)} to {formatDate(returnDatetime)}
										</div>
									</div>
								{/if}
							</div>

							<!-- Availability Status -->
							{#if pickupDatetime && returnDatetime}
								<div class="space-y-4">
									<div
										class="rounded-2xl border border-slate-700/50 bg-slate-800/50 p-5"
										in:fade={{ duration: 300 }}
									>
										<h4 class="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-200">
											<Shield class="h-5 w-5 text-teal-400" />
											Availability Status
										</h4>

										{#if checkingAvailability}
											<div
												class="flex items-center gap-3 text-slate-300"
												in:fade={{ duration: 200 }}
											>
												<Loader2 class="h-6 w-6 animate-spin text-teal-400" />
												<div>
													<p class="font-medium">Checking availability...</p>
													<p class="text-sm text-slate-400">This won't take long</p>
												</div>
											</div>
										{:else if availabilityError && !isAvailable}
											<div class="flex items-start gap-3 text-red-400" in:scale={{ duration: 300 }}>
												<div class="rounded-full bg-red-500/20 p-2">
													<XCircle class="h-5 w-5" />
												</div>
												<div>
													<p class="font-semibold">Not Available</p>
													<p class="text-sm text-red-300">{availabilityError}</p>
												</div>
											</div>
										{:else if isAvailable === true}
											<div
												class="flex items-start gap-3 text-green-400"
												in:scale={{ duration: 300, easing: elasticOut }}
											>
												<div class="rounded-full bg-green-500/20 p-2">
													<CheckCircle2 class="h-5 w-5" />
												</div>
												<div>
													<p class="font-semibold">Available!</p>
													<p class="text-sm text-green-300">Vehicle is ready for your dates</p>
												</div>
											</div>
										{:else if isAvailable === false}
											<div class="flex items-start gap-3 text-red-400" in:scale={{ duration: 300 }}>
												<div class="rounded-full bg-red-500/20 p-2">
													<XCircle class="h-5 w-5" />
												</div>
												<div>
													<p class="font-semibold">Not Available</p>
													<p class="text-sm text-red-300">Try different dates</p>
												</div>
											</div>
										{:else if formErrors.pickupDatetime || formErrors.returnDatetime}
											<div class="flex items-start gap-3 text-yellow-400">
												<div class="rounded-full bg-yellow-500/20 p-2">
													<AlertTriangle class="h-5 w-5" />
												</div>
												<div>
													<p class="font-semibold">Check Input</p>
													<p class="text-sm text-yellow-300">Please correct the errors above</p>
												</div>
											</div>
										{:else}
											<div class="flex items-start gap-3 text-slate-400">
												<div class="rounded-full bg-slate-500/20 p-2">
													<Info class="h-5 w-5" />
												</div>
												<div>
													<p class="font-medium">Ready to Check</p>
													<p class="text-sm">Select dates to verify availability</p>
												</div>
											</div>
										{/if}
									</div>

									<!-- Estimated Cost Preview -->
									{#if estimatedCost && isAvailable}
										<div
											class="rounded-2xl border border-slate-700/50 bg-gradient-to-r from-slate-800/80 to-slate-900/80 p-5"
											in:fly={{ y: 20, duration: 500, easing: backOut }}
										>
											<h4 class="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-200">
												<DollarSign class="h-5 w-5 text-teal-400" />
												Estimated Cost
											</h4>
											<div class="space-y-3">
												<div class="flex items-center justify-between">
													<span class="text-slate-400">Rental ({calculateDuration()})</span>
													<span class="text-xl font-bold text-teal-400"
														>{formatNumber(estimatedCost)}</span
													>
												</div>
												<div class="flex items-center justify-between text-sm">
													<span class="text-slate-500">Security Deposit</span>
													<span class="text-slate-300"
														>{formatNumber(vehicle.security_deposit)}</span
													>
												</div>
												<div class="border-t border-slate-700 pt-3">
													<div class="flex items-center justify-between">
														<span class="font-semibold text-white">Total Payable</span>
														<span
															class="bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-2xl font-bold text-transparent"
														>
															{formatNumber(estimatedCost + vehicle.security_deposit)}
														</span>
													</div>
												</div>
											</div>
										</div>
									{/if}
								</div>
							{/if}

							<!-- Next Button -->
							<div class="pt-6">
								<button
									on:click={nextStep}
									disabled={checkingAvailability ||
										!isAvailable ||
										Object.keys(formErrors).length > 0}
									class="flex w-full items-center justify-center gap-3 rounded-2xl bg-gradient-to-r from-teal-500 to-cyan-600 px-8 py-4 text-lg font-semibold text-white shadow-lg transition-all duration-200 hover:scale-105 hover:shadow-xl disabled:cursor-not-allowed disabled:from-slate-600 disabled:to-slate-700 disabled:opacity-50 disabled:hover:scale-100"
								>
									{#if checkingAvailability}
										<Loader2 class="h-5 w-5 animate-spin" />
										Checking...
									{:else}
										Continue to Location
										<ArrowRight class="h-5 w-5" />
									{/if}
								</button>
							</div>
						</div>
					{:else if currentStep === 2}
						<!-- Step 2: Location & Review -->
						<div
							class="space-y-6"
							in:fly={{
								x: slideDirection * 300,
								duration: 500,
								easing: quintOut
							}}
							out:fly={{
								x: slideDirection * -300,
								duration: 300,
								easing: quintOut
							}}
						>
							<div class="mb-6 text-center">
								<div
									class="mx-auto mb-4 h-16 w-16 rounded-full border border-emerald-500/30 bg-emerald-500/20 p-4"
								>
									<MapPin class="mx-auto h-8 w-8 text-emerald-400" />
								</div>
								<h3 class="mb-2 text-2xl font-bold text-white">Pick-up & Drop-off</h3>
								<p class="text-slate-400">Where should we meet you?</p>
							</div>

							<!-- Enhanced Location Inputs with LocationPicker -->
							<div class="space-y-4">
								<!-- Pickup Location -->
								<div
									class="rounded-2xl border border-slate-700/50 bg-slate-800/50 p-5 backdrop-blur-sm"
								>
									<label class="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-300">
										<div class="rounded-full bg-green-500/20 p-1">
											<Navigation class="h-4 w-4 text-green-400" />
										</div>
										Pickup Location
									</label>

									<button
										on:click={() => openLocationPicker('pickup')}
										class="relative w-full rounded-xl border-2 border-slate-700 bg-slate-900/60 py-4 pl-12 pr-4 text-left text-gray-100 transition-all duration-200 hover:border-slate-600 focus:border-teal-400 focus:ring-2 focus:ring-teal-400/30"
									>
										<MapPin
											class="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-teal-400"
										/>
										{pickupLocation || 'Select pickup location...'}
									</button>

									{#if formErrors.pickupLocation}
										<p
											class="mt-2 flex items-center gap-1 text-sm text-red-400"
											transition:slide={{ duration: 200 }}
										>
											<AlertCircle class="h-4 w-4" />
											{formErrors.pickupLocation}
										</p>
									{/if}

									<!-- Location Details -->
									{#if pickupLocationData}
										<div
											class="mt-3 rounded-xl border border-teal-500/30 bg-teal-500/10 p-3"
											transition:fade={{ duration: 300 }}
										>
											<div class="flex items-center gap-3">
												<div class="rounded-full bg-teal-500/20 p-1">
													<CheckCircle2 class="h-4 w-4 text-teal-400" />
												</div>
												<div>
													<p class="text-sm font-medium text-teal-300">Location Confirmed</p>
													<p class="text-xs text-teal-400/80">
														{pickupLocationData.lat.toFixed(6)}, {pickupLocationData.lng.toFixed(6)}
													</p>
												</div>
											</div>
										</div>
									{/if}
								</div>

								<!-- Dropoff Location -->
								<div
									class="rounded-2xl border border-slate-700/50 bg-slate-800/50 p-5 backdrop-blur-sm"
								>
									<label class="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-300">
										<div class="rounded-full bg-red-500/20 p-1">
											<MapPin class="h-4 w-4 text-red-400" />
										</div>
										Drop-off Location
									</label>

									<button
										on:click={() => openLocationPicker('dropoff')}
										class="relative w-full rounded-xl border-2 border-slate-700 bg-slate-900/60 py-4 pl-12 pr-4 text-left text-gray-100 transition-all duration-200 hover:border-slate-600 focus:border-teal-400 focus:ring-2 focus:ring-teal-400/30"
									>
										<MapPin
											class="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-teal-400"
										/>
										{dropoffLocation || 'Select drop-off location...'}
									</button>

									{#if formErrors.dropoffLocation}
										<p
											class="mt-2 flex items-center gap-1 text-sm text-red-400"
											transition:slide={{ duration: 200 }}
										>
											<AlertCircle class="h-4 w-4" />
											{formErrors.dropoffLocation}
										</p>
									{/if}

									<!-- Location Details -->
									{#if dropoffLocationData}
										<div
											class="mt-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3"
											transition:fade={{ duration: 300 }}
										>
											<div class="flex items-center gap-3">
												<div class="rounded-full bg-emerald-500/20 p-1">
													<CheckCircle2 class="h-4 w-4 text-emerald-400" />
												</div>
												<div>
													<p class="text-sm font-medium text-emerald-300">Drop-off Confirmed</p>
													<p class="text-xs text-emerald-400/80">
														{dropoffLocationData.lat.toFixed(6)}, {dropoffLocationData.lng.toFixed(
															6
														)}
													</p>
												</div>
											</div>
										</div>
									{/if}
								</div>
							</div>

							<!-- Booking Summary -->
							{#if estimatedCost}
								<div
									class="rounded-2xl border border-slate-700/50 bg-gradient-to-br from-slate-800/80 to-slate-900/80 p-6 shadow-xl"
									in:fade={{ duration: 300 }}
								>
									<h4 class="mb-6 flex items-center gap-2 text-xl font-semibold text-white">
										<CreditCard class="h-6 w-6 text-teal-400" />
										Booking Summary
									</h4>

									<!-- Trip Details -->
									<div class="mb-6 space-y-4">
										<div class="rounded-xl border border-slate-700/30 bg-slate-900/50 p-4">
											<div class="mb-3 flex items-center gap-3">
												<Calendar class="h-5 w-5 text-teal-400" />
												<span class="font-semibold text-slate-200">Trip Duration</span>
											</div>
											<div class="grid grid-cols-2 gap-4 text-sm">
												<div>
													<p class="mb-1 text-slate-400">Pickup</p>
													<p class="font-medium text-gray-200">{formatDate(pickupDatetime)}</p>
												</div>
												<div>
													<p class="mb-1 text-slate-400">Return</p>
													<p class="font-medium text-gray-200">{formatDate(returnDatetime)}</p>
												</div>
											</div>
											<div class="mt-3 text-center">
												<span
													class="rounded-full bg-teal-500/20 px-3 py-1 text-sm font-medium text-teal-300"
												>
													{calculateDuration()} total
												</span>
											</div>
										</div>
									</div>

									<!-- Cost Breakdown -->
									<div class="space-y-3">
										<div class="flex items-center justify-between">
											<span class="text-slate-400">Rental Cost</span>
											<span class="text-lg font-semibold text-gray-100"
												>{formatNumber(estimatedCost)}</span
											>
										</div>
										<div class="flex items-center justify-between">
											<span class="text-slate-400">Security Deposit (Refundable)</span>
											<span class="text-lg font-semibold text-gray-100"
												>{formatNumber(vehicle.security_deposit)}</span
											>
										</div>
										<div class="border-t border-slate-700 pt-3">
											<div class="flex items-center justify-between">
												<span class="text-xl font-bold text-white">Total Payable</span>
												<span
													class="bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-2xl font-bold text-transparent"
												>
													{formatNumber(estimatedCost + vehicle.security_deposit)}
												</span>
											</div>
										</div>
									</div>

									<div class="mt-4 rounded-xl border border-slate-700/30 bg-slate-900/30 p-3">
										<p class="text-xs leading-relaxed text-slate-400">
											<Info class="mr-2 inline h-4 w-4" />
											Security deposit is fully refundable after vehicle return. Final charges may vary
											based on usage.
										</p>
									</div>
								</div>
							{/if}

							<!-- Error Display -->
							{#if bookingError}
								<div
									class="flex items-center gap-3 rounded-2xl border border-red-500/30 bg-red-600/20 p-4 text-red-300"
									transition:slide={{ duration: 300 }}
								>
									<AlertTriangle class="h-5 w-5 flex-shrink-0" />
									<div>
										<p class="font-semibold">Booking Error</p>
										<p class="text-sm">{bookingError}</p>
									</div>
								</div>
							{/if}

							<!-- Action Buttons -->
							<div class="flex gap-4 pt-6">
								<button
									on:click={prevStep}
									class="flex-1 rounded-2xl bg-slate-700 px-6 py-4 text-lg font-semibold text-slate-200 transition-all duration-200 hover:scale-105 hover:bg-slate-600"
								>
									Back
								</button>
								<button
									on:click={submitBooking}
									disabled={bookingLoading ||
										Object.keys(formErrors).length > 0 ||
										!pickupLocation.trim() ||
										!dropoffLocation.trim()}
									class="flex-2 flex items-center justify-center gap-3 rounded-2xl bg-gradient-to-r from-teal-500 to-cyan-600 px-8 py-4 text-lg font-semibold text-white shadow-lg transition-all duration-200 hover:scale-105 hover:shadow-xl disabled:cursor-not-allowed disabled:from-slate-600 disabled:to-slate-700 disabled:opacity-50 disabled:hover:scale-100"
								>
									{#if bookingLoading}
										<Loader2 class="h-5 w-5 animate-spin" />
										Processing...
									{:else}
										<Check class="h-5 w-5" />
										Confirm Booking
									{/if}
								</button>
							</div>
						</div>
					{:else if currentStep === 3 && bookingResponse}
						<!-- Step 3: Success -->
						<div
							class="flex min-h-[60vh] flex-col items-center justify-center text-center"
							in:fly={{ y: 50, duration: 700, easing: backOut }}
						>
							<!-- Success Animation -->
							<div class="mb-8" in:scale={{ duration: 800, easing: elasticOut }}>
								<div class="relative">
									<div
										class="flex h-32 w-32 items-center justify-center rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 shadow-2xl"
									>
										{#if showSuccessAnimation}
											<PartyPopper class="h-16 w-16 animate-bounce text-white" />
										{:else}
											<CheckCircle2 class="h-16 w-16 text-white" />
										{/if}
									</div>
									<div
										class="absolute -right-4 -top-4 flex h-8 w-8 animate-pulse items-center justify-center rounded-full bg-yellow-400"
									>
										<Sparkles class="h-5 w-5 text-yellow-900" />
									</div>
								</div>
							</div>

							<div class="mb-8">
								<h2
									class="mb-4 bg-gradient-to-r from-teal-400 to-cyan-500 bg-clip-text text-3xl font-bold text-transparent"
								>
									Booking Confirmed!
								</h2>
								<p class="mb-2 text-lg text-slate-300">
									Your {vehicle.brand}
									{vehicle.name} is ready!
								</p>
								<p class="mb-6 text-sm text-slate-400">
									Order ID: <span class="rounded bg-slate-800 px-2 py-1 font-mono text-slate-200"
										>{bookingResponse.order_id}</span
									>
								</p>
							</div>

							<!-- OTP Display -->
							<div
								class="mb-8 w-full max-w-md rounded-3xl border border-slate-700/50 bg-gradient-to-br from-slate-800/80 to-slate-900/80 p-8 shadow-2xl"
								in:scale={{ duration: 500, delay: 300, easing: backOut }}
							>
								<div class="mb-6 text-center">
									<div
										class="mx-auto mb-4 h-14 w-14 rounded-full border border-purple-500/30 bg-purple-500/20 p-3"
									>
										<KeyRound class="mx-auto h-8 w-8 text-purple-400" />
									</div>
									<h3 class="mb-2 text-xl font-bold text-slate-200">Your Pickup OTP</h3>
									<p class="text-sm text-slate-400">Present this code for vehicle pickup</p>
								</div>

								<div class="rounded-2xl border border-slate-700/50 bg-slate-900/60 p-6">
									<div class="text-center">
										<p
											class="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text font-mono text-4xl font-bold tracking-wider text-transparent"
										>
											{bookingResponse.otp}
										</p>
									</div>
								</div>

								<div class="mt-4 rounded-xl border border-slate-700/30 bg-slate-900/30 p-3">
									<p class="text-center text-xs text-slate-400">
										Keep this OTP safe and present it to our representative during pickup
									</p>
								</div>
							</div>

							<!-- Action Buttons -->
							<div class="flex w-full max-w-md flex-col gap-4">
								<button
									on:click={() => goto('/bookings')}
									class="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-teal-500 to-cyan-600 px-8 py-4 text-lg font-semibold text-white shadow-lg transition-all duration-200 hover:scale-105 hover:shadow-xl"
								>
									<Award class="h-5 w-5" />
									View My Bookings
								</button>
								<button
									on:click={() => goto('/')}
									class="rounded-2xl border border-slate-600 bg-slate-800/70 px-8 py-3 font-medium text-slate-300 transition-all duration-200 hover:border-teal-500 hover:bg-slate-700"
								>
									Back to Home
								</button>
							</div>

							<!-- Auto-redirect notice -->
							<div class="mt-8 text-center">
								<p class="mb-2 text-sm text-slate-400">
									Redirecting to your bookings in a few seconds...
								</p>
								<div class="mx-auto h-2 w-full max-w-xs overflow-hidden rounded-full bg-slate-800">
									<div
										class="animate-redirect-progress h-full rounded-full bg-gradient-to-r from-teal-500 to-cyan-600"
									></div>
								</div>
							</div>
						</div>
					{/if}
				{/key}
			</div>
		{/if}
	</main>

	<!-- Success Overlay Animation -->
	{#if showSuccessAnimation}
		<div
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md"
			transition:fade={{ duration: 500 }}
		>
			<div class="text-center" in:scale={{ duration: 800, easing: elasticOut }}>
				<div
					class="mb-6 flex h-40 w-40 items-center justify-center rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 shadow-2xl"
				>
					<Check class="h-20 w-20 text-white" />
				</div>
				<h2 class="mb-4 text-4xl font-bold text-white">Success!</h2>
				<p class="text-xl text-slate-300">Your booking has been confirmed</p>
			</div>
		</div>
	{/if}
</div>

<style>
	:global(.font-quicksand) {
		font-family: 'Quicksand', sans-serif;
	}

	/* Enhanced datetime input styling */
	input[type='datetime-local'] {
		color-scheme: dark;
	}

	input[type='datetime-local']::-webkit-calendar-picker-indicator {
		filter: invert(0.7) brightness(1.2) sepia(0.4) hue-rotate(140deg);
		cursor: pointer;
		opacity: 0.8;
		margin-left: 8px;
	}

	input[type='datetime-local']::-webkit-calendar-picker-indicator:hover {
		opacity: 1;
		transform: scale(1.1);
		transition: transform 0.2s ease;
	}

	/* Smooth animations */
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

	/* Enhanced bounce animation */
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

	/* Pulse animation for loading states */
	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}

	.animate-pulse {
		animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	/* Custom scrollbar for better mobile experience */
	::-webkit-scrollbar {
		width: 6px;
	}

	::-webkit-scrollbar-track {
		background: #1e293b;
	}

	::-webkit-scrollbar-thumb {
		background: #475569;
		border-radius: 3px;
	}

	::-webkit-scrollbar-thumb:hover {
		background: #64748b;
	}
</style>
