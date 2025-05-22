import type { LayoutLoad } from './$types';
import { authStore } from '$lib/stores/auth';

export const prerender = false;
export const load: LayoutLoad = async () => {
	// Check localStorage directly for user data
	let user: { email: string; role: string; token: string } | null = null;
	if (typeof window !== 'undefined') {
		try {
			const userData = localStorage.getItem('authUser');
			if (userData) {
				user = JSON.parse(userData);
				user.role = 'user'; // Ensure role is "user"
			}
		} catch (e) {
			console.error('Failed to parse user data', e);
		}
	}

	authStore.set(user);

	return { user };
};
