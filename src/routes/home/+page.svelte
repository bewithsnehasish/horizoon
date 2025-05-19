<script lang="ts">
  import { onMount } from 'svelte';
  import { motion, AnimatePresence } from 'svelte/motion';
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
      logo: '/adhora.png',
    },
    {
      type: 'onboarding',
      image: '/image1.png',
      title: 'Getting Started With',
      highlightedText: 'Adorah',
      description:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt',
    },
    {
      type: 'onboarding',
      image: '/image2.png',
      title: 'Add to Favorites:',
      highlightedText: 'Keep Your Favorite Services Close',
      description:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt',
    },
    {
      type: 'welcome',
      image: '/image3.png',
      title: 'Your Ultimate',
      highlightedText: 'Adorah',
      description: 'Experience',
    },
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
        class="h-full w-full bg-blue-500 flex items-center justify-center"
      >
        <div class="relative w-24 h-24 rounded-full bg-white flex items-center justify-center">
          <img src={screens[0].logo || '/placeholder.svg'} alt="Adorah Logo" width={80} height={80} />
        </div>
      </motion.div>
    {:else}
      <motion.div
        key={currentScreen}
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -50 }}
        class="h-full w-full flex flex-col"
      >
        {#if currentScreen < screens.length - 1}
          <!-- Onboarding Screens -->
          <div class="flex-1 flex flex-col">
            <div class="flex justify-end p-4">
              <CustomButton variant="secondary" on:click={handleSkip} class="text-sm px-4 h-9">
                Skip
              </CustomButton>
            </div>
            <div class="flex-1 flex flex-col items-center px-6">
              <div class="relative w-full aspect-square rounded-full overflow-hidden mb-8">
                <img src={screens[currentScreen].image || '/placeholder.svg'} alt="Onboarding" class="object-cover" />
              </div>
              <h1 class="text-2xl font-semibold text-black text-center mb-2">
                {screens[currentScreen].title}{' '}
                <span class="text-blue-500">{screens[currentScreen].highlightedText}</span>
              </h1>
              <p class="text-center text-gray-500 mb-8">{screens[currentScreen].description}</p>
              <div class="flex items-center gap-4 mb-8">
                {#each screens.slice(1, -1) as _, idx}
                  <div
                    class="w-2 h-2 rounded-full"
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
                  class="w-12 h-12 p-0 rounded-full"
                >
                  <ChevronLeft class="h-6 w-6" />
                </CustomButton>
                <CustomButton variant="outline" on:click={handleNext} class="w-12 h-12 p-0 rounded-full">
                  <ChevronRight class="h-6 w-6" />
                </CustomButton>
              </div>
            </div>
          </div>
        {:else}
          <!-- Welcome Screen -->
          <div class="flex-1 flex flex-col items-center px-6 pt-12">
            <div class="relative w-full mb-8">
              <img
                src={screens[currentScreen].image || '/placeholder.svg'}
                alt="Welcome"
                width={500}
                height={500}
                class="w-full h-auto"
              />
            </div>
            <h1 class="text-2xl text-black font-semibold text-center mb-2">
              {screens[currentScreen].title}{' '}
              <span class="text-blue-500">{screens[currentScreen].highlightedText}</span>
            </h1>
            <p class="text-center text-gray-500 mb-8">{screens[currentScreen].description}</p>
            <a href="/signup">
              <CustomButton class="w-full mb-4" size="lg">Let's Get Started</CustomButton>
            </a>
            <div class="flex items-center gap-2 text-sm">
              <span class="text-gray-500">Already have an account?</span>
              <button class="text-blue-500 font-medium hover:text-blue-600">
                <a href="/signin">Login</a>
              </button>
            </div>
          </div>
        {/if}
      </motion.div>
    {/if}
  </AnimatePresence>
</div>

