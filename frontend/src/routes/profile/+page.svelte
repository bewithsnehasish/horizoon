<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getAuthToken, logout } from '$lib/stores/auth';
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
		HelpCircle
	} from 'lucide-svelte';
	import { fade } from 'svelte/transition';

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
	const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://0.0.0.0:8000';
	const API_URL = `${API_BASE_URL}/authentication/get-client-details/`;

	function getInitials(name: string | null): string {
		if (!name) return 'H';
		const parts = name.trim().split(' ');
		if (parts.length > 1 && parts[0] && parts[parts.length - 1]) {
			return parts[0][0].toUpperCase() + parts[parts.length - 1][0].toUpperCase();
		} else if (parts[0] && parts[0].length >= 2) {
			return parts[0].substring(0, 2).toUpperCase();
		} else if (parts[0] && parts[0].length === 1) {
			return parts[0][0].toUpperCase();
		}
		return 'H';
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
					// Redirect to /completeprofile if no details are added
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

	const profileLinks = [
		{
			label: 'Edit Profile',
			icon: Edit3,
			action: () => goto('/completeprofile'),
			color: 'text-sky-400'
		},
		{
			label: 'My Bookings',
			icon: CalendarDays,
			action: () => goto('/bookings'),
			color: 'text-amber-400'
		},
		{
			label: 'Become a Renter',
			icon: Car,
			action: () => goto('/renter-application'),
			color: 'text-emerald-400',
			highlight: true
		}
	];

	const supportLinks = [
		{
			label: 'Help & Support',
			icon: HelpCircle,
			action: () => goto('/support'),
			color: 'text-purple-400'
		},
		{
			label: 'Terms & Conditions',
			icon: FileText,
			action: () => goto('/terms'),
			color: 'text-slate-400'
		}
	];
</script>

<div class="font-quicksand min-h-screen bg-slate-950 text-gray-200 antialiased">
	<!-- Profile Header -->
	<header class="sticky top-0 z-40 bg-slate-950/90 px-4 py-4 shadow-sm backdrop-blur-xl">
		<div class="mx-auto flex max-w-3xl items-center justify-between">
			<button
				on:click={() => (window.history.length > 1 ? window.history.back() : goto('/'))}
				class="rounded-full p-2.5 text-slate-300 transition-colors hover:bg-slate-800 hover:text-white"
				aria-label="Go back"
			>
				<ChevronLeft class="h-6 w-6" />
			</button>
			<h1 class="text-xl font-semibold text-gray-100 sm:text-2xl">Profile</h1>
			<button
				on:click={() => goto('/completeprofile')}
				class="rounded-full p-2.5 text-slate-300 transition-colors hover:bg-slate-800 hover:text-white {userData &&
				userData.details !== null
					? 'opacity-100'
					: 'pointer-events-none opacity-0'}"
				aria-label="Edit Profile"
			>
				<Edit3 class="h-5 w-5" />
			</button>
		</div>
	</header>

	<main class="pb-24 pt-4 sm:pb-28">
		{#if loading}
			<div
				class="flex min-h-[calc(100vh-150px)] flex-col items-center justify-center"
				transition:fade={{ duration: 300 }}
			>
				<Loader2 class="mb-6 h-12 w-12 animate-spin text-teal-400" />
				<p class="text-lg font-medium text-slate-200">Loading your profile...</p>
			</div>
		{:else if error}
			<div
				class="mx-auto mt-16 max-w-md rounded-3xl border border-slate-700/50 bg-slate-900/80 p-8 text-center shadow-xl"
				transition:fade={{ duration: 300 }}
			>
				<ShieldAlert class="mx-auto mb-5 h-16 w-16 text-red-400" />
				<h2 class="mb-3 text-xl font-semibold text-red-300">
					{userData && userData.details === null ? 'Complete Your Profile' : 'Access Denied'}
				</h2>
				<p class="mb-8 text-sm text-slate-300">{error}</p>
				<button
					on:click={() =>
						userData && userData.details === null ? goto('/completeprofile') : goto('/intro')}
					class="w-full rounded-xl bg-gradient-to-r from-teal-500 to-cyan-600 px-6 py-3 text-base font-semibold text-white shadow-md transition-transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-teal-400/50"
				>
					{userData && userData.details === null ? 'Complete Profile' : 'Login / Sign Up'}
				</button>
			</div>
		{:else if userData && userData.details}
			<div class="mx-auto max-w-3xl space-y-8 px-4">
				<!-- User Info Card -->
				<section
					class="relative overflow-hidden rounded-3xl border border-slate-700/50 bg-gradient-to-br from-slate-800/80 to-slate-900/90 p-6 shadow-2xl"
					transition:fade={{ duration: 300 }}
				>
					<div
						class="absolute -right-16 -top-10 h-48 w-48 rounded-full bg-teal-600/20 opacity-70 blur-3xl filter"
					></div>
					<div
						class="absolute -bottom-12 -left-20 h-56 w-56 rounded-full bg-sky-600/10 opacity-60 blur-3xl filter"
					></div>

					<div
						class="relative z-10 flex flex-col items-center space-y-5 sm:flex-row sm:items-start sm:space-x-6 sm:space-y-0"
					>
						<div
							class="flex h-24 w-24 flex-shrink-0 items-center justify-center rounded-full border-2 border-teal-400/50 bg-gradient-to-tl from-teal-500 to-sky-500 text-4xl font-bold text-white shadow-xl ring-4 ring-slate-950/30 sm:h-28 sm:w-28 sm:text-5xl"
						>
							{getInitials(userData.details.name)}
						</div>
						<div class="flex-grow text-center sm:text-left">
							<h2
								class="bg-gradient-to-r from-gray-100 to-slate-300 bg-clip-text text-3xl font-bold leading-tight text-transparent sm:text-4xl"
							>
								{userData.details.name}
							</h2>
							<p class="mt-1.5 text-base font-medium text-teal-300">@{userData.client.username}</p>
							<p class="mt-2 line-clamp-2 text-sm text-slate-400">
								Your personal hub for managing rides and experiences with Horizoon.
							</p>
						</div>
					</div>
				</section>

				<!-- Account Details Section -->
				<section
					class="rounded-3xl border border-slate-800/70 bg-slate-900/80 p-6 shadow-xl"
					transition:fade={{ duration: 300 }}
				>
					<h3 class="mb-5 border-b border-slate-700/60 pb-3 text-xl font-semibold text-gray-100">
						Personal Information
					</h3>
					<dl class="space-y-5">
						<div class="flex items-start">
							<div
								class="mr-4 flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl border border-slate-700 bg-slate-800/60"
							>
								<Mail class="h-5 w-5 text-teal-400" />
							</div>
							<div>
								<dt class="text-xs font-medium text-slate-400">Email Address</dt>
								<dd class="mt-0.5 text-base font-semibold text-gray-200">
									{userData.client.email}
								</dd>
							</div>
						</div>
						<div class="flex items-start">
							<div
								class="mr-4 flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl border border-slate-700 bg-slate-800/60"
							>
								<Phone class="h-5 w-5 text-teal-400" />
							</div>
							<div>
								<dt class="text-xs font-medium text-slate-400">Phone Number</dt>
								<dd class="mt-0.5 text-base font-semibold text-gray-200">
									{userData.details.phone || 'Not provided'}
								</dd>
							</div>
						</div>
						<div class="flex items-start">
							<div
								class="mr-4 flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl border border-slate-700 bg-slate-800/60"
							>
								<Award class="h-5 w-5 text-teal-400" />
							</div>
							<div>
								<dt class="text-xs font-medium text-slate-400">Gender</dt>
								<dd class="mt-0.5 text-base font-semibold text-gray-200">
									{userData.details.gender || 'Not specified'}
								</dd>
							</div>
						</div>
					</dl>
				</section>

				<!-- Profile Links Section -->
				<section
					class="divide-y divide-slate-800/70 rounded-3xl border border-slate-800/70 bg-slate-900/80 shadow-xl"
					transition:fade={{ duration: 300 }}
				>
					{#each profileLinks as link (link.label)}
						<button
							on:click={link.action}
							class="group flex w-full items-center justify-between px-5 py-4 transition-colors duration-200 ease-out hover:bg-slate-800/50
								{link.highlight ? 'bg-teal-600/10 hover:bg-teal-600/20' : ''}"
						>
							<div class="flex items-center">
								<div
									class="flex h-10 w-10 flex-shrink-0 items-center justify-center bg-slate-800/60 {link.highlight
										? 'bg-teal-500/20'
										: ''} mr-4 rounded-lg border border-slate-700 transition-colors group-hover:border-slate-600"
								>
									<svelte:component
										this={link.icon}
										class="h-5 w-5 {link.color} transition-opacity group-hover:opacity-80"
									/>
								</div>
								<span
									class="text-base font-semibold text-gray-200 group-hover:text-gray-100 {link.highlight
										? 'text-teal-300 group-hover:text-teal-200'
										: ''}"
								>
									{link.label}
								</span>
							</div>
							<ChevronRight
								class="h-5 w-5 text-slate-500 transition-transform group-hover:translate-x-0.5 group-hover:text-slate-300"
							/>
						</button>
					{/each}
				</section>

				<!-- Support & Legal Links -->
				<section
					class="divide-y divide-slate-800/70 rounded-3xl border border-slate-800/70 bg-slate-900/80 shadow-xl"
					transition:fade={{ duration: 300 }}
				>
					{#each supportLinks as link (link.label)}
						<button
							on:click={link.action}
							class="group flex w-full items-center justify-between px-5 py-4 transition-colors duration-200 ease-out hover:bg-slate-800/50"
						>
							<div class="flex items-center">
								<div
									class="mr-4 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg border border-slate-700 bg-slate-800/60 transition-colors group-hover:border-slate-600"
								>
									<svelte:component
										this={link.icon}
										class="h-5 w-5 {link.color} transition-opacity group-hover:opacity-80"
									/>
								</div>
								<span class="text-base font-semibold text-gray-200 group-hover:text-gray-100"
									>{link.label}</span
								>
							</div>
							<ChevronRight
								class="h-5 w-5 text-slate-500 transition-transform group-hover:translate-x-0.5 group-hover:text-slate-300"
							/>
						</button>
					{/each}
				</section>

				<!-- Logout Button -->
				<section class="mt-8">
					<button
						on:click={handleLogout}
						class="group flex w-full items-center justify-center rounded-xl bg-rose-800/40 px-5 py-3.5 font-semibold text-rose-300 shadow-md transition-all duration-200 hover:bg-rose-700/50 hover:text-rose-200 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-rose-500 focus:ring-offset-2 focus:ring-offset-slate-950"
					>
						<LogOut class="mr-2.5 h-5 w-5" />
						Log Out
					</button>
				</section>
			</div>
		{/if}
	</main>
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
