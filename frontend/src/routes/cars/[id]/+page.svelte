<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import axios from 'axios';
	import {
		Loader2,
		AlertTriangle,
		ChevronLeft,
		Star,
		Users,
		Fuel,
		Zap,
		Palette,
		Gauge,
		Car,
		ShieldCheck,
		MapPin,
		CalendarDays,
		Clock3,
		DollarSign,
		Sparkles as StarIconFull,
		StarHalf
	} from 'lucide-svelte';

	// Interfaces
	interface Vehicle {
		id: string;
		vehicle_number: string;
		name: string;
		brand: string;
		model: string;
		vehicle_type: 'Car' | 'Bike' | 'SUV' | 'Scooter' | 'Truck' | 'Other';
		transmission: 'Manual' | 'Automatic';
		fuel_type: 'Petrol' | 'Diesel' | 'Electric' | 'CNG';
		seating_capacity: number;
		mileage: number;
		engine_cc: number;
		color: string;
		top_speed: number;
		location: string;
		current_odometer: number;
		insurance_expiry_date: string;
		price_per_day: number;
		price_per_hour: number;
		security_deposit: number;
		late_fee_per_hour: number;
		image_1: string;
		image_2: string | null;
		image_3: string | null;
		rating: number;
		total_trips: number;
		current_status: string;
		owner_id: string;
	}

	interface Renter {
		full_name: string;
		address: string;
		profile_pic: string | null;
		rating: number;
		status: boolean;
	}

	interface SpecItem {
		icon: typeof Fuel;
		label: string;
		value: string | number;
		iconColor?: string;
	}

	// State Variables
	let vehicle: Vehicle | null = null;
	let renter: Renter | null = null;
	let loadingVehicle = true;
	let loadingRenter = false;
	let errorVehicle: string | null = null;
	let errorRenter: string | null = null;
	let currentImageIndex = 0;
	let vehicleSpecs: SpecItem[] = [];
	let isFavorite = false;

	// API Configuration
	const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://0.0.0.0:8000';
	const vehicleApiUrl = `${API_BASE_URL}/business/vehicle_details/`;
	const renterApiUrl = `${API_BASE_URL}/authentication/get_renter_details/`;

	// Computed Values
	$: vehicleId = $page.params.id;
	$: images = vehicle
		? [vehicle.image_1, vehicle.image_2, vehicle.image_3].filter(
				(img) => img && img !== 'url_or_base64_image_2' && img !== 'url_or_base64_image_3'
			)
		: [];

	// Helper Functions
	function getImageSource(
		image: string | null,
		defaultType: 'vehicle' | 'profile' = 'vehicle'
	): string {
		if (!image) {
			return defaultType === 'profile'
				? 'https://via.placeholder.com/100x100?text=N/A'
				: 'https://via.placeholder.com/800x600?text=No+Image';
		}
		if (image.startsWith('data:image')) return image;
		return image;
	}

	function formatNumber(num: number): string {
		return num.toLocaleString('en-IN');
	}

	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-GB', {
			day: '2-digit',
			month: 'short',
			year: 'numeric'
		});
	}

	const renderStars = (rating: number) => {
		const stars = [];
		const fullStars = Math.floor(rating);
		const hasHalfStar = rating % 1 >= 0.5;
		for (let i = 0; i < fullStars; i++) stars.push('full');
		if (hasHalfStar) stars.push('half');
		const emptyStars = 5 - stars.length;
		for (let i = 0; i < emptyStars; i++) stars.push('empty');
		return stars;
	};

	// Data Fetching
	async function fetchVehicleDetails() {
		loadingVehicle = true;
		errorVehicle = null;
		try {
			const response = await axios.post(vehicleApiUrl, { vehicle_id: vehicleId });
			if (response.data && response.data.vehicle) {
				vehicle = response.data.vehicle;
				updateVehicleSpecs();
				if (vehicle?.owner_id) {
					await fetchRenterDetails(vehicle.owner_id);
				}
			} else {
				errorVehicle = 'Vehicle details not found.';
			}
		} catch (err: any) {
			console.error('Error fetching vehicle:', err);
			errorVehicle = 'Could not load vehicle details. Please try again.';
		} finally {
			loadingVehicle = false;
		}
	}

	async function fetchRenterDetails(renterId: string) {
		loadingRenter = true;
		errorRenter = null;
		try {
			const response = await axios.post(renterApiUrl, { renter_id: renterId });
			if (response.data) {
				renter = response.data;
			} else {
				errorRenter = 'Renter details not found.';
			}
		} catch (err: any) {
			console.error('Error fetching renter:', err);
			errorRenter = 'Could not load owner details.';
		} finally {
			loadingRenter = false;
		}
	}

	function updateVehicleSpecs() {
		if (!vehicle) return;
		vehicleSpecs = [
			{ icon: Users, label: 'Seats', value: vehicle.seating_capacity },
			{
				icon: vehicle.fuel_type === 'Electric' ? Zap : Fuel,
				label: 'Fuel',
				value: vehicle.fuel_type,
				iconColor: vehicle.fuel_type === 'Electric' ? 'text-green-400' : 'text-orange-400'
			},
			{ icon: Car, label: 'Transmission', value: vehicle.transmission },
			{ icon: Gauge, label: 'Mileage', value: `${vehicle.mileage} kmpl` },
			{ icon: Zap, label: 'Engine', value: `${vehicle.engine_cc} cc` },
			{ icon: Palette, label: 'Color', value: vehicle.color },
			{ icon: Gauge, label: 'Top Speed', value: `${vehicle.top_speed} km/h` },
			{
				icon: ShieldCheck,
				label: 'Insured Till',
				value: formatDate(vehicle.insurance_expiry_date)
			},
			{ icon: Gauge, label: 'Odometer', value: `${formatNumber(vehicle.current_odometer)} km` },
			{ icon: Car, label: 'Reg. No.', value: vehicle.vehicle_number }
		];
	}

	// UI Interactions
	function changeImage(index: number) {
		if (index >= 0 && index < images.length) currentImageIndex = index;
	}

	function nextImage() {
		currentImageIndex = (currentImageIndex + 1) % images.length;
	}

	function prevImage() {
		currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
	}

	function toggleFavorite() {
		isFavorite = !isFavorite;
	}

	onMount(() => {
		if (vehicleId) {
			fetchVehicleDetails();
		} else {
			errorVehicle = 'No vehicle ID specified.';
			loadingVehicle = false;
		}
	});
