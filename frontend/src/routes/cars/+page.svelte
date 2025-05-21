<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import axios from 'axios';

	// Lucide Icons
	import {
		Search,
		SlidersHorizontal,
		Star,
		Users,
		Fuel,
		Zap,
		ChevronLeft,
		ChevronRight,
		FilterX,
		Check,
		X,
		Car,
		CarFront,
		Sparkles
	} from 'lucide-svelte';
	import { Loader2 } from 'lucide-svelte';

	// Interface based on API response and backend choices
	interface Vehicle {
		id: string;
		name: string;
		brand: string;
		vehicle_type: 'Car' | 'Bike' | 'SUV' | 'Scooter' | 'Truck' | 'Other';
		location: string;
		price_per_day: number;
		price_per_hour: number;
		image_1: string;
		current_status: string;
		rating: number;
		seating_capacity: number;
		transmission?: 'Manual' | 'Automatic';
		fuel_type?: 'Petrol' | 'Diesel' | 'Electric' | 'CNG';
	}

	const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
	const vehiclesApiUrl = `${API_BASE_URL}/business/vehicles/`;

	// State variables
	let allVehicles: Vehicle[] = [];
	let vehiclesLoading = true;
	let vehiclesError: string | null = null;
	let searchTerm = '';
	let showFiltersPanel = false;
	let sortBy = 'rating';
	let currentPage = 1;
	const carsPerPage = 8;

	// Filter states
	let selectedVehicleTypes: string[] = [];
	let selectedFuelTypes: string[] = [];
	let selectedTransmissions: string[] = [];
	let priceRange = 5000;
	let maxPriceFound = 5000;

	// Filter options from backend
	const vehicleTypeChoices = ['Car', 'Bike', 'SUV', 'Scooter', 'Truck', 'Other'];
	const fuelTypeChoices = ['Petrol', 'Diesel', 'Electric', 'CNG'];
	const transmissionChoices = ['Manual', 'Automatic'];

	// Vehicle type to category mapping for icons and colors
	const vehicleTypeStyles = {
		Car: { icon: Car, color: 'text-sky-400', bgColor: 'bg-sky-500/20' },
		SUV: { icon: CarFront, color: 'text-amber-400', bgColor: 'bg-amber-500/20' },
		Bike: { icon: Car, color: 'text-sky-400', bgColor: 'bg-sky-500/20' }, // Using Car as placeholder
		Scooter: { icon: Car, color: 'text-sky-400', bgColor: 'bg-sky-500/20' }, // Using Car as placeholder
		Truck: { icon: Car, color: 'text-sky-400', bgColor: 'bg-sky-500/20' }, // Using Car as placeholder
		Other: { icon: Car, color: 'text-sky-400', bgColor: 'bg-sky-500/20' } // Using Car as placeholder
	};

	async function fetchAllVehicles() {
		vehiclesLoading = true;
		vehiclesError = null;
		try {
			const response = await axios.get(vehiclesApiUrl);
			if (response.data && response.data.vehicles && Array.isArray(response.data.vehicles)) {
				allVehicles = response.data.vehicles;
				if (allVehicles.length > 0) {
					maxPriceFound = Math.max(...allVehicles.map((v) => v.price_per_day), 0) || 5000;
					priceRange = maxPriceFound;
				}
			} else {
				allVehicles = [];
				vehiclesError = 'Unexpected API response format for vehicles.';
			}
		} catch (error) {
			console.error('Error fetching vehicles:', error);
			vehiclesError = 'Could not load vehicles. Please try again later.';
			allVehicles = [];
		} finally {
			vehiclesLoading = false;
		}
	}

	onMount(() => {
		fetchAllVehicles();
		const queryParams = new URLSearchParams($page.url.search);
		searchTerm = queryParams.get('q') || '';
	});

	// Reactive filtered and sorted vehicles
	$: filteredAndSortedVehicles = allVehicles
		.filter((vehicle) => {
			const searchTermLower = searchTerm.toLowerCase();
			const matchesSearch =
				vehicle.name.toLowerCase().includes(searchTermLower) ||
				vehicle.brand.toLowerCase().includes(searchTermLower) ||
				vehicle.location.toLowerCase().includes(searchTermLower);

			const matchesPrice = vehicle.price_per_day <= priceRange;
			const matchesVehicleType =
				selectedVehicleTypes.length === 0 || selectedVehicleTypes.includes(vehicle.vehicle_type);
			const matchesFuelType =
				selectedFuelTypes.length === 0 ||
				(vehicle.fuel_type && selectedFuelTypes.includes(vehicle.fuel_type));
			const matchesTransmission =
				selectedTransmissions.length === 0 ||
				(vehicle.transmission && selectedTransmissions.includes(vehicle.transmission));

			return (
				matchesSearch &&
				matchesPrice &&
				matchesVehicleType &&
				matchesFuelType &&
				matchesTransmission
			);
		})
		.sort((a, b) => {
			if (sortBy === 'rating') return (b.rating || 0) - (a.rating || 0);
			if (sortBy === 'priceLowToHigh') return a.price_per_day - b.price_per_day;
			if (sortBy === 'priceHighToLow') return b.price_per_day - a.price_per_day;
			if (sortBy === 'name') return a.name.localeCompare(b.name);
			return 0;
		});

	// Pagination logic
	$: totalPages = Math.ceil(filteredAndSortedVehicles.length / carsPerPage);
	$: paginatedVehicles = filteredAndSortedVehicles.slice(
		(currentPage - 1) * carsPerPage,
		currentPage * carsPerPage
	);

	// Reset to page 1 when filters or search term change
	$: {
		searchTerm, priceRange, selectedVehicleTypes, selectedFuelTypes, selectedTransmissions, sortBy;
		currentPage = 1;
	}

	const navigateToVehicleDetail = (vehicleId: string) => {
		goto(`/cars/${vehicleId}`);
	};

	const clearFilters = () => {
		selectedVehicleTypes = [];
		selectedFuelTypes = [];
		selectedTransmissions = [];
		priceRange = maxPriceFound;
		sortBy = 'rating';
		currentPage = 1;
	};

	const applyAndCloseFilters = () => {
		showFiltersPanel = false;
		currentPage = 1;
	};

	function toggleFilter(array: string[], value: string) {
		const index = array.indexOf(value);
		if (index === -1) {
			array.push(value);
		} else {
			array.splice(index, 1);
		}
		return array;
	}
