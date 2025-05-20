import type { LayoutLoad } from './$types';
import { authStore } from '$lib/stores/auth';
import '../app.css';
import { get } from 'svelte/store';
import { redirect } from '@sveltejs/kit';

export const load: LayoutLoad = async ({ url, depends }) => {
    // This ensures client-side only behavior
    depends('app:auth');
    
    // Only run auth logic on client
    if (typeof window === 'undefined') {
        return {};
    }

    // Wait for store to sync with localStorage
    await new Promise(resolve => setTimeout(resolve, 50));
    
    const user = get(authStore);
    const isAuthenticated = !!user;
    const path = url.pathname;

    console.log('Auth check - User:', user, 'Path:', path);

    // Public routes that don't require auth
    const publicRoutes = ['/intro', '/signin', '/signup'];
    
    if (!isAuthenticated && !publicRoutes.includes(path)) {
        throw redirect(307, '/intro');
    }

    if (isAuthenticated && publicRoutes.includes(path)) {
        throw redirect(307, user?.role === 'admin' ? '/adminhome' : '/home');
    }

    return { user };
};

export const ssr = false;  // Disable SSR for this layout
export const csr = true;   // Ensure CSR is enabled