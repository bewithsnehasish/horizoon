
// this file is generated — do not edit it


/// <reference types="@sveltejs/kit" />

/**
 * Environment variables [loaded by Vite](https://vitejs.dev/guide/env-and-mode.html#env-files) from `.env` files and `process.env`. Like [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), this module cannot be imported into client-side code. This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured).
 * 
 * _Unlike_ [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), the values exported from this module are statically injected into your bundle at build time, enabling optimisations like dead code elimination.
 * 
 * ```ts
 * import { API_KEY } from '$env/static/private';
 * ```
 * 
 * Note that all environment variables referenced in your code should be declared (for example in an `.env` file), even if they don't have a value until the app is deployed:
 * 
 * ```
 * MY_FEATURE_FLAG=""
 * ```
 * 
 * You can override `.env` values from the command line like so:
 * 
 * ```bash
 * MY_FEATURE_FLAG="enabled" npm run dev
 * ```
 */
declare module '$env/static/private' {
	export const VITE_API_BASE_URL: string;
	export const PYENV_ROOT: string;
	export const ZSH_CACHE_DIR: string;
	export const LOGNAME: string;
	export const I3SOCK: string;
	export const STARSHIP_CONFIG: string;
	export const COLORTERM: string;
	export const DBUS_SESSION_BUS_ADDRESS: string;
	export const TERM: string;
	export const PWD: string;
	export const XDG_SESSION_TYPE: string;
	export const QT_QPA_PLATFORMTHEME: string;
	export const KITTY_INSTALLATION_DIR: string;
	export const NVIM: string;
	export const KITTY_PUBLIC_KEY: string;
	export const XDG_RUNTIME_DIR: string;
	export const DESKTOP_STARTUP_ID: string;
	export const DEBUGINFOD_URLS: string;
	export const LANG: string;
	export const PATH: string;
	export const MOTD_SHOWN: string;
	export const MASON: string;
	export const USER: string;
	export const NVM_DIR: string;
	export const SHELL: string;
	export const ZPFX: string;
	export const CAPACITOR_ANDROID_STUDIO_PATH: string;
	export const VIMRUNTIME: string;
	export const XDG_SEAT_PATH: string;
	export const XDG_CURRENT_DESKTOP: string;
	export const OLDPWD: string;
	export const STARSHIP_SESSION_KEY: string;
	export const KITTY_PID: string;
	export const NVIM_LOG_FILE: string;
	export const XDG_VTNR: string;
	export const WINDOWID: string;
	export const HOME: string;
	export const DESKTOP_SESSION: string;
	export const SHLVL: string;
	export const XDG_SESSION_ID: string;
	export const TERMINFO: string;
	export const MYVIMRC: string;
	export const BUN_INSTALL: string;
	export const STARSHIP_SHELL: string;
	export const DISPLAY: string;
	export const XDG_SESSION_DESKTOP: string;
	export const PYENV_SHELL: string;
	export const _: string;
	export const XAUTHORITY: string;
	export const MAIL: string;
	export const ANDROID_HOME: string;
	export const KITTY_WINDOW_ID: string;
	export const XDG_SESSION_PATH: string;
	export const XDG_DATA_DIRS: string;
	export const XDG_SEAT: string;
	export const PMSPEC: string;
	export const GTK_MODULES: string;
	export const XDG_SESSION_CLASS: string;
	export const NODE_ENV: string;
}

/**
 * Similar to [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private), except that it only includes environment variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`), and can therefore safely be exposed to client-side code.
 * 
 * Values are replaced statically at build time.
 * 
 * ```ts
 * import { PUBLIC_BASE_URL } from '$env/static/public';
 * ```
 */
declare module '$env/static/public' {
	
}

/**
 * This module provides access to runtime environment variables, as defined by the platform you're running on. For example if you're using [`adapter-node`](https://github.com/sveltejs/kit/tree/main/packages/adapter-node) (or running [`vite preview`](https://svelte.dev/docs/kit/cli)), this is equivalent to `process.env`. This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured).
 * 
 * This module cannot be imported into client-side code.
 * 
 * Dynamic environment variables cannot be used during prerendering.
 * 
 * ```ts
 * import { env } from '$env/dynamic/private';
 * console.log(env.DEPLOYMENT_SPECIFIC_VARIABLE);
 * ```
 * 
 * > In `dev`, `$env/dynamic` always includes environment variables from `.env`. In `prod`, this behavior will depend on your adapter.
 */
declare module '$env/dynamic/private' {
	export const env: {
		VITE_API_BASE_URL: string;
		PYENV_ROOT: string;
		ZSH_CACHE_DIR: string;
		LOGNAME: string;
		I3SOCK: string;
		STARSHIP_CONFIG: string;
		COLORTERM: string;
		DBUS_SESSION_BUS_ADDRESS: string;
		TERM: string;
		PWD: string;
		XDG_SESSION_TYPE: string;
		QT_QPA_PLATFORMTHEME: string;
		KITTY_INSTALLATION_DIR: string;
		NVIM: string;
		KITTY_PUBLIC_KEY: string;
		XDG_RUNTIME_DIR: string;
		DESKTOP_STARTUP_ID: string;
		DEBUGINFOD_URLS: string;
		LANG: string;
		PATH: string;
		MOTD_SHOWN: string;
		MASON: string;
		USER: string;
		NVM_DIR: string;
		SHELL: string;
		ZPFX: string;
		CAPACITOR_ANDROID_STUDIO_PATH: string;
		VIMRUNTIME: string;
		XDG_SEAT_PATH: string;
		XDG_CURRENT_DESKTOP: string;
		OLDPWD: string;
		STARSHIP_SESSION_KEY: string;
		KITTY_PID: string;
		NVIM_LOG_FILE: string;
		XDG_VTNR: string;
		WINDOWID: string;
		HOME: string;
		DESKTOP_SESSION: string;
		SHLVL: string;
		XDG_SESSION_ID: string;
		TERMINFO: string;
		MYVIMRC: string;
		BUN_INSTALL: string;
		STARSHIP_SHELL: string;
		DISPLAY: string;
		XDG_SESSION_DESKTOP: string;
		PYENV_SHELL: string;
		_: string;
		XAUTHORITY: string;
		MAIL: string;
		ANDROID_HOME: string;
		KITTY_WINDOW_ID: string;
		XDG_SESSION_PATH: string;
		XDG_DATA_DIRS: string;
		XDG_SEAT: string;
		PMSPEC: string;
		GTK_MODULES: string;
		XDG_SESSION_CLASS: string;
		NODE_ENV: string;
		[key: `PUBLIC_${string}`]: undefined;
		[key: `${string}`]: string | undefined;
	}
}

/**
 * Similar to [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), but only includes variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`), and can therefore safely be exposed to client-side code.
 * 
 * Note that public dynamic environment variables must all be sent from the server to the client, causing larger network requests — when possible, use `$env/static/public` instead.
 * 
 * Dynamic environment variables cannot be used during prerendering.
 * 
 * ```ts
 * import { env } from '$env/dynamic/public';
 * console.log(env.PUBLIC_DEPLOYMENT_SPECIFIC_VARIABLE);
 * ```
 */
declare module '$env/dynamic/public' {
	export const env: {
		[key: `PUBLIC_${string}`]: string | undefined;
	}
}
