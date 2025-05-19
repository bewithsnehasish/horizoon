<script lang="ts">
	import { onMount } from 'svelte';
	import { motion } from 'svelte/motion';
	import { ChevronRight, ChevronLeft } from 'lucide-svelte';
	import CustomButton from '$lib/components/CustomButton.svelte';

	interface Screen {
		type: 'splash' | 'onboarding' | 'welcome';
		logo?: string;
		image?: string;
		title?: string;
		highlightedText?: string;
		description?: string;
	}

	const screens: Screen[] = [
		{
			type: 'splash',
			logo: '/adhora.png'
		},
		{
			type: 'onboarding',
			image: '/image1.png',
			title: 'Getting Started With',
			highlightedText: 'Adorah',
			description:
				'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt'
		},
		{
			type: 'onboarding',
			image: '/image2.png',
			title: 'Add to Favorites:',
			highlightedText: 'Keep Your Favorite Services Close',
			description:
				'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt'
		},
		{
			type: 'welcome',
			image: '/image3.png',
			title: 'Your Ultimate',
			highlightedText: 'Adorah',
			description: 'Experience'
		}
	];

	let currentScreen = 0;
	let showSplash = true;

	onMount(() => {
		if (showSplash) {
			const timer = setTimeout(() => {
				showSplash = false;
				currentScreen = 1;
			}, 1000);
			return () => clearTimeout(timer);
		}
	});

	const handleNext = () => {
		if (currentScreen < screens.length - 1) {
			currentScreen += 1;
		}
	};

	const handlePrev = () => {
		if (currentScreen > 0) {
			currentScreen -= 1;
		}
	};

	const handleSkip = () => {
		currentScreen = screens.length - 1;
	};
</script>

<div class="h-screen w-full bg-white">
	<AnimatePresence mode="wait">
		{#if showSplash}
			<motion.div
				key="splash"
				initial={{ opacity: 0 }}
				animate={{ opacity: 1 }}
				exit={{ opacity: 0 }}
				class="flex h-full w-full items-center justify-center bg-blue-500"
			>
				<div class="relative flex h-24 w-24 items-center justify-center rounded-full bg-white">
					<img
						src={screens[0].logo || '/placeholder.svg'}
						alt="Adorah Logo"
						width={80}
						height={80}
					/>
				</div>
			</motion.div>
		{:else}
			<motion.div
				key={currentScreen}
				initial={{ opacity: 0, x: 50 }}
				animate={{ opacity: 1, x: 0 }}
				exit={{ opacity: 0, x: -50 }}
				class="flex h-full w-full flex-col"
			>
				{#if currentScreen < screens.length - 1}
					<!-- Onboarding Screens -->
					<div class="flex flex-1 flex-col">
						<div class="flex justify-end p-4">
							<CustomButton variant="secondary" on:click={handleSkip} class="h-9 px-4 text-sm">
								Skip
							</CustomButton>
						</div>
						<div class="flex flex-1 flex-col items-center px-6">
							<div class="relative mb-8 aspect-square w-full overflow-hidden rounded-full">
								<img
									src={screens[currentScreen].image || '/placeholder.svg'}
									alt="Onboarding"
									class="object-cover"
								/>
							</div>
							<h1 class="mb-2 text-center text-2xl font-semibold text-black">
								{screens[currentScreen].title}{' '}
								<span class="text-blue-500">{screens[currentScreen].highlightedText}</span>
							</h1>
							<p class="mb-8 text-center text-gray-500">{screens[currentScreen].description}</p>
							<div class="mb-8 flex items-center gap-4">
								{#each screens.slice(1, -1) as _, idx}
									<div
										class="h-2 w-2 rounded-full"
										class:bg-blue-500={idx === currentScreen - 1}
										class:bg-gray-200={idx !== currentScreen - 1}
									/>
								{/each}
							</div>
							<div class="flex items-center gap-4">
								<CustomButton
									variant="outline"
									on:click={handlePrev}
									disabled={currentScreen === 0}
									class="h-12 w-12 rounded-full p-0"
								>
									<ChevronLeft class="h-6 w-6" />
								</CustomButton>
								<CustomButton
									variant="outline"
									on:click={handleNext}
									class="h-12 w-12 rounded-full p-0"
								>
									<ChevronRight class="h-6 w-6" />
								</CustomButton>
							</div>
						</div>
					</div>
				{:else}
					<!-- Welcome Screen -->
					<div class="flex flex-1 flex-col items-center px-6 pt-12">
						<div class="relative mb-8 w-full">
							<img
								src={screens[currentScreen].image || '/placeholder.svg'}
								alt="Welcome"
								width={500}
								height={500}
								class="h-auto w-full"
							/>
						</div>
						<h1 class="mb-2 text-center text-2xl font-semibold text-black">
							{screens[currentScreen].title}{' '}
							<span class="text-blue-500">{screens[currentScreen].highlightedText}</span>
						</h1>
						<p class="mb-8 text-center text-gray-500">{screens[currentScreen].description}</p>
						<a href="/signup">
							<CustomButton class="mb-4 w-full" size="lg">Let's Get Started</CustomButton>
						</a>
						<div class="flex items-center gap-2 text-sm">
							<span class="text-gray-500">Already have an account?</span>
							<button class="font-medium text-blue-500 hover:text-blue-600">
								<a href="/signin">Login</a>
							</button>
						</div>
					</div>
				{/if}
			</motion.div>
		{/if}
	</AnimatePresence>
</div>
