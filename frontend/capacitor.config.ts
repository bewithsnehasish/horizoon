import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
	appId: 'com.horizoon.app',
	appName: 'Horizoon',
	webDir: 'build',
	android: {
		loggingBehavior: 'production' // Minimize logs
	},
	// Add this for better web compatibility
	plugins: {
		Geolocation: {
			permissions: {
				location: 'always'
			}
		},
		FirebaseAuthentication: {
			skipNativeAuth: false,
			providers: ['google.com']
		},
		GoogleAuth: {
			scopes: ['profile', 'email'],
			serverClientId: 'YOUR_GOOGLE_SERVER_CLIENT_ID', // From Firebase
			forceCodeForRefreshToken: true
		}
	}
};

export default config;
