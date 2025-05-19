import { json, type RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ request }) => {
	const { email, password } = await request.json();

	// Mock validation (replace with real backend logic)
	if (email === 'user@example.com' && password === 'password') {
		return json({ token: 'mock-jwt-token', role: 'user', email }, { status: 200 });
	} else if (email === 'admin@example.com' && password === 'password') {
		return json({ token: 'mock-jwt-token', role: 'admin', email }, { status: 200 });
	} else {
		return json({ error: 'Invalid credentials' }, { status: 401 });
	}
};
