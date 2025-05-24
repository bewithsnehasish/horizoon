<script lang="ts">
	import { goto } from '$app/navigation';
	import { slide, fade, scale, fly } from 'svelte/transition';
	import { quintOut, backOut } from 'svelte/easing';
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
		XCircle,
		Clock,
		Navigation,
		Receipt,
		Phone,
		Download,
		Share,
		Filter,
		RefreshCw,
		Star,
		Zap,
		Calendar,
		CreditCard,
		AlertCircle,
		CheckCircle,
		PlayCircle,
		XOctagon,
		History,
		Bell,
		Settings,
		MoreVertical,
		Eye,
		EyeOff
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
	let showOtpId: string | null = null;
	let refreshing = false;

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

	// Refresh bookings
	async function refreshBookings() {
		refreshing = true;
		try {
			const response = await axios.post(ordersApiUrl, { authToken });
			if (response.data && Array.isArray(response.data.orders)) {
				bookings = response.data.orders;
			}
		} catch (err: any) {
			console.error('Error refreshing bookings:', err);
		} finally {
			refreshing = false;
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

	const formatDateShort = (dateString: string) => {
		return new Date(dateString).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric'
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

	// Check if booking can be cancelled
	function canCancelBooking(pickupDateTime: string): boolean {
		const now = new Date();
		const pickup = new Date(pickupDateTime);
		const hoursDiff = (pickup.getTime() - now.getTime()) / (1000 * 60 * 60);
		return hoursDiff > 3;
	}

	// Get time until pickup
	function getTimeUntilPickup(pickupDateTime: string): string {
		const now = new Date();
		const pickup = new Date(pickupDateTime);
		const diff = pickup.getTime() - now.getTime();

		if (diff <= 0) return 'Now';

		const days = Math.floor(diff / (1000 * 60 * 60 * 24));
		const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

		if (days > 0) return `${days}d ${hours}h`;
		if (hours > 0) return `${hours}h`;
		return 'Soon';
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

	// Status colors and configuration
	const statusConfig: Record<
		BookingStatus,
		{
			text: string;
			bg: string;
			icon: any;
			border: string;
			gradient: string;
			lightBg: string;
		}
	> = {
		Upcoming: {
			text: 'text-sky-300',
			bg: 'bg-sky-500/20',
			icon: Clock,
			border: 'border-sky-500/30',
			gradient: 'from-sky-500/20 to-cyan-500/20',
			lightBg: 'bg-sky-500/10'
		},
		Active: {
			text: 'text-emerald-300',
			bg: 'bg-emerald-500/20',
			icon: PlayCircle,
			border: 'border-emerald-500/30',
			gradient: 'from-emerald-500/20 to-teal-500/20',
			lightBg: 'bg-emerald-500/10'
		},
		Completed: {
			text: 'text-teal-400',
			bg: 'bg-teal-600/20',
			icon: CheckCircle,
			border: 'border-teal-600/30',
			gradient: 'from-teal-500/20 to-cyan-500/20',
			lightBg: 'bg-teal-500/10'
		},
		Cancelled: {
			text: 'text-rose-400',
			bg: 'bg-rose-600/20',
			icon: XOctagon,
			border: 'border-rose-600/30',
			gradient: 'from-rose-500/20 to-red-500/20',
			lightBg: 'bg-rose-500/10'
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

	const toggleOtpVisibility = (id: string) => {
		showOtpId = showOtpId === id ? null : id;
	};

	// Filter buttons with counts
	$: filterButtonsWithCounts = [
		{
			label: 'All',
			value: 'All' as const,
			count: bookings.length,
			icon: History
		},
		{
			label: 'Upcoming',
			value: 'Upcoming' as const,
			count: bookings.filter(
				(b) => mapOrderStatus(b.order_status, b.pickup_datetime, b.return_datetime) === 'Upcoming'
			).length,
			icon: Clock
		},
		{
			label: 'Active',
			value: 'Active' as const,
			count: bookings.filter(
				(b) => mapOrderStatus(b.order_status, b.pickup_datetime, b.return_datetime) === 'Active'
			).length,
			icon: PlayCircle
		},
		{
			label: 'Completed',
			value: 'Completed' as const,
			count: bookings.filter(
				(b) => mapOrderStatus(b.order_status, b.pickup_datetime, b.return_datetime) === 'Completed'
			).length,
			icon: CheckCircle
		},
		{
			label: 'Cancelled',
			value: 'Cancelled' as const,
			count: bookings.filter(
				(b) => mapOrderStatus(b.order_status, b.pickup_datetime, b.return_datetime) === 'Cancelled'
			).length,
			icon: XOctagon
		}
	];

	// Fetch bookings on mount
	import { onMount } from 'svelte';
	onMount(() => {
		fetchBookings();
	});
</script>

<div class="font-quicksand min-h-screen bg-slate-950 text-gray-200 antialiased">
	<!-- Enhanced Mobile Header -->
	<header
		class="sticky top-0 z-40 border-b border-slate-700/50 bg-gradient-to-r from-slate-900/95 to-slate-800/95 backdrop-blur-xl"
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

				<div class="flex-1 text-center">
					<h1 class="text-xl font-bold text-gray-100">My Bookings</h1>
					{#if !loading && bookings.length > 0}
						<p class="text-sm text-slate-400">{bookings.length} total bookings</p>
					{/if}
				</div>

				<button
					on:click={refreshBookings}
					disabled={refreshing}
					class="rounded-full bg-slate-800/60 p-2.5 text-slate-300 transition-all duration-200 hover:bg-slate-700 hover:text-teal-400 disabled:opacity-50"
					aria-label="Refresh bookings"
				>
					<RefreshCw class="h-5 w-5 {refreshing ? 'animate-spin' : ''}" />
				</button>
			</div>
		</div>
	</header>

	<main class="px-4 py-6">
		{#if loading}
			<div
				class="flex min-h-[60vh] flex-col items-center justify-center"
				transition:fade={{ duration: 300 }}
			>
				<div class="relative mb-6">
					<div
						class="h-20 w-20 animate-pulse rounded-full bg-gradient-to-r from-teal-500 to-cyan-600"
					></div>
					<Loader2 class="absolute inset-0 m-auto h-8 w-8 animate-spin text-white" />
				</div>
				<p class="text-lg font-medium text-slate-200">Loading your bookings...</p>
				<p class="mt-2 text-sm text-slate-400">Please wait a moment</p>
			</div>
		{:else if error}
			<div
				class="flex min-h-[60vh] flex-col items-center justify-center rounded-3xl border border-slate-700/50 bg-slate-800/50 p-8 text-center shadow-xl"
				transition:fade={{ duration: 300 }}
			>
				<div class="mb-6 rounded-full bg-red-500/20 p-4">
					<AlertTriangle class="h-12 w-12 text-red-400" />
				</div>
				<h2 class="mb-2 text-xl font-semibold text-red-300">Unable to Load Bookings</h2>
				<p class="mb-6 max-w-md text-sm text-slate-400">{error}</p>
				<div class="flex gap-3">
					<button
						on:click={fetchBookings}
						class="rounded-2xl bg-gradient-to-r from-teal-500 to-cyan-600 px-6 py-3 font-semibold text-white shadow-lg transition-all duration-200 hover:scale-105 hover:shadow-xl"
					>
						Try Again
					</button>
					<button
						on:click={() => goto('/support')}
						class="rounded-2xl border border-slate-600 bg-slate-800/70 px-6 py-3 font-semibold text-slate-300 transition-all duration-200 hover:border-teal-500 hover:bg-slate-700"
					>
						Get Help
					</button>
				</div>
			</div>
		{:else if bookings.length > 0}
			<!-- Enhanced Filter Tabs -->
			<div class="mb-6">
				<div
					class="flex space-x-2 overflow-x-auto rounded-2xl border border-slate-700/50 bg-slate-800/60 p-2 shadow-lg"
				>
					{#each filterButtonsWithCounts as filterBtn (filterBtn.value)}
						<button
							on:click={() => (activeFilter = filterBtn.value)}
							class={`flex items-center gap-2 whitespace-nowrap rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-200 ${
								activeFilter === filterBtn.value
									? 'scale-105 bg-gradient-to-r from-teal-500 to-cyan-600 text-white shadow-lg'
									: 'text-slate-300 hover:bg-slate-700/50 hover:text-gray-100'
							}`}
						>
							<svelte:component this={filterBtn.icon} class="h-4 w-4" />
							{filterBtn.label}
							{#if filterBtn.count > 0}
								<span
									class={`rounded-full px-2 py-0.5 text-xs ${
										activeFilter === filterBtn.value
											? 'bg-white/20 text-white'
											: 'bg-slate-600 text-slate-300'
									}`}
								>
									{filterBtn.count}
								</span>
							{/if}
						</button>
					{/each}
				</div>
			</div>

			<!-- Enhanced Bookings Grid -->
			<div class="space-y-4">
				{#each filteredBookings as booking, index (booking.id)}
					{@const status = mapOrderStatus(
						booking.order_status,
						booking.pickup_datetime,
						booking.return_datetime
					)}
					{@const config = statusConfig[status]}
					<div
						class="rounded-3xl border bg-gradient-to-br from-slate-800/80 to-slate-900/80 shadow-xl hover:shadow-2xl {config.border} overflow-hidden backdrop-blur-sm transition-all duration-300 hover:-translate-y-0.5"
						in:fly={{ y: 50, duration: 300, delay: index * 100 }}
					>
						<!-- Card Header -->
						<div class="relative overflow-hidden">
							<div class="absolute inset-0 bg-gradient-to-r {config.gradient}"></div>
							<div class="relative p-5">
								<div class="mb-4 flex items-start justify-between">
									<div class="flex items-center gap-3">
										<div class="relative">
											<img
												src={getImageSource(booking.vehicle.image_1)}
												alt="{booking.vehicle.brand} {booking.vehicle.name}"
												class="h-16 w-16 rounded-2xl border border-slate-700/50 object-cover shadow-lg"
												loading="lazy"
											/>
											<div
												class="absolute -right-1 -top-1 {config.bg} {config.text} rounded-full border p-1.5 {config.border}"
											>
												<svelte:component this={config.icon} class="h-3 w-3" />
											</div>
										</div>
										<div>
											<h3 class="mb-1 text-lg font-bold text-gray-100">
												{booking.vehicle.brand}
												{booking.vehicle.name}
											</h3>
											<p class="text-sm text-slate-400">{booking.vehicle.model}</p>
											<div class="mt-1 flex items-center gap-2">
												<div class="flex items-center gap-1">
													<Star class="h-3 w-3 fill-yellow-400 text-yellow-400" />
													<span class="text-xs text-slate-300">{booking.vehicle.rating}</span>
												</div>
												<span class="text-slate-600">•</span>
												<span class="text-xs text-slate-400">{booking.vehicle.vehicle_type}</span>
											</div>
										</div>
									</div>

									<div class="text-right">
										<div
											class={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold ${config.bg} ${config.text} border ${config.border}`}
										>
											<svelte:component this={config.icon} class="h-3 w-3" />
											{status}
										</div>
										{#if status === 'Upcoming'}
											<p class="mt-1 text-xs text-slate-400">
												in {getTimeUntilPickup(booking.pickup_datetime)}
											</p>
										{/if}
									</div>
								</div>

								<!-- Trip Details Row -->
								<div class="mb-4 grid grid-cols-2 gap-4">
									<div class="rounded-2xl border border-slate-700/30 bg-slate-900/30 p-3">
										<div class="mb-1 flex items-center gap-2">
											<div class="rounded-full bg-green-500/20 p-1">
												<Navigation class="h-3 w-3 text-green-400" />
											</div>
											<span class="text-xs font-medium text-slate-400">Pickup</span>
										</div>
										<p class="line-clamp-1 text-sm font-semibold text-gray-200">
											{booking.pickup_location}
										</p>
										<p class="text-xs text-slate-400">
											{formatDateShort(booking.pickup_datetime)} • {formatTime(
												booking.pickup_datetime
											)}
										</p>
									</div>

									<div class="rounded-2xl border border-slate-700/30 bg-slate-900/30 p-3">
										<div class="mb-1 flex items-center gap-2">
											<div class="rounded-full bg-red-500/20 p-1">
												<MapPin class="h-3 w-3 text-red-400" />
											</div>
											<span class="text-xs font-medium text-slate-400">Drop-off</span>
										</div>
										<p class="line-clamp-1 text-sm font-semibold text-gray-200">
											{booking.dropoff_location}
										</p>
										<p class="text-xs text-slate-400">
											{formatDateShort(booking.return_datetime)} • {formatTime(
												booking.return_datetime
											)}
										</p>
									</div>
								</div>

								<!-- Price and Actions Row -->
								<div class="flex items-center justify-between">
									<div>
										<p
											class="bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-xl font-bold text-transparent"
										>
											₹{parseFloat(booking.rental_amount).toLocaleString()}
										</p>
										<p class="text-xs text-slate-400">Total amount</p>
									</div>

									<div class="flex items-center gap-2">
										{#if booking.otp && status !== 'Cancelled'}
											<button
												on:click={() => toggleOtpVisibility(booking.id)}
												class="rounded-2xl border border-purple-500/30 bg-gradient-to-r from-purple-500/20 to-pink-500/20 px-4 py-2.5 text-sm font-medium text-purple-300 transition-all duration-200 hover:from-purple-500/30 hover:to-pink-500/30"
											>
												<div class="flex items-center gap-2">
													{#if showOtpId === booking.id}
														<EyeOff class="h-4 w-4" />
													{:else}
														<Eye class="h-4 w-4" />
													{/if}
													OTP
												</div>
											</button>
										{/if}

										<button
											on:click={() => toggleExpandBooking(booking.id)}
											class="rounded-2xl bg-slate-700/60 p-2.5 text-slate-300 transition-all duration-200 hover:bg-slate-600 hover:text-teal-400"
											aria-label="View details"
										>
											<ChevronDown
												class="h-5 w-5 transition-transform duration-300 {expandedBookingId ===
												booking.id
													? 'rotate-180'
													: ''}"
											/>
										</button>
									</div>
								</div>

								<!-- OTP Display -->
								{#if booking.otp && showOtpId === booking.id && status !== 'Cancelled'}
									<div
										class="mt-4 rounded-2xl border border-purple-500/30 bg-gradient-to-r from-purple-500/10 to-pink-500/10 p-4"
										transition:slide={{ duration: 200 }}
									>
										<div class="mb-2 flex items-center justify-between">
											<div class="flex items-center gap-2">
												<ShieldCheck class="h-5 w-5 text-purple-400" />
												<span class="text-sm font-semibold text-purple-300">Your OTP</span>
											</div>
											<button
												on:click={() => navigator.clipboard?.writeText(booking.otp || '')}
												class="text-xs text-purple-400 hover:text-purple-300"
											>
												Copy
											</button>
										</div>
										<div class="rounded-xl bg-slate-900/50 p-3 text-center">
											<p class="font-mono text-2xl font-bold tracking-wider text-purple-300">
												{booking.otp}
											</p>
										</div>
										<p class="mt-2 text-center text-xs text-slate-400">
											Present this OTP for pickup verification
										</p>
									</div>
								{/if}
							</div>
						</div>

						<!-- Expandable Details -->
						{#if expandedBookingId === booking.id}
							<div
								transition:slide={{ duration: 300, easing: quintOut }}
								class="border-t border-slate-700/50 bg-slate-900/30"
							>
								<div class="p-5">
									<!-- Detailed Information Grid -->
									<div class="mb-6 grid grid-cols-1 gap-4">
										<div class="rounded-2xl border border-slate-700/50 bg-slate-800/50 p-4">
											<h4 class="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-200">
												<Receipt class="h-4 w-4 text-teal-400" />
												Booking Details
											</h4>
											<div class="grid grid-cols-2 gap-4 text-sm">
												<div>
													<p class="mb-1 text-xs text-slate-500">Order ID</p>
													<p class="font-mono text-xs text-gray-200">{booking.id.slice(-8)}</p>
												</div>
												<div>
													<p class="mb-1 text-xs text-slate-500">Vehicle Number</p>
													<p class="font-semibold text-gray-200">
														{booking.vehicle.vehicle_number}
													</p>
												</div>
												<div>
													<p class="mb-1 text-xs text-slate-500">Payment Status</p>
													<div class="flex items-center gap-1">
														{#if booking.payment_status.toLowerCase() === 'paid'}
															<CheckCircle class="h-3 w-3 text-green-400" />
															<span class="text-xs font-medium text-green-300">Paid</span>
														{:else}
															<AlertCircle class="h-3 w-3 text-amber-400" />
															<span class="text-xs font-medium text-amber-300"
																>{booking.payment_status}</span
															>
														{/if}
													</div>
												</div>
												<div>
													<p class="mb-1 text-xs text-slate-500">Booked On</p>
													<p class="text-xs text-gray-200">{formatDate(booking.created_at)}</p>
												</div>
											</div>
										</div>

										<!-- Cost Breakdown -->
										<div class="rounded-2xl border border-slate-700/50 bg-slate-800/50 p-4">
											<h4 class="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-200">
												<CreditCard class="h-4 w-4 text-teal-400" />
												Cost Breakdown
											</h4>
											<div class="space-y-2 text-sm">
												<div class="flex justify-between">
													<span class="text-slate-400">Rental Amount</span>
													<span class="font-semibold text-teal-400"
														>₹{parseFloat(booking.rental_amount).toFixed(2)}</span
													>
												</div>
												<div class="flex justify-between">
													<span class="text-slate-400">Security Deposit</span>
													<span class="font-semibold text-gray-200"
														>₹{parseFloat(booking.security_deposit).toFixed(2)}</span
													>
												</div>
												{#if booking.late_fee}
													<div class="flex justify-between">
														<span class="text-slate-400">Late Fee</span>
														<span class="font-semibold text-rose-400"
															>₹{parseFloat(booking.late_fee).toFixed(2)}</span
														>
													</div>
												{/if}
												<div class="mt-2 border-t border-slate-600/50 pt-2">
													<div class="flex justify-between text-base">
														<span class="font-semibold text-white">Total</span>
														<span class="font-bold text-teal-400">
															₹{(
																parseFloat(booking.rental_amount) +
																parseFloat(booking.security_deposit) +
																(booking.late_fee ? parseFloat(booking.late_fee) : 0)
															).toFixed(2)}
														</span>
													</div>
												</div>
											</div>
										</div>

										{#if booking.actual_return_datetime}
											<div class="rounded-2xl border border-slate-700/50 bg-slate-800/50 p-4">
												<h4
													class="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-200"
												>
													<Calendar class="h-4 w-4 text-teal-400" />
													Actual Return
												</h4>
												<p class="text-sm text-gray-200">
													{formatDate(booking.actual_return_datetime)} at {formatTime(
														booking.actual_return_datetime
													)}
												</p>
											</div>
										{/if}
									</div>

									<!-- Action Buttons -->
									<div class="grid grid-cols-1 gap-3">
										{#if status === 'Upcoming' && canCancelBooking(booking.pickup_datetime)}
											<button
												on:click={() => showCancelConfirm(booking.id)}
												class="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-rose-500/80 to-red-600/80 px-6 py-3.5 text-sm font-semibold text-white shadow-lg transition-all duration-200 hover:scale-105 hover:from-rose-600 hover:to-red-700"
											>
												<XOctagon class="h-4 w-4" />
												Cancel Booking
											</button>
										{/if}

										<div class="grid grid-cols-2 gap-3">
											{#if status === 'Completed' || status === 'Cancelled'}
												<button
													on:click={() => showInvoice(booking.id)}
													class="flex items-center justify-center gap-2 rounded-2xl bg-slate-700/80 px-4 py-3 text-sm font-semibold text-slate-200 transition-all duration-200 hover:scale-105 hover:bg-slate-600"
												>
													<FileText class="h-4 w-4" />
													Invoice
												</button>
											{/if}
											<button
												on:click={() => goto('/support')}
												class="flex items-center justify-center gap-2 rounded-2xl border border-teal-500/50 bg-teal-600/20 px-4 py-3 text-sm font-semibold text-teal-300 transition-all duration-200 hover:scale-105 hover:bg-teal-600/30"
											>
												<MessageSquare class="h-4 w-4" />
												Support
											</button>
										</div>
									</div>
								</div>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{:else}
			<!-- Empty State -->
			<div
				class="flex min-h-[60vh] flex-col items-center justify-center rounded-3xl border border-slate-700/50 bg-slate-800/50 p-8 text-center shadow-xl"
				transition:fade={{ duration: 300 }}
			>
				<div class="mb-6 rounded-full bg-teal-500/20 p-6">
					<Car class="h-16 w-16 text-teal-400" />
				</div>
				<h2 class="mb-4 text-xl font-semibold text-gray-100">No Bookings Yet</h2>
				<p class="mb-8 max-w-md text-sm leading-relaxed text-slate-400">
					You haven't made any bookings yet. Start exploring our amazing fleet and book your first
					ride!
				</p>
				<div class="flex w-full max-w-xs flex-col gap-3">
					<button
						on:click={() => goto('/cars')}
						class="rounded-2xl bg-gradient-to-r from-teal-500 to-cyan-600 px-8 py-4 font-semibold text-white shadow-lg transition-all duration-200 hover:scale-105 hover:shadow-xl"
					>
						Explore Vehicles
					</button>
					<button
						on:click={() => goto('/offers')}
						class="rounded-2xl border border-slate-600 bg-slate-800/70 px-8 py-3 font-medium text-slate-300 transition-all duration-200 hover:border-teal-500 hover:bg-slate-700"
					>
						View Offers
					</button>
				</div>
			</div>
		{/if}
	</main>

	<!-- Enhanced Invoice Modal -->
	{#if showInvoiceId}
		{@const booking = bookings.find((b) => b.id === showInvoiceId)}
		{#if booking}
			<div
				class="fixed inset-0 z-50 flex items-end justify-center bg-black/80 p-4 backdrop-blur-md sm:items-center"
				transition:fade={{ duration: 200 }}
				on:click|self={closeInvoice}
			>
				<div
					class="max-h-[85vh] w-full max-w-lg overflow-hidden rounded-t-3xl border border-slate-700/50 bg-gradient-to-br from-slate-800/95 to-slate-900/95 shadow-2xl backdrop-blur-xl sm:rounded-3xl"
					transition:fly={{ y: 300, duration: 300, easing: backOut }}
				>
					<!-- Modal Header -->
					<div
						class="sticky top-0 border-b border-slate-700/50 bg-slate-800/90 p-6 backdrop-blur-sm"
					>
						<div class="flex items-center justify-between">
							<div class="flex items-center gap-3">
								<div class="rounded-full bg-teal-500/20 p-2">
									<Receipt class="h-5 w-5 text-teal-400" />
								</div>
								<div>
									<h2 class="text-lg font-semibold text-gray-100">Invoice</h2>
									<p class="text-sm text-slate-400">#{booking.id.slice(-8)}</p>
								</div>
							</div>
							<button
								on:click={closeInvoice}
								class="rounded-full p-2 text-slate-400 transition-all duration-200 hover:bg-slate-700 hover:text-teal-400"
							>
								<XCircle class="h-5 w-5" />
							</button>
						</div>
					</div>

					<!-- Modal Content -->
					<div class="overflow-y-auto p-6">
						<!-- Vehicle Info -->
						<div
							class="mb-6 flex items-center gap-4 rounded-2xl border border-slate-700/50 bg-slate-900/50 p-4"
						>
							<img
								src={getImageSource(booking.vehicle.image_1)}
								alt="{booking.vehicle.brand} {booking.vehicle.name}"
								class="h-16 w-16 rounded-xl object-cover shadow-md"
							/>
							<div class="flex-1">
								<h3 class="text-lg font-semibold text-gray-100">
									{booking.vehicle.brand}
									{booking.vehicle.name}
								</h3>
								<p class="text-sm text-slate-400">{booking.vehicle.model}</p>
								<p class="mt-1 text-xs text-slate-500">{booking.vehicle.vehicle_number}</p>
							</div>
							<div class="text-right">
								<div class="flex items-center gap-1">
									<Star class="h-4 w-4 fill-yellow-400 text-yellow-400" />
									<span class="text-sm font-medium text-gray-200">{booking.vehicle.rating}</span>
								</div>
							</div>
						</div>

						<!-- Trip Details -->
						<div class="mb-6 space-y-4">
							<div class="rounded-2xl border border-slate-700/50 bg-slate-900/50 p-4">
								<h4 class="mb-3 text-sm font-semibold text-slate-200">Trip Details</h4>
								<div class="space-y-3 text-sm">
									<div class="flex justify-between">
										<span class="text-slate-400">Pickup</span>
										<div class="text-right">
											<p class="font-medium text-gray-200">{booking.pickup_location}</p>
											<p class="text-xs text-slate-500">
												{formatDate(booking.pickup_datetime)} • {formatTime(
													booking.pickup_datetime
												)}
											</p>
										</div>
									</div>
									<div class="flex justify-between">
										<span class="text-slate-400">Drop-off</span>
										<div class="text-right">
											<p class="font-medium text-gray-200">{booking.dropoff_location}</p>
											<p class="text-xs text-slate-500">
												{formatDate(booking.return_datetime)} • {formatTime(
													booking.return_datetime
												)}
											</p>
										</div>
									</div>
									{#if booking.actual_return_datetime}
										<div class="flex justify-between">
											<span class="text-slate-400">Actual Return</span>
											<div class="text-right">
												<p class="font-medium text-gray-200">Returned</p>
												<p class="text-xs text-slate-500">
													{formatDate(booking.actual_return_datetime)} • {formatTime(
														booking.actual_return_datetime
													)}
												</p>
											</div>
										</div>
									{/if}
								</div>
							</div>

							<!-- Cost Breakdown -->
							<div class="rounded-2xl border border-slate-700/50 bg-slate-900/50 p-4">
								<h4 class="mb-3 text-sm font-semibold text-slate-200">Payment Summary</h4>
								<div class="space-y-2 text-sm">
									<div class="flex justify-between">
										<span class="text-slate-400">Rental Amount</span>
										<span class="font-semibold text-teal-400"
											>₹{parseFloat(booking.rental_amount).toFixed(2)}</span
										>
									</div>
									<div class="flex justify-between">
										<span class="text-slate-400">Security Deposit</span>
										<span class="font-semibold text-gray-200"
											>₹{parseFloat(booking.security_deposit).toFixed(2)}</span
										>
									</div>
									{#if booking.late_fee}
										<div class="flex justify-between">
											<span class="text-slate-400">Late Fee</span>
											<span class="font-semibold text-rose-400"
												>₹{parseFloat(booking.late_fee).toFixed(2)}</span
											>
										</div>
									{/if}
									<div class="mt-3 border-t border-slate-600/50 pt-2">
										<div class="flex justify-between text-base">
											<span class="font-semibold text-white">Total Paid</span>
											<span class="text-lg font-bold text-teal-400">
												₹{(
													parseFloat(booking.rental_amount) +
													parseFloat(booking.security_deposit) +
													(booking.late_fee ? parseFloat(booking.late_fee) : 0)
												).toFixed(2)}
											</span>
										</div>
									</div>
								</div>
							</div>
						</div>

						<!-- Action Buttons -->
						<div class="grid grid-cols-2 gap-3">
							<button
								on:click={() => {
									/* Add download functionality */
								}}
								class="flex items-center justify-center gap-2 rounded-2xl bg-slate-700/80 px-4 py-3 text-sm font-semibold text-slate-200 transition-all duration-200 hover:bg-slate-600"
							>
								<Download class="h-4 w-4" />
								Download
							</button>
							<button
								on:click={() => {
									/* Add share functionality */
								}}
								class="flex items-center justify-center gap-2 rounded-2xl border border-teal-500/50 bg-teal-600/20 px-4 py-3 text-sm font-semibold text-teal-300 transition-all duration-200 hover:bg-teal-600/30"
							>
								<Share class="h-4 w-4" />
								Share
							</button>
						</div>
					</div>
				</div>
			</div>
		{/if}
	{/if}

	<!-- Enhanced Cancel Confirmation Modal -->
	{#if showCancelConfirmId}
		<div
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-md"
			transition:fade={{ duration: 200 }}
			on:click|self={closeCancelConfirm}
		>
			<div
				class="w-full max-w-md rounded-3xl border border-slate-700/50 bg-gradient-to-br from-slate-800/95 to-slate-900/95 shadow-2xl backdrop-blur-xl"
				transition:scale={{ duration: 300, easing: backOut }}
			>
				<div class="p-6">
					<div class="mb-4 flex items-center gap-3">
						<div class="rounded-full bg-rose-500/20 p-3">
							<AlertTriangle class="h-6 w-6 text-rose-400" />
						</div>
						<div>
							<h2 class="text-lg font-semibold text-gray-100">Cancel Booking</h2>
							<p class="text-sm text-slate-400">This action cannot be undone</p>
						</div>
					</div>

					<p class="mb-6 text-sm leading-relaxed text-slate-300">
						Are you sure you want to cancel this booking? Your payment will be refunded according to
						our cancellation policy.
					</p>

					{#if cancelError}
						<div
							class="mb-4 flex items-center gap-2 rounded-2xl border border-red-500/30 bg-red-600/20 p-3 text-sm text-red-300"
							transition:slide={{ duration: 200 }}
						>
							<AlertTriangle class="h-4 w-4" />
							{cancelError}
						</div>
					{/if}

					<div class="grid grid-cols-2 gap-3">
						<button
							on:click={closeCancelConfirm}
							class="rounded-2xl bg-slate-700/80 px-4 py-3 text-sm font-semibold text-slate-200 transition-all duration-200 hover:bg-slate-600"
						>
							Keep Booking
						</button>
						<button
							on:click={() => cancelBooking(showCancelConfirmId)}
							disabled={cancelLoading}
							class="rounded-2xl bg-gradient-to-r from-rose-500 to-red-600 px-4 py-3 text-sm font-semibold text-white transition-all duration-200 hover:from-rose-600 hover:to-red-700 disabled:opacity-50"
						>
							{#if cancelLoading}
								<div class="flex items-center justify-center gap-2">
									<Loader2 class="h-4 w-4 animate-spin" />
									Cancelling...
								</div>
							{:else}
								Cancel Booking
							{/if}
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}
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

	.line-clamp-1 {
		overflow: hidden;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 1;
	}
</style>