</script>

<div class="font-quicksand min-h-screen bg-slate-950 pb-20 text-gray-200 antialiased">
	<!-- Header -->
	<header class="sticky top-0 z-30 bg-slate-900/80 p-4 shadow-xl backdrop-blur-lg">
		<div class="mx-auto flex max-w-7xl items-center gap-4">
			<button
				on:click={() => (window.history.length > 1 ? window.history.back() : goto('/'))}
				class="rounded-full p-2 text-slate-300 hover:bg-slate-800 hover:text-teal-400"
				aria-label="Go back"
			>
				<ChevronLeft class="h-6 w-6" />
			</button>
			<div class="relative flex-grow">
				<div class="absolute inset-y-0 left-0 flex items-center pl-3">
					<Search class="h-5 w-5 text-slate-400" />
				</div>
				<input
					type="search"
					bind:value={searchTerm}
					placeholder="Search vehicles, brands, or locations..."
					class="w-full rounded-full border border-slate-700/80 bg-slate-800/70 py-2.5 pl-10 pr-4 text-sm text-gray-100 placeholder-slate-400 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/30"
				/>
			</div>
			<button
				on:click={() => (showFiltersPanel = !showFiltersPanel)}
				class="rounded-full border border-slate-700/80 bg-slate-800/70 p-2.5 text-slate-300 hover:bg-slate-800 hover:text-teal-400"
				aria-label="Toggle Filters"
				aria-expanded={showFiltersPanel}
			>
				<SlidersHorizontal class="h-5 w-5" />
			</button>
		</div>
	</header>

	<main class="mx-auto max-w-7xl px-4 py-8 sm:px-6">
		<div class="mb-8 flex flex-col items-center justify-between gap-4 sm:flex-row">
			<h1 class="text-3xl font-bold text-gray-100">
				Explore Our Fleet
				{#if !vehiclesLoading}
					<span class="text-teal-400">({filteredAndSortedVehicles.length})</span>
				{/if}
			</h1>
			<div class="relative">
				<select
					bind:value={sortBy}
					class="rounded-full border border-slate-700/80 bg-slate-800/70 px-4 py-2 pr-8 text-sm text-gray-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500/30"
				>
					<option value="rating">Sort by Rating</option>
					<option value="priceLowToHigh">Price: Low to High</option>
					<option value="priceHighToLow">Price: High to Low</option>
					<option value="name">Name (A-Z)</option>
				</select>
			</div>
		</div>

		{#if vehiclesLoading}
			<div class="flex min-h-[50vh] flex-col items-center justify-center">
				<Loader2 class="mb-4 h-12 w-12 animate-spin text-teal-400" />
				<p class="text-lg text-slate-400">Loading our fleet...</p>
			</div>
		{:else if vehiclesError}
			<div
				class="flex min-h-[50vh] flex-col items-center justify-center rounded-2xl bg-slate-800/70 p-8 shadow-lg"
			>
				<AlertTriangle class="mb-4 h-12 w-12 text-red-400" />
				<h2 class="mb-2 text-2xl font-semibold text-red-300">Error</h2>
				<p class="mb-6 text-slate-400">{vehiclesError}</p>
				<button
					on:click={fetchAllVehicles}
					class="rounded-full bg-teal-500 px-6 py-2.5 text-white hover:bg-teal-600"
				>
					Retry
				</button>
			</div>
		{:else if paginatedVehicles.length > 0}
			<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
				{#each paginatedVehicles as vehicle (vehicle.id)}
					<div
						on:click={() => navigateToVehicleDetail(vehicle.id)}
						on:keydown={(e) => e.key === 'Enter' && navigateToVehicleDetail(vehicle.id)}
						role="button"
						tabindex="0"
						class="group rounded-2xl border border-slate-700/50 bg-slate-800/70 shadow-lg transition-all hover:-translate-y-1 hover:shadow-xl hover:ring-2 hover:ring-teal-500/30"
					>
						<div class="relative h-48 overflow-hidden rounded-t-2xl">
							<img
								src={vehicle.image_1}
								alt="{vehicle.brand} {vehicle.name}"
								class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
								loading="lazy"
							/>
							<div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
							<div
								class="absolute right-3 top-3 rounded-full bg-slate-900/80 px-3 py-1 text-xs text-yellow-400"
							>
								<Star class="inline h-4 w-4 fill-yellow-400" />
								{vehicle.rating.toFixed(1)}
							</div>
							{#if vehicle.current_status === 'available'}
								<span
									class="absolute left-3 top-3 rounded-full bg-green-500 px-3 py-1 text-xs text-white"
								>
									Available
								</span>
							{:else}
								<span
									class="absolute left-3 top-3 rounded-full bg-yellow-600 px-3 py-1 text-xs text-white"
								>
									On Request
								</span>
							{/if}
						</div>
						<div class="p-5">
							<h2 class="text-xl font-semibold text-gray-100 group-hover:text-teal-400">
								{vehicle.brand}
								{vehicle.name}
							</h2>
							<div class="flex items-center gap-2 text-sm text-slate-400">
								<svelte:component
									this={vehicleTypeStyles[vehicle.vehicle_type].icon}
									class="h-4 w-4 {vehicleTypeStyles[vehicle.vehicle_type].color}"
								/>
								<span>{vehicle.vehicle_type}</span>
							</div>
							<p class="mt-1 flex items-center text-sm text-slate-500">
								<span class="mr-1 text-slate-400">📍</span>
								{vehicle.location}
							</p>
							<div class="mt-4 flex items-center justify-between">
								<div class="flex items-center gap-2 text-sm text-slate-400">
									<Users class="h-4 w-4 text-teal-400" />
									<span>{vehicle.seating_capacity} Seats</span>
								</div>
								{#if vehicle.fuel_type}
									<div class="flex items-center gap-2 text-sm text-slate-400">
										{#if vehicle.fuel_type === 'Electric'}
											<Zap class="h-4 w-4 text-green-400" />
										{:else}
											<Fuel class="h-4 w-4 text-orange-400" />
										{/if}
										<span>{vehicle.fuel_type}</span>
									</div>
								{/if}
							</div>
							{#if vehicle.transmission}
								<p class="mt-2 text-sm text-slate-400">{vehicle.transmission}</p>
							{/if}
							<div class="mt-4 flex items-center justify-between">
								<p class="text-xl font-bold text-teal-400">
									₹{vehicle.price_per_day.toLocaleString()}<span class="text-sm text-slate-400"
										>/day</span
									>
								</p>
								<button
									on:click|stopPropagation={() => navigateToVehicleDetail(vehicle.id)}
									class="rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-4 py-2 text-sm text-white hover:from-teal-600 hover:to-cyan-700"
								>
									View Details
								</button>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{:else}
			<div
				class="flex min-h-[50vh] flex-col items-center justify-center rounded-2xl bg-slate-800/70 p-8 shadow-lg"
			>
				<FilterX class="mb-4 h-16 w-16 text-teal-400/50" />
				<h2 class="mb-2 text-2xl font-semibold text-gray-100">No Vehicles Found</h2>
				<p class="mb-6 text-slate-400">Adjust your search or filters to find more vehicles.</p>
				<button
					on:click={clearFilters}
					class="rounded-full bg-teal-500 px-6 py-2.5 text-white hover:bg-teal-600"
				>
					Clear Filters
				</button>
			</div>
		{/if}

		<!-- Pagination -->
		{#if filteredAndSortedVehicles.length > carsPerPage}
			<div class="mt-10 flex items-center justify-center gap-2">
				<button
					on:click={() => (currentPage = Math.max(1, currentPage - 1))}
					disabled={currentPage === 1}
					class="rounded-full p-2 text-slate-400 hover:bg-slate-800 hover:text-teal-400 disabled:opacity-50"
				>
					<ChevronLeft class="h-5 w-5" />
				</button>
				{#each Array(totalPages) as _, i}
					{@const pageNum = i + 1}
					{#if totalPages <= 7 || pageNum === 1 || pageNum === totalPages || Math.abs(pageNum - currentPage) <= 1}
						<button
							on:click={() => (currentPage = pageNum)}
							class:bg-teal-500={currentPage === pageNum}
							class:text-white={currentPage === pageNum}
							class:bg-slate-800={currentPage !== pageNum}
							class:text-slate-400={currentPage !== pageNum}
							class="rounded-full px-4 py-2 text-sm hover:bg-slate-700 hover:text-teal-400"
						>
							{pageNum}
						</button>
					{:else if (totalPages > 7 && pageNum === 2 && currentPage > 3) || (totalPages > 7 && pageNum === totalPages - 1 && currentPage < totalPages - 2)}
						<span class="px-2 text-slate-500">...</span>
					{/if}
				{/each}
				<button
					on:click={() => (currentPage = Math.min(totalPages, currentPage + 1))}
					disabled={currentPage === totalPages}
					class="rounded-full p-2 text-slate-400 hover:bg-slate-800 hover:text-teal-400 disabled:opacity-50"
				>
					<ChevronRight class="h-5 w-5" />
				</button>
			</div>
		{/if}
	</main>

	<!-- Filters Panel -->
	{#if showFiltersPanel}
		<div
			class="fixed inset-0 z-40 bg-black/70 backdrop-blur-md"
			on:click={() => (showFiltersPanel = false)}
			on:keydown={(e) => e.key === 'Escape' && (showFiltersPanel = false)}
		></div>
		<aside
			class="fixed right-0 top-0 z-50 h-full w-[320px] max-w-[90vw] transform bg-slate-900 p-6 shadow-xl transition-transform duration-300"
			class:translate-x-0={showFiltersPanel}
			class:translate-x-full={!showFiltersPanel}
		>
			<div class="mb-6 flex items-center justify-between">
				<h2 class="text-xl font-semibold text-gray-100">Filters</h2>
				<button
					on:click={() => (showFiltersPanel = false)}
					class="rounded-full p-1.5 text-slate-400 hover:bg-slate-800 hover:text-teal-400"
				>
					<X class="h-6 w-6" />
				</button>
			</div>
			<div class="space-y-6">
				<!-- Vehicle Type Filter -->
				<div>
					<h3 class="mb-3 text-sm font-semibold text-gray-100">Vehicle Type</h3>
					<div class="grid grid-cols-2 gap-2">
						{#each vehicleTypeChoices as type}
							<button
								on:click={() => (selectedVehicleTypes = toggleFilter(selectedVehicleTypes, type))}
								class:bg-teal-500={selectedVehicleTypes.includes(type)}
								class:text-white={selectedVehicleTypes.includes(type)}
								class:bg-slate-800={selectedVehicleTypes.includes(type)}
								class:text-slate-400={selectedVehicleTypes.includes(type)}
								class="flex items-center justify-center gap-2 rounded-full border border-slate-700/80 px-3 py-2 text-sm hover:bg-slate-700 hover:text-teal-400"
							>
								{#if selectedVehicleTypes.includes(type)}
									<Check class="h-4 w-4" />
								{/if}
								{type}
							</button>
						{/each}
					</div>
				</div>

				<!-- Fuel Type Filter -->
				<div>
					<h3 class="mb-3 text-sm font-semibold text-gray-100">Fuel Type</h3>
					<div class="grid grid-cols-2 gap-2">
						{#each fuelTypeChoices as type}
							<button
								on:click={() => (selectedFuelTypes = toggleFilter(selectedFuelTypes, type))}
								class:bg-teal-500={selectedFuelTypes.includes(type)}
								class:text-white={selectedFuelTypes.includes(type)}
								class:bg-slate-800={selectedFuelTypes.includes(type)}
								class:text-slate-400={selectedFuelTypes.includes(type)}
								class="flex items-center justify-center gap-2 rounded-full border border-slate-700/80 px-3 py-2 text-sm hover:bg-slate-700 hover:text-teal-400"
							>
								{#if selectedFuelTypes.includes(type)}
									<Check class="h-4 w-4" />
								{/if}
								{type}
							</button>
						{/each}
					</div>
				</div>

				<!-- Transmission Filter -->
				<div>
					<h3 class="mb-3 text-sm font-semibold text-gray-100">Transmission</h3>
					<div class="grid grid-cols-2 gap-2">
						{#each transmissionChoices as type}
							<button
								on:click={() => (selectedTransmissions = toggleFilter(selectedTransmissions, type))}
								class:bg-teal-500={selectedTransmissions.includes(type)}
								class:text-white={selectedTransmissions.includes(type)}
								class:bg-slate-800={selectedTransmissions.includes(type)}
								class:text-slate-400={selectedTransmissions.includes(type)}
								class="flex items-center justify-center gap-2 rounded-full border border-slate-700/80 px-3 py-2 text-sm hover:bg-slate-700 hover:text-teal-400"
							>
								{#if selectedTransmissions.includes(type)}
									<Check class="h-4 w-4" />
								{/if}
								{type}
							</button>
						{/each}
					</div>
				</div>

				<!-- Price Range Filter -->
				<div>
					<label class="mb-3 block text-sm font-semibold text-gray-100">
						Price Range: <span class="text-teal-400">₹{priceRange.toLocaleString()}</span>
					</label>
					<input
						id="priceRange"
						type="range"
						min="0"
						max={maxPriceFound}
						step="100"
						bind:value={priceRange}
						class="h-2 w-full rounded-full bg-slate-700 accent-teal-500"
					/>
					<div class="mt-2 flex justify-between text-xs text-slate-400">
						<span>₹0</span>
						<span>₹{maxPriceFound.toLocaleString()}</span>
					</div>
				</div>

				<div class="space-y-3">
					<button
						on:click={applyAndCloseFilters}
						class="w-full rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 py-3 text-sm text-white hover:from-teal-600 hover:to-cyan-700"
					>
						Apply Filters
					</button>
					<button
						on:click={clearFilters}
						class="w-full rounded-full border border-slate-700/80 bg-slate-800/70 py-3 text-sm text-slate-300 hover:bg-slate-700 hover:text-teal-400"
					>
						Clear Filters
					</button>
				</div>
			</div>
		</aside>
	{/if}
</div>

<style>
	/* Custom styles for range input */
	input[type='range']::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 16px;
		height: 16px;
		background: #14b8a6; /* teal-500 */
		border-radius: 50%;
		border: 2px solid #1e293b; /* slate-800 */
		cursor: pointer;
	}
	input[type='range']::-moz-range-thumb {
		width: 16px;
		height: 16px;
		background: #14b8a6;
		border-radius: 50%;
		border: 2px solid #1e293b;
		cursor: pointer;
	}
</style>
