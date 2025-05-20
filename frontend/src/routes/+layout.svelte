<!-- <script lang="ts"> -->
<!-- 	import '../app.css'; -->
<!-- 	import { authStore } from '$lib/stores/auth'; -->
<!-- </script> -->
<!---->
<!-- <div class="min-h-screen bg-black"> -->
<!-- 	{#if $authStore}{/if} -->
<!-- 	<main class=" mx-auto"> -->
<!-- 		<slot /> -->
<!-- 	</main> -->
<!-- </div> -->

<!-- src/routes/+layout.svelte -->
<script lang="ts">
<<<<<<< HEAD
    import '../app.css';
    import { authStore } from '$lib/stores/auth';
    import { onMount } from 'svelte';

    // Optional: Add a loading state
    let loading = true;
    
    onMount(() => {
        loading = false;
    });
</script>

{#if loading}
    <div class="min-h-screen bg-black flex items-center justify-center">
        Loading...
    </div>
{:else}
    <div class="min-h-screen bg-black">
        {#if $authStore}{/if}
        <main class="mx-auto">
            <slot />
        </main>
    </div>
{/if}
=======
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import '../app.css';
	import { authStore, getAuthToken } from '$lib/stores/auth';

	// Lucide Icons for the bottom navigation
	import { Home, Search, CalendarDays, User as UserIcon } from 'lucide-svelte';

	const PUBLIC_ROUTES = ['/intro', '/signin', '/signup'];
	const USER_ROUTES = ['/', '/profile', '/completeprofile'];

	// Bottom Navigation Data
	const navItems = [
		{ icon: Home, label: 'Home', href: '/' },
		{ icon: Search, label: 'Explore', href: '/cars' },
		{ icon: CalendarDays, label: 'Bookings', href: '/bookings' },
		{ icon: UserIcon, label: 'Profile', href: '/profile' }
	];

	// Watch for changes in the page URL and authStore
	$: path = $page.url.pathname;
	$: user = $authStore;

	$: {
		if (browser) {
			const isPublicRoute = PUBLIC_ROUTES.includes(path);
			const isUserRoute = USER_ROUTES.some((route) => path.startsWith(route));

			console.log('Client-side - User:', user);
			console.log('Client-side - authToken:', getAuthToken());
			console.log('Client-side - Path:', path);
			console.log('Client-side - isPublicRoute:', isPublicRoute);
			console.log('Client-side - isUserRoute:', isUserRoute);

			// If user is not logged in
			if (!user) {
				// Allow access to public routes
				if (isPublicRoute) {
					console.log('Allowing unauthenticated user to access public route:', path);
				} else {
					// Redirect to /intro for non-public routes
					console.log('Redirecting unauthenticated user to /intro from:', path);
					goto('/intro', { replaceState: true });
				}
			}

			// If user is logged in
			if (user) {
				// Redirect logged-in users away from public routes to /
				if (isPublicRoute) {
					console.log('Redirecting logged-in user to / from:', path);
					goto('/', { replaceState: true });
				} else if (isUserRoute) {
					console.log('Allowing logged-in user to access protected route:', path);
				}
			}
		}
	}
</script>

<div class="font-quicksand min-h-screen bg-slate-950 pb-20 text-gray-200 antialiased">
	<!-- This slot will render the content of your +page.svelte files -->
	<slot />

	<!-- Global Bottom Navigation Bar -->
	{#if !PUBLIC_ROUTES.some((route) => path.startsWith(route))}
		<nav
			class="fixed bottom-0 left-0 right-0 z-30 flex w-full items-center justify-around rounded-t-2xl border-t border-slate-700/50 bg-slate-900/80 px-4 py-3 shadow-2xl backdrop-blur-lg"
		>
			{#each navItems as item (item.label)}
				{@const isActive = item.href === '/' ? path === item.href : path.startsWith(item.href)}
				<a
					href={item.href}
					class="flex min-w-[60px] flex-col items-center rounded-lg p-2 transition-colors duration-200 {isActive
						? 'text-teal-400'
						: 'text-slate-400 hover:text-slate-200'}"
					aria-label={item.label}
				>
					<div
						class="mb-0.5 rounded-full p-2 transition-all duration-200 {isActive
							? 'scale-110 bg-teal-500/10 shadow-md shadow-teal-500/30'
							: 'group-hover:bg-slate-700/50'}"
					>
						<svelte:component this={item.icon} class="h-6 w-6" />
					</div>
					<span class="text-xs font-medium">{item.label}</span>
				</a>
			{/each}
		</nav>
	{/if}
</div>

<style>
	:global(.font-quicksand) {
		font-family: 'Quicksand', sans-serif;
	}
</style>
>>>>>>> 99030e754e9ac06eb63021760836ffc9ee173051
