<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import axios from 'axios'; // Import Axios

	// Lucide Icons
	import {
		MapPin,
		Search,
		User,
		Loader2,
		AlertTriangle,
		XCircle,
		CalendarDays, // For Bookings (Bottom Nav)
		Car, // General Car (Category)
		CarFront, // For SUV type (Category)
		Zap, // For Electric Cars (Category)
		Sparkles, // For Luxury/Premium (Category & Rating)
		Ship, // Logo
		ChevronRight
	} from 'lucide-svelte';

	// Define the Vehicle interface based on API response
	interface Vehicle {
		id: string;
		name: string;
		brand: string;
		vehicle_type: string;
		location: string;
		price_per_day: number;
		price_per_hour: number;
		image_1: string; // Base64 encoded image
		current_status: string;
		rating: number;
		seating_capacity: number;
	}

	// Page State
	let searchQuery = '';
	let currentUserLocation: string | null = null;
	let locationLoading = true;
	let locationError: string | null = null;

	let featuredCars: Vehicle[] = [];
	let vehiclesLoading = true;
	let vehiclesError: string | null = null;

	const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
	const nominatimUserAgent = 'HorizoonCarRentalApp/1.0 (Svelte Edition)';
	const vehiclesApiUrl = `${API_BASE_URL}/business/vehicles/`;
	// const vehiclesApiUrl = 'http://0.0.0.0:8000/business/vehicles/'; // API URL

	// Car Categories Data
	const carCategories = [
		{
			name: 'Car',
			icon: Car,
			color: 'text-sky-400',
			bgColor: 'bg-sky-500/20',
			action: () => goto('/cars')
		},
		{
			name: 'Bike',
			icon: CarFront,
			color: 'text-amber-400',
			bgColor: 'bg-amber-500/20',
			action: () => goto('/cars')
		},
		{
			name: 'Electric',
			icon: Zap,
			color: 'text-green-400',
			bgColor: 'bg-green-500/20',
			action: () => goto('/cars')
		},
		{
			name: 'Truck',
			icon: Sparkles,
			color: 'text-fuchsia-400',
			bgColor: 'bg-fuchsia-500/20',
			action: () => goto('/cars')
		}
	];

	// Bottom Navigation Data
	const navItems = [
		{ icon: Search, label: 'Explore', href: '/' }, // Adjusted Home to Explore with /
		{ icon: Car, label: 'Rides', href: '/cars' },
		{ icon: CalendarDays, label: 'Bookings', href: '/bookings' },
		{ icon: User, label: 'Profile', href: '/profile' }
	];

	async function fetchFeaturedCars() {
		vehiclesLoading = true;
		vehiclesError = null;
		try {
			const response = await axios.get(vehiclesApiUrl);
			if (response.data && response.data.vehicles) {
				featuredCars = response.data.vehicles;
			} else {
				featuredCars = []; // Or handle as error
				vehiclesError = 'Unexpected API response format.';
			}
		} catch (error) {
			console.error('Error fetching featured cars:', error);
			vehiclesError = 'Could not load featured cars. Please try again later.';
			featuredCars = []; // Set to empty on error
		} finally {
			vehiclesLoading = false;
		}
	}

	onMount(() => {
		const fetchCurrentLocation = async () => {
			if (!navigator.geolocation) {
				locationError = 'Location services not supported.';
				locationLoading = false;
				return;
			}
			locationLoading = true;
			locationError = null;
			navigator.geolocation.getCurrentPosition(
				async (position) => {
					const { latitude, longitude } = position.coords;
					try {
						const geoResponse = await fetch(
							`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=16&addressdetails=1`,
							{ headers: { 'User-Agent': nominatimUserAgent } }
						);
						if (!geoResponse.ok) throw new Error(`Geocoding failed: ${geoResponse.status}`);
						const geoData = await geoResponse.json();
						if (geoData && geoData.display_name) {
							currentUserLocation = geoData.display_name;
						} else if (geoData && geoData.address) {
							const addr = geoData.address;
							const parts = [
								addr.road || addr.pedestrian,
								addr.suburb || addr.neighbourhood,
								addr.city_district,
								addr.city || addr.town || addr.village,
								addr.postcode
							].filter(Boolean);
							currentUserLocation =
								parts.join(', ') || `Lat: ${latitude.toFixed(3)}, Lon: ${longitude.toFixed(3)}`;
						} else {
							currentUserLocation = `Lat: ${latitude.toFixed(3)}, Lon: ${longitude.toFixed(3)}`;
						}
					} catch (geoErr: any) {
						console.error('Reverse geocoding error:', geoErr);
						currentUserLocation = `Lat: ${latitude.toFixed(3)}, Lon: ${longitude.toFixed(3)}`;
						locationError = 'Could not fetch detailed address.';
					} finally {
						locationLoading = false;
					}
				},
				(err) => {
					locationLoading = false;
					switch (err.code) {
						case err.PERMISSION_DENIED:
							locationError = 'Location permission denied. Adjust settings.';
							break;
						case err.POSITION_UNAVAILABLE:
							locationError = 'Location information unavailable.';
							break;
						case err.TIMEOUT:
							locationError = 'Location request timed out.';
							break;
						default:
							locationError = 'Unable to fetch location.';
					}
					console.error('Geolocation error:', err);
					currentUserLocation = 'Location not available';
				},
				{ enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
			);
		};

		fetchCurrentLocation();
		fetchFeaturedCars();
	});
</script>

<div class="font-quicksand min-h-screen bg-slate-950 pb-28 text-gray-300 antialiased">
	<!-- Header -->
	<header
		class="sticky top-0 z-30 rounded-b-3xl bg-slate-900/70 p-4 shadow-xl backdrop-blur-lg sm:p-5"
	>
		<div class="mb-4 flex items-center justify-between">
			<a href="/" class="flex items-center gap-2 text-white">
				<Ship class="h-8 w-8 text-teal-400" />
				<h1 class="text-3xl font-bold tracking-tight">
					Horiz<span class="text-teal-400">oo</span>n
				</h1>
			</a>
			<button
				on:click={() => goto('/profile')}
				class="rounded-full p-2 transition-colors hover:bg-slate-700/50"
			>
				<User class="h-6 w-6 text-slate-300" />
			</button>
		</div>

		<div
			class="flex items-center rounded-xl bg-slate-800/80 p-1 shadow-md transition-all focus-within:ring-2 focus-within:ring-teal-500"
		>
			<div class="p-2.5 text-slate-400">
				<Search class="h-5 w-5" />
			</div>
			<input
				class="flex-grow bg-transparent py-2.5 pr-3 text-sm font-medium text-gray-100 placeholder-slate-400 focus:outline-none"
				placeholder="Search cars, e.g. 'SUV in New York'"
				type="text"
				bind:value={searchQuery}
				on:keyup={(e) => {
					if (e.key === 'Enter') goto(`/cars?q=${searchQuery}`);
				}}
			/>
		</div>
		<div class="mt-3 flex min-w-0 items-center text-xs text-slate-400">
			{#if locationLoading}
				<Loader2 class="mr-2 h-4 w-4 flex-shrink-0 animate-spin text-teal-400" />
				<span class="truncate">Finding nearby locations...</span>
			{:else if locationError && !currentUserLocation?.startsWith('Lat:')}
				{#if locationError.includes('permission denied')}
					<XCircle class="mr-1.5 h-3.5 w-3.5 flex-shrink-0 text-yellow-500" />
				{:else}
					<AlertTriangle class="mr-1.5 h-3.5 w-3.5 flex-shrink-0 text-red-500" />
				{/if}
				<span class="truncate text-xs">{locationError}</span>
			{:else if currentUserLocation}
				<MapPin class="mr-1.5 h-3.5 w-3.5 flex-shrink-0 text-teal-500" />
				<span class="truncate text-xs">{currentUserLocation}</span>
			{/if}
		</div>
	</header>

	<!-- Hero Section -->
	<section
		class="relative mt-1 flex h-[55vh] items-center justify-center overflow-hidden text-center sm:h-[60vh]"
	>
		<div class="absolute inset-0 z-10 bg-gradient-to-b from-slate-950/10 to-slate-950/90"></div>
		<img
			src="https://images.unsplash.com/photo-1513036191774-b2badb8fcb76?q=80&w=1976&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
			alt="Scenic road with a car"
			class="absolute inset-0 h-full w-full object-cover"
		/>
		<div class="relative z-20 mx-auto max-w-2xl p-6">
			<h2
				class="shadow-text mb-4 text-4xl font-bold leading-tight tracking-tight text-white sm:text-5xl"
			>
				Your Journey Starts Here.
			</h2>
			<p class="shadow-text-sm mb-8 text-lg text-gray-200/90 sm:text-xl">
				Discover amazing cars for your next adventure. Horizoon offers comfort, style, and
				reliability.
			</p>
			<button
				on:click={() => goto('/cars')}
				class="transform rounded-lg bg-gradient-to-r from-teal-500 to-cyan-600 px-8 py-3.5 text-lg font-semibold text-white shadow-lg transition-all duration-300 ease-out hover:scale-105 hover:from-teal-600 hover:to-cyan-700 focus:outline-none focus:ring-4 focus:ring-teal-500/50"
			>
				Explore All Cars
			</button>
		</div>
	</section>

	<!-- Car Categories Section -->
	<section class="px-4 py-8 sm:py-12">
		<div class="mb-6 flex items-center justify-between">
			<h2 class="text-2xl font-semibold text-gray-100">Browse by Category</h2>
			<a
				href="/cars/categories"
				class="group flex items-center text-sm font-medium text-teal-400 hover:text-teal-300"
			>
				See All <ChevronRight class="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1" />
			</a>
		</div>
		<div class="grid grid-cols-2 gap-4 sm:grid-cols-4 sm:gap-5">
			{#each carCategories as category (category.name)}
				<button
					on:click={category.action}
					class="group flex aspect-square transform flex-col items-center justify-center rounded-2xl bg-slate-800/70 p-4 shadow-lg transition-all duration-300 ease-out hover:-translate-y-1 hover:bg-slate-700/80 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 focus:ring-offset-slate-950"
				>
					<div
						class="rounded-full p-3.5 {category.bgColor} mb-3 transition-transform duration-300 ease-out group-hover:scale-110 group-hover:shadow-md {category.color.replace(
							'text-',
							'shadow-'
						)}/30"
					>
						<svelte:component this={category.icon} class="{category.color} h-8 w-8 sm:h-9" />
					</div>
					<span class="text-center text-base font-semibold text-gray-200">{category.name}</span>
				</button>
			{/each}
		</div>
	</section>

	<!-- Featured Cars Section -->
	<section class="px-4 py-8 sm:py-12">
		<div class="mb-6 flex items-center justify-between">
			<h2 class="text-2xl font-semibold text-gray-100">Popular Rides</h2>
			<a
				href="/cars/popular"
				class="group flex items-center text-sm font-medium text-teal-400 hover:text-teal-300"
			>
				View More <ChevronRight
					class="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1"
				/>
			</a>
		</div>

		{#if vehiclesLoading}
			<div class="flex h-64 items-center justify-center">
				<Loader2 class="h-12 w-12 animate-spin text-teal-400" />
				<p class="ml-3 text-lg text-slate-400">Loading amazing rides...</p>
			</div>
		{:else if vehiclesError}
			<div
				class="flex h-64 flex-col items-center justify-center rounded-lg bg-slate-800/50 p-6 text-center"
			>
				<AlertTriangle class="mb-4 h-12 w-12 text-red-400" />
				<p class="mb-2 text-lg text-red-300">Oops! Something went wrong.</p>
				<p class="mb-4 text-sm text-slate-400">{vehiclesError}</p>
				<button
					on:click={fetchFeaturedCars}
					class="rounded-lg bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-teal-500"
				>
					Try Again
				</button>
			</div>
		{:else if featuredCars.length > 0}
			<div class="grid grid-cols-1 gap-5 sm:gap-6 md:grid-cols-2 lg:grid-cols-3">
				{#each featuredCars as car (car.id)}
					<div
						on:click={() => goto(`/cars/${car.id}`)}
						class="group cursor-pointer overflow-hidden rounded-2xl bg-slate-800/70 shadow-lg transition-all duration-300 ease-out hover:bg-slate-800 hover:shadow-xl hover:ring-2 hover:ring-teal-500/30"
					>
						<div class="relative h-48 sm:h-56">
							<img
								src={car.image_1}
								alt="{car.brand} {car.name}"
								class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
							/>
							<div
								class="absolute right-3 top-3 flex items-center rounded-full bg-slate-900/80 px-2.5 py-1 text-xs font-semibold text-yellow-400 backdrop-blur-sm"
							>
								<Sparkles class="mr-1 h-3.5 w-3.5 text-yellow-500" />
								{car.rating.toFixed(1)}
							</div>
							{#if car.current_status === 'available'}
								<span
									class="absolute left-3 top-3 rounded-full bg-green-500/80 px-2 py-0.5 text-xs font-semibold text-white backdrop-blur-sm"
								>
									Available
								</span>
							{:else}
								<span
									class="absolute left-3 top-3 rounded-full bg-yellow-600/80 px-2 py-0.5 text-xs font-semibold text-white backdrop-blur-sm"
								>
									On Request
								</span>
							{/if}
						</div>
						<div class="p-5">
							<h3
								class="mb-1 truncate text-xl font-semibold text-gray-100 transition-colors group-hover:text-teal-400"
							>
								{car.brand}
								{car.name}
							</h3>
							<p class="mb-1 text-sm text-slate-400">{car.vehicle_type}</p>
							<p class="mb-3 text-xs text-slate-500">
								<MapPin class="mr-1 inline h-3 w-3" />{car.location}
							</p>
							<div class="flex items-center justify-between">
								<p class="text-xl font-bold text-teal-400">
									₹{car.price_per_day.toLocaleString()}<span
										class="text-xs font-medium text-slate-400">/day</span
									>
								</p>
								<button
									class="rounded-lg bg-teal-600 px-4 py-2 text-xs font-semibold text-white transition-colors hover:bg-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-400 focus:ring-offset-2 focus:ring-offset-slate-800"
								>
									Book Now
								</button>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{:else}
			<div
				class="flex h-64 flex-col items-center justify-center rounded-lg bg-slate-800/50 p-6 text-center"
			>
				<Car class="mb-4 h-12 w-12 text-slate-500" />
				<p class="text-lg text-slate-400">No cars available at the moment.</p>
				<p class="text-sm text-slate-500">Please check back later!</p>
			</div>
		{/if}
	</section>

	<!-- Bottom Navigation -->
	<nav
		class="fixed bottom-0 left-0 right-0 z-30 flex w-full items-center justify-around rounded-t-2xl border-t border-slate-700/50 bg-slate-900/80 px-4 py-3 shadow-2xl backdrop-blur-lg"
	>
		{#each navItems as item (item.label)}
			{@const isActive =
				$page.url.pathname === item.href ||
				($page.url.pathname.startsWith(item.href) && item.href !== '/')}
			<a
				href={item.href}
				class="flex min-w-[60px] flex-col items-center rounded-lg p-2 transition-colors duration-200
					   {isActive ? 'text-teal-400' : 'text-slate-400 hover:text-slate-200'}"
				aria-label={item.label}
			>
				<div
					class="mb-0.5 rounded-full p-2 transition-all duration-200
						   {isActive
						? 'scale-110 bg-teal-500/10 shadow-md shadow-teal-500/30'
						: 'group-hover:bg-slate-700/50'}"
				>
					<svelte:component this={item.icon} class="h-6 w-6" />
				</div>
				<span class="text-xs font-medium">{item.label}</span>
			</a>
		{/each}
	</nav>
</div>

<style>
	:global(.font-quicksand) {
		font-family: 'Quicksand', sans-serif;
	}
	.shadow-text {
		text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
	}
	.shadow-text-sm {
		text-shadow: 0 1px 5px rgba(0, 0, 0, 0.4);
	}
</style>
