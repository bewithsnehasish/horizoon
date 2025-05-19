<script lang="ts">
	import { App } from '@capacitor/app';
	import { Capacitor } from '@capacitor/core';
	import { page } from '$app/stores';

	export let exitPaths: string[] = [];
	export let showExitConfirmationToast: (message: string) => void;

	if (Capacitor.isNativePlatform()) {
		App.addListener('backButton', () => {
			const currentPath = $page.url.pathname;
			if (exitPaths.includes(currentPath)) {
				showExitConfirmationToast('Press back again to exit');
				// Logic to handle double-back press (requires additional state)
			} else {
				history.back();
			}
		});
	}
</script>
