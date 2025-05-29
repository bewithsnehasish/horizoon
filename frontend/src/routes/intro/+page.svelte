<!-- src/routes/intro/+page.svelte -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { Motion } from 'svelte-motion';
	import { Car, ChevronRight, Star, Users, Shield } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import { goto } from '$app/navigation';
	import { logout } from '$lib/stores/auth';

	let showSplash = true;
	let showContent = false;

	onMount(() => {
		logout();

		const timer = setTimeout(() => {
			showSplash = false;
			showContent = true;
		}, 2000);

		return () => clearTimeout(timer);
	});

	const handleGetStarted = () => {
		goto('/signup');
	};

	const handleSignIn = () => {
		goto('/signin');
	};
</script>

<svelte:head>
	<title>Horizoon - Premium Vehicle Rental</title>
	<meta
		name="description"
		content="Your journey, our wheels - Premium vehicle rental made simple"
	/>
</svelte:head>

<!-- Splash Screen -->
{#if showSplash}
	<Motion
		initial={{ opacity: 0, scale: 0.8 }}
		animate={{ opacity: 1, scale: 1 }}
		exit={{ opacity: 0, scale: 1.2 }}
		transition={{ duration: 0.8 }}
		let:motion
	>
		<div use:motion class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950">
			<div class="text-center">
				<div class="relative mb-4">
					<div class="relative mx-auto h-80 w-80 p-1">
						<div class="flex h-full w-full items-center justify-center rounded-full bg-slate-950">
							<img src="/fullLogo.svg" alt="Premium Vehicle" class="h-full w-full object-cover" />
						</div>
					</div>
				</div>
			</div>
		</div>
	</Motion>
{/if}

<!-- Main Content -->
{#if showContent}
	<div class="relative overflow-hidden">
		<!-- Background with Vehicle Wallpaper -->
		<div class="absolute inset-0">
			<img
				src="https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?q=80&w=1920&auto=format&fit=crop"
				alt="Premium Vehicle"
				class="h-full w-full object-cover"
			/>
			<!-- Dark Overlay -->
			<div
				class="absolute inset-0 bg-gradient-to-r from-slate-950/95 via-slate-950/80 to-slate-950/40"
			></div>
		</div>

		<!-- Content -->
		<div class="relative z-10 flex min-h-screen items-center">
			<div class="mx-auto max-w-7xl px-6 py-20">
				<div class="grid items-center gap-12 lg:grid-cols-2">
					<!-- Left Side - Text Content -->
					<Motion
						initial={{ x: -50, opacity: 0 }}
						animate={{ x: 0, opacity: 1 }}
						transition={{ duration: 0.8, delay: 0.2 }}
						let:motion
					>
						<div use:motion class="space-y-8">
							<!-- Brand & Logo -->
							<div class="mb-6 flex items-center gap-3">
								<div class="h-12 w-12 rounded-full bg-gradient-to-r from-teal-500 to-cyan-600 p-1">
									<div
										class="flex h-full w-full items-center justify-center rounded-full bg-slate-950"
									>
										<img src="/logo.svg" alt="Horizoon" class="h-full w-full object-cover" />
									</div>
								</div>
								<span
									class="bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-2xl font-bold text-transparent"
								>
									Horizoon
								</span>
							</div>

							<!-- Main Heading -->
							<div class="space-y-4">
								<h1 class="text-4xl font-bold leading-tight text-white md:text-6xl">
									Your Journey,
									<br />
									<span
										class="bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-transparent"
									>
										Our Wheels
									</span>
								</h1>
								<p class="max-w-lg text-xl leading-relaxed text-slate-300">
									Experience premium vehicle rental with instant booking, 24/7 support, and a fleet
									of luxury cars at your fingertips.
								</p>
							</div>

							<!-- Stats -->
							<div class="flex gap-8">
								<div class="text-center">
									<div class="mb-1 flex items-center justify-center gap-1">
										<span class="text-2xl font-bold text-teal-400">4.9</span>
										<Star class="h-5 w-5 fill-current text-yellow-400" />
									</div>
									<p class="text-sm text-slate-400">App Rating</p>
								</div>
								<div class="text-center">
									<div class="mb-1 text-2xl font-bold text-teal-400">50K+</div>
									<p class="text-sm text-slate-400">Happy Users</p>
								</div>
								<div class="text-center">
									<div class="mb-1 text-2xl font-bold text-teal-400">500+</div>
									<p class="text-sm text-slate-400">Premium Cars</p>
								</div>
							</div>

							<!-- Features -->
							<div class="space-y-3">
								<div class="flex items-center gap-3">
									<div class="h-2 w-2 rounded-full bg-teal-400"></div>
									<span class="text-slate-300">Instant booking & verification</span>
								</div>
								<div class="flex items-center gap-3">
									<div class="h-2 w-2 rounded-full bg-cyan-400"></div>
									<span class="text-slate-300">Premium fleet with insurance</span>
								</div>
								<div class="flex items-center gap-3">
									<div class="h-2 w-2 rounded-full bg-teal-400"></div>
									<span class="text-slate-300">24/7 customer support</span>
								</div>
							</div>

							<!-- CTA Buttons -->
							<div class="space-y-4 pt-4">
								<Button
									size="lg"
									onclick={handleGetStarted}
									class="w-full transform rounded-2xl bg-gradient-to-r from-teal-500 to-cyan-600 px-8 py-4 font-semibold text-white shadow-xl transition-all duration-300 hover:scale-105 hover:from-teal-600 hover:to-cyan-700 hover:shadow-2xl sm:w-auto"
								>
									<span class="flex items-center gap-2">
										Get Started
										<ChevronRight class="h-5 w-5" />
									</span>
								</Button>

								<div class="flex items-center gap-2">
									<span class="text-slate-400">Already have an account?</span>
									<button
										onclick={handleSignIn}
										class="font-semibold text-teal-400 transition-colors duration-200 hover:text-teal-300 hover:underline"
									>
										Sign In
									</button>
								</div>
							</div>
						</div>
					</Motion>

					<!-- Right Side - Car Gradient Visual -->
					<Motion
						initial={{ x: 50, opacity: 0, scale: 0.9 }}
						animate={{ x: 0, opacity: 1, scale: 1 }}
						transition={{ duration: 1, delay: 0.4 }}
						let:motion
					>
						<div use:motion class="relative hidden lg:block">
							<!-- Gradient Car Silhouette -->
							<div class="relative">
								<!-- Glow Effect -->
								<div
									class="absolute inset-0 rounded-full bg-gradient-to-r from-teal-500/30 to-cyan-500/30 blur-3xl"
								></div>

								<!-- Car SVG with Gradient -->
								<div class="relative">
									<svg viewBox="0 0 400 200" class="mx-auto w-full max-w-md">
										<defs>
											<linearGradient id="carGradient" x1="0%" y1="0%" x2="100%" y2="100%">
												<stop offset="0%" style="stop-color:#14B8A6" />
												<stop offset="50%" style="stop-color:#06B6D4" />
												<stop offset="100%" style="stop-color:#0891B2" />
											</linearGradient>
											<filter id="glow">
												<feGaussianBlur stdDeviation="3" result="coloredBlur" />
												<feMerge>
													<feMergeNode in="coloredBlur" />
													<feMergeNode in="SourceGraphic" />
												</feMerge>
											</filter>
										</defs>

										<!-- Car Body -->
										<path
											d="M80 120 L100 100 L140 95 L260 95 L300 100 L320 120 L320 140 L310 145 L300 140 L100 140 L90 145 L80 140 Z"
											fill="url(#carGradient)"
											filter="url(#glow)"
											opacity="0.9"
										/>

										<!-- Car Wheels -->
										<circle cx="120" cy="140" r="15" fill="url(#carGradient)" filter="url(#glow)" />
										<circle cx="280" cy="140" r="15" fill="url(#carGradient)" filter="url(#glow)" />

										<!-- Car Windows -->
										<path
											d="M110 120 L125 105 L140 100 L260 100 L275 105 L290 120 L280 115 L120 115 Z"
											fill="rgba(148, 163, 184, 0.3)"
											opacity="0.8"
										/>
									</svg>
								</div>

								<!-- Floating Elements -->
								<div
									class="absolute right-10 top-10 h-3 w-3 animate-bounce rounded-full bg-teal-400 delay-300"
								></div>
								<div
									class="absolute bottom-20 left-10 h-2 w-2 animate-bounce rounded-full bg-cyan-400 delay-700"
								></div>
								<div
									class="absolute right-0 top-1/2 h-4 w-4 animate-pulse rounded-full bg-gradient-to-r from-teal-400 to-cyan-400"
								></div>
							</div>
						</div>
					</Motion>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	/* Enhanced animations */
	@keyframes float {
		0%,
		100% {
			transform: translateY(0px);
		}
		50% {
			transform: translateY(-10px);
		}
	}

	:global(.animate-float) {
		animation: float 3s ease-in-out infinite;
	}

	/* Custom scrollbar */
	:global(::-webkit-scrollbar) {
		width: 6px;
	}

	:global(::-webkit-scrollbar-track) {
		background: #1e293b;
	}

	:global(::-webkit-scrollbar-thumb) {
		background: linear-gradient(to bottom, #14b8a6, #06b6d4);
		border-radius: 3px;
	}
</style>
