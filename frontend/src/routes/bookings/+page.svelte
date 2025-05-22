<script lang="ts">
	import { goto } from '$app/navigation';
	import { slide, fade, scale } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import axios from 'axios';
	import {
		CalendarDays,
		Car,
		MapPin,
		DollarSign,
		CheckCircle2,
		Loader2,
		ShieldCheck,
		ChevronLeft,
		ChevronDown,
		FileText,
		MessageSquare,
		AlertTriangle,
		XCircle
	} from 'lucide-svelte';
	import { getAuthToken } from '$lib/stores/auth';

	type BookingStatus = 'Upcoming' | 'Active' | 'Completed' | 'Cancelled';

	interface Vehicle {
		id: string;
		vehicle_number: string;
		name: string;
		brand: string;
		model: string;
		vehicle_type: string;
		image_1: string;
		image_2: string | null;
		image_3: string | null;
		rating: number;
		price_per_hour: string;
		price_per_day: string;
		current_status: string;
	}

	interface Booking {
		id: string;
		vehicle: Vehicle;
		pickup_datetime: string;
		return_datetime: string;
		actual_return_datetime: string | null;
		pickup_location: string;
		dropoff_location: string;
		rental_amount: string;
		security_deposit: string;
		late_fee: string | null;
		payment_status: string;
		order_status: string;
		created_at: string;
		otp: string | null;
	}

	// State variables
	let bookings: Booking[] = [];
	let loading = true;
	let error: string | null = null;
	let activeFilter: BookingStatus | 'All' = 'All';
	let expandedBookingId: string | null = null;
	let showInvoiceId: string | null = null;
	let showCancelConfirmId: string | null = null;
	let cancelLoading = false;
	let cancelError: string | null = null;

	// API configuration
	const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://0.0.0.0:8000';
	const ordersApiUrl = `${API_BASE_URL}/business/user_orders/`;
	const cancelApiUrl = `${API_BASE_URL}/business/booking/cancel/`;

	const authToken = getAuthToken();

	// Fetch bookings
	async function fetchBookings() {
		loading = true;
		error = null;
		try {
			const response = await axios.post(ordersApiUrl, { authToken });
			if (response.data && Array.isArray(response.data.orders)) {
				bookings = response.data.orders;
			} else {
				error = 'No bookings found.';
			}
		} catch (err: any) {
			console.error('Error fetching bookings:', err);
			error = 'Could not load bookings. Please try again.';
		} finally {
			loading = false;
		}
	}

	// Cancel booking
	async function cancelBooking(orderId: string) {
		cancelLoading = true;
		cancelError = null;
		try {
			const response = await axios.post(cancelApiUrl, {
				authToken,
				order_id: orderId
			});
			if (response.data.success) {
				bookings = bookings.map((b) =>
					b.id === orderId ? { ...b, order_status: 'cancelled', otp: null } : b
				);
				showCancelConfirmId = null;
			} else {
				cancelError = response.data.message || 'Failed to cancel booking.';
			}
		} catch (err: any) {
			console.error('Error cancelling booking:', err);
			cancelError = err.response?.data?.message || 'An error occurred while cancelling.';
		} finally {
			cancelLoading = false;
		}
	}

	// Image handling
	function getImageSource(image: string | null): string {
		if (!image) return 'https://via.placeholder.com/800x600?text=No+Image';
		if (image.startsWith('data:image')) return image;
		return image;
	}

	// Format dates and times
	const formatDate = (dateString: string) => {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	};

	const formatTime = (dateString: string) => {
		return new Date(dateString).toLocaleTimeString('en-US', {
			hour: '2-digit',
			minute: '2-digit',
			hour12: true
		});
	};

	// Map order status
	function mapOrderStatus(status: string, pickup: string, returnDate: string): BookingStatus {
		const now = new Date();
		const pickupDate = new Date(pickup);
		const returnDateTime = new Date(returnDate);

		if (status.toLowerCase() === 'completed') return 'Completed';
		if (status.toLowerCase() === 'cancelled') return 'Cancelled';
		if (status.toLowerCase() === 'pending' && now >= pickupDate && now <= returnDateTime)
			return 'Active';
		if (status.toLowerCase() === 'pending' && now < pickupDate) return 'Upcoming';
		return 'Upcoming';
	}

	// Check if booking can be cancelled (more than 3 hours before pickup)
	function canCancelBooking(pickupDateTime: string): boolean {
		const now = new Date();
		const pickup = new Date(pickupDateTime);
		const hoursDiff = (pickup.getTime() - now.getTime()) / (1000 * 60 * 60);
		return hoursDiff > 3;
	}

	// Computed filtered bookings
	$: filteredBookings = bookings
		.filter((booking) => {
			const status = mapOrderStatus(
				booking.order_status,
				booking.pickup_datetime,
				booking.return_datetime
			);
			return activeFilter === 'All' || status === activeFilter;
		})
		.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

	// Status colors and icons
	const statusColors: Record<
		BookingStatus,
		{ text: string; bg: string; icon: any; border: string }
	> = {
		Upcoming: {
			text: 'text-sky-300',
			bg: 'bg-sky-500/20',
			icon: ShieldCheck,
			border: 'border-sky-500/30'
		},
		Active: {
			text: 'text-emerald-300',
			bg: 'bg-emerald-500/20',
			icon: Loader2,
			border: 'border-emerald-500/30'
		},
		Completed: {
			text: 'text-teal-400',
			bg: 'bg-teal-600/20',
			icon: CheckCircle2,
			border: 'border-teal-600/30'
		},
		Cancelled: {
			text: 'text-rose-400',
			bg: 'bg-rose-600/20',
			icon: XCircle,
			border: 'border-rose-600/30'
		}
	};

	// UI interactions
	const toggleExpandBooking = (id: string) => {
		expandedBookingId = expandedBookingId === id ? null : id;
	};

	const showInvoice = (id: string) => {
		showInvoiceId = id;
	};

	const closeInvoice = () => {
		showInvoiceId = null;
	};

	const showCancelConfirm = (id: string) => {
		showCancelConfirmId = id;
	};

	const closeCancelConfirm = () => {
		showCancelConfirmId = null;
		cancelError = null;
	};

	const filterButtons: { label: string; value: BookingStatus | 'All' }[] = [
		{ label: 'All', value: 'All' },
		{ label: 'Upcoming', value: 'Upcoming' },
		{ label: 'Active', value: 'Active' },
		{ label: 'Completed', value: 'Completed' },
		{ label: 'Cancelled', value: 'Cancelled' }
	];

	// Fetch bookings on mount
	import { onMount } from 'svelte';
	onMount(() => {
		fetchBookings();
	});
