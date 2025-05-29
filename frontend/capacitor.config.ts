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
		CapacitorAssets: {
			iconPath: 'static/logo.png',

			// Skip splash screen generation
			splashPath: undefined,

			// Optional: Disable splash screen generation completely
			android: {
				splashPath: undefined
			},
			ios: {
				splashPath: undefined
			}
		},

		// Disable splash screen plugin if you have it
		SplashScreen: {
			launchShowDuration: 0,
			launchAutoHide: true,
			backgroundColor: '#000000',
			androidSplashResourceName: 'splash',
			androidScaleType: 'CENTER_CROP',
			showSpinner: false,
			androidSpinnerStyle: 'large',
			iosSpinnerStyle: 'small',
			spinnerColor: '#999999',
			splashFullScreen: true,
			splashImmersive: true,
			layoutName: 'launch_splash',
			useDialog: true
		},

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
