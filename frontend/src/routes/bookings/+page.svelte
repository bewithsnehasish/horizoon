<script lang="ts">
	import { goto } from '$app/navigation';
	import { slide } from 'svelte/transition'; // For transitions
	import { quintOut } from 'svelte/easing'; // For easing

	// Lucide Icons
	import {
		CalendarDays,
		Car,
		MapPin, // For Pickup/Dropoff Location
		DollarSign, // For Total Price
		CheckCircle2, // For Completed Bookings
		Loader2, // For Ongoing or Processing Bookings (or AlertCircle for issues)
		ShieldCheck, // For Confirmed (Upcoming)
		ChevronLeft,
		ChevronDown,
		FileText, // For Invoice/Details
		MessageSquare // For Support regarding booking
	} from 'lucide-svelte';

	type BookingStatus = 'Upcoming' | 'Active' | 'Completed' | 'Cancelled';

	interface Booking {
		id: string;
		carName: string;
		carBrand: string;
		carImage: string;
		pickupDate: string;
		dropoffDate: string;
		pickupLocation: string;
		dropoffLocation: string;
		totalPrice: number;
		status: BookingStatus;
		bookingDate: string; // When the booking was made
		features?: string[]; // e.g., ['GPS Included', 'Child Seat']
	}

	// Mock Booking Data
	const mockBookings: Booking[] = [
		{
			id: 'booking-001',
			carName: 'Tesla Model S Plaid',
			carBrand: 'Tesla',
			carImage:
				'https://images.unsplash.com/photo-1610470832703-95d40c3fad55?w=500&auto=format&fit=crop&q=60',
			pickupDate: '2023-12-05T09:00:00Z',
			dropoffDate: '2023-12-08T17:00:00Z',
			pickupLocation: 'San Francisco Airport (SFO)',
			dropoffLocation: 'Downtown Los Angeles Office',
			totalPrice: 450.75,
			status: 'Upcoming',
			bookingDate: '2023-11-20T10:30:00Z',
			features: ['Autopilot Enabled', 'Premium Connectivity']
		},
		{
			id: 'booking-002',
			carName: 'BMW M4 Competition',
			carBrand: 'BMW',
			carImage: 'https://images.unsplash.com/photo-1617531653332-bd46c24f2068?q=80',
			pickupDate: '2023-11-15T10:00:00Z',
			dropoffDate: '2023-11-18T10:00:00Z',
			pickupLocation: 'Miami International Airport (MIA)',
			dropoffLocation: 'Miami International Airport (MIA)',
			totalPrice: 620.0,
			status: 'Completed',
			bookingDate: '2023-11-01T14:00:00Z'
		},
		{
			id: 'booking-003',
			carName: 'Audi RS6 Avant',
			carBrand: 'Audi',
			carImage: 'https://images.unsplash.com/photo-1618056210931-39f730ebbf67?q=80&w=2069',
			pickupDate: '2023-11-28T14:00:00Z', // Current date could make this 'Active'
			dropoffDate: '2023-12-02T14:00:00Z',
			pickupLocation: 'Denver Union Station',
			dropoffLocation: 'Aspen Showmass Village',
			totalPrice: 750.5,
			status: 'Active',
			bookingDate: '2023-11-10T09:15:00Z',
			features: ['Ski Rack', 'All-Wheel Drive']
		},
		{
			id: 'booking-004',
			carName: 'Toyota Camry XSE',
			carBrand: 'Toyota',
			carImage:
				'https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8VG95b3RhJTIwQ2Ftcnl8ZW58MHx8MHx8fDA%3D',
			pickupDate: '2023-10-20T12:00:00Z',
			dropoffDate: '2023-10-22T12:00:00Z',
			pickupLocation: "Chicago O'Hare (ORD)",
			dropoffLocation: 'Magnificent Mile Hotel',
			totalPrice: 180.25,
			status: 'Cancelled',
			bookingDate: '2023-10-05T11:45:00Z'
		}
	];

	let activeFilter: BookingStatus | 'All' = 'All';
	let expandedBookingId: string | null = null;

	// Format dates for display
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

	$: filteredBookings = mockBookings
		.filter((booking) => activeFilter === 'All' || booking.status === activeFilter)
		.sort((a, b) => new Date(b.bookingDate).getTime() - new Date(a.bookingDate).getTime()); // Sort by most recent booking

	const statusColors: Record<
		BookingStatus,
		{ text: string; bg: string; icon: any; border?: string }
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
		}, // Loader2 needs animate-spin
		Completed: {
			text: 'text-teal-400',
			bg: 'bg-teal-600/20',
			icon: CheckCircle2,
			border: 'border-teal-600/30'
		},
		Cancelled: {
			text: 'text-rose-400',
			bg: 'bg-rose-600/20',
			icon: FileText,
			border: 'border-rose-600/30'
		} // Using FileText to suggest view details/reason
	};

	const toggleExpandBooking = (id: string) => {
		expandedBookingId = expandedBookingId === id ? null : id;
	};

	const filterButtons: { label: string; value: BookingStatus | 'All' }[] = [
		{ label: 'All', value: 'All' },
		{ label: 'Upcoming', value: 'Upcoming' },
		{ label: 'Active', value: 'Active' },
		{ label: 'Completed', value: 'Completed' },
		{ label: 'Cancelled', value: 'Cancelled' }
	];