</script>

<div class="font-quicksand min-h-screen bg-slate-950 text-gray-200 antialiased">
	<!-- Header -->
	<header class="sticky top-0 z-40 bg-slate-950/90 px-4 py-4 shadow-sm backdrop-blur-xl">
		<div class="mx-auto flex max-w-4xl items-center justify-between">
			<button
				on:click={() => (window.history.length > 1 ? window.history.back() : goto('/'))}
				class="rounded-full bg-slate-800/60 p-2 transition-colors hover:bg-slate-700"
				aria-label="Go back"
			>
				<ChevronLeft class="h-6 w-6 text-slate-300" />
			</button>
			<h1 class="text-xl font-semibold text-gray-100 sm:text-2xl">My Bookings</h1>
			<div class="w-10"></div>
		</div>
	</header>

	<main class="mx-auto max-w-4xl px-4 py-8 sm:px-6">
		{#if loading}
			<div
				class="flex min-h-[60vh] flex-col items-center justify-center"
				transition:fade={{ duration: 300 }}
			>
				<Loader2 class="mb-4 h-12 w-12 animate-spin text-teal-400" />
				<p class="text-lg font-medium text-slate-200">Loading Bookings...</p>
			</div>
		{:else if error}
			<div
				class="flex min-h-[60vh] flex-col items-center justify-center rounded-3xl bg-slate-900/80 p-8 text-center shadow-xl"
				transition:fade={{ duration: 300 }}
			>
				<AlertTriangle class="mb-4 h-16 w-16 text-red-400" />
				<h2 class="mb-2 text-xl font-semibold text-red-300">Error</h2>
				<p class="mb-6 text-sm text-slate-400">{error}</p>
				<button
					on:click={fetchBookings}
					class="rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-6 py-2.5 font-semibold text-white shadow-md transition-transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-teal-400/50"
				>
					Try Again
				</button>
			</div>
		{:else if filteredBookings.length > 0}
			<!-- Filter Tabs -->
			<div class="mb-8">
				<div class="flex space-x-2 overflow-x-auto rounded-xl bg-slate-800/60 p-1.5 shadow-md">
					{#each filterButtons as filterBtn (filterBtn.value)}
						<button
							on:click={() => (activeFilter = filterBtn.value)}
							class={`flex-1 rounded-lg px-4 py-2 text-sm font-semibold transition-all duration-200 ${
								activeFilter === filterBtn.value
									? 'bg-gradient-to-r from-teal-500 to-cyan-600 text-white shadow-md'
									: 'text-slate-300 hover:bg-slate-700/50 hover:text-gray-100'
							}`}
						>
							{filterBtn.label}
						</button>
					{/each}
				</div>
			</div>

			<div class="space-y-6">
				{#each filteredBookings as booking (booking.id)}
					{@const sColor =
						statusColors[
							mapOrderStatus(booking.order_status, booking.pickup_datetime, booking.return_datetime)
						]}
					<div
						class="rounded-3xl border bg-slate-800/80 shadow-lg {sColor.border} overflow-hidden transition-all duration-300 hover:shadow-xl"
						in:fade={{ duration: 300 }}
					>
						<button
							on:click={() => toggleExpandBooking(booking.id)}
							class="w-full p-5 text-left sm:p-6"
							aria-expanded={expandedBookingId === booking.id}
							aria-controls="booking-details-{booking.id}"
						>
							<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:gap-5">
								<img
									src={getImageSource(booking.vehicle.image_1)}
									alt="{booking.vehicle.brand} {booking.vehicle.name}"
									class="h-36 w-full rounded-2xl border border-slate-700 object-cover shadow-md sm:h-28 sm:w-36"
									loading="lazy"
								/>
								<div class="flex-grow">
									<div class="mb-2 flex items-start justify-between">
										<h2 class="text-xl font-semibold text-gray-100 sm:text-2xl">
											{booking.vehicle.brand}
											{booking.vehicle.name}
										</h2>
										<div
											class="ml-2 flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold {sColor.bg} {sColor.text} border {sColor.border}"
										>
											<svelte:component
												this={sColor.icon}
												class="h-4 w-4 {mapOrderStatus(
													booking.order_status,
													booking.pickup_datetime,
													booking.return_datetime
												) === 'Active'
													? 'animate-spin'
													: ''}"
											/>
											{mapOrderStatus(
												booking.order_status,
												booking.pickup_datetime,
												booking.return_datetime
											)}
										</div>
									</div>
									<p class="text-sm text-slate-400">{booking.vehicle.model}</p>
									<div class="mt-2 flex flex-wrap items-center gap-3 text-sm text-slate-300">
										<div class="flex items-center gap-1.5">
											<CalendarDays class="h-4 w-4 text-sky-400" />
											<span>{formatDate(booking.pickup_datetime)}</span>
										</div>
										<span class="text-slate-600">-</span>
										<div class="flex items-center gap-1.5">
											<CalendarDays class="h-4 w-4 text-sky-400" />
											<span>{formatDate(booking.return_datetime)}</span>
										</div>
									</div>
								</div>
								<ChevronDown
									class="h-6 w-6 text-slate-400 transition-transform duration-300 sm:ml-auto {expandedBookingId ===
									booking.id
										? 'rotate-180'
										: ''}"
								/>
							</div>
						</button>

						{#if expandedBookingId === booking.id}
							<div
								transition:slide={{ duration: 300, easing: quintOut }}
								class="border-t border-slate-700/50 px-5 pb-6 pt-4 sm:px-6"
								id="booking-details-{booking.id}"
							>
								<h4 class="mb-3 text-sm font-semibold text-slate-200">Booking Details</h4>
								<dl class="grid grid-cols-1 gap-x-6 gap-y-4 text-sm sm:grid-cols-2">
									<div>
										<dt class="text-xs text-slate-500">Pickup</dt>
										<dd class="flex items-center gap-1.5 font-medium text-gray-200">
											<MapPin class="h-4 w-4 text-orange-400" />
											{booking.pickup_location} at {formatTime(booking.pickup_datetime)}
										</dd>
									</div>
									<div>
										<dt class="text-xs text-slate-500">Drop-off</dt>
										<dd class="flex items-center gap-1.5 font-medium text-gray-200">
											<MapPin class="h-4 w-4 text-orange-400" />
											{booking.dropoff_location} at {formatTime(booking.return_datetime)}
										</dd>
									</div>
									{#if booking.actual_return_datetime}
										<div>
											<dt class="text-xs text-slate-500">Actual Return</dt>
											<dd class="flex items-center gap-1.5 font-medium text-gray-200">
												<CalendarDays class="h-4 w-4 text-sky-400" />
												{formatDate(booking.actual_return_datetime)} at
												{formatTime(booking.actual_return_datetime)}
											</dd>
										</div>
									{/if}
									<div>
										<dt class="text-xs text-slate-500">Rental Amount</dt>
										<dd class="flex items-center gap-1 font-semibold text-teal-400">
											<DollarSign class="h-4 w-4" />
											₹{parseFloat(booking.rental_amount).toFixed(2)}
										</dd>
									</div>
									<div>
										<dt class="text-xs text-slate-500">Security Deposit</dt>
										<dd class="flex items-center gap-1 font-semibold text-gray-200">
											<ShieldCheck class="h-4 w-4 text-teal-400" />
											₹{parseFloat(booking.security_deposit).toFixed(2)}
										</dd>
									</div>
									{#if booking.late_fee}
										<div>
											<dt class="text-xs text-slate-500">Late Fee</dt>
											<dd class="flex items-center gap-1 font-semibold text-rose-400">
												<DollarSign class="h-4 w-4" />
												₹{parseFloat(booking.late_fee).toFixed(2)}
											</dd>
										</div>
									{/if}
									<div>
										<dt class="text-xs text-slate-500">Payment Status</dt>
										<dd class="text-gray-200">
											{booking.payment_status.toUpperCase()}
										</dd>
									</div>
									<div>
										<dt class="text-xs text-slate-500">Booked On</dt>
										<dd class="text-gray-200">{formatDate(booking.created_at)}</dd>
									</div>
								</dl>

								{#if booking.otp && mapOrderStatus(booking.order_status, booking.pickup_datetime, booking.return_datetime) !== 'Cancelled'}
									<div class="mt-4 rounded-xl bg-slate-900/50 p-4">
										<p class="text-sm font-semibold text-slate-200">Your OTP</p>
										<div class="my-2 flex items-center justify-start gap-2">
											<ShieldCheck class="h-5 w-5 text-teal-400" />
											<p
												class="rounded-lg bg-slate-800/50 px-4 py-2 text-xl font-bold tracking-wider text-teal-300"
											>
												{booking.otp}
											</p>
										</div>
										<p class="text-xs text-slate-500">Present this OTP for pickup verification.</p>
									</div>
								{/if}

								<div class="mt-6 flex flex-col gap-3 sm:flex-row">
									{#if mapOrderStatus(booking.order_status, booking.pickup_datetime, booking.return_datetime) === 'Upcoming' && canCancelBooking(booking.pickup_datetime)}
										<button
											on:click={() => showCancelConfirm(booking.id)}
											class="flex-1 rounded-xl bg-rose-600/80 px-4 py-2.5 text-sm font-semibold text-white shadow-md transition-transform hover:scale-105 hover:bg-rose-700"
										>
											Cancel Booking
										</button>
									{/if}
									{#if mapOrderStatus(booking.order_status, booking.pickup_datetime, booking.return_datetime) === 'Completed' || mapOrderStatus(booking.order_status, booking.pickup_datetime, booking.return_datetime) === 'Cancelled'}
										<button
											on:click={() => showInvoice(booking.id)}
											class="flex-1 rounded-xl bg-slate-700/80 px-4 py-2.5 text-sm font-semibold text-slate-200 shadow-md transition-transform hover:scale-105 hover:bg-slate-600"
										>
											<FileText class="mr-2 inline h-4 w-4" /> View Invoice
										</button>
									{/if}
									<button
										on:click={() => goto('/support')}
										class="flex-1 rounded-xl border border-teal-500/50 bg-teal-600/30 px-4 py-2.5 text-sm font-semibold text-teal-300 shadow-md transition-transform hover:scale-105 hover:bg-teal-600/40"
									>
										<MessageSquare class="mr-2 inline h-4 w-4" /> Contact Support
									</button>
								</div>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{:else}
			<div
				class="flex min-h-[60vh] flex-col items-center justify-center rounded-3xl bg-slate-900/80 p-8 text-center shadow-xl"
				transition:fade={{ duration: 300 }}
			>
				<Car class="mb-4 h-16 w-16 text-teal-400/50" />
				<h2 class="mb-2 text-xl font-semibold text-gray-100">No Bookings Found</h2>
				<p class="mb-6 max-w-md text-sm text-slate-400">
					You haven't made any bookings yet, or no bookings match the current filter.
				</p>
				<button
					on:click={() => goto('/cars')}
					class="rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-6 py-2.5 font-semibold text-white shadow-md transition-transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-teal-400/50"
				>
					Book a Car Now
				</button>
			</div>
		{/if}

		<!-- Invoice Popup -->
		{#if showInvoiceId}
			{@const booking = bookings.find((b) => b.id === showInvoiceId)}
			{#if booking}
				<div
					class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
					transition:fade={{ duration: 200 }}
					on:click|self={closeInvoice}
				>
					<div
						class="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-3xl bg-slate-800/90 p-6 shadow-xl"
						transition:scale={{ duration: 300, easing: quintOut }}
					>
						<div class="mb-4 flex items-center justify-between">
							<h2 class="text-xl font-semibold text-gray-100">Invoice</h2>
							<button
								on:click={closeInvoice}
								class="rounded-full p-2 text-slate-400 hover:bg-slate-700"
							>
								<XCircle class="h-5 w-5" />
							</button>
						</div>
						<div class="space-y-4">
							<div class="flex items-center gap-3">
								<img
									src={getImageSource(booking.vehicle.image_1)}
									alt="{booking.vehicle.brand} {booking.vehicle.name}"
									class="h-20 w-20 rounded-xl object-cover shadow-md"
								/>
								<div>
									<h3 class="text-lg font-semibold text-gray-100">
										{booking.vehicle.brand}
										{booking.vehicle.name}
									</h3>
									<p class="text-sm text-slate-400">{booking.vehicle.model}</p>
								</div>
							</div>
							<div class="rounded-xl bg-slate-900/50 p-4">
								<h4 class="mb-3 text-sm font-semibold text-slate-200">Invoice Details</h4>
								<dl class="grid grid-cols-1 gap-y-2 text-sm">
									<div class="flex justify-between">
										<dt class="text-slate-500">Order ID</dt>
										<dd class="font-mono text-gray-200">{booking.id}</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-slate-500">Pickup</dt>
										<dd class="text-gray-200">
											{formatDate(booking.pickup_datetime)} at {formatTime(booking.pickup_datetime)}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-slate-500">Drop-off</dt>
										<dd class="text-gray-200">
											{formatDate(booking.return_datetime)} at {formatTime(booking.return_datetime)}
										</dd>
									</div>
									{#if booking.actual_return_datetime}
										<div class="flex justify-between">
											<dt class="text-slate-500">Actual Return</dt>
											<dd class="text-gray-200">
												{formatDate(booking.actual_return_datetime)} at
												{formatTime(booking.actual_return_datetime)}
											</dd>
										</div>
									{/if}
									<div class="flex justify-between">
										<dt class="text-slate-500">Rental Amount</dt>
										<dd class="font-semibold text-teal-400">
											₹{parseFloat(booking.rental_amount).toFixed(2)}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-slate-500">Security Deposit</dt>
										<dd class="font-semibold text-gray-200">
											₹{parseFloat(booking.security_deposit).toFixed(2)}
										</dd>
									</div>
									{#if booking.late_fee}
										<div class="flex justify-between">
											<dt class="text-slate-500">Late Fee</dt>
											<dd class="font-semibold text-rose-400">
												₹{parseFloat(booking.late_fee).toFixed(2)}
											</dd>
										</div>
									{/if}
									<div class="flex justify-between text-base font-semibold">
										<dt class="text-white">Total</dt>
										<dd class="text-teal-400">
											₹{(
												parseFloat(booking.rental_amount) +
												parseFloat(booking.security_deposit) +
												(booking.late_fee ? parseFloat(booking.late_fee) : 0)
											).toFixed(2)}
										</dd>
									</div>
								</dl>
							</div>
							<div class="flex justify-end">
								<button
									on:click={closeInvoice}
									class="rounded-xl bg-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 transition-transform hover:scale-105 hover:bg-slate-600"
								>
									Close
								</button>
							</div>
						</div>
					</div>
				</div>
			{/if}
		{/if}

		<!-- Cancel Confirmation Popup -->
		{#if showCancelConfirmId}
			<div
				class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
				transition:fade={{ duration: 200 }}
				on:click|self={closeCancelConfirm}
			>
				<div
					class="w-full max-w-md rounded-3xl bg-slate-800/90 p-6 shadow-xl"
					transition:scale={{ duration: 300, easing: quintOut }}
				>
					<div class="mb-4 flex items-center justify-between">
						<h2 class="text-lg font-semibold text-gray-100">Confirm Cancellation</h2>
						<button
							on:click={closeCancelConfirm}
							class="rounded-full p-2 text-slate-400 hover:bg-slate-700"
						>
							<XCircle class="h-5 w-5" />
						</button>
					</div>
					<p class="mb-4 text-sm text-slate-300">
						Are you sure you want to cancel this booking? This action cannot be undone.
					</p>
					{#if cancelError}
						<div
							class="mb-4 flex items-center gap-2 rounded-xl bg-red-600/20 p-3 text-sm text-red-300"
							transition:slide={{ duration: 200 }}
						>
							<AlertTriangle class="h-4 w-4" />
							{cancelError}
						</div>
					{/if}
					<div class="flex justify-end gap-3">
						<button
							on:click={closeCancelConfirm}
							class="rounded-xl bg-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 transition-transform hover:scale-105 hover:bg-slate-600"
						>
							Keep Booking
						</button>
						<button
							on:click={() => cancelBooking(showCancelConfirmId)}
							disabled={cancelLoading}
							class="rounded-xl bg-rose-600 px-4 py-2 text-sm font-semibold text-white transition-transform hover:scale-105 hover:bg-rose-700 disabled:opacity-50 disabled:hover:scale-100"
						>
							{#if cancelLoading}
								<Loader2 class="mr-2 inline h-4 w-4 animate-spin" />
								Cancelling...
							{:else}
								Cancel Booking
							{/if}
						</button>
					</div>
				</div>
			</div>
		{/if}
	</main>
</div>

<style>
	:global(.font-quicksand) {
		font-family: 'Quicksand', sans-serif;
	}
	.overflow-x-auto::-webkit-scrollbar {
		height: 6px;
	}
	.overflow-x-auto::-webkit-scrollbar-thumb {
		background-color: theme('colors.slate.700');
		border-radius: 10px;
	}
</style>
