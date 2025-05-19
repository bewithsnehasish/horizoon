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

	// Allow unauthenticated users to access /intro, /signin, and /signup
	if (!isAuthenticated && !['/intro', '/signin', '/signup'].includes(path)) {
		throw redirect(307, '/intro');
	}

	// Redirect authenticated users away from /intro, /signin, and /signup
	if (isAuthenticated && ['/intro', '/signin', '/signup'].includes(path)) {
		throw redirect(307, user.role === 'admin' ? '/adminhome' : '/home');
	}

	// Protect admin routes
	if (path.startsWith('/admin') && !isAdmin) {
		throw redirect(307, '/home');
	}

	return { user };
};
