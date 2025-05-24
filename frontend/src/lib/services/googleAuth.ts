import { FirebaseAuthentication } from '@capacitor-firebase/authentication';
import { Capacitor } from '@capacitor/core';
import { signInWithCredential, GoogleAuthProvider } from 'firebase/auth';
import { auth } from '$lib/firebase';

export interface GoogleAuthResult {
	success: boolean;
	user?: any;
	error?: string;
	idToken?: string;
}

export const signInWithGoogle = async (): Promise<GoogleAuthResult> => {
	try {
		console.log('Starting Google Sign-In...');

		if (Capacitor.isNativePlatform()) {
			console.log('Using native Google Sign-In');

			// Use Capacitor Firebase Authentication plugin for native
			const result = await FirebaseAuthentication.signInWithGoogle();

			if (result.user && result.credential?.idToken) {
				// Also sign in to Firebase JS SDK for consistency
				const credential = GoogleAuthProvider.credential(result.credential.idToken);
				const firebaseResult = await signInWithCredential(auth, credential);

				return {
					success: true,
					user: firebaseResult.user,
					idToken: result.credential.idToken
				};
			} else {
				throw new Error('Failed to get user data or ID token');
			}
		} else {
			console.log('Using web Google Sign-In');

			// Use Firebase Auth directly for web
			const result = await FirebaseAuthentication.signInWithGoogle();

			if (result.user && result.credential?.idToken) {
				return {
					success: true,
					user: result.user,
					idToken: result.credential.idToken
				};
			} else {
				throw new Error('Failed to get user data or ID token');
			}
		}
	} catch (error: any) {
		console.error('Google Sign-In Error:', error);

		// Handle specific error cases
		if (error.code === 'auth/popup-closed-by-user') {
			return {
				success: false,
				error: 'Sign-in was cancelled'
			};
		} else if (error.code === 'auth/network-request-failed') {
			return {
				success: false,
				error: 'Network error. Please check your connection.'
			};
		}

		return {
			success: false,
			error: error.message || 'Google authentication failed'
		};
	}
};

export const signOutGoogle = async (): Promise<void> => {
	try {
		await FirebaseAuthentication.signOut();
	} catch (error) {
		console.error('Sign out error:', error);
	}
};
