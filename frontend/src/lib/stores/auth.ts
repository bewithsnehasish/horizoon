import { writable } from 'svelte/store';
<<<<<<< HEAD
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
=======

type User = {
	token: string;
	role: string;
	email: string;
};

// Helper function for safe localStorage access
const getLocalStorageItem = (key: string): string | null => {
	if (typeof window !== 'undefined') {
		return localStorage.getItem(key);
	}
	return null;
};

// Initialize authStore with data from localStorage
const initialUser = ((): User | null => {
	const authUser = getLocalStorageItem('authUser');
	const token = getLocalStorageItem('authToken');

	if (authUser && token) {
		try {
			console.log('Initial user - authUser:', authUser);
			console.log('Initial user - token:', token);
			return {
				...JSON.parse(authUser),
				token,
				role: 'user'
			};
		} catch (e) {
			console.error('Failed to parse authUser:', e);
			return null;
		}
	}
	return null;
})();

export const authStore = writable<User | null>(initialUser);

// Subscribe to authStore changes and update localStorage
authStore.subscribe((user) => {
	if (typeof window !== 'undefined') {
		console.log('authStore updated - User:', user);
		if (user) {
			localStorage.setItem('authUser', JSON.stringify({ email: user.email, role: user.role }));
			if (user.token) {
				localStorage.setItem('authToken', user.token);
				console.log('Setting authToken:', user.token);
			} else {
				console.warn('authToken is undefined, not setting in localStorage');
			}
		} else {
			console.log('Clearing localStorage because user is null');
			localStorage.removeItem('authUser');
			localStorage.removeItem('authToken');
		}
	}
});
>>>>>>> 99030e754e9ac06eb63021760836ffc9ee173051

export function getAuthToken(): string | null {
	const token = getLocalStorageItem('authToken');
	console.log('getAuthToken called - Token:', token);
	return token;
}

// Login function
export async function login(email: string, password: string) {
	try {
		const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
		const response = await fetch(`${API_BASE_URL}/authentication/login/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ email, password })
		});

		if (!response.ok) {
			const errorData = await response.json();
			return { success: false, error: errorData.error || 'Login failed' };
		}

		const data = await response.json();
		console.log('Login response:', data);

		if (!data.token) {
			console.error('Login response missing token:', data);
			return { success: false, error: 'Invalid response from server: missing token' };
		}

		const user: User = {
			token: data.token,
			role: 'user',
			email
		};

		authStore.set(user);
		return { success: true, error: null };
	} catch (error) {
		console.error('Login network error:', error);
		return { success: false, error: 'Network error' };
	}
}

// Signup function
export async function signup(username: string, email: string, password: string) {
	try {
		const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
		const response = await fetch(`${API_BASE_URL}/authentication/register/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ username, email, password })
		});

		if (!response.ok) {
			const errorData = await response.json();
			return { success: false, error: errorData.error || 'Registration failed' };
		}

		const data = await response.json();
		console.log('Signup response:', data);

		if (!data.token) {
			console.error('Signup response missing token:', data);
			return { success: false, error: 'Invalid response from server: missing token' };
		}

		const user: User = {
			token: data.token,
			role: 'user',
			email
		};

		authStore.set(user);
		return { success: true, error: null };
	} catch (error) {
		console.error('Signup network error:', error);
		return { success: false, error: 'Network error' };
	}
}

// Logout function
export function logout() {
	authStore.set(null);
}
