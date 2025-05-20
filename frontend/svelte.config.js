import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const config = {
	preprocess: vitePreprocess(),
	onwarn: (warning, handler) => {
		if (warning.code.startsWith('a11y-')) {
			return;
		}
		handler(warning);
	},
	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: null,
			precompress: false,
			strict: false
		})
	}
};

export default config;
