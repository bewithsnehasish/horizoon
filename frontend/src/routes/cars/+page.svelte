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
		Sparkles,
		MapPin,
		Settings,
		Heart,
		Filter,
		Grid3X3,
		List,
		ArrowUpDown
	} from 'lucide-svelte';
	import { Loader2, AlertTriangle } from 'lucide-svelte';

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
	let viewMode = 'grid'; // 'grid' or 'list'
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
		Bike: { icon: Car, color: 'text-cyan-400', bgColor: 'bg-cyan-500/20' },
		Scooter: { icon: Car, color: 'text-emerald-400', bgColor: 'bg-emerald-500/20' },
		Truck: { icon: Car, color: 'text-orange-400', bgColor: 'bg-orange-500/20' },
		Other: { icon: Car, color: 'text-purple-400', bgColor: 'bg-purple-500/20' }
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

	// Get active filters count
	$: activeFiltersCount =
		selectedVehicleTypes.length +
		selectedFuelTypes.length +
		selectedTransmissions.length +
		(priceRange !== maxPriceFound ? 1 : 0);
</script>

<div class="font-quicksand min-h-screen bg-slate-950 text-gray-200 antialiased">
	<!-- Enhanced Mobile Header -->
	<header
		class="sticky top-0 z-30 border-b border-slate-700/50 bg-gradient-to-r from-slate-900/95 to-slate-800/95 backdrop-blur-xl"
	>
		<div class="px-4 py-3">
			<!-- Top Row -->
			<div class="mb-3 flex items-center justify-between">
				<button
					on:click={() => (window.history.length > 1 ? window.history.back() : goto('/'))}
					class="rounded-full bg-slate-800/60 p-2.5 text-slate-300 transition-all duration-200 hover:bg-slate-700 hover:text-teal-400"
					aria-label="Go back"
				>
					<ChevronLeft class="h-5 w-5" />
				</button>

				<div class="flex items-center gap-2">
					<button
						on:click={() => (viewMode = viewMode === 'grid' ? 'list' : 'grid')}
						class="rounded-full bg-slate-800/60 p-2.5 text-slate-300 transition-all duration-200 hover:bg-slate-700 hover:text-teal-400"
						aria-label="Toggle view mode"
					>
						{#if viewMode === 'grid'}
							<List class="h-5 w-5" />
						{:else}
							<Grid3X3 class="h-5 w-5" />
						{/if}
					</button>
					<button
						on:click={() => (showFiltersPanel = !showFiltersPanel)}
						class="relative rounded-full bg-slate-800/60 p-2.5 text-slate-300 transition-all duration-200 hover:bg-slate-700 hover:text-teal-400"
						aria-label="Toggle Filters"
						aria-expanded={showFiltersPanel}
					>
						<Filter class="h-5 w-5" />
						{#if activeFiltersCount > 0}
							<span
								class="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-teal-500 text-xs font-medium text-white"
							>
								{activeFiltersCount}
							</span>
						{/if}
					</button>
				</div>
			</div>

			<!-- Search Bar -->
			<div class="relative">
				<div class="absolute inset-y-0 left-0 flex items-center pl-4">
					<Search class="h-5 w-5 text-slate-400" />
				</div>
				<input
					type="search"
					bind:value={searchTerm}
					placeholder="Search vehicles, brands, or locations..."
					class="w-full rounded-2xl border border-slate-700/50 bg-slate-800/70 py-3.5 pl-12 pr-4 text-gray-100 placeholder-slate-400 transition-all duration-200 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/30"
				/>
			</div>
		</div>
	</header>

	<main class="px-4 py-6">
		<!-- Results Header -->
		<div class="mb-6">
			<div class="mb-4 flex items-center justify-between">
				<div>
					<h1 class="mb-1 text-2xl font-bold text-gray-100">Available Vehicles</h1>
					{#if !vehiclesLoading}
						<p class="text-sm text-slate-400">
							{filteredAndSortedVehicles.length} vehicles found
						</p>
					{/if}
				</div>

				<!-- Sort Dropdown -->
				<div class="relative">
					<select
						bind:value={sortBy}
						class="appearance-none rounded-xl border border-slate-700/50 bg-slate-800/70 px-4 py-2.5 pr-8 text-sm text-gray-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500/30"
					>
						<option value="rating">⭐ Rating</option>
						<option value="priceLowToHigh">💰 Price: Low to High</option>
						<option value="priceHighToLow">💰 Price: High to Low</option>
						<option value="name">🔤 Name (A-Z)</option>
					</select>
					<ArrowUpDown
						class="pointer-events-none absolute right-2 top-1/2 h-4 w-4 -translate-y-1/2 transform text-slate-400"
					/>
				</div>
			</div>

			<!-- Active Filters Display -->
			{#if activeFiltersCount > 0}
				<div class="mb-4 flex flex-wrap gap-2">
					{#each selectedVehicleTypes as type}
						<span
							class="inline-flex items-center gap-1 rounded-full border border-teal-500/30 bg-teal-500/20 px-3 py-1.5 text-xs font-medium text-teal-300"
						>
							{type}
							<button
								on:click={() => (selectedVehicleTypes = toggleFilter(selectedVehicleTypes, type))}
								class="hover:text-teal-100"
							>
								<X class="h-3 w-3" />
							</button>
						</span>
					{/each}
					{#each selectedFuelTypes as type}
						<span
							class="inline-flex items-center gap-1 rounded-full border border-cyan-500/30 bg-cyan-500/20 px-3 py-1.5 text-xs font-medium text-cyan-300"
						>
							{type}
							<button
								on:click={() => (selectedFuelTypes = toggleFilter(selectedFuelTypes, type))}
								class="hover:text-cyan-100"
							>
								<X class="h-3 w-3" />
							</button>
						</span>
					{/each}
					{#each selectedTransmissions as type}
						<span
							class="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/20 px-3 py-1.5 text-xs font-medium text-emerald-300"
						>
							{type}
							<button
								on:click={() => (selectedTransmissions = toggleFilter(selectedTransmissions, type))}
								class="hover:text-emerald-100"
							>
								<X class="h-3 w-3" />
							</button>
						</span>
					{/each}
					{#if priceRange !== maxPriceFound}
						<span
							class="inline-flex items-center gap-1 rounded-full border border-purple-500/30 bg-purple-500/20 px-3 py-1.5 text-xs font-medium text-purple-300"
						>
							Under ₹{priceRange.toLocaleString()}
							<button on:click={() => (priceRange = maxPriceFound)} class="hover:text-purple-100">
								<X class="h-3 w-3" />
							</button>
						</span>
					{/if}
					<button
						on:click={clearFilters}
						class="rounded-full border border-slate-600 px-3 py-1.5 text-xs font-medium text-slate-400 transition-all duration-200 hover:border-teal-500 hover:text-teal-400"
					>
						Clear All
					</button>
				</div>
			{/if}
		</div>

		{#if vehiclesLoading}
			<div class="flex min-h-[60vh] flex-col items-center justify-center">
				<div class="relative">
					<div
						class="h-20 w-20 animate-pulse rounded-full bg-gradient-to-r from-teal-500 to-cyan-600"
					></div>
					<Loader2 class="absolute inset-0 m-auto h-8 w-8 animate-spin text-white" />
				</div>
				<p class="mt-6 text-lg text-slate-400">Loading our amazing fleet...</p>
			</div>
		{:else if vehiclesError}
			<div
				class="flex min-h-[60vh] flex-col items-center justify-center rounded-3xl border border-slate-700/50 bg-slate-800/50 p-8 shadow-xl"
			>
				<div class="mb-4 rounded-full bg-red-500/20 p-4">
					<AlertTriangle class="h-12 w-12 text-red-400" />
				</div>
				<h2 class="mb-2 text-2xl font-semibold text-red-300">Oops! Something went wrong</h2>
				<p class="mb-6 max-w-md text-center text-slate-400">{vehiclesError}</p>
				<button
					on:click={fetchAllVehicles}
					class="rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-8 py-3 font-medium text-white shadow-lg transition-all duration-200 hover:from-teal-600 hover:to-cyan-700 hover:shadow-xl"
				>
					Try Again
				</button>
			</div>
		{:else if paginatedVehicles.length > 0}
			<!-- Vehicle Grid/List -->
			<div class={viewMode === 'grid' ? 'grid grid-cols-1 gap-4 sm:grid-cols-2' : 'space-y-4'}>
				{#each paginatedVehicles as vehicle (vehicle.id)}
					{#if viewMode === 'grid'}
						<!-- Grid Card Design -->
						<div
							on:click={() => navigateToVehicleDetail(vehicle.id)}
							on:keydown={(e) => e.key === 'Enter' && navigateToVehicleDetail(vehicle.id)}
							role="button"
							tabindex="0"
							class="group overflow-hidden rounded-3xl border border-slate-700/50 bg-gradient-to-br from-slate-800/80 to-slate-900/80 shadow-xl backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 hover:border-teal-500/30 hover:shadow-2xl"
						>
							<!-- Image Section -->
							<div class="relative h-48 overflow-hidden">
								<img
									src={vehicle.image_1}
									alt="{vehicle.brand} {vehicle.name}"
									class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
									loading="lazy"
								/>
								<div
									class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"
								></div>

								<!-- Status and Rating Badges -->
								<div class="absolute left-3 right-3 top-3 flex items-start justify-between">
									{#if vehicle.current_status === 'available'}
										<span
											class="rounded-full bg-green-500/90 px-3 py-1.5 text-xs font-medium text-white shadow-lg backdrop-blur-sm"
										>
											✨ Available
										</span>
									{:else}
										<span
											class="rounded-full bg-amber-500/90 px-3 py-1.5 text-xs font-medium text-white shadow-lg backdrop-blur-sm"
										>
											⏳ On Request
										</span>
									{/if}

									<div class="rounded-full bg-slate-900/90 px-3 py-1.5 shadow-lg backdrop-blur-sm">
										<div class="flex items-center gap-1">
											<Star class="h-4 w-4 fill-yellow-400 text-yellow-400" />
											<span class="text-xs font-medium text-white">{vehicle.rating.toFixed(1)}</span
											>
										</div>
									</div>
								</div>

								<!-- Vehicle Type Badge -->
								<div class="absolute bottom-3 left-3">
									<div
										class="flex items-center gap-2 rounded-full bg-slate-900/90 px-3 py-1.5 shadow-lg backdrop-blur-sm"
									>
										<svelte:component
											this={vehicleTypeStyles[vehicle.vehicle_type].icon}
											class="h-4 w-4 {vehicleTypeStyles[vehicle.vehicle_type].color}"
										/>
										<span class="text-xs font-medium text-white">{vehicle.vehicle_type}</span>
									</div>
								</div>
							</div>

							<!-- Content Section -->
							<div class="p-5">
								<div class="mb-3">
									<h3
										class="line-clamp-1 text-xl font-bold text-gray-100 transition-colors duration-200 group-hover:text-teal-400"
									>
										{vehicle.brand}
										{vehicle.name}
									</h3>
									<div class="mt-1 flex items-center gap-1 text-sm text-slate-400">
										<MapPin class="h-4 w-4" />
										<span class="line-clamp-1">{vehicle.location}</span>
									</div>
								</div>

								<!-- Features Row -->
								<div class="mb-4 grid grid-cols-2 gap-3">
									<div
										class="flex items-center gap-2 rounded-xl bg-slate-800/50 px-3 py-2 text-sm text-slate-300"
									>
										<Users class="h-4 w-4 text-teal-400" />
										<span>{vehicle.seating_capacity} Seats</span>
									</div>
									{#if vehicle.fuel_type}
										<div
											class="flex items-center gap-2 rounded-xl bg-slate-800/50 px-3 py-2 text-sm text-slate-300"
										>
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
									<div class="mb-4">
										<span
											class="inline-block rounded-full border border-purple-500/30 bg-gradient-to-r from-purple-500/20 to-pink-500/20 px-3 py-1 text-xs font-medium text-purple-300"
										>
											{vehicle.transmission}
										</span>
									</div>
								{/if}

								<!-- Price and CTA -->
								<div class="flex items-center justify-between">
									<div>
										<p
											class="bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-2xl font-bold text-transparent"
										>
											₹{vehicle.price_per_day.toLocaleString()}
										</p>
										<p class="text-xs text-slate-400">per day</p>
									</div>
									<button
										on:click|stopPropagation={() => navigateToVehicleDetail(vehicle.id)}
										class="transform rounded-2xl bg-gradient-to-r from-teal-500 to-cyan-600 px-6 py-3 text-sm font-medium text-white shadow-lg transition-all duration-200 hover:scale-105 hover:from-teal-600 hover:to-cyan-700 hover:shadow-xl"
									>
										Book Now
									</button>
								</div>
							</div>
						</div>
					{:else}
						<!-- List View Design -->
						<div
							on:click={() => navigateToVehicleDetail(vehicle.id)}
							on:keydown={(e) => e.key === 'Enter' && navigateToVehicleDetail(vehicle.id)}
							role="button"
							tabindex="0"
							class="group overflow-hidden rounded-2xl border border-slate-700/50 bg-gradient-to-r from-slate-800/80 to-slate-900/80 shadow-lg backdrop-blur-sm transition-all duration-300 hover:border-teal-500/30 hover:shadow-xl"
						>
							<div class="flex">
								<!-- Image -->
								<div class="relative h-32 w-32 flex-shrink-0">
									<img
										src={vehicle.image_1}
										alt="{vehicle.brand} {vehicle.name}"
										class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
										loading="lazy"
									/>
									<div class="absolute inset-0 bg-gradient-to-r from-transparent to-black/20"></div>
								</div>

								<!-- Content -->
								<div class="flex-1 p-4">
									<div class="mb-2 flex items-start justify-between">
										<div>
											<h3
												class="text-lg font-bold text-gray-100 transition-colors duration-200 group-hover:text-teal-400"
											>
												{vehicle.brand}
												{vehicle.name}
											</h3>
											<div class="flex items-center gap-1 text-sm text-slate-400">
												<MapPin class="h-3 w-3" />
												<span>{vehicle.location}</span>
											</div>
										</div>
										<div class="flex items-center gap-1 rounded-full bg-slate-900/50 px-2 py-1">
											<Star class="h-3 w-3 fill-yellow-400 text-yellow-400" />
											<span class="text-xs text-white">{vehicle.rating.toFixed(1)}</span>
										</div>
									</div>

									<div class="mb-3 flex items-center gap-4 text-xs text-slate-300">
										<div class="flex items-center gap-1">
											<Users class="h-3 w-3 text-teal-400" />
											<span>{vehicle.seating_capacity}</span>
										</div>
										{#if vehicle.fuel_type}
											<div class="flex items-center gap-1">
												{#if vehicle.fuel_type === 'Electric'}
													<Zap class="h-3 w-3 text-green-400" />
												{:else}
													<Fuel class="h-3 w-3 text-orange-400" />
												{/if}
												<span>{vehicle.fuel_type}</span>
											</div>
										{/if}
										{#if vehicle.transmission}
											<span class="rounded bg-purple-500/20 px-2 py-0.5 text-xs text-purple-300">
												{vehicle.transmission}
											</span>
										{/if}
									</div>

									<div class="flex items-end justify-between">
										<div>
											<p
												class="bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-xl font-bold text-transparent"
											>
												₹{vehicle.price_per_day.toLocaleString()}
											</p>
											<p class="text-xs text-slate-400">per day</p>
										</div>
										{#if vehicle.current_status === 'available'}
											<span class="rounded-full bg-green-500/20 px-2 py-1 text-xs text-green-300">
												Available
											</span>
										{:else}
											<span class="rounded-full bg-amber-500/20 px-2 py-1 text-xs text-amber-300">
												On Request
											</span>
										{/if}
									</div>
								</div>
							</div>
						</div>
					{/if}
				{/each}
			</div>
		{:else}
			<div
				class="flex min-h-[60vh] flex-col items-center justify-center rounded-3xl border border-slate-700/50 bg-slate-800/50 p-8 shadow-xl"
			>
				<div class="mb-6 rounded-full bg-teal-500/20 p-6">
					<FilterX class="h-16 w-16 text-teal-400" />
				</div>
				<h2 class="mb-4 text-2xl font-semibold text-gray-100">No Vehicles Found</h2>
				<p class="mb-8 max-w-md text-center text-slate-400">
					We couldn't find any vehicles matching your criteria. Try adjusting your filters or search
					terms.
				</p>
				<button
					on:click={clearFilters}
					class="rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-8 py-3 font-medium text-white shadow-lg transition-all duration-200 hover:from-teal-600 hover:to-cyan-700 hover:shadow-xl"
				>
					Clear All Filters
				</button>
			</div>
		{/if}

		<!-- Enhanced Pagination -->
		{#if filteredAndSortedVehicles.length > carsPerPage}
			<div class="mt-8 flex items-center justify-center">
				<div
					class="flex items-center gap-2 rounded-2xl border border-slate-700/50 bg-slate-800/50 p-2 backdrop-blur-sm"
				>
					<button
						on:click={() => (currentPage = Math.max(1, currentPage - 1))}
						disabled={currentPage === 1}
						class="rounded-xl p-3 text-slate-400 transition-all duration-200 hover:bg-slate-700 hover:text-teal-400 disabled:cursor-not-allowed disabled:opacity-50"
					>
						<ChevronLeft class="h-5 w-5" />
					</button>

					{#each Array(Math.min(totalPages, 5)) as _, i}
						{@const pageNum = i + 1}
						<button
							on:click={() => (currentPage = pageNum)}
							class:bg-gradient-to-r={currentPage === pageNum}
							class:from-teal-500={currentPage === pageNum}
							class:to-cyan-600={currentPage === pageNum}
							class:text-white={currentPage === pageNum}
							class:shadow-lg={currentPage === pageNum}
							class:bg-slate-700={currentPage !== pageNum}
							class:text-slate-400={currentPage !== pageNum}
							class="min-w-[44px] rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200 hover:bg-slate-700 hover:text-teal-400"
						>
							{pageNum}
						</button>
					{/each}

					<button
						on:click={() => (currentPage = Math.min(totalPages, currentPage + 1))}
						disabled={currentPage === totalPages}
						class="rounded-xl p-3 text-slate-400 transition-all duration-200 hover:bg-slate-700 hover:text-teal-400 disabled:cursor-not-allowed disabled:opacity-50"
					>
						<ChevronRight class="h-5 w-5" />
					</button>
				</div>
			</div>
		{/if}
	</main>

	<!-- Enhanced Mobile-First Filters Panel -->
	{#if showFiltersPanel}
		<div
			class="fixed inset-0 z-40 bg-black/80 backdrop-blur-md"
			on:click={() => (showFiltersPanel = false)}
			on:keydown={(e) => e.key === 'Escape' && (showFiltersPanel = false)}
		></div>
		<aside
			class="fixed inset-x-0 bottom-0 z-50 max-h-[80vh] transform rounded-t-3xl border-t border-slate-700/50 bg-gradient-to-t from-slate-900 to-slate-800 shadow-2xl transition-transform duration-300"
			class:translate-y-0={showFiltersPanel}
			class:translate-y-full={!showFiltersPanel}
		>
			<!-- Handle Bar -->
			<div class="flex justify-center pb-2 pt-3">
				<div class="h-1.5 w-12 rounded-full bg-slate-600"></div>
			</div>

			<div class="max-h-[calc(80vh-60px)] overflow-y-auto px-6 pb-6">
				<!-- Header -->
				<div
					class="sticky top-0 -mx-6 mb-6 flex items-center justify-between border-b border-slate-700/50 bg-slate-800/90 px-6 py-4 backdrop-blur-sm"
				>
					<h2 class="text-xl font-bold text-gray-100">Filters</h2>
					<div class="flex items-center gap-2">
						{#if activeFiltersCount > 0}
							<span class="rounded-full bg-teal-500/20 px-3 py-1 text-sm font-medium text-teal-300">
								{activeFiltersCount} active
							</span>
						{/if}
						<button
							on:click={() => (showFiltersPanel = false)}
							class="rounded-full p-2 text-slate-400 transition-all duration-200 hover:bg-slate-700 hover:text-teal-400"
						>
							<X class="h-6 w-6" />
						</button>
					</div>
				</div>

				<div class="space-y-6">
					<!-- Vehicle Type Filter -->
					<div>
						<h3 class="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-100">
							<Car class="h-5 w-5 text-teal-400" />
							Vehicle Type
						</h3>
						<div class="grid grid-cols-2 gap-3">
							{#each vehicleTypeChoices as type}
								<button
									on:click={() => (selectedVehicleTypes = toggleFilter(selectedVehicleTypes, type))}
									class="flex items-center justify-center gap-2 rounded-2xl border px-4 py-3 text-sm font-medium transition-all duration-200"
									class:bg-gradient-to-r={selectedVehicleTypes.includes(type)}
									class:from-teal-500={selectedVehicleTypes.includes(type)}
									class:to-cyan-600={selectedVehicleTypes.includes(type)}
									class:text-white={selectedVehicleTypes.includes(type)}
									class:shadow-lg={selectedVehicleTypes.includes(type)}
									class:border-teal-500={selectedVehicleTypes.includes(type)}
									class:bg-slate-800={!selectedVehicleTypes.includes(type)}
									class:text-slate-300={!selectedVehicleTypes.includes(type)}
									class:border-slate-600={!selectedVehicleTypes.includes(type)}
									class:hover:border-teal-500={!selectedVehicleTypes.includes(type)}
									class:hover:text-teal-400={!selectedVehicleTypes.includes(type)}
								>
									<svelte:component this={vehicleTypeStyles[type].icon} class="h-4 w-4" />
									{type}
								</button>
							{/each}
						</div>
					</div>

					<!-- Fuel Type Filter -->
					<div>
						<h3 class="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-100">
							<Fuel class="h-5 w-5 text-orange-400" />
							Fuel Type
						</h3>
						<div class="grid grid-cols-2 gap-3">
							{#each fuelTypeChoices as type}
								<button
									on:click={() => (selectedFuelTypes = toggleFilter(selectedFuelTypes, type))}
									class="flex items-center justify-center gap-2 rounded-2xl border px-4 py-3 text-sm font-medium transition-all duration-200"
									class:bg-gradient-to-r={selectedFuelTypes.includes(type)}
									class:from-cyan-500={selectedFuelTypes.includes(type)}
									class:to-blue-600={selectedFuelTypes.includes(type)}
									class:text-white={selectedFuelTypes.includes(type)}
									class:shadow-lg={selectedFuelTypes.includes(type)}
									class:border-cyan-500={selectedFuelTypes.includes(type)}
									class:bg-slate-800={!selectedFuelTypes.includes(type)}
									class:text-slate-300={!selectedFuelTypes.includes(type)}
									class:border-slate-600={!selectedFuelTypes.includes(type)}
									class:hover:border-cyan-500={!selectedFuelTypes.includes(type)}
									class:hover:text-cyan-400={!selectedFuelTypes.includes(type)}
								>
									{#if type === 'Electric'}
										<Zap class="h-4 w-4" />
									{:else}
										<Fuel class="h-4 w-4" />
									{/if}
									{type}
								</button>
							{/each}
						</div>
					</div>

					<!-- Transmission Filter -->
					<div>
						<h3 class="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-100">
							<Settings class="h-5 w-5 text-purple-400" />
							Transmission
						</h3>
						<div class="grid grid-cols-2 gap-3">
							{#each transmissionChoices as type}
								<button
									on:click={() =>
										(selectedTransmissions = toggleFilter(selectedTransmissions, type))}
									class="flex items-center justify-center gap-2 rounded-2xl border px-4 py-3 text-sm font-medium transition-all duration-200"
									class:bg-gradient-to-r={selectedTransmissions.includes(type)}
									class:from-emerald-500={selectedTransmissions.includes(type)}
									class:to-green-600={selectedTransmissions.includes(type)}
									class:text-white={selectedTransmissions.includes(type)}
									class:shadow-lg={selectedTransmissions.includes(type)}
									class:border-emerald-500={selectedTransmissions.includes(type)}
									class:bg-slate-800={!selectedTransmissions.includes(type)}
									class:text-slate-300={!selectedTransmissions.includes(type)}
									class:border-slate-600={!selectedTransmissions.includes(type)}
									class:hover:border-emerald-500={!selectedTransmissions.includes(type)}
									class:hover:text-emerald-400={!selectedTransmissions.includes(type)}
								>
									<Settings class="h-4 w-4" />
									{type}
								</button>
							{/each}
						</div>
					</div>

					<!-- Price Range Filter -->
					<div>
						<h3 class="mb-4 text-lg font-semibold text-gray-100">
							Price Range:
							<span
								class="bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text font-bold text-transparent"
							>
								₹{priceRange.toLocaleString()}
							</span>
						</h3>
						<div class="rounded-2xl border border-slate-700/50 bg-slate-800/50 p-4">
							<input
								type="range"
								min="0"
								max={maxPriceFound}
								step="100"
								bind:value={priceRange}
								class="h-3 w-full cursor-pointer rounded-full bg-teal-600 accent-teal-500"
							/>
							<div class="mt-3 flex justify-between text-sm text-slate-400">
								<span>₹0</span>
								<span>₹{maxPriceFound.toLocaleString()}</span>
							</div>
						</div>
					</div>
				</div>

				<!-- Action Buttons -->
				<div
					class="sticky bottom-0 -mx-6 mt-6 border-t border-slate-700/50 bg-slate-800/90 px-6 py-4 backdrop-blur-sm"
				>
					<div class="grid grid-cols-2 gap-4">
						<button
							on:click={clearFilters}
							class="rounded-2xl border border-slate-600 bg-slate-800/70 py-4 font-medium text-slate-300 transition-all duration-200 hover:border-teal-500 hover:bg-slate-700 hover:text-teal-400"
						>
							Clear All
						</button>
						<button
							on:click={applyAndCloseFilters}
							class="rounded-2xl bg-gradient-to-r from-teal-500 to-cyan-600 py-4 font-medium text-white shadow-lg transition-all duration-200 hover:from-teal-600 hover:to-cyan-700 hover:shadow-xl"
						>
							Apply Filters
						</button>
					</div>
				</div>
			</div>
		</aside>
	{/if}
</div>

<style>
	/* Enhanced range input styling */
	input[type='range'] {
		-webkit-appearance: none;
		appearance: none;
		background: transparent;
		cursor: pointer;
	}

	input[type='range']::-webkit-slider-track {
		background: #334155;
		height: 12px;
		border-radius: 6px;
	}

	input[type='range']::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		height: 24px;
		width: 24px;
		border-radius: 50%;
		background: linear-gradient(135deg, #14b8a6, #06b6d4);
		cursor: pointer;
		border: 3px solid #1e293b;
		box-shadow: 0 4px 8px rgba(20, 184, 166, 0.3);
	}

	input[type='range']::-moz-range-track {
		background: #334155;
		height: 12px;
		border-radius: 6px;
		border: none;
	}

	input[type='range']::-moz-range-thumb {
		height: 24px;
		width: 24px;
		border-radius: 50%;
		background: linear-gradient(135deg, #14b8a6, #06b6d4);
		cursor: pointer;
		border: 3px solid #1e293b;
		box-shadow: 0 4px 8px rgba(20, 184, 166, 0.3);
	}

	/* Smooth scrolling for the filter panel */
	aside {
		scroll-behavior: smooth;
	}

	/* Text truncation utilities */
	.line-clamp-1 {
		overflow: hidden;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 1;
	}
</style>
