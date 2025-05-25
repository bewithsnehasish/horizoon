import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { browser } from '$app/environment';

const firebaseConfig = {
	apiKey: 'AIzaSyCICGua0HV97vVoeNbQHZFYXpNZfcv9XC8',
	authDomain: 'horizoon-wheels.firebasestorage.app',
	projectId: 'horizoon-wheels',
	storageBucket: 'horizoon-wheels.firebasestorage.app',
	messagingSenderId: '123456789',
	appId: '1:14943130044:android:2a6d832b8f8bcd0fa0dbb9'
};

// Initialize Firebase only in browser
let app: any = null;
let auth: any = null;

if (browser) {
	app = initializeApp(firebaseConfig);
	auth = getAuth(app);
}

export { auth };
