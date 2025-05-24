<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getAuthToken, logout } from '$lib/stores/auth';
	import { fade, slide, scale, fly } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import {
		Mail,
		Phone,
		Award,
		LogOut,
		Edit3,
		ChevronLeft,
		ChevronRight,
		Loader2,
		ShieldAlert,
		CalendarDays,
		Car,
		FileText,
		HelpCircle,
		User,
		Settings,
		Bell,
		Star,
		Crown,
		Gift,
		Shield,
		Headphones,
		BookOpen,
		Camera,
		Share2,
		Copy,
		Check,
		Zap,
		Target,
		Activity,
		Wallet,
		CreditCard,
		Bookmark
	} from 'lucide-svelte';

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

	let userData: UserProfileData | null = null;
	let loading = true;
	let error: string | null = null;
	let showShareMenu = false;
	let copySuccess = false;
	let expandedSection = '';
	let profileImageUrl = '';

	const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://0.0.0.0:8000';
	const API_URL = `${API_BASE_URL}/authentication/get-client-details/`;

	function getInitials(name: string | null): string {
		if (!name) return 'U';
		const parts = name.trim().split(' ');
		if (parts.length > 1 && parts[0] && parts[parts.length - 1]) {
			return parts[0][0].toUpperCase() + parts[parts.length - 1][0].toUpperCase();
		} else if (parts[0] && parts[0].length >= 2) {
			return parts[0].substring(0, 2).toUpperCase();
		} else if (parts[0] && parts[0].length === 1) {
			return parts[0][0].toUpperCase();
		}
		return 'U';
	}

	onMount(async () => {
		const authToken = getAuthToken();

		if (!authToken) {
			error = 'Authentication token not found. Redirecting to login...';
			loading = false;
			setTimeout(() => goto('/intro'), 2000);
			return;
		}

		try {
			const response = await fetch(API_URL, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ authToken })
			});

			const responseData = await response.json();

			if (!response.ok) {
				if (
					responseData.error &&
					responseData.error.toLowerCase().includes('invalid authentication token')
				) {
					logout();
					goto('/intro');
					return;
				}
				throw new Error(
					responseData.message || responseData.error || `Server error: ${response.status}`
				);
			}

			if (responseData.success) {
				userData = responseData.data as UserProfileData;
				if (userData.details === null) {
					setTimeout(() => goto('/completeprofile'), 1000);
					error = 'Please complete your profile to continue.';
					loading = false;
					return;
				}
			} else {
				throw new Error(responseData.message || 'Failed to retrieve profile data.');
			}
		} catch (err: any) {
			console.error('Failed to fetch profile:', err);
			error = err.message || 'An unexpected network error occurred.';
		} finally {
			if (userData?.details !== null) {
				loading = false;
			}
		}
	});

	const handleLogout = () => {
		logout();
		goto('/intro');
	};

	const shareProfile = async () => {
		try {
			if (navigator.share) {
				await navigator.share({
					title: `${userData?.details?.name}'s Profile`,
					text: 'Check out my profile on Horizoon!',
					url: window.location.href
				});
			} else {
				showShareMenu = true;
			}
		} catch (error) {
			console.error('Error sharing:', error);
		}
	};

	const copyProfileLink = async () => {
		try {
			await navigator.clipboard.writeText(window.location.href);
			copySuccess = true;
			setTimeout(() => {
				copySuccess = false;
				showShareMenu = false;
			}, 2000);
		} catch (error) {
			console.error('Failed to copy:', error);
		}
	};

	const toggleSection = (section: string) => {
		expandedSection = expandedSection === section ? '' : section;
	};

	// Enhanced profile sections with better organization
	const quickActions = [
		{
			label: 'Edit Profile',
			icon: Edit3,
			action: () => goto('/completeprofile'),
			color: 'text-sky-400',
			bg: 'bg-sky-500/20',
			border: 'border-sky-500/30',
			description: 'Update your personal information'
		},
		{
			label: 'My Bookings',
			icon: CalendarDays,
			action: () => goto('/bookings'),
			color: 'text-emerald-400',
			bg: 'bg-emerald-500/20',
			border: 'border-emerald-500/30',
			description: 'View your trip history',
			badge: '3'
		}
		// {
		// 	label: 'Payment Methods',
		// 	icon: CreditCard,
		// 	action: () => goto('/payment-methods'),
		// 	color: 'text-purple-400',
		// 	bg: 'bg-purple-500/20',
		// 	border: 'border-purple-500/30',
		// 	description: 'Manage cards & wallets'
		// },
		// {
		// 	label: 'Saved Vehicles',
		// 	icon: Bookmark,
		// 	action: () => goto('/favorites'),
		// 	color: 'text-rose-400',
		// 	bg: 'bg-rose-500/20',
		// 	border: 'border-rose-500/30',
		// 	description: 'Your favorite rides'
		// }
	];

	const accountLinks = [
		{
			label: 'Become a Host',
			icon: Car,
			action: () => goto('/renter-application'),
			color: 'text-teal-400',
			bg: 'bg-teal-500/20',
			border: 'border-teal-500/30',
			highlight: true,
			description: 'Start earning with your vehicle',
			badge: 'New'
		},
		{
			label: 'Referral Program',
			icon: Gift,
			action: () => goto('/referrals'),
			color: 'text-amber-400',
			bg: 'bg-amber-500/20',
			border: 'border-amber-500/30',
			description: 'Earn rewards by referring friends'
		}
		// {
		// 	label: 'Notifications',
		// 	icon: Bell,
		// 	action: () => goto('/notifications'),
		// 	color: 'text-indigo-400',
		// 	bg: 'bg-indigo-500/20',
		// 	border: 'border-indigo-500/30',
		// 	description: 'Manage your alerts'
		// },
		// {
		// 	label: 'App Settings',
		// 	icon: Settings,
		// 	action: () => goto('/settings'),
		// 	color: 'text-slate-400',
		// 	bg: 'bg-slate-500/20',
		// 	border: 'border-slate-500/30',
		// 	description: 'Preferences & privacy'
		// }
	];

	const supportLinks = [
		{
			label: 'Help & Support',
			icon: Headphones,
			action: () => goto('/support'),
			color: 'text-amber-400',
			bg: 'bg-amber-500/20',
			border: 'border-amber-500/30',
			description: '24/7 customer support'
		},
		{
			label: 'Safety Center',
			icon: Shield,
			action: () => goto('/safety'),
			color: 'text-green-400',
			bg: 'bg-green-500/20',
			border: 'border-green-500/30',
			description: 'Safety tips & guidelines'
		},
		{
			label: 'Terms & Conditions',
			icon: FileText,
			action: () => goto('/terms'),
			color: 'text-slate-400',
			bg: 'bg-slate-500/20',
			border: 'border-slate-500/30',
			description: 'Legal information'
		},
		{
			label: 'Privacy Policy',
			icon: BookOpen,
			action: () => goto('/privacy'),
			color: 'text-indigo-400',
			bg: 'bg-indigo-500/20',
			border: 'border-indigo-500/30',
			description: 'How we protect your data'
		}
	];

	// Profile completion percentage calculation
	$: profileCompletion = userData?.details ? calculateProfileCompletion(userData) : 0;

	function calculateProfileCompletion(data: UserProfileData): number {
		let completed = 0;
		const total = 4; // Total fields to check

		if (data.details?.name) completed++;
		if (data.client?.email) completed++;
		if (data.details?.phone) completed++;
		if (data.details?.gender) completed++;

		return Math.round((completed / total) * 100);
	}
