<script lang="ts">
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