<!-- src/routes/intro/+page.svelte -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { Motion } from 'svelte-motion';
	import { ChevronRight, ChevronLeft } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import { goto } from '$app/navigation'; // Import goto for client-side navigation
	import { logout } from '$lib/stores/auth'; // Import authStore and logout

	interface Screen {
		id: number;
		type: 'splash' | 'onboarding' | 'welcome';
		logo?: string;
		image?: string;
		title?: string;
		highlightedText?: string;
		description?: string;
	}

	let currentScreenIndex = 0;
	let showSplash = true;
	let animationDirection: 'next' | 'prev' = 'next';

	const screens: Screen[] = [
		{
			id: 0,
			type: 'splash',
			logo: 'https://picsum.photos/1000'
		},
		{
			id: 1,
			type: 'onboarding',
			image: 'https://cdn.pixabay.com/photo/2022/07/31/20/32/volkswagen-7356817_1280.jpg',
			title: 'Urgent Need',
			highlightedText: 'of a New Car?',
			description:
				'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt'
		},
		{
			id: 2,
			type: 'onboarding',
			image: 'https://cdn.pixabay.com/photo/2015/08/03/00/32/car-872717_1280.png',
			title: 'Add to Favorites:',
			highlightedText: 'Join Us and made your Car',
			description:
				'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt'
		},
		{
			id: 3,
			type: 'welcome',
			image: 'https://cdn.pixabay.com/photo/2021/01/01/21/09/challenger-5880009_1280.jpg',
			title: 'Your Ultimate',
			highlightedText: 'Renting Car',
			description: 'Experience'
		}
	];

	let currentScreen = screens[currentScreenIndex];

	onMount(() => {
		// Clear authentication state when landing on /intro
		logout(); // This clears localStorage and authStore
		console.log('Intro Page - Cleared authentication state');

		if (showSplash) {
			const timer = setTimeout(() => {
				showSplash = false;
				currentScreenIndex = 1;
				updateScreen();
			}, 1000);
			return () => clearTimeout(timer);
		}
	});

	const updateScreen = () => {
		currentScreen = screens[currentScreenIndex];
	};

	const handleNext = () => {
		if (currentScreenIndex < screens.length - 1) {
			animationDirection = 'next';
			currentScreenIndex++;
			updateScreen();
		}
	};

	const handlePrev = () => {
		if (currentScreenIndex > 0) {
			animationDirection = 'prev';
			currentScreenIndex--;
			updateScreen();
		}
	};

	const handleSkip = () => {
		animationDirection = 'next';
		currentScreenIndex = screens.length - 1;
		updateScreen();
	};

	// Use goto for navigation to /login
	const handleGetStarted = () => {
		goto('/signup');
	};

	const getTransition = () => {
		const xOffset = animationDirection === 'next' ? 50 : -50;
		return {
			initial: { opacity: 0, x: xOffset },
			animate: { opacity: 1, x: 0 },
			exit: { opacity: 0, x: -xOffset },
			transition: { duration: 0.5 }
		};
	};
</script>

<div class="h-screen w-full bg-black">
	{#if showSplash}
		<Motion
			initial={{ opacity: 0 }}
			animate={{ opacity: 1 }}
			exit={{ opacity: 0 }}
			transition={{ duration: 0.5 }}
			let:motion
		>
			<div use:motion class="flex h-full w-full items-center justify-center bg-black">
				<div class="relative flex h-24 w-24 items-center justify-center rounded-full bg-black">
					<img
						src={screens[0].logo ?? '/placeholder.svg'}
						alt="App Logo"
						class="h-full w-full rounded-full object-contain"
					/>
				</div>
			</div>
		</Motion>
	{:else}
		<Motion {...getTransition()} let:motion class="absolute inset-0 flex h-full w-full flex-col">
			<div use:motion class="flex h-full w-full flex-col">
				{#if currentScreen.type === 'onboarding'}
					<div class="flex justify-end p-4">
						<Button
							variant="secondary"
							on:click={handleSkip}
							class="h-9 px-4 text-sm text-gray-500 hover:text-blue-500"
						>
							Skip
						</Button>
					</div>
				{/if}
				{#if currentScreen.type === 'welcome'}
					<div class="h-12"></div>
				{/if}

				<div class="flex flex-1 flex-col items-center px-6">
					{#if currentScreen.image}
						<div class="relative mb-8 aspect-square w-full overflow-hidden rounded-full">
							<img
								src={currentScreen.image}
								alt={currentScreen.type === 'welcome' ? 'Welcome' : 'Onboarding'}
								class="h-full w-full object-cover"
							/>
						</div>
					{/if}

					<h1 class="mb-2 text-center text-2xl font-semibold text-white">
						{currentScreen.title}
						{#if currentScreen.highlightedText}
							<span class="text-blue-500">
								{' '}{currentScreen.highlightedText}
							</span>
						{/if}
					</h1>
					<p class="mb-8 max-w-md text-center text-gray-500">
						{currentScreen.description}
					</p>

					{#if currentScreen.type === 'onboarding'}
						<div class="mb-8 flex items-center gap-4">
							{#each screens.slice(1, -1) as _, idx}
								<div
									class={`h-2 w-2 rounded-full ${idx === currentScreenIndex - 1 ? 'bg-blue-500' : 'bg-gray-200'}`}
								></div>
							{/each}
						</div>
						<div class="flex items-center gap-4">
							<Button
								variant="outline"
								on:click={handlePrev}
								disabled={currentScreenIndex === 0}
								class="h-12 w-12 rounded-full bg-white p-0 text-black hover:bg-gray-200"
							>
								<ChevronLeft class="h-6 w-6" />
							</Button>
							<Button
								variant="outline"
								on:click={handleNext}
								class="h-12 w-12 rounded-full bg-white p-0 text-black hover:bg-gray-200"
							>
								<ChevronRight class="h-6 w-6" />
							</Button>
						</div>
					{:else if currentScreen.type === 'welcome'}
						<Button
							size="lg"
							on:click={handleGetStarted}
							class="mb-4 w-full max-w-sm bg-blue-500 text-white hover:bg-blue-600"
						>
							Let's Get Started
						</Button>
						<div class="flex items-center gap-2 text-sm">
							<span class="text-gray-500">Already have an account?</span>
							<button
								on:click={handleGetStarted}
								class="font-medium text-blue-500 hover:text-blue-600"
							>
								Sign In
							</button>
						</div>
					{/if}
				</div>
			</div>
		</Motion>
	{/if}
</div>

<style>
	:global(.bg-blue-500) {
		background-color: #3b82f6;
	}
	:global(.hover\:bg-blue-600:hover) {
		background-color: #2563eb;
	}
	:global(.text-gray-500) {
		color: #6b7280;
	}
	:global(.bg-gray-200) {
		background-color: #e5e7eb;
	}
	:global(.hover\:bg-gray-200:hover) {
		background-color: #d1d5db;
	}
	:global(.text-blue-500) {
		color: #3b82f6;
	}
	:global(.hover\:text-blue-600:hover) {
		color: #2563eb;
	}
</style>
