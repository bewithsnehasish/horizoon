export interface User {
	token: string;
	role: 'user' | 'admin';
	email: string;
}
