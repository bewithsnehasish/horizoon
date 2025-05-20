<!-- src/routes/cars/+page.svelte -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

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
		FilterX
	} from 'lucide-svelte';

	// Car Interface
	interface Car {
		id: string;
		name: string;
		brand: string;
		type: 'Sedan' | 'SUV' | 'Electric' | 'Luxury' | 'Hatchback' | 'Convertible';
		pricePerDay: number;
		image: string;
		rating: number;
		seats: number;
		fuelType: 'Petrol' | 'Diesel' | 'Electric' | 'Hybrid';
		range?: number;
		location?: string;
		features: string[];
		colorsAvailable: string[];
	}

	// Mock Car Data (Replace with API call in a real app)
	const mockCars: Car[] = [
		{
			id: 'tesla-model-3',
			name: 'Tesla Model 3',
			brand: 'Tesla',
			type: 'Electric',
			pricePerDay: 95,
			image:
				'https://images.unsplash.com/photo-1610470832703-95d40c3fad55?w=500&auto=format&fit=crop&q=60',
			rating: 4.9,
			seats: 5,
			fuelType: 'Electric',
			range: 350,
			location: 'San Francisco, CA',
			features: ['Autopilot', 'Panoramic Roof', 'Premium Audio'],
			colorsAvailable: ['#DB2777', '#14B8A6', '#EFF6FF']
		},
		{
			id: 'bmw-x7',
			name: 'BMW X7',
			brand: 'BMW',
			type: 'SUV',
			pricePerDay: 180,
			image:
				'https://images.unsplash.com/photo-1603764365431-483436562596?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=70',
			rating: 4.8,
			seats: 7,
			fuelType: 'Petrol',
			location: 'New York, NY',
			features: ['Heated Seats', 'Sunroof', 'Parking Assist'],
			colorsAvailable: ['#1E293B', '#F1F5F9', '#0EA5E9']
		},
		{
			id: 'audi-a6',
			name: 'Audi A6',
			brand: 'Audi',
			type: 'Sedan',
			pricePerDay: 110,
			image:
				'https://images.unsplash.com/photo-1616422285623-13ff0162193c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=70',
			rating: 4.7,
			seats: 5,
			fuelType: 'Diesel',
			features: ['Virtual Cockpit', 'Ambient Lighting', 'Leather Seats'],
			colorsAvailable: ['#64748B', '#334155', '#DC2626']
		},
		{
			id: 'mercedes-c-class',
			name: 'Mercedes C-Class',
			brand: 'Mercedes-Benz',
			type: 'Luxury',
			pricePerDay: 130,
			image:
				'https://images.unsplash.com/photo-1587050106610-185f45BOLz-c-A?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=70',
			rating: 4.8,
			seats: 5,
			fuelType: 'Petrol',
			features: ['Burmester Sound', 'Adaptive Cruise', 'MBUX System'],
			colorsAvailable: ['#A1A1AA', '#111827', '#FDE68A']
		},
		{
			id: 'ford-mustang',
			name: 'Ford Mustang GT',
			brand: 'Ford',
			type: 'Convertible',
			pricePerDay: 150,
			image:
				'https://images.unsplash.com/photo-1549927681-f2a408912ddb?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=70',
			rating: 4.6,
			seats: 4,
			fuelType: 'Petrol',
			features: ['V8 Engine', 'Performance Pack', 'Convertible Top'],
			colorsAvailable: ['#FACC15', '#1D4ED8', '#4B5563']
		},
		{
			id: 'toyota-rav4',
			name: 'Toyota RAV4 Hybrid',
			brand: 'Toyota',
			type: 'SUV',
			pricePerDay: 85,
			image:
				'https://images.unsplash.com/photo-1618434499042-669eadf8df98?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=70',
			rating: 4.5,
			seats: 5,
			fuelType: 'Hybrid',
			range: 580,
			features: ['Fuel Efficient', 'AWD', 'Toyota Safety Sense'],
			colorsAvailable: ['#047857', '#6B7280', '#D1D5DB']
		},
		{
			id: 'honda-civic',
			name: 'Honda Civic Type R',
			brand: 'Honda',
			type: 'Hatchback',
			pricePerDay: 90,
			image:
				'https://images.unsplash.com/photo-1620760452567-cd3dec70fcc3?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=70',
			rating: 4.7,
			seats: 4,
			fuelType: 'Petrol',
			features: ['Sporty Design', 'Manual Transmission', 'Great Handling'],
			colorsAvailable: ['#DC2626', '#F8FAFC', '#0F172A']
		},
		{
			id: 'porsche-911',
			name: 'Porsche 911 Carrera',
			brand: 'Porsche',
			type: 'Luxury',
			pricePerDay: 250,
			image:
				'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=70',
			rating: 4.9,
			seats: 4,
			fuelType: 'Petrol',
			features: ['Iconic Design', 'Performance', 'PDK Transmission'],
			colorsAvailable: ['#EAB308', '#020617', '#78716C']
		}
	];

	// State for search, filters, sorting, and pagination
	let searchTerm = '';
	let showFiltersPanel = false;
	let sortBy = 'rating';
	let priceRange = 300; // Max price filter (default to max price in dataset)
	let carTypeFilter: string = 'All'; // Car type filter
	let currentPage = 1;
	const carsPerPage = 8;

	// Compute max price for the range slider
	const maxPrice = Math.max(...mockCars.map((car) => car.pricePerDay));

	// Reset priceRange to maxPrice on mount
	onMount(() => {
		priceRange = maxPrice;
	});

	// Reactive filtered and sorted cars
	$: filteredCars = mockCars
		.filter((car) => {
			// Search filter
			const matchesSearch =
				car.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
				car.brand.toLowerCase().includes(searchTerm.toLowerCase()) ||
				car.type.toLowerCase().includes(searchTerm.toLowerCase());

			// Price filter
			const matchesPrice = car.pricePerDay <= priceRange;

			// Car type filter
			const matchesType = carTypeFilter === 'All' || car.type === carTypeFilter;

			return matchesSearch && matchesPrice && matchesType;
		})
		.sort((a, b) => {
			if (sortBy === 'rating') return b.rating - a.rating;
			if (sortBy === 'priceLowToHigh') return a.pricePerDay - b.pricePerDay;
			if (sortBy === 'priceHighToLow') return b.pricePerDay - a.pricePerDay;
			if (sortBy === 'name') return a.name.localeCompare(b.name); // Added sorting by name
			return 0;
		});

	// Pagination logic
	$: totalPages = Math.ceil(filteredCars.length / carsPerPage);
	$: paginatedCars = filteredCars.slice((currentPage - 1) * carsPerPage, currentPage * carsPerPage);

	// Reset to page 1 when filters change
	$: {
		searchTerm, priceRange, carTypeFilter, sortBy;
		currentPage = 1;
	}

	const navigateToCarDetail = (carId: string) => {
		goto(`/cars/${carId}`);
	};

	const clearFilters = () => {
		searchTerm = '';
		sortBy = 'rating';
		priceRange = maxPrice;
		carTypeFilter = 'All';
		showFiltersPanel = false;
		currentPage = 1;
	};