</script>

<div class="font-quicksand min-h-screen bg-slate-950 text-gray-200 antialiased">
	<!-- Enhanced Mobile Header -->
	<header
		class="sticky top-0 z-40 border-b border-slate-700/50 bg-gradient-to-r from-slate-900/95 to-slate-800/95 backdrop-blur-xl"
	>
		<div class="px-4 py-3">
			<div class="flex items-center justify-between">
				<button
					on:click={() => (window.history.length > 1 ? window.history.back() : goto('/'))}
					class="rounded-full bg-slate-800/60 p-2.5 text-slate-300 transition-all duration-200 hover:bg-slate-700 hover:text-teal-400"
					aria-label="Go back"
				>
					<ChevronLeft class="h-5 w-5" />
				</button>

				<div class="flex-1 text-center">
					<h1 class="text-xl font-bold text-gray-100">Profile</h1>
					{#if userData?.details}
						<p class="text-sm text-slate-400">
							Welcome back, {userData.details.name.split(' ')[0]}!
						</p>
					{/if}
				</div>

				<div class="flex items-center gap-2">
					<button
						on:click={shareProfile}
						class="rounded-full bg-slate-800/60 p-2.5 text-slate-300 transition-all duration-200 hover:bg-slate-700 hover:text-teal-400"
						aria-label="Share profile"
					>
						<Share2 class="h-5 w-5" />
					</button>
					<button
						on:click={() => goto('/completeprofile')}
						class="rounded-full bg-slate-800/60 p-2.5 text-slate-300 transition-all duration-200 hover:bg-slate-700 hover:text-teal-400"
						aria-label="Settings"
					>
						<Settings class="h-5 w-5" />
					</button>
				</div>
			</div>
		</div>
	</header>

	<main class="pb-6">
		{#if loading}
			<div
				class="flex min-h-[calc(100vh-150px)] flex-col items-center justify-center px-4"
				transition:fade={{ duration: 300 }}
			>
				<div class="relative mb-6">
					<div
						class="h-20 w-20 animate-pulse rounded-full bg-gradient-to-r from-teal-500 to-cyan-600"
					></div>
					<Loader2 class="absolute inset-0 m-auto h-8 w-8 animate-spin text-white" />
				</div>
				<p class="mb-2 text-lg font-medium text-slate-200">Loading your profile...</p>
				<p class="text-sm text-slate-400">Setting up your dashboard</p>
			</div>
		{:else if error}
			<div
				class="mx-4 mx-auto mt-16 max-w-md rounded-3xl border border-slate-700/50 bg-slate-800/50 p-8 text-center shadow-xl backdrop-blur-sm"
				transition:fade={{ duration: 300 }}
			>
				<div class="mx-auto mb-6 w-fit rounded-full bg-red-500/20 p-4">
					<ShieldAlert class="h-12 w-12 text-red-400" />
				</div>
				<h2 class="mb-3 text-xl font-semibold text-red-300">
					{userData && userData.details === null ? 'Complete Your Profile' : 'Access Denied'}
				</h2>
				<p class="mb-8 text-sm leading-relaxed text-slate-300">{error}</p>
				<button
					on:click={() =>
						userData && userData.details === null ? goto('/completeprofile') : goto('/intro')}
					class="w-full rounded-2xl bg-gradient-to-r from-teal-500 to-cyan-600 px-6 py-3.5 text-base font-semibold text-white shadow-lg transition-all duration-200 hover:scale-105 hover:shadow-xl"
				>
					{userData && userData.details === null ? 'Complete Profile' : 'Login / Sign Up'}
				</button>
			</div>
		{:else if userData && userData.details}
			<div class="space-y-6 px-4 pt-6">
				<!-- Enhanced Profile Header Card -->
				<section
					class="relative overflow-hidden rounded-3xl border border-slate-700/50 bg-gradient-to-br from-slate-800/80 to-slate-900/80 shadow-2xl backdrop-blur-sm"
					transition:fade={{ duration: 300 }}
				>
					<!-- Animated Background Effects -->
					<div
						class="absolute -right-16 -top-10 h-48 w-48 animate-pulse rounded-full bg-teal-600/20 opacity-70 blur-3xl"
					></div>
					<div
						class="absolute -bottom-12 -left-20 h-56 w-56 animate-pulse rounded-full bg-cyan-600/10 opacity-60 blur-3xl delay-1000"
					></div>

					<div class="relative z-10 p-6">
						<!-- Profile Picture and Basic Info -->
						<div class="mb-6 flex flex-col items-center text-center">
							<div class="relative mb-4">
								<div
									class="flex h-32 w-32 items-center justify-center rounded-full border-4 border-teal-400/50 bg-gradient-to-br from-teal-500 to-cyan-600 text-4xl font-bold text-white shadow-2xl ring-4 ring-slate-950/30"
								>
									{getInitials(userData.details.name)}
								</div>
								<!-- Profile completion ring -->
								<button
									on:click={() => goto('/completeprofile')}
									class="absolute -bottom-2 -right-2 rounded-full border-2 border-slate-700 bg-slate-800 p-3 text-teal-400 shadow-lg transition-all duration-200 hover:bg-slate-700 hover:text-teal-300"
									aria-label="Edit avatar"
								>
									<Camera class="h-5 w-5" />
								</button>
							</div>

							<div>
								<h2
									class="mb-2 bg-gradient-to-r from-gray-100 to-slate-300 bg-clip-text text-3xl font-bold text-transparent"
								>
									{userData.details.name}
								</h2>
								<p class="mb-3 text-lg font-medium text-teal-300">@{userData.client.username}</p>

								<!-- Membership Badge -->
								<div class="mb-4 flex items-center justify-center gap-2">
									<div
										class="flex items-center gap-2 rounded-full border border-teal-500/30 bg-gradient-to-r from-teal-500/20 to-cyan-500/20 px-4 py-2"
									>
										<Crown class="h-4 w-4 text-teal-400" />
										<span class="text-sm font-medium text-teal-300">Premium Member</span>
									</div>
								</div>

								<!-- Profile Completion -->
								<div class="mb-4 rounded-2xl border border-slate-700/50 bg-slate-900/50 p-4">
									<div class="mb-2 flex items-center justify-between">
										<span class="text-sm font-medium text-slate-300">Profile Completion</span>
										<span class="text-sm font-bold text-teal-400">{profileCompletion}%</span>
									</div>
									<div class="h-2 w-full rounded-full bg-slate-700">
										<div
											class="h-2 rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 transition-all duration-1000"
											style="width: {profileCompletion}%"
										></div>
									</div>
									{#if profileCompletion < 100}
										<p class="mt-2 text-xs text-slate-400">
											Complete your profile to unlock all features
										</p>
									{/if}
								</div>
							</div>
						</div>
					</div>
				</section>

				<!-- Quick Actions Section -->
				<section
					class="overflow-hidden rounded-3xl border border-slate-700/50 bg-slate-800/50 shadow-xl backdrop-blur-sm"
					transition:fade={{ duration: 300, delay: 100 }}
				>
					<div class="border-b border-slate-700/50 p-5">
						<h3 class="flex items-center gap-2 text-lg font-semibold text-gray-100">
							<Zap class="h-5 w-5 text-teal-400" />
							Quick Actions
						</h3>
						<p class="mt-1 text-sm text-slate-400">Manage your account efficiently</p>
					</div>
					<div class="grid grid-cols-2 gap-1">
						{#each quickActions as action, index}
							<button
								on:click={action.action}
								class="group flex flex-col items-center p-5 text-center transition-all duration-200 hover:bg-slate-700/30"
								in:scale={{ duration: 200, delay: index * 50 }}
							>
								<div
									class="flex h-14 w-14 items-center justify-center rounded-2xl border {action.border} {action.bg} relative mb-3 transition-transform duration-200 group-hover:scale-110"
								>
									<svelte:component this={action.icon} class="h-6 w-6 {action.color}" />
									{#if action.badge}
										<span
											class="absolute -right-1 -top-1 rounded-full bg-teal-500 px-1.5 py-0.5 text-xs font-bold text-white"
										>
											{action.badge}
										</span>
									{/if}
								</div>
								<span class="mb-1 text-sm font-semibold text-gray-200 group-hover:text-gray-100">
									{action.label}
								</span>
								<p class="text-xs leading-tight text-slate-400">{action.description}</p>
							</button>
						{/each}
					</div>
				</section>

				<!-- Personal Information Section -->
				<section
					class="overflow-hidden rounded-3xl border border-slate-700/50 bg-slate-800/50 shadow-xl backdrop-blur-sm"
					transition:fade={{ duration: 300, delay: 200 }}
				>
					<button
						on:click={() => toggleSection('personal')}
						class="w-full border-b border-slate-700/50 p-5 text-left transition-colors duration-200 hover:bg-slate-700/30"
					>
						<div class="flex items-center justify-between">
							<div>
								<h3 class="flex items-center gap-2 text-lg font-semibold text-gray-100">
									<User class="h-5 w-5 text-teal-400" />
									Personal Information
								</h3>
								<p class="mt-1 text-sm text-slate-400">Your account details</p>
							</div>
							<ChevronRight
								class="h-5 w-5 text-slate-500 transition-transform duration-200 {expandedSection ===
								'personal'
									? 'rotate-90'
									: ''}"
							/>
						</div>
					</button>

					{#if expandedSection === 'personal'}
						<div class="p-5" transition:slide={{ duration: 300 }}>
							<div class="space-y-4">
								<!-- Email -->
								<div
									class="flex items-start gap-4 rounded-2xl border border-slate-700/30 bg-slate-900/30 p-4 transition-colors duration-200 hover:bg-slate-800/40"
								>
									<div
										class="flex h-12 w-12 items-center justify-center rounded-xl border border-slate-700 bg-slate-800/60"
									>
										<Mail class="h-5 w-5 text-teal-400" />
									</div>
									<div class="flex-1">
										<dt class="mb-1 text-xs font-medium text-slate-400">Email Address</dt>
										<dd class="text-base font-semibold text-gray-200">{userData.client.email}</dd>
										<p class="mt-1 text-xs text-slate-500">Verified account</p>
									</div>
									<button
										on:click={() => navigator.clipboard?.writeText(userData.client.email)}
										class="p-2 text-slate-400 transition-colors duration-200 hover:text-teal-400"
									>
										<Copy class="h-4 w-4" />
									</button>
								</div>

								<!-- Phone -->
								<div
									class="flex items-start gap-4 rounded-2xl border border-slate-700/30 bg-slate-900/30 p-4 transition-colors duration-200 hover:bg-slate-800/40"
								>
									<div
										class="flex h-12 w-12 items-center justify-center rounded-xl border border-slate-700 bg-slate-800/60"
									>
										<Phone class="h-5 w-5 text-teal-400" />
									</div>
									<div class="flex-1">
										<dt class="mb-1 text-xs font-medium text-slate-400">Phone Number</dt>
										<dd class="text-base font-semibold text-gray-200">
											{userData.details.phone || 'Not provided'}
										</dd>
										<p class="mt-1 text-xs text-slate-500">
											{userData.details.phone ? 'Verified number' : 'Add phone for security'}
										</p>
									</div>
									<button
										on:click={() =>
											userData.details.phone &&
											navigator.clipboard?.writeText(userData.details.phone)}
										class="p-2 text-slate-400 transition-colors duration-200 hover:text-teal-400"
									>
										<Copy class="h-4 w-4" />
									</button>
								</div>

								<!-- Gender -->
								<div
									class="flex items-start gap-4 rounded-2xl border border-slate-700/30 bg-slate-900/30 p-4 transition-colors duration-200 hover:bg-slate-800/40"
								>
									<div
										class="flex h-12 w-12 items-center justify-center rounded-xl border border-slate-700 bg-slate-800/60"
									>
										<Award class="h-5 w-5 text-teal-400" />
									</div>
									<div class="flex-1">
										<dt class="mb-1 text-xs font-medium text-slate-400">Gender</dt>
										<dd class="text-base font-semibold text-gray-200">
											{userData.details.gender || 'Not specified'}
										</dd>
										<p class="mt-1 text-xs text-slate-500">Used for personalization</p>
									</div>
								</div>
							</div>
						</div>
					{/if}
				</section>

				<!-- Account Settings Section -->
				<section
					class="overflow-hidden rounded-3xl border border-slate-700/50 bg-slate-800/50 shadow-xl backdrop-blur-sm"
					transition:fade={{ duration: 300, delay: 300 }}
				>
					<div class="border-b border-slate-700/50 p-5">
						<h3 class="flex items-center gap-2 text-lg font-semibold text-gray-100">
							<Settings class="h-5 w-5 text-teal-400" />
							Account & Services
						</h3>
						<p class="mt-1 text-sm text-slate-400">Manage your account preferences</p>
					</div>
					<div class="divide-y divide-slate-700/30">
						{#each accountLinks as link, index}
							<button
								on:click={link.action}
								class="group flex w-full items-center justify-between p-5 transition-all duration-200 hover:bg-slate-700/30 {link.highlight
									? 'bg-teal-500/5 hover:bg-teal-500/10'
									: ''}"
								in:slide={{ duration: 200, delay: index * 50 }}
							>
								<div class="flex items-center gap-4">
									<div
										class="flex h-12 w-12 items-center justify-center rounded-xl border {link.border} {link.bg} relative transition-transform duration-200 group-hover:scale-110"
									>
										<svelte:component this={link.icon} class="h-5 w-5 {link.color}" />
										{#if link.badge}
											<span
												class="absolute -right-1 -top-1 rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 px-1.5 py-0.5 text-xs font-bold text-white"
											>
												{link.badge}
											</span>
										{/if}
									</div>
									<div class="text-left">
										<span
											class="text-base font-semibold text-gray-200 group-hover:text-gray-100 {link.highlight
												? 'text-teal-300'
												: ''} block"
										>
											{link.label}
										</span>
										<p class="text-sm text-slate-400">{link.description}</p>
									</div>
								</div>
								<ChevronRight
									class="h-5 w-5 text-slate-500 transition-all duration-200 group-hover:translate-x-0.5 group-hover:text-teal-400"
								/>
							</button>
						{/each}
					</div>
				</section>

				<!-- Support & Legal Section -->
				<section
					class="overflow-hidden rounded-3xl border border-slate-700/50 bg-slate-800/50 shadow-xl backdrop-blur-sm"
					transition:fade={{ duration: 300, delay: 400 }}
				>
					<div class="border-b border-slate-700/50 p-5">
						<h3 class="flex items-center gap-2 text-lg font-semibold text-gray-100">
							<HelpCircle class="h-5 w-5 text-teal-400" />
							Support & Legal
						</h3>
						<p class="mt-1 text-sm text-slate-400">Get help and review policies</p>
					</div>
					<div class="divide-y divide-slate-700/30">
						{#each supportLinks as link, index}
							<button
								on:click={link.action}
								class="group flex w-full items-center justify-between p-5 transition-all duration-200 hover:bg-slate-700/30"
								in:slide={{ duration: 200, delay: index * 50 }}
							>
								<div class="flex items-center gap-4">
									<div
										class="flex h-12 w-12 items-center justify-center rounded-xl border {link.border} {link.bg} transition-transform duration-200 group-hover:scale-110"
									>
										<svelte:component this={link.icon} class="h-5 w-5 {link.color}" />
									</div>
									<div class="text-left">
										<span
											class="block text-base font-semibold text-gray-200 group-hover:text-gray-100"
										>
											{link.label}
										</span>
										<p class="text-sm text-slate-400">{link.description}</p>
									</div>
								</div>
								<ChevronRight
									class="h-5 w-5 text-slate-500 transition-all duration-200 group-hover:translate-x-0.5 group-hover:text-teal-400"
								/>
							</button>
						{/each}
					</div>
				</section>

				<!-- Enhanced Logout Section -->
				<section class="mb-8 mt-8">
					<button
						on:click={handleLogout}
						class="group flex w-full items-center justify-center gap-3 rounded-2xl border border-rose-500/30 bg-gradient-to-r from-rose-500/20 to-red-500/20 px-6 py-4 font-semibold text-rose-300 shadow-lg backdrop-blur-sm transition-all duration-200 hover:scale-105 hover:from-rose-500/30 hover:to-red-500/30 hover:text-rose-200 hover:shadow-xl"
						transition:fade={{ duration: 300, delay: 500 }}
					>
						<LogOut class="h-5 w-5 transition-transform duration-200 group-hover:scale-110" />
						Sign Out
						<span class="text-xs opacity-60">| Logout from all devices</span>
					</button>
				</section>
			</div>
		{/if}
	</main>

	<!-- Share Menu Modal -->
	{#if showShareMenu}
		<div
			class="fixed inset-0 z-50 flex items-end bg-black/80 backdrop-blur-md"
			transition:fade={{ duration: 200 }}
			on:click={() => (showShareMenu = false)}
		>
			<div
				class="w-full rounded-t-3xl border-t border-slate-700/50 bg-gradient-to-t from-slate-900 to-slate-800 p-6"
				transition:fly={{ y: 300, duration: 300, easing: backOut }}
				on:click|stopPropagation
			>
				<div class="mb-4 flex justify-center">
					<div class="h-1.5 w-12 rounded-full bg-slate-600"></div>
				</div>

				<h3 class="mb-6 text-center text-lg font-semibold text-gray-100">Share Profile</h3>

				<div class="grid grid-cols-1 gap-3">
					<button
						on:click={copyProfileLink}
						class="flex items-center gap-4 rounded-2xl border border-slate-700/50 bg-slate-800/50 p-4 transition-all duration-200 hover:bg-slate-700/50"
					>
						<div class="rounded-full border border-teal-500/30 bg-teal-500/20 p-3">
							{#if copySuccess}
								<Check class="h-5 w-5 text-green-400" />
							{:else}
								<Copy class="h-5 w-5 text-teal-400" />
							{/if}
						</div>
						<div class="text-left">
							<p class="font-semibold text-gray-200">
								{copySuccess ? 'Copied to clipboard!' : 'Copy Profile Link'}
							</p>
							<p class="text-sm text-slate-400">Share your profile with others</p>
						</div>
					</button>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	:global(.font-quicksand) {
		font-family: 'Quicksand', sans-serif;
	}

	.line-clamp-2 {
		overflow: hidden;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 2;
	}
</style>