</script>

<div class="font-quicksand min-h-screen bg-slate-950 text-gray-200 antialiased">
	<!-- Header -->
	<header class="sticky top-0 z-30 bg-slate-950/90 px-4 py-3 shadow-sm backdrop-blur-lg">
		<div class="mx-auto flex max-w-7xl items-center justify-between">
			<button
				on:click={() => window.history.back()}
				class="rounded-full bg-slate-800/50 p-2 transition-colors hover:bg-slate-700"
				aria-label="Go back"
			>
				<ChevronLeft class="h-6 w-6 text-slate-300" />
			</button>
			<h1 class="flex-auto truncate text-lg font-semibold text-gray-100 sm:text-xl">
				{#if vehicle}{vehicle.brand} {vehicle.name}{:else}Vehicle Details{/if}
			</h1>
		</div>
	</header>

	<main class="mx-auto max-w-7xl px-4 pt-4 sm:px-6">
		{#if loadingVehicle}
			<div class="flex min-h-[80vh] flex-col items-center justify-center">
				<Loader2 class="mb-4 h-12 w-12 animate-spin text-teal-400" />
				<p class="text-lg text-slate-400">Loading your ride...</p>
			</div>
		{:else if errorVehicle}
			<div
				class="flex min-h-[80vh] flex-col items-center justify-center rounded-3xl bg-slate-800/50 p-8 shadow-2xl"
			>
				<AlertTriangle class="mb-4 h-16 w-16 text-red-400" />
				<h2 class="mb-2 text-2xl font-semibold text-red-300">Something Went Wrong</h2>
				<p class="mb-6 text-slate-400">{errorVehicle}</p>
				<button
					on:click={fetchVehicleDetails}
					class="rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-8 py-3 text-white transition-transform hover:scale-105 hover:from-teal-600 hover:to-cyan-700"
				>
					Try Again
				</button>
			</div>
		{:else if vehicle}
			<!-- Image Carousel -->
			<section class="relative mb-6 h-[40vh] overflow-hidden rounded-3xl shadow-2xl sm:h-[50vh]">
				{#if images.length > 0}
					<img
						src={getImageSource(images[currentImageIndex])}
						alt="{vehicle.brand} {vehicle.name} - Image {currentImageIndex + 1}"
						class="h-full w-full object-cover transition-transform duration-500 ease-in-out"
					/>
					<div
						class="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/50"
					></div>
					{#if vehicle.current_status === 'available'}
						<span
							class="absolute left-4 top-4 rounded-full bg-green-500/90 px-3 py-1.5 text-xs font-medium text-white shadow-md"
						>
							Available
						</span>
					{:else}
						<span
							class="absolute left-4 top-4 rounded-full bg-yellow-600/90 px-3 py-1.5 text-xs font-medium text-white shadow-md"
						>
							On Request
						</span>
					{/if}
					<div
						class="absolute right-4 top-4 rounded-full bg-slate-900/80 px-3 py-1.5 text-xs font-medium text-yellow-400 shadow-md"
					>
						<Star class="inline h-3.5 w-3.5 fill-yellow-400" />
						{vehicle.rating.toFixed(1)}
					</div>
					{#if images.length > 1}
						<div class="absolute bottom-4 left-1/2 flex -translate-x-1/2 gap-2">
							{#each images as _, i}
								<button
									on:click={() => changeImage(i)}
									class="h-2 w-2 rounded-full transition-all {currentImageIndex === i
										? 'scale-125 bg-teal-400'
										: 'bg-slate-400/50 hover:bg-slate-200/80'}"
									aria-label="View image {i + 1}"
								></button>
							{/each}
						</div>
						<button
							on:click={prevImage}
							class="absolute left-4 top-1/2 -translate-y-1/2 rounded-full bg-slate-900/60 p-2 text-white transition-all hover:scale-110 hover:bg-slate-900/80"
						>
							<ChevronLeft class="h-5 w-5" />
						</button>
						<button
							on:click={nextImage}
							class="absolute right-4 top-1/2 -translate-y-1/2 rounded-full bg-slate-900/60 p-2 text-white transition-all hover:scale-110 hover:bg-slate-900/80"
						>
							<ChevronLeft class="h-5 w-5 rotate-180" />
						</button>
					{/if}
				{:else}
					<div class="flex h-full w-full items-center justify-center rounded-3xl bg-slate-800">
						<Car class="h-16 w-16 text-slate-500" />
						<p class="ml-3 text-slate-400">No images available</p>
					</div>
				{/if}
			</section>

			<!-- Vehicle Info -->
			<section class="mb-8">
				<div class="mb-4 flex items-center justify-between">
					<div>
						<h2 class="text-3xl font-bold text-white sm:text-4xl">
							{vehicle.brand}
							{vehicle.name}
						</h2>
						<p class="mt-1 text-sm text-slate-400">{vehicle.model} • {vehicle.vehicle_type}</p>
					</div>
				</div>
				<div class="flex flex-wrap items-center gap-4 text-sm">
					<div class="flex items-center gap-1 text-yellow-400">
						{#each renderStars(vehicle.rating) as starType}
							{#if starType === 'full'}
								<StarIconFull class="h-4 w-4 fill-current" />
							{:else if starType === 'half'}
								<StarHalf class="h-4 w-4 fill-current" />
							{:else}
								<Star class="h-4 w-4 text-slate-600" />
							{/if}
						{/each}
						<span class="ml-1 text-slate-300">{vehicle.rating.toFixed(1)}</span>
					</div>
					<div class="flex items-center gap-1 text-slate-400">
						<CalendarDays class="h-4 w-4" />
						{vehicle.total_trips} Trips
					</div>
					<div class="flex items-center gap-1 text-slate-400">
						<MapPin class="h-4 w-4 text-teal-400" />
						{vehicle.location}
					</div>
				</div>
			</section>

			<!-- Specifications -->
			<section class="mb-8">
				<h3 class="mb-4 text-xl font-semibold text-white">Specifications</h3>
				<div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
					{#each vehicleSpecs as spec}
						<div
							class="flex items-center rounded-xl bg-slate-800/50 p-3 transition-transform hover:scale-105"
						>
							<div
								class="mr-3 flex h-10 w-10 items-center justify-center rounded-full bg-slate-700/70"
							>
								<svelte:component
									this={spec.icon}
									class="h-5 w-5 {spec.iconColor || 'text-teal-400'}"
								/>
							</div>
							<div>
								<p class="text-xs text-slate-400">{spec.label}</p>
								<p class="text-sm font-medium text-gray-200">{spec.value}</p>
							</div>
						</div>
					{/each}
				</div>
			</section>

			<!-- Renter Details -->
			<section class="mb-8">
				<h3 class="mb-4 text-xl font-semibold text-white">Hosted by</h3>
				{#if loadingRenter}
					<div class="flex items-center rounded-2xl bg-slate-800/50 p-4">
						<Loader2 class="mr-3 h-6 w-6 animate-spin text-teal-400" />
						<p class="text-slate-400">Loading host details...</p>
					</div>
				{:else if errorRenter}
					<div class="rounded-2xl bg-slate-800/50 p-4 text-center">
						<AlertTriangle class="mx-auto mb-2 h-6 w-6 text-yellow-500" />
						<p class="text-sm text-yellow-300">{errorRenter}</p>
					</div>
				{:else if renter}
					<div class="rounded-2xl bg-slate-800/50 p-5 shadow-lg">
						<div class="flex flex-col items-center gap-4 sm:flex-row">
							<div class="relative">
								<img
									src={getImageSource(renter.profile_pic, 'profile')}
									alt={renter.full_name}
									class="h-20 w-20 rounded-full border-2 border-teal-500/30 object-cover shadow-md sm:h-24 sm:w-24"
								/>
							</div>
							<div class="text-center sm:text-left">
								<h4 class="text-lg font-semibold text-white">{renter.full_name}</h4>
								<div
									class="mt-1 flex items-center justify-center gap-1 text-yellow-400 sm:justify-start"
								>
									{#each renderStars(renter.rating) as starType}
										{#if starType === 'full'}
											<StarIconFull class="h-4 w-4 fill-current" />
										{:else if starType === 'half'}
											<StarHalf class="h-4 w-4 fill-current" />
										{:else}
											<Star class="h-4 w-4 text-slate-600" />
										{/if}
									{/each}
									<span class="ml-1 text-sm text-slate-300">{renter.rating.toFixed(1)}</span>
								</div>
								<p class="mt-2 line-clamp-2 text-sm text-slate-400">{renter.address}</p>
							</div>
						</div>
					</div>
				{:else}
					<div class="rounded-2xl bg-slate-800/50 p-4">
						<p class="text-sm text-slate-400">Host details not available.</p>
					</div>
				{/if}
			</section>

			<!-- Pricing -->
			<section class="mb-8">
				<h3 class="mb-4 text-xl font-semibold text-white">Pricing Details</h3>
				<div class="space-y-4 rounded-2xl bg-slate-800/50 p-5 shadow-lg">
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<DollarSign class="h-5 w-5 text-teal-400" />
							<span class="text-sm text-slate-400">Per Day</span>
						</div>
						<p class="text-xl font-bold text-teal-400">₹{formatNumber(vehicle.price_per_day)}</p>
					</div>
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<Clock3 class="h-5 w-5 text-teal-400" />
							<span class="text-sm text-slate-400">Per Hour</span>
						</div>
						<p class="text-lg font-semibold text-gray-200">
							₹{formatNumber(vehicle.price_per_hour)}
						</p>
					</div>
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<ShieldCheck class="h-5 w-5 text-teal-400" />
							<span class="text-sm text-slate-400">Security Deposit</span>
						</div>
						<p class="text-sm text-gray-200">₹{formatNumber(vehicle.security_deposit)}</p>
					</div>
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<Clock3 class="h-5 w-5 text-teal-400" />
							<span class="text-sm text-slate-400">Late Fee</span>
						</div>
						<p class="text-sm text-gray-200">₹{formatNumber(vehicle.late_fee_per_hour)}/hour</p>
					</div>
				</div>
			</section>
		{/if}
	</main>

	<!-- Sticky Booking Bar -->
	{#if vehicle && !loadingVehicle && !errorVehicle}
		<div
			class=" left-0 z-30 w-full bg-slate-900/90 p-4 pb-12 shadow-[0_-8px_20px_rgba(0,0,0,0.3)] backdrop-blur-lg"
		>
			<div class="mx-auto flex max-w-7xl items-center justify-between gap-4">
				<div>
					<p class="text-sm text-slate-400">Starting at</p>
					<p class="text-xl font-bold text-teal-400">
						₹{formatNumber(vehicle.price_per_hour)}<span class="text-sm font-medium text-slate-400"
							>/hr</span
						>
					</p>
				</div>
				<button
					on:click={() => goto(`/bookings/new?vehicleId=${vehicle.id}`)}
					class="rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-8 py-3 text-sm font-semibold text-white shadow-lg transition-transform hover:scale-105 hover:from-teal-600 hover:to-cyan-700 focus:outline-none focus:ring-4 focus:ring-teal-500/50"
				>
					Book Now
				</button>
			</div>
		</div>
	{/if}
</div>

<style>
	:global(.font-quicksand) {
		font-family: 'Quicksand', sans-serif;
	}
	@keyframes fadeIn {
		from {
			opacity: 0.7;
			transform: scale(1.02);
		}
		to {
			opacity: 1;
			transform: scale(1);
		}
	}
	img.object-cover {
		animation: fadeIn 0.5s ease-in-out;
	}
</style>