</script>

<div class="font-quicksand min-h-screen bg-slate-950 text-gray-200 antialiased">
	<!-- Bookings Page Header -->
	<header class="sticky top-0 z-30 bg-slate-950/80 p-4 shadow-sm backdrop-blur-lg">
		<div class="mx-auto flex max-w-4xl items-center justify-between">
			<button
				on:click={() => (window.history.length > 1 ? window.history.back() : goto('/'))}
				class="rounded-full p-2.5 text-slate-300 transition-colors hover:bg-slate-800 hover:text-white"
				aria-label="Go back"
			>
				<ChevronLeft class="h-6 w-6" />
			</button>
			<h1 class="text-xl font-semibold text-gray-100">My Bookings</h1>
			<div class="w-11"><!-- Placeholder for symmetry or future icon --></div>
		</div>
	</header>

	<main class="mx-auto max-w-4xl px-4 py-6 sm:py-8">
		<!-- Filter Tabs -->
		<div class="mb-8">
			<div
				class="flex space-x-2 overflow-x-auto rounded-xl border border-slate-700/60 bg-slate-800/70 p-1.5 shadow-md sm:space-x-3"
			>
				{#each filterButtons as filterBtn (filterBtn.value)}
					<button
						on:click={() => (activeFilter = filterBtn.value)}
						class="whitespace-nowrap rounded-lg px-3 py-2 text-sm font-semibold transition-all duration-200 ease-out focus:outline-none sm:px-4
							   {activeFilter === filterBtn.value
							? 'bg-teal-500 text-white shadow-md'
							: 'text-slate-300 hover:bg-slate-700/50 hover:text-gray-100'}"
					>
						{filterBtn.label}
					</button>
				{/each}
			</div>
		</div>

		{#if filteredBookings.length > 0}
			<div class="space-y-6">
				{#each filteredBookings as booking (booking.id)}
					{@const sColor = statusColors[booking.status]}
					<div
						class="rounded-2xl border bg-gradient-to-br from-slate-800/90 to-slate-900/90 shadow-xl {sColor.border ||
							'border-slate-700/50'} overflow-hidden transition-all duration-300 ease-out hover:shadow-2xl"
					>
						<button
							on:click={() => toggleExpandBooking(booking.id)}
							class="w-full p-5 text-left focus:outline-none sm:p-6"
							aria-expanded={expandedBookingId === booking.id}
							aria-controls="booking-details-{booking.id}"
						>
							<div class="flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:gap-5">
								<img
									src={booking.carImage}
									alt={booking.carName}
									class="h-32 w-full rounded-xl border border-slate-700 object-cover shadow-md sm:h-24 sm:w-32"
									loading="lazy"
								/>
								<div class="flex-grow">
									<div class="mb-1 flex items-start justify-between">
										<h2
											class="text-lg font-semibold text-gray-100 transition-colors group-hover:text-teal-300 sm:text-xl"
										>
											{booking.carName}
										</h2>
										<div
											class="ml-2 flex flex-shrink-0 items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold {sColor.bg} {sColor.text} border {sColor.border ||
												'border-transparent'}"
										>
											<svelte:component
												this={sColor.icon}
												class="h-3.5 w-3.5 {booking.status === 'Active' ? 'animate-spin' : ''}"
											/>
											{booking.status}
										</div>
									</div>
									<p class="mb-2 text-sm font-medium text-slate-400">{booking.carBrand}</p>
									<div class="flex items-center gap-3 text-xs text-slate-300 sm:gap-4">
										<div class="flex items-center gap-1.5">
											<CalendarDays class="h-3.5 w-3.5 text-sky-400" />
											<span>{formatDate(booking.pickupDate)}</span>
										</div>
										<span class="text-slate-600">-</span>
										<div class="flex items-center gap-1.5">
											<CalendarDays class="h-3.5 w-3.5 text-sky-400" />
											<span>{formatDate(booking.dropoffDate)}</span>
										</div>
									</div>
								</div>
								<ChevronDown
									class="h-6 w-6 transform text-slate-500 transition-transform duration-300 sm:ml-auto {expandedBookingId ===
									booking.id
										? 'rotate-180'
										: 'rotate-0'}"
								/>
							</div>
						</button>

						{#if expandedBookingId === booking.id}
							<div
								transition:slide={{ duration: 300, easing: quintOut }}
								class="border-t border-slate-700/70 px-5 pb-6 pt-2 sm:px-6"
								id="booking-details-{booking.id}"
							>
								<h4 class="mb-3 mt-2 text-sm font-semibold text-slate-300">Booking Details:</h4>
								<dl class="grid grid-cols-1 gap-x-6 gap-y-3 text-sm sm:grid-cols-2">
									<div>
										<dt class="text-xs text-slate-500">Pickup</dt>
										<dd class="flex items-center gap-1.5 font-medium text-slate-200">
											<MapPin class="h-3.5 w-3.5 flex-shrink-0 text-orange-400" />
											{booking.pickupLocation} at {formatTime(booking.pickupDate)}
										</dd>
									</div>
									<div>
										<dt class="text-xs text-slate-500">Drop-off</dt>
										<dd class="flex items-center gap-1.5 font-medium text-slate-200">
											<MapPin class="h-3.5 w-3.5 flex-shrink-0 text-orange-400" />
											{booking.dropoffLocation} at {formatTime(booking.dropoffDate)}
										</dd>
									</div>
									<div>
										<dt class="text-xs text-slate-500">Total Price</dt>
										<dd class="flex items-center gap-1 font-semibold text-teal-400">
											<DollarSign class="h-3.5 w-3.5" />
											{booking.totalPrice.toFixed(2)}
										</dd>
									</div>
									<div>
										<dt class="text-xs text-slate-500">Booked On</dt>
										<dd class="text-slate-300">{formatDate(booking.bookingDate)}</dd>
									</div>
									{#if booking.features && booking.features.length > 0}
										<div class="sm:col-span-2">
											<dt class="mb-1 text-xs text-slate-500">Included Features</dt>
											<dd class="flex flex-wrap gap-2">
												{#each booking.features as feature}
													<span
														class="rounded-md border border-slate-600 bg-slate-700/80 px-2.5 py-1 text-xs text-slate-300"
														>{feature}</span
													>
												{/each}
											</dd>
										</div>
									{/if}
								</dl>
								<div class="mt-6 flex flex-col gap-3 sm:flex-row">
									{#if booking.status === 'Upcoming' || booking.status === 'Active'}
										<button
											class="flex-1 rounded-lg bg-sky-600 px-4 py-2.5 text-center text-sm font-semibold text-white shadow-md transition-colors hover:bg-sky-500"
										>
											Manage Booking
										</button>
									{/if}
									{#if booking.status === 'Completed' || booking.status === 'Cancelled'}
										<button
											class="flex flex-1 items-center justify-center gap-2 rounded-lg bg-slate-700 px-4 py-2.5 text-center text-sm font-semibold text-slate-200 shadow-md transition-colors hover:bg-slate-600"
										>
											<FileText class="h-4 w-4" /> View Invoice
										</button>
									{/if}
									<button
										class="flex flex-1 items-center justify-center gap-2 rounded-lg border border-teal-500/50 bg-teal-600/30 px-4 py-2.5 text-center text-sm font-semibold text-teal-300 shadow-md transition-colors hover:bg-teal-600/40"
									>
										<MessageSquare class="h-4 w-4" /> Contact Support
									</button>
								</div>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{:else}
			<div
				class="flex min-h-[50vh] flex-col items-center justify-center rounded-2xl bg-slate-800/50 p-8 text-center shadow-lg"
			>
				<Car class="mb-6 h-20 w-20 text-teal-500/50" />
				<h2 class="mb-2 text-2xl font-semibold text-gray-100">No Bookings Yet</h2>
				<p class="mb-6 max-w-md text-slate-400">
					It looks like you haven't made any bookings yet, or no bookings match the current filter.
				</p>
				<button
					on:click={() => goto('/cars')}
					class="transform rounded-lg bg-gradient-to-r from-teal-500 to-sky-600 px-8 py-3 font-semibold text-white shadow-lg transition-all hover:scale-105 hover:from-teal-600 hover:to-sky-700"
				>
					Explore Cars & Book Now
				</button>
			</div>
		{/if}
	</main>
</div>

<style>
	/* Additional global styles or component-specific styles can go here */
	.overflow-x-auto::-webkit-scrollbar {
		height: 4px; /* For horizontal scrollbar if tabs overflow */
	}
	.overflow-x-auto::-webkit-scrollbar-thumb {
		background-color: theme('colors.slate.700');
		border-radius: 10px;
	}
</style>
