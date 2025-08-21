import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),
	kit: {
		adapter: adapter({
			// Generate a single index.html file for SPA behavior
			fallback: 'index.html',
			// Output directory (default is 'build')
			pages: 'build',
			assets: 'build'
		})
		// Remove the prerender config - it's not needed for SPA mode
	}
};

export default config;