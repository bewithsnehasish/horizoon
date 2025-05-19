import type { LayoutLoad } from './$types';
import { authStore } from '$lib/stores/auth';
import '../app.css';
import { get } from 'svelte/store';
import { redirect } from '@sveltejs/kit';

export const load: LayoutLoad = async ({ url }) => {
	const user = get(authStore);
	const isAuthenticated = !!user;
	const isAdmin = user?.role === 'admin';
	const path = url.pathname;

	// Debug: Log the user and authentication state
	console.log('Layout Load - User:', user);
	console.log('Layout Load - isAuthenticated:', isAuthenticated);
	console.log('Layout Load - Path:', path);

	// Allow unauthenticated users to access /intro, /signin, and /signup
	if (!isAuthenticated && !['/intro', '/signin', '/signup'].includes(path)) {
		console.log('Redirecting unauthenticated user to /intro');
		throw redirect(307, '/intro');
	}

	// Redirect authenticated users away from /intro, /signin, and /signup
	if (isAuthenticated && ['/intro', '/signin', '/signup'].includes(path)) {
		console.log('Redirecting authenticated user to home/adminhome');
		throw redirect(307, user.role === 'admin' ? '/adminhome' : '/home');
	}

	// Protect routes that require authentication (e.g., /completeprofile)
	if (!isAuthenticated && path === '/completeprofile') {
		console.log('Redirecting unauthenticated user from /completeprofile to /intro');
		throw redirect(307, '/intro');
	}

	// Protect admin routes
	if (path.startsWith('/admin') && !isAdmin) {
		console.log('Redirecting non-admin user from admin route to /home');
		throw redirect(307, '/home');
	}

	return { user };
};
