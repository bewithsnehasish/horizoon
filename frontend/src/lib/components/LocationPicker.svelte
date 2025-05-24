<script lang="ts">
	import { onMount, createEventDispatcher } from 'svelte';
	import { browser } from '$app/environment';
	import { fade, fly, scale } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';

	import {
		MapPin,
		Search,
		Loader2,
		AlertTriangle,
		CheckCircle2,
		Navigation,
		X,
		Crosshair,
		RotateCcw
	} from 'lucide-svelte';

	interface LocationData {
		lat: number;
		lng: number;
		address: string;
		name?: string;
	}

	export let initialLocation: string = '';
	export let placeholder: string = 'Enter location...';
	export let label: string = 'Location';

	const dispatch = createEventDispatcher<{
		locationSelected: LocationData;
		locationCleared: void;
	}>();

	// Map state
	let map: any = null;
	let mapContainer: HTMLDivElement;
	let currentMarker: any = null;
	let userLocationMarker: any = null;

	// Location state
	let selectedLocation: LocationData | null = null;
	let userLocation: LocationData | null = null;
	let searchResults: LocationData[] = [];

	// UI state
	let isMapVisible = false;
	let isLocating = false;
	let isSearching = false;
	let searchQuery = '';
	let locationError: string | null = null;
	let searchError: string | null = null;

	// Dynamic imports for Leaflet (SSR safe)
	let L: any = null;

	// Search timeout ID for cleanup
	let searchTimeoutId: NodeJS.Timeout | null = null;

	onMount(async () => {
		if (!browser) return;

		try {
			L = await import('leaflet');
			// Import CSS
			await import('leaflet/dist/leaflet.css');

			// Fix default icon issues
			delete (L.Icon.Default.prototype as any)._getIconUrl;
			L.Icon.Default.mergeOptions({
				iconRetinaUrl:
					'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
				iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
				shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png'
			});
		} catch (error) {
			console.error('Failed to load Leaflet:', error);
			locationError = 'Map functionality unavailable';
		}
	});

	// Initialize map when container is available
	function initMap() {
		if (!L || !mapContainer || map) return;

		map = L.map(mapContainer).setView([20.5937, 78.9629], 5); // India center

		L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '© OpenStreetMap contributors',
			maxZoom: 18
		}).addTo(map);

		// Handle map clicks
		map.on('click', handleMapClick);

		// Get user location on map init
		getCurrentLocation();
	}

	// Get current location
	async function getCurrentLocation() {
		if (!browser || !navigator.geolocation) {
			locationError = 'Geolocation not supported';
			return;
		}

		isLocating = true;
		locationError = null;

		try {
			const position = await new Promise<GeolocationPosition>((resolve, reject) => {
				navigator.geolocation.getCurrentPosition(resolve, reject, {
					enableHighAccuracy: true,
					timeout: 15000,
					maximumAge: 300000
				});
			});

			const lat = position.coords.latitude;
			const lng = position.coords.longitude;

			// Reverse geocode to get address
			const address = await reverseGeocode(lat, lng);

			userLocation = { lat, lng, address };

			if (map) {
				map.setView([lat, lng], 15);

				// Add user location marker
				if (userLocationMarker) {
					map.removeLayer(userLocationMarker);
				}

				userLocationMarker = L.circleMarker([lat, lng], {
					color: '#3b82f6',
					fillColor: '#60a5fa',
					fillOpacity: 0.8,
					radius: 8,
					weight: 2
				}).addTo(map);

				userLocationMarker.bindPopup(`
					<div class="text-center">
						<strong>Your Location</strong><br>
						<small>${address}</small>
					</div>
				`);
			}
		} catch (error: any) {
			console.error('Geolocation error:', error);
			switch (error.code) {
				case error.PERMISSION_DENIED:
					locationError = 'Location access denied';
					break;
				case error.POSITION_UNAVAILABLE:
					locationError = 'Location unavailable';
					break;
				case error.TIMEOUT:
					locationError = 'Location request timeout';
					break;
				default:
					locationError = 'Unable to get location';
			}
		} finally {
			isLocating = false;
		}
	}

	// Handle map clicks
	function handleMapClick(e: any) {
		const lat = e.latlng.lat;
		const lng = e.latlng.lng;

		setLocationOnMap(lat, lng);
	}

	// Set location on map and reverse geocode
	async function setLocationOnMap(lat: number, lng: number) {
		try {
			const address = await reverseGeocode(lat, lng);
			const location: LocationData = { lat, lng, address };

			updateMapMarker(location);
			selectedLocation = location;
		} catch (error) {
			console.error('Reverse geocoding failed:', error);
			// Still allow setting location with coordinates
			const location: LocationData = {
				lat,
				lng,
				address: `${lat.toFixed(6)}, ${lng.toFixed(6)}`
			};
			updateMapMarker(location);
			selectedLocation = location;
		}
	}

	// Update map marker
	function updateMapMarker(location: LocationData) {
		if (!map) return;

		// Remove existing marker
		if (currentMarker) {
			map.removeLayer(currentMarker);
		}

		// Add new marker
		currentMarker = L.marker([location.lat, location.lng]).addTo(map).bindPopup(`
				<div class="text-center">
					<strong>Selected Location</strong><br>
					<small>${location.address}</small>
				</div>
			`);

		map.setView([location.lat, location.lng], 15);
	}

	// Reverse geocoding
	async function reverseGeocode(lat: number, lng: number): Promise<string> {
		try {
			const response = await fetch(
				`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=16&addressdetails=1`,
				{ headers: { 'User-Agent': 'HorizoonApp/1.0' } }
			);

			const data = await response.json();
			return data.display_name || `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
		} catch (error) {
			throw new Error('Geocoding failed');
		}
	}

	// Search locations
	async function searchLocations(query: string) {
		if (!query.trim() || query.length < 3) {
			searchResults = [];
			return;
		}

		isSearching = true;
		searchError = null;

		try {
			const response = await fetch(
				`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&addressdetails=1&countrycodes=in`,
				{ headers: { 'User-Agent': 'HorizoonApp/1.0' } }
			);

			const data = await response.json();

			searchResults = data.map((result: any) => ({
				lat: parseFloat(result.lat),
				lng: parseFloat(result.lon),
				address: result.display_name,
				name: result.name
			}));
		} catch (error) {
			console.error('Search error:', error);
			searchError = 'Search failed. Please try again.';
			searchResults = [];
		} finally {
			isSearching = false;
		}
	}

	// Select search result
	function selectSearchResult(location: LocationData) {
		selectedLocation = location;
		updateMapMarker(location);
		searchResults = [];
		searchQuery = location.address;
	}

	// Use current location
	function useCurrentLocation() {
		if (userLocation) {
			selectedLocation = userLocation;
			updateMapMarker(userLocation);
		}
	}

	// Confirm location selection
	function confirmLocation() {
		if (selectedLocation) {
			dispatch('locationSelected', selectedLocation);
			closeMap();
		}
	}

	// Open map modal
	function openMap() {
		if (!L) {
			locationError = 'Map not available';
			return;
		}

		isMapVisible = true;

		// Initialize map after modal is rendered
		setTimeout(() => {
			initMap();
		}, 100);
	}

	// Close map modal
	function closeMap() {
		isMapVisible = false;
		if (map) {
			map.remove();
			map = null;
		}
		currentMarker = null;
		userLocationMarker = null;
		searchResults = [];
		searchQuery = '';

		// Clear any pending search timeout
		if (searchTimeoutId) {
			clearTimeout(searchTimeoutId);
			searchTimeoutId = null;
		}
	}

	// Clear selection
	function clearLocation() {
		selectedLocation = null;
		dispatch('locationCleared');
		if (currentMarker && map) {
			map.removeLayer(currentMarker);
			currentMarker = null;
		}
	}

	// Handle search query changes with proper cleanup
	function handleSearchQueryChange() {
		// Clear existing timeout
		if (searchTimeoutId) {
			clearTimeout(searchTimeoutId);
		}

		// Set new timeout
		if (searchQuery && isMapVisible && searchQuery.length >= 3) {
			searchTimeoutId = setTimeout(() => {
				searchLocations(searchQuery);
			}, 500);
		} else {
			searchResults = [];
		}
	}

	// FIXED: Replace the problematic reactive statement with this:
	$: if (searchQuery !== undefined && isMapVisible !== undefined) {
		handleSearchQueryChange();
	}
</script>

<!-- Location Input Field -->
<div class="space-y-2">
	<label class="flex items-center gap-2 text-sm font-semibold text-slate-300">
		<MapPin class="h-4 w-4 text-teal-400" />
		{label}
	</label>

	<div class="relative">
		<input
			type="text"
			value={selectedLocation?.address || initialLocation}
			{placeholder}
			readonly
			on:click={openMap}
			class="w-full cursor-pointer rounded-xl border-2 border-slate-700 bg-slate-900/60 py-4 pl-12 pr-12 text-gray-100 placeholder-slate-500 transition-all duration-200 hover:border-slate-600 focus:border-teal-400 focus:ring-2 focus:ring-teal-400/30"
		/>

		<MapPin class="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-teal-400" />

		{#if selectedLocation}
			<button
				on:click={clearLocation}
				class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 transition-colors hover:text-red-400"
			>
				<X class="h-5 w-5" />
			</button>
		{:else}
			<button
				on:click={openMap}
				class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 transition-colors hover:text-teal-400"
			>
				<Search class="h-5 w-5" />
			</button>
		{/if}
	</div>
</div>

<!-- Map Modal -->
{#if isMapVisible}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm"
		transition:fade={{ duration: 300 }}
		on:click|self={closeMap}
	>
		<div
			class="relative max-h-[90vh] w-full max-w-4xl overflow-hidden rounded-3xl border border-slate-700/50 bg-slate-900 shadow-2xl"
			transition:scale={{ duration: 400, easing: quintOut }}
		>
			<!-- Modal Header -->
			<div
				class="relative z-10 border-b border-slate-600/50 bg-gradient-to-r from-slate-800 to-slate-700 p-6"
			>
				<div class="flex items-center justify-between">
					<div>
						<h3 class="text-xl font-bold text-white">{label}</h3>
						<p class="text-sm text-slate-400">Click on map or search for a location</p>
					</div>
					<button
						on:click={closeMap}
						class="rounded-full bg-slate-700 p-2 text-slate-300 transition-all duration-200 hover:bg-slate-600 hover:text-white"
					>
						<X class="h-6 w-6" />
					</button>
				</div>

				<!-- Search Bar -->
				<div class="relative mt-4">
					<div class="relative">
						<Search class="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
						<input
							type="text"
							bind:value={searchQuery}
							placeholder="Search for places..."
							class="w-full rounded-xl border border-slate-600 bg-slate-800/80 py-3 pl-12 pr-4 text-gray-100 placeholder-slate-400 transition-all duration-200 focus:border-teal-400 focus:outline-none focus:ring-2 focus:ring-teal-400/30"
						/>
						{#if isSearching}
							<Loader2
								class="absolute right-4 top-1/2 h-5 w-5 -translate-y-1/2 animate-spin text-teal-400"
							/>
						{/if}
					</div>

					<!-- Search Results -->
					{#if searchResults.length > 0}
						<div
							class="absolute left-0 right-0 top-full z-20 mt-2 max-h-48 overflow-y-auto rounded-xl border border-slate-600 bg-slate-800 shadow-xl"
							transition:fly={{ y: -10, duration: 200 }}
						>
							{#each searchResults as result}
								<button
									on:click={() => selectSearchResult(result)}
									class="w-full border-b border-slate-600 p-3 text-left transition-colors last:border-b-0 hover:bg-slate-700"
								>
									<div class="flex items-center gap-2">
										<MapPin class="h-4 w-4 flex-shrink-0 text-teal-400" />
										<div class="min-w-0">
											<p class="truncate font-medium text-gray-200">{result.name || 'Location'}</p>
											<p class="truncate text-sm text-slate-400">{result.address}</p>
										</div>
									</div>
								</button>
							{/each}
						</div>
					{/if}

					{#if searchError}
						<div
							class="absolute left-0 right-0 top-full z-20 mt-2 rounded-xl border border-red-500/30 bg-red-500/20 p-3"
						>
							<p class="flex items-center gap-2 text-sm text-red-300">
								<AlertTriangle class="h-4 w-4" />
								{searchError}
							</p>
						</div>
					{/if}
				</div>

				<!-- Quick Actions -->
				<div class="mt-4 flex gap-3">
					<button
						on:click={getCurrentLocation}
						disabled={isLocating}
						class="flex items-center gap-2 rounded-xl border border-teal-500/30 bg-teal-500/20 px-4 py-2 text-sm font-medium text-teal-300 transition-all duration-200 hover:bg-teal-500/30 disabled:opacity-50"
					>
						{#if isLocating}
							<Loader2 class="h-4 w-4 animate-spin" />
						{:else}
							<Crosshair class="h-4 w-4" />
						{/if}
						{isLocating ? 'Locating...' : 'Use Current Location'}
					</button>

					{#if userLocation}
						<button
							on:click={useCurrentLocation}
							class="flex items-center gap-2 rounded-xl border border-blue-500/30 bg-blue-500/20 px-4 py-2 text-sm font-medium text-blue-300 transition-all duration-200 hover:bg-blue-500/30"
						>
							<Navigation class="h-4 w-4" />
							Use My Location
						</button>
					{/if}
				</div>

				{#if locationError}
					<div class="mt-3 flex items-center gap-2 text-sm text-red-400">
						<AlertTriangle class="h-4 w-4" />
						{locationError}
					</div>
				{/if}
			</div>

			<!-- Map Container -->
			<div class="relative h-96">
				<div bind:this={mapContainer} class="h-full w-full bg-slate-800"></div>

				<!-- Loading Overlay -->
				{#if !map}
					<div class="absolute inset-0 flex items-center justify-center bg-slate-800">
						<div class="text-center">
							<Loader2 class="mx-auto mb-2 h-8 w-8 animate-spin text-teal-400" />
							<p class="text-slate-300">Loading map...</p>
						</div>
					</div>
				{/if}
			</div>

			<!-- Selected Location Display -->
			{#if selectedLocation}
				<div class="border-t border-slate-600/50 bg-slate-800 p-4">
					<div class="flex items-center gap-3">
						<div class="rounded-full bg-teal-500/20 p-2">
							<CheckCircle2 class="h-5 w-5 text-teal-400" />
						</div>
						<div class="min-w-0 flex-1">
							<p class="font-medium text-gray-200">Selected Location</p>
							<p class="truncate text-sm text-slate-400">{selectedLocation.address}</p>
						</div>
					</div>
				</div>
			{/if}

			<!-- Modal Footer -->
			<div class="border-t border-slate-600/50 bg-slate-800 p-6">
				<div class="flex gap-4">
					<button
						on:click={closeMap}
						class="flex-1 rounded-xl bg-slate-700 px-6 py-3 font-medium text-slate-300 transition-all duration-200 hover:bg-slate-600"
					>
						Cancel
					</button>
					<button
						on:click={confirmLocation}
						disabled={!selectedLocation}
						class="flex-2 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-600 px-8 py-3 font-semibold text-white shadow-lg transition-all duration-200 hover:scale-105 hover:shadow-xl disabled:cursor-not-allowed disabled:from-slate-600 disabled:to-slate-700 disabled:opacity-50 disabled:hover:scale-100"
					>
						Confirm Location
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	:global(.leaflet-container) {
		background: #1e293b !important;
	}

	:global(.leaflet-control-attribution) {
		background: rgba(30, 41, 59, 0.8) !important;
		color: #94a3b8 !important;
	}

	:global(.leaflet-popup-content-wrapper) {
		background: #334155 !important;
		color: #f1f5f9 !important;
		border-radius: 12px !important;
	}

	:global(.leaflet-popup-tip) {
		background: #334155 !important;
	}
</style>
