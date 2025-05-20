import { writable } from 'svelte/store';
import { browser } from '$app/environment';

type User = {
    token: string;
    role: 'user' | 'admin';
    email: string;
};

// Initialize with null on server, or with localStorage value on client
const initialUser = browser ? JSON.parse(localStorage.getItem('authUser') || 'null') : null;

export const authStore = writable<User | null>(initialUser);

// Only subscribe to changes on client
if (browser) {
    authStore.subscribe((user) => {
        if (user) {
            localStorage.setItem('authUser', JSON.stringify(user));
        } else {
            localStorage.removeItem('authUser');
        }
    });
}

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
