import { writable } from 'svelte/store';
import { signInWithGoogle, signOutGoogle } from '$lib/services/googleAuth';

type User = {
	token: string;
	role: string;
	email: string;
	name?: string;
	avatar?: string;
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
			localStorage.setItem(
				'authUser',
				JSON.stringify({
					email: user.email,
					role: user.role,
					name: user.name,
					avatar: user.avatar
				})
			);
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

export function getAuthToken(): string | null {
	const token = getLocalStorageItem('authToken');
	console.log('getAuthToken called - Token:', token);
	return token;
}

// Regular login function
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

// Google login function
export async function loginWithGoogle() {
	try {
		console.log('Starting Google login process...');

		// Get Google ID token from Firebase
		const googleResult = await signInWithGoogle();

		if (!googleResult.success || !googleResult.idToken) {
			return {
				success: false,
				error: googleResult.error || 'Failed to authenticate with Google'
			};
		}

		console.log('Google authentication successful, sending to backend...');

		// Send Google ID token to your backend
		const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
		const response = await fetch(`${API_BASE_URL}/authentication/google-login/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				id_token: googleResult.idToken,
				email: googleResult.user?.email,
				username: googleResult.user?.displayName || googleResult.user?.email?.split('@')[0]
			})
		});

		if (!response.ok) {
			const errorData = await response.json();
			return { success: false, error: errorData.error || 'Backend authentication failed' };
		}

		const data = await response.json();
		console.log('Backend Google login response:', data);

		if (!data.token) {
			console.error('Google login response missing token:', data);
			return { success: false, error: 'Invalid response from server: missing token' };
		}

		// Create user object with Google data
		const user: User = {
			token: data.token, // This is your backend's authToken
			role: 'user',
			email: googleResult.user?.email || '',
			name: googleResult.user?.displayName || googleResult.user?.email?.split('@')[0],
			avatar: googleResult.user?.photoURL
		};

		authStore.set(user);
		return { success: true, error: null, message: data.message };
	} catch (error: any) {
		console.error('Google login error:', error);
		return {
			success: false,
			error: error.message || 'Google authentication failed'
		};
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

// Enhanced logout function
export async function logout() {
	try {
		// Sign out from Google if signed in
		await signOutGoogle();
	} catch (error) {
		console.error('Error signing out from Google:', error);
	} finally {
		// Always clear the auth store
		authStore.set(null);
	}
}
