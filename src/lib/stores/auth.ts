import { writable } from 'svelte/store';
import type { User } from '$lib/types/user';

export const authStore = writable<User | null>(null);

// Login function
export async function login(email: string, password: string) {
	const response = await fetch('/api/login', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ email, password })
	});
	const data = await response.json();
	if (response.ok) {
		authStore.set({ token: data.token, role: data.role, email });
	}
	return { success: response.ok, error: data.error };
}

// Signup function
export async function signup(email: string, password: string) {
	const response = await fetch('/api/signup', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ email, password })
	});
	const data = await response.json();
	if (response.ok) {
		authStore.set({ token: data.token, role: data.role, email });
	}
	return { success: response.ok, error: data.error };
}

// Logout function
export function logout() {
	authStore.set(null);
}
