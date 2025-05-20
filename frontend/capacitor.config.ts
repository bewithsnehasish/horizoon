import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
	appId: 'com.horizoon.app',
	appName: 'Horizoon',
	webDir: 'build',
	android: {
		loggingBehavior: 'production' // Minimize logs
	}
};

export default config;