</script>

<div class="font-quicksand min-h-screen bg-slate-950 pb-20 text-gray-200 antialiased">
	<!-- Explore Page Header -->
	<header class="sticky top-0 z-30 bg-slate-950/80 p-4 shadow-md backdrop-blur-lg">
		<div class="mx-auto flex max-w-7xl items-center gap-4">
			<button
				on:click={() => (window.history.length > 1 ? window.history.back() : goto('/'))}
				class="rounded-full p-2.5 text-slate-300 transition-colors hover:bg-slate-800 hover:text-white"
				aria-label="Go back"
			>
				<ChevronLeft class="h-6 w-6" />
			</button>
			<div class="relative flex-grow">
				<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
					<Search class="h-5 w-5 text-slate-400" />
				</div>
				<input
					type="search"
					bind:value={searchTerm}
					placeholder="Search cars by name, brand, or type..."
					class="w-full rounded-xl border border-slate-700 bg-slate-800/70 py-3 pl-10 pr-4 text-gray-100 placeholder-slate-400 transition-colors focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500"
				/>
			</div>
			<button
				on:click={() => (showFiltersPanel = !showFiltersPanel)}
				class="rounded-xl border border-slate-700 bg-slate-800/70 p-3 text-slate-300 transition-colors hover:border-teal-500/50 hover:text-teal-400"
				aria-label="Toggle Filters"
				aria-expanded={showFiltersPanel}
			>
				<SlidersHorizontal class="h-5 w-5" />
			</button>
		</div>
	</header>

	<main class="mx-auto max-w-7xl px-4 py-6 sm:py-8">
		<div class="mb-6 flex flex-col items-center justify-between gap-4 sm:flex-row">
			<h1
				class="bg-gradient-to-r from-teal-400 to-sky-500 bg-clip-text text-3xl font-bold text-transparent"
			>
				Explore Our Fleet ({filteredCars.length})
			</h1>
			<div class="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800/70 p-1">
				<span class="px-2 text-xs text-slate-400">Sort by:</span>
				<select
					bind:value={sortBy}
					class="cursor-pointer rounded-md bg-slate-800 p-2 text-sm text-gray-200 focus:outline-none focus:ring-1 focus:ring-teal-500"
				>
					<option value="rating">Rating</option>
					<option value="priceLowToHigh">Price: Low to High</option>
					<option value="priceHighToLow">Price: High to Low</option>
					<option value="name">Name (A-Z)</option>
				</select>
			</div>
		</div>

		{#if paginatedCars.length > 0}
			<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 sm:gap-8 lg:grid-cols-3 xl:grid-cols-4">
				{#each paginatedCars as car (car.id)}
					<div
						on:click={() => navigateToCarDetail(car.id)}
						on:keydown={(e) => e.key === 'Enter' && navigateToCarDetail(car.id)}
						role="button"
						tabindex="0"
						class="group cursor-pointer overflow-hidden rounded-2xl border border-slate-700/50 bg-gradient-to-br from-slate-800/70 to-slate-900/80 shadow-xl transition-all duration-300 ease-out hover:-translate-y-1 hover:border-teal-500/30 hover:shadow-2xl"
					>
						<div class="relative h-56 sm:h-64">
							<img
								src={car.image}
								alt={car.name}
								class="h-full w-full object-cover transition-transform duration-500 ease-in-out group-hover:scale-105"
								loading="lazy"
							/>
							<div
								class="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent"
							></div>
							<div
								class="absolute right-3 top-3 flex items-center gap-1 rounded-full bg-slate-900/80 px-2.5 py-1 text-xs font-semibold text-yellow-300 shadow-md backdrop-blur-sm"
							>
								<Star class="h-3.5 w-3.5 fill-yellow-400 text-yellow-400" />
								{car.rating.toFixed(1)}
							</div>
							<div class="absolute bottom-3 left-3">
								<span
									class="rounded-lg border border-teal-500/30 bg-teal-500/20 px-3 py-1.5 text-xs font-semibold text-teal-300 backdrop-blur-sm"
									>{car.type}</span
								>
							</div>
						</div>
						<div class="p-5">
							<h2
								class="mb-1 truncate text-xl font-semibold text-gray-100 transition-colors group-hover:text-teal-400"
							>
								{car.name}
							</h2>
							<p class="mb-3 text-sm font-medium text-slate-400">{car.brand}</p>

							<div class="mb-4 flex items-center justify-between text-sm text-slate-300">
								<div class="flex items-center gap-1.5">
									<Users class="h-4 w-4 text-sky-400" />
									<span>{car.seats} Seats</span>
								</div>
								<div class="flex items-center gap-1.5">
									{#if car.fuelType === 'Electric'}
										<Zap class="h-4 w-4 text-green-400" />
										<span>{car.range} km range</span>
									{:else}
										<Fuel class="h-4 w-4 text-orange-400" />
										<span>{car.fuelType}</span>
									{/if}
								</div>
							</div>

							<div class="flex items-center justify-between">
								<p class="text-2xl font-bold text-teal-400">
									${car.pricePerDay}<span class="text-xs font-medium text-slate-400">/day</span>
								</p>
								<button
									class="transform rounded-lg bg-gradient-to-r from-teal-500 to-sky-600 px-5 py-2.5 text-sm font-semibold text-white shadow-md transition-all duration-300 hover:from-teal-600 hover:to-sky-700 group-hover:scale-105"
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
				class="flex min-h-[50vh] flex-col items-center justify-center rounded-2xl bg-slate-800/50 p-8 text-center shadow-lg"
			>
				<FilterX class="mb-6 h-20 w-20 text-teal-500/50" />
				<h2 class="mb-2 text-2xl font-semibold text-gray-100">No Cars Found</h2>
				<p class="max-w-md text-slate-400">
					We couldn't find any cars matching your current search "{searchTerm}". Try adjusting your
					search or filters.
				</p>
				<button
					on:click={clearFilters}
					class="mt-6 rounded-lg bg-teal-600 px-6 py-2.5 font-semibold text-white shadow-md transition-colors hover:bg-teal-500"
				>
					Clear Search & Filters
				</button>
			</div>
		{/if}

		<!-- Dynamic Pagination -->
		{#if filteredCars.length > carsPerPage}
			<div class="mt-10 flex items-center justify-center gap-2">
				<button
					on:click={() => (currentPage = currentPage - 1)}
					disabled={currentPage === 1}
					class="rounded-lg bg-slate-800 p-2.5 text-slate-400 hover:text-teal-400 disabled:cursor-not-allowed disabled:opacity-50"
					aria-label="Previous page"
				>
					<ChevronLeft class="h-5 w-5" />
				</button>
				{#each Array(totalPages) as _, i}
					{@const pageNum = i + 1}
					<button
						on:click={() => (currentPage = pageNum)}
						class="rounded-lg px-4 py-2 text-sm font-medium {currentPage === pageNum
							? 'bg-teal-500 text-white'
							: 'bg-slate-800 text-slate-400 hover:bg-slate-700'}"
						aria-label={`Page ${pageNum}`}
						aria-current={currentPage === pageNum ? 'page' : undefined}
					>
						{pageNum}
					</button>
				{/each}
				<button
					on:click={() => (currentPage = currentPage + 1)}
					disabled={currentPage === totalPages}
					class="rounded-lg bg-slate-800 p-2.5 text-slate-400 hover:text-teal-400 disabled:cursor-not-allowed disabled:opacity-50"
					aria-label="Next page"
				>
					<ChevronRight class="h-5 w-5" />
				</button>
			</div>
		{/if}
	</main>

	<!-- Filters Panel -->
	{#if showFiltersPanel}
		<div
			class="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
			on:click={() => (showFiltersPanel = false)}
			on:keydown={(e) => e.key === 'Escape' && (showFiltersPanel = false)}
			aria-hidden="true"
		></div>
		<div
			class="fixed right-0 top-0 z-50 h-full w-80 max-w-[90vw] transform bg-slate-900 p-6 shadow-2xl transition-transform duration-300 ease-out {showFiltersPanel
				? 'translate-x-0'
				: 'translate-x-full'}"
			role="dialog"
			aria-modal="true"
			aria-label="Filters panel"
		>
			<div class="mb-6 flex items-center justify-between">
				<h2 class="text-xl font-semibold text-gray-100">Filters</h2>
				<button
					on:click={() => (showFiltersPanel = false)}
					class="rounded-full p-2 text-slate-400 hover:bg-slate-800"
					aria-label="Close filters panel"
				>
					×
				</button>
			</div>
			<div class="space-y-6 text-sm">
				<!-- Price Range Filter -->
				<label class="block">
					<span class="text-slate-300">Price Range: ${priceRange}</span>
					<input
						type="range"
						min="0"
						max={maxPrice}
						bind:value={priceRange}
						class="mt-1 w-full accent-teal-500"
					/>
				</label>

				<!-- Car Type Filter -->
				<label class="block">
					<span class="text-slate-300">Car Type:</span>
					<select
						bind:value={carTypeFilter}
						class="mt-1 w-full rounded-md border border-slate-700 bg-slate-800 p-2 text-gray-200 focus:ring-teal-500"
					>
						<option value="All">All</option>
						<option value="Sedan">Sedan</option>
						<option value="SUV">SUV</option>
						<option value="Electric">Electric</option>
						<option value="Luxury">Luxury</option>
						<option value="Hatchback">Hatchback</option>
						<option value="Convertible">Convertible</option>
					</select>
				</label>

				<button
					on:click={() => (showFiltersPanel = false)}
					class="w-full rounded-lg bg-teal-600 py-2.5 font-semibold text-white hover:bg-teal-500"
				>
					Apply Filters
				</button>
				<button
					on:click={clearFilters}
					class="w-full rounded-lg bg-slate-700 py-2.5 font-semibold text-slate-300 hover:bg-slate-600"
				>
					Clear Filters
				</button>
			</div>
		</div>
	{/if}
</div>

<style>
	input[type='range']::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 16px;
		height: 16px;
		background: #14b8a6;
		border-radius: 50%;
		cursor: pointer;
		border: 2px solid #0f766e;
	}

	input[type='range']::-moz-range-thumb {
		width: 16px;
		height: 16px;
		background: #14b8a6;
		border-radius: 50%;
		cursor: pointer;
		border: 2px solid #0f766e;
	}
</style>
