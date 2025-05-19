import { writable } from 'svelte/store';
import type { User } from '$lib/types/user';

// Initialize authStore with data from localStorage (if available)
const initialUser =
	typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('authUser') || 'null') : null;

export const authStore = writable<User | null>(initialUser);

// Subscribe to authStore changes and save to localStorage
authStore.subscribe((user) => {
	if (typeof window !== 'undefined') {
		localStorage.setItem('authUser', JSON.stringify(user));
	}
});

export function getAuthToken(): string | null {
	return localStorage.getItem('authToken');
}

// Login function
export async function login(email: string, password: string) {
	const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
	const response = await fetch(`${API_BASE_URL}/authentication/login/`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ email, password })
	});
	const data = await response.json();
	if (response.ok) {
		localStorage.setItem('authToken', data.token);
		localStorage.setItem('userRole', JSON.stringify(data.user_type));
		authStore.set({
			token: data.token,
			role: data.user_type === 'Client' ? 'user' : 'admin',
			email
		});
	}
	return { success: response.ok, error: data.error };
}

// Signup function
export async function signup(username: string, email: string, password: string) {
	const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
	const response = await fetch(`${API_BASE_URL}/authentication/register/`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ username, email, password })
	});
	const data = await response.json();
	if (response.ok) {
		localStorage.setItem('authToken', data.token);
		localStorage.setItem('userRole', JSON.stringify(data.user_type));
		authStore.set({
			token: data.token,
			role: data.user_type === 'Client' ? 'user' : 'admin',
			email
		});
	}
	return { success: response.ok, error: data.error };
}

// Logout function
export function logout() {
	localStorage.removeItem('authToken');
	authStore.set(null);
}
