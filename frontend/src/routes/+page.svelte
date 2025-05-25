<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import axios from 'axios';
	import { fade, scale, fly } from 'svelte/transition';
	import { getAuthToken } from '$lib/stores/auth';

	import {
		MapPin,
		Search,
		User,
		Loader2,
		AlertTriangle,
		CalendarDays,
		Car,
		CarFront,
		Zap,
		Sparkles,
		Ship,
		ChevronRight,
		Star,
		Users
	} from 'lucide-svelte';

	interface Vehicle {
		id: string;
		name: string;
		brand: string;
		vehicle_type: string;
		location: string;
		price_per_day: number;
		price_per_hour: number;
		image_1: string;
		current_status: string;
		rating: number;
		seating_capacity: number;
	}

	interface ClientDetails {
		username: string;
		email: string;
	}

	interface UserMoreDetails {
		name: string;
		phone: string;
		gender: string;
	}

	interface UserProfileData {
		client: ClientDetails;
		details: UserMoreDetails | null;
	}

	let searchQuery = '';
	let currentUserLocation: string | null = null;
	let locationLoading = true;
	let locationError: string | null = null;
	let showLocationRetry = false;

	let featuredCars: Vehicle[] = [];
	let vehiclesLoading = true;
	let vehiclesError: string | null = null;
	let profileError: string | null = null;

	// Dynamic imports for Capacitor (to avoid SSR issues)
	let Capacitor: any = null;
	let Geolocation: any = null;
	let NativeSettings: any = null;
	let AndroidSettings: any = null;
	let IOSSettings: any = null;

	const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://0.0.0.0:8000';
	const nominatimUserAgent = 'HorizoonCarRentalApp/1.0 (Svelte Edition)';
	const vehiclesApiUrl = `${API_BASE_URL}/business/vehicles/`;
	const clientDetailsApiUrl = `${API_BASE_URL}/authentication/get-client-details/`;

	const carCategories = [
		{
			name: 'Car',
			icon: Car,
			gradient: 'from-blue-500 via-purple-500 to-pink-500',
			shadowColor: 'shadow-blue-500/25',
			action: () => goto('/cars')
		},
		{
			name: 'Bike',
			icon: CarFront,
			gradient: 'from-amber-400 via-orange-500 to-red-500',
			shadowColor: 'shadow-orange-500/25',
			action: () => goto('/cars')
		},
		{
			name: 'Electric',
			icon: Zap,
			gradient: 'from-green-400 via-emerald-500 to-teal-500',
			shadowColor: 'shadow-emerald-500/25',
			action: () => goto('/cars')
		},
		{
			name: 'Truck',
			icon: Sparkles,
			gradient: 'from-purple-500 via-pink-500 to-rose-500',
			shadowColor: 'shadow-purple-500/25',
			action: () => goto('/cars')
		}
	];

	// Image handling
	function getImageSource(image: string): string {
		if (!image) return 'https://via.placeholder.com/800x600?text=No+Image';
		if (image.startsWith('data:image')) return image;
		return image;
	}

	async function checkClientDetails() {
		const authToken = getAuthToken();
		if (!authToken) {
			return;
		}

		try {
			const response = await axios.post(clientDetailsApiUrl, { authToken });
			if (response.data.success && response.data.data.details === null) {
				profileError = 'Please complete your profile to continue.';
				setTimeout(() => goto('/completeprofile'), 1000);
			}
		} catch (err) {
			console.error('Error checking client details:', err);
			profileError = 'Failed to verify profile. Please try again.';
		}
	}

	async function fetchFeaturedCars() {
		vehiclesLoading = true;
		vehiclesError = null;
		try {
			const response = await axios.get(vehiclesApiUrl);
			if (response.data && response.data.vehicles) {
				featuredCars = response.data.vehicles;
			} else {
				featuredCars = [];
				vehiclesError = 'Unexpected API response format.';
			}
		} catch (error) {
			console.error('Error fetching featured cars:', error);
			vehiclesError = 'Could not load featured cars. Please try again later.';
			featuredCars = [];
		} finally {
			vehiclesLoading = false;
		}
	}

	// Load Capacitor modules dynamically
	async function loadCapacitorModules() {
		if (!browser) return false;

		try {
			const [capacitorCore, capacitorGeolocation, capacitorSettings] = await Promise.all([
				import('@capacitor/core'),
				import('@capacitor/geolocation'),
				import('capacitor-native-settings')
			]);

			Capacitor = capacitorCore.Capacitor;
			Geolocation = capacitorGeolocation.Geolocation;
			NativeSettings = capacitorSettings.NativeSettings;
			AndroidSettings = capacitorSettings.AndroidSettings;
			IOSSettings = capacitorSettings.IOSSettings;
			return true;
		} catch (error) {
			console.error('Error loading Capacitor modules:', error);
			return false;
		}
	}

	// Enhanced location fetching with proper Capacitor integration
	const fetchCurrentLocation = async () => {
		if (!browser) {
			locationError = 'Location not available on server';
			locationLoading = false;
			return;
		}

		locationLoading = true;
		locationError = null;
		showLocationRetry = false;
		currentUserLocation = null;

		try {
			// Load Capacitor modules if not already loaded
			const modulesLoaded = await loadCapacitorModules();

			// Check if running on native platform
			if (!modulesLoaded || !Capacitor?.isNativePlatform()) {
				await fetchLocationWeb();
				return;
			}

			// Step 1: Check current permissions
			const permissionStatus = await Geolocation.checkPermissions();
			console.log('Permission status:', permissionStatus);

			// Step 2: Request permissions if not granted
			if (permissionStatus.location !== 'granted') {
				const requestResult = await Geolocation.requestPermissions();
				console.log('Request result:', requestResult);

				if (requestResult.location !== 'granted') {
					locationError = 'Location permission not granted. Using default location.';
					currentUserLocation = 'Location not available';
					locationLoading = false;
					return;
				}
			}

			// Step 3: Try to get location
			try {
				const position = await Geolocation.getCurrentPosition({
					enableHighAccuracy: true,
					timeout: 15000,
					maximumAge: 0
				});

				await processLocationCoordinates(position.coords.latitude, position.coords.longitude);
			} catch (locationErr: any) {
				console.error('Location error:', locationErr);

				if (
					locationErr.message?.includes('location unavailable') ||
					locationErr.message?.includes('GPS') ||
					locationErr.code === 2 ||
					locationErr.code === 'LOCATION_UNAVAILABLE'
				) {
					await handleGPSNotEnabled();
				} else {
					locationError = 'Could not fetch location. Please try again.';
					currentUserLocation = 'Location not available';
					showLocationRetry = true;
				}
			}
		} catch (error: any) {
			console.error('Permission error:', error);
			locationError = 'Location services error.';
			currentUserLocation = 'Location not available';
			showLocationRetry = true;
		} finally {
			locationLoading = false;
		}
	};

	// Handle GPS not enabled with proper browser checks
	const handleGPSNotEnabled = async () => {
		if (!browser || !Capacitor) {
			locationError = 'GPS not available. Please enable location services.';
			currentUserLocation = 'Location not available';
			showLocationRetry = true;
			return;
		}

		try {
			if (Capacitor.getPlatform() === 'android') {
				// For Android, try to use location accuracy plugin if available
				if (
					browser &&
					typeof window !== 'undefined' &&
					window.cordova &&
					window.cordova.plugins &&
					window.cordova.plugins.locationAccuracy
				) {
					window.cordova.plugins.locationAccuracy.canRequest((canRequest: boolean) => {
						if (canRequest) {
							window.cordova.plugins.locationAccuracy.request(
								async () => {
									console.log('GPS enabled successfully');
									await retryLocationAfterGPSEnable();
								},
								(error: any) => {
									console.error('GPS enable error:', error);
									locationError = 'GPS not enabled. Please enable location services manually.';
									currentUserLocation = 'Location not available';
									showLocationRetry = true;
								},
								window.cordova.plugins.locationAccuracy.REQUEST_PRIORITY_HIGH_ACCURACY
							);
						} else {
							locationError = 'Cannot request GPS enable. Please enable manually.';
							currentUserLocation = 'Location not available';
							showLocationRetry = true;
						}
					});
				} else {
					locationError = 'GPS is turned off. Please enable location services.';
					currentUserLocation = 'Location not available';
					showLocationRetry = true;
				}
			} else {
				locationError = 'GPS is turned off. Please enable location services.';
				currentUserLocation = 'Location not available';
				showLocationRetry = true;
			}
		} catch (gpsError: any) {
			console.error('GPS handling error:', gpsError);
			locationError = 'GPS not enabled. Please enable location services.';
			currentUserLocation = 'Location not available';
			showLocationRetry = true;
		}
	};

	// Retry location after GPS is enabled
	const retryLocationAfterGPSEnable = async () => {
		if (!Geolocation) return;

		try {
			const position = await Geolocation.getCurrentPosition({
				enableHighAccuracy: true,
				timeout: 10000,
				maximumAge: 0
			});

			await processLocationCoordinates(position.coords.latitude, position.coords.longitude);
		} catch (error) {
			console.error('Retry location error:', error);
			locationError = 'Could not fetch location after GPS enable.';
			currentUserLocation = 'Location not available';
			showLocationRetry = true;
		}
	};

	// Web fallback for browsers
	const fetchLocationWeb = async () => {
		if (!browser || !navigator.geolocation) {
			locationError = 'Location services not supported.';
			locationLoading = false;
			return;
		}

		navigator.geolocation.getCurrentPosition(
			async (position) => {
				await processLocationCoordinates(position.coords.latitude, position.coords.longitude);
			},
			(err) => {
				locationLoading = false;
				switch (err.code) {
					case err.PERMISSION_DENIED:
						locationError = 'Location permission denied.';
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
				currentUserLocation = 'Location not available';
				showLocationRetry = true;
			},
			{ enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
		);
	};

	// Process coordinates with reverse geocoding
	const processLocationCoordinates = async (latitude: number, longitude: number) => {
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

			locationError = null;
			showLocationRetry = false;
		} catch (geoErr: any) {
			console.error('Reverse geocoding error:', geoErr);
			currentUserLocation = `Lat: ${latitude.toFixed(3)}, Lon: ${longitude.toFixed(3)}`;
			locationError = 'Could not fetch detailed address.';
		} finally {
			locationLoading = false;
		}
	};

	// Open device settings for location
	const openLocationSettings = async () => {
		if (!browser || !NativeSettings || !Capacitor) return;

		try {
			if (Capacitor.isNativePlatform()) {
				if (Capacitor.getPlatform() === 'android') {
					await NativeSettings.open({
						optionAndroid: AndroidSettings.Location
					});
				} else if (Capacitor.getPlatform() === 'ios') {
					await NativeSettings.open({
						optionIOS: IOSSettings.LocationServices
					});
				}
			}
		} catch (error) {
			console.error('Error opening settings:', error);
		}
	};

	const retryLocation = async () => {
		await fetchCurrentLocation();
	};

	$: sortedFeaturedCars = featuredCars.sort((a, b) => b.rating - a.rating);

	onMount(() => {
		if (browser) {
			fetchCurrentLocation();
			fetchFeaturedCars();
			checkClientDetails();
		}
	});
</script>

<div
	class="font-quicksand min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 pb-28 text-gray-300 antialiased"
>
	<!-- Animated Background Elements -->
	<div class="pointer-events-none fixed inset-0 overflow-hidden">
		<div
			class="absolute -right-40 -top-40 h-80 w-80 rounded-full bg-gradient-to-br from-teal-500/10 to-cyan-500/5 blur-3xl"
		></div>
		<div
			class="absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-gradient-to-br from-purple-500/10 to-pink-500/5 blur-3xl"
		></div>
	</div>

	<!-- Header with Enhanced Gradient -->
	<header
		class="sticky top-0 z-40 rounded-b-3xl border-b border-teal-500/20 bg-gradient-to-r from-slate-900/90 via-slate-800/90 to-slate-900/90 px-4 py-6 shadow-2xl backdrop-blur-xl"
	>
		<div class="mb-6 flex items-center justify-between">
			<a href="/" class="group flex items-center gap-3 text-white">
				<div
					class="rounded-xl bg-gradient-to-br from-teal-400 to-cyan-500 p-2 shadow-lg transition-all duration-300 group-hover:shadow-teal-500/25"
				>
					<Ship class="h-7 w-7 text-white" />
				</div>
				<h1
					class="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-3xl font-bold tracking-tight text-transparent"
				>
					Horiz<span
						class="bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-transparent"
						>oo</span
					>n
				</h1>
			</a>
			<button
				on:click={() => goto('/profile')}
				class="group relative rounded-xl border border-slate-600/50 bg-gradient-to-br from-slate-800 to-slate-700 p-3 transition-all duration-300 hover:border-teal-500/50 hover:shadow-lg hover:shadow-teal-500/20"
			>
				<User class="h-6 w-6 text-slate-300 transition-colors group-hover:text-teal-300" />
				<div
					class="absolute inset-0 rounded-xl bg-gradient-to-br from-teal-500/0 to-cyan-500/0 transition-all duration-300 group-hover:from-teal-500/10 group-hover:to-cyan-500/10"
				></div>
			</button>
		</div>

		<!-- Enhanced Search Bar -->
		<div class="relative">
			<div
				class="flex items-center rounded-2xl border border-slate-600/30 bg-gradient-to-r from-slate-800/90 to-slate-700/90 p-1 shadow-lg transition-all duration-300 focus-within:border-teal-500/50 focus-within:shadow-lg focus-within:shadow-teal-500/20"
			>
				<div class="p-3 text-slate-400">
					<Search class="h-5 w-5" />
				</div>
				<input
					class="flex-grow bg-transparent py-3 pr-4 text-sm font-medium text-gray-100 placeholder-slate-400 focus:outline-none"
					placeholder="Search cars, bikes, trucks..."
					type="text"
					bind:value={searchQuery}
					on:keyup={(e) => {
						if (e.key === 'Enter') goto(`/cars?q=${searchQuery}`);
					}}
				/>
				<button
					class="mr-2 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-500 px-4 py-2 text-sm font-semibold text-white shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-teal-500/25"
					on:click={() => goto(`/cars?q=${searchQuery}`)}
				>
					Search
				</button>
			</div>
		</div>

		<!-- Location Display -->
		<div class="mt-3 flex min-w-0 items-center text-xs">
			{#if locationLoading}
				<div
					class="flex items-center gap-2 rounded-full border border-teal-500/30 bg-gradient-to-r from-teal-500/20 to-cyan-500/20 px-3 py-2"
				>
					<Loader2 class="h-3.5 w-3.5 animate-spin text-teal-400" />
					<span class="font-medium text-teal-300">Finding location...</span>
				</div>
			{:else if locationError}
				<div
					class="flex items-center gap-2 rounded-full border border-yellow-500/30 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 px-3 py-2"
				>
					<AlertTriangle class="h-3.5 w-3.5 text-yellow-400" />
					<span class="font-medium text-yellow-300">{locationError}</span>
					{#if showLocationRetry}
						<button
							on:click={retryLocation}
							class="ml-2 rounded-full bg-yellow-500/20 px-2 py-1 text-xs font-medium text-yellow-300 transition-colors hover:bg-yellow-500/30"
						>
							Retry
						</button>
						<button
							on:click={openLocationSettings}
							class="ml-1 rounded-full bg-yellow-500/20 px-2 py-1 text-xs font-medium text-yellow-300 transition-colors hover:bg-yellow-500/30"
						>
							Settings
						</button>
					{/if}
				</div>
			{:else if currentUserLocation}
				<div
					class="flex items-center gap-2 rounded-full border border-teal-500/30 bg-gradient-to-r from-teal-500/20 to-cyan-500/20 px-3 py-2"
				>
					<MapPin class="h-3.5 w-3.5 text-teal-400" />
					<span class="truncate font-medium text-teal-300">{currentUserLocation}</span>
				</div>
			{/if}
		</div>
	</header>

	<!-- Profile Error with Enhanced Styling -->
	{#if profileError}
		<div
			class="mx-4 mt-4 rounded-2xl border border-yellow-500/30 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 p-4 text-center shadow-lg"
			transition:fade={{ duration: 300 }}
		>
			<div class="flex items-center justify-center gap-2 text-sm text-yellow-300">
				<AlertTriangle class="h-5 w-5" />
				<span class="font-medium">{profileError}</span>
			</div>
		</div>
	{/if}

	<!-- Enhanced Hero Section -->
	<section
		class="relative mt-4 flex h-[55vh] items-center justify-center overflow-hidden text-center"
	>
		<div
			class="absolute inset-0 z-10 bg-gradient-to-b from-slate-950/20 via-slate-950/40 to-slate-950/90"
		></div>
		<div
			class="z-5 absolute inset-0 bg-gradient-to-r from-teal-500/10 via-transparent to-cyan-500/10"
		></div>
		<img
			src="https://images.unsplash.com/photo-1513036191774-b2badb8fcb76?q=80&w=1976&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
			alt="Scenic road with a car"
			class="absolute inset-0 h-full w-full object-cover"
		/>
		<div class="relative z-20 mx-auto max-w-2xl px-6" in:fly={{ y: 50, duration: 800, delay: 200 }}>
			<h2
				class="shadow-text mb-6 bg-gradient-to-r from-white via-gray-100 to-white bg-clip-text text-4xl font-bold leading-tight tracking-tight text-transparent sm:text-5xl"
			>
				Your Journey Starts Here
			</h2>
			<p class="shadow-text-sm mb-8 text-lg font-medium text-gray-200/90">
				Discover amazing vehicles for your next adventure with Horizoon
			</p>
			<button
				on:click={() => goto('/cars')}
				class="group relative overflow-hidden rounded-2xl bg-gradient-to-r from-teal-500 via-cyan-500 to-teal-600 px-8 py-4 text-lg font-bold text-white shadow-2xl transition-all duration-300 hover:scale-105 hover:shadow-teal-500/25 focus:outline-none focus:ring-2 focus:ring-teal-500/50"
			>
				<div
					class="absolute inset-0 translate-x-[-100%] bg-gradient-to-r from-white/0 via-white/20 to-white/0 transition-transform duration-1000 group-hover:translate-x-[100%]"
				></div>
				<span class="relative flex items-center gap-2">
					Explore All Cars
					<ChevronRight class="h-5 w-5 transition-transform group-hover:translate-x-1" />
				</span>
			</button>
		</div>
	</section>

	<!-- Enhanced Car Categories Section -->
	<section class="px-4 py-8">
		<div class="mb-6 flex items-center justify-between">
			<h2
				class="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-2xl font-bold text-transparent"
			>
				Browse by Category
			</h2>
			<a
				href="/cars/categories"
				class="group flex items-center text-sm font-semibold text-teal-400 transition-colors hover:text-teal-300"
			>
				See All
				<ChevronRight class="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1" />
			</a>
		</div>
		<div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
			{#each carCategories as category, i (category.name)}
				<button
					on:click={category.action}
					class="group relative flex h-28 flex-col items-center justify-center overflow-hidden rounded-2xl border border-slate-600/30 bg-gradient-to-br from-slate-800/80 to-slate-700/80 p-4 shadow-lg transition-all duration-300 hover:-translate-y-1 hover:border-teal-500/50 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-teal-500/50"
					in:scale={{ duration: 400, delay: i * 100 }}
				>
					<div
						class="absolute inset-0 bg-gradient-to-br {category.gradient} opacity-0 transition-opacity duration-300 group-hover:opacity-10"
					></div>
					<div
						class="relative mb-3 rounded-2xl bg-gradient-to-br p-3 {category.gradient} shadow-lg {category.shadowColor} transition-all duration-300 group-hover:scale-110"
					>
						<svelte:component this={category.icon} class="h-6 w-6 text-white" />
					</div>
					<span
						class="relative text-sm font-bold text-gray-200 transition-colors group-hover:text-white"
						>{category.name}</span
					>
				</button>
			{/each}
		</div>
	</section>

	<!-- Enhanced Featured Cars Section -->
	<section class="px-4 py-8">
		<div class="mb-6 flex items-center justify-between">
			<h2
				class="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-2xl font-bold text-transparent"
			>
				Popular Rides
			</h2>
			<a
				href="/cars/popular"
				class="group flex items-center text-sm font-semibold text-teal-400 transition-colors hover:text-teal-300"
			>
				View More
				<ChevronRight class="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1" />
			</a>
		</div>

		{#if vehiclesLoading}
			<div class="flex h-48 items-center justify-center" transition:fade={{ duration: 300 }}>
				<div class="flex flex-col items-center gap-4">
					<Loader2 class="h-12 w-12 animate-spin text-teal-400" />
					<p class="text-lg font-medium text-slate-200">Loading amazing rides...</p>
				</div>
			</div>
		{:else if vehiclesError}
			<div
				class="flex h-48 flex-col items-center justify-center rounded-2xl border border-red-500/30 bg-gradient-to-br from-red-500/20 to-orange-500/20 p-6 text-center shadow-lg"
				transition:fade={{ duration: 300 }}
			>
				<AlertTriangle class="mb-3 h-12 w-12 text-red-400" />
				<p class="mb-2 text-lg font-semibold text-red-300">Error Loading Cars</p>
				<p class="mb-4 text-sm text-slate-400">{vehiclesError}</p>
				<button
					on:click={fetchFeaturedCars}
					class="rounded-xl bg-gradient-to-r from-teal-500 to-cyan-500 px-6 py-3 text-sm font-bold text-white shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-teal-500/25"
				>
					Try Again
				</button>
			</div>
		{:else if sortedFeaturedCars.length > 0}
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
				{#each sortedFeaturedCars as car, i (car.id)}
					<div
						on:click={() => goto(`/cars/${car.id}`)}
						on:keydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								goto(`/cars/${car.id}`);
							}
						}}
						role="button"
						tabindex="0"
						class="group cursor-pointer overflow-hidden rounded-2xl border border-slate-600/30 bg-gradient-to-br from-slate-800/80 to-slate-700/80 shadow-xl transition-all duration-300 hover:-translate-y-2 hover:border-teal-500/50 hover:shadow-2xl hover:shadow-teal-500/20"
						transition:scale={{ duration: 400, delay: i * 100 }}
					>
						<div class="relative h-48 overflow-hidden">
							<div
								class="absolute inset-0 z-10 bg-gradient-to-t from-slate-900/50 to-transparent"
							></div>
							<img
								src={getImageSource(car.image_1)}
								alt="{car.brand} {car.name}"
								class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
							/>

							<!-- Enhanced Status and Rating Badges -->
							<div class="absolute right-3 top-3 z-20 flex flex-col gap-2">
								<div
									class="flex items-center rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 px-3 py-1 text-xs font-bold text-white shadow-lg"
								>
									<Star class="mr-1 h-3 w-3 fill-white" />
									{car.rating.toFixed(1)}
								</div>
							</div>

							<div class="absolute left-3 top-3 z-20">
								{#if car.current_status === 'available'}
									<span
										class="rounded-full bg-gradient-to-r from-green-500 to-emerald-500 px-3 py-1 text-xs font-bold text-white shadow-lg"
									>
										Available
									</span>
								{:else}
									<span
										class="rounded-full bg-gradient-to-r from-yellow-500 to-orange-500 px-3 py-1 text-xs font-bold text-white shadow-lg"
									>
										On Request
									</span>
								{/if}
							</div>
						</div>

						<div class="p-5">
							<h3
								class="mb-2 text-xl font-bold text-gray-100 transition-colors group-hover:text-teal-300"
							>
								{car.brand}
								{car.name}
							</h3>
							<p class="mb-1 text-sm font-medium text-slate-400">{car.vehicle_type}</p>
							<div class="mb-3 flex items-center gap-4 text-xs text-slate-500">
								<div class="flex items-center gap-1">
									<MapPin class="h-3 w-3 text-teal-400" />
									<span>{car.location}</span>
								</div>
								<div class="flex items-center gap-1">
									<Users class="h-3 w-3 text-purple-400" />
									<span>{car.seating_capacity} seats</span>
								</div>
							</div>
							<div class="flex items-center justify-between">
								<div class="flex flex-col">
									<p
										class="bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-2xl font-bold text-transparent"
									>
										₹{car.price_per_day.toLocaleString()}
									</p>
									<span class="text-xs font-medium text-slate-400">per day</span>
								</div>
								<button
									class="group/btn relative overflow-hidden rounded-xl bg-gradient-to-r from-teal-500 to-cyan-500 px-4 py-2 text-sm font-bold text-white shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-teal-500/25"
								>
									<div
										class="absolute inset-0 translate-x-[-100%] bg-gradient-to-r from-white/0 via-white/20 to-white/0 transition-transform duration-700 group-hover/btn:translate-x-[100%]"
									></div>
									<span class="relative">Book Now</span>
								</button>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{:else}
			<div
				class="flex h-48 flex-col items-center justify-center rounded-2xl border border-slate-600/30 bg-gradient-to-br from-slate-800/80 to-slate-700/80 p-6 text-center shadow-lg"
				transition:fade={{ duration: 300 }}
			>
				<Car class="mb-3 h-12 w-12 text-slate-400" />
				<p class="text-lg font-semibold text-slate-200">No cars available</p>
				<p class="text-sm text-slate-400">Check back later for amazing rides!</p>
			</div>
		{/if}
	</section>
</div>

<style>
	:global(.font-quicksand) {
		font-family: 'Quicksand', sans-serif;
	}
	.shadow-text {
		text-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
	}
	.shadow-text-sm {
		text-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
	}
</style>
