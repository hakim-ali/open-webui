import { error } from '@sveltejs/kit';

/** @type {import('@sveltejs/kit').Handle} */
export async function handle({ event, resolve }) {
	// Check if the route is admin-related and return 404 error
	if (event.url.pathname.startsWith('/admin')) {
		throw error(404, 'Admin functionality is disabled');
	}

	// Check if the route is admin-related API and return 404 error
	if (event.url.pathname.startsWith('/api/v1/functions') ||
		event.url.pathname.startsWith('/openai') || 
		event.url.pathname.startsWith('/api/v1/pipelines')) {
		throw error(404, 'Admin functionality is disabled');
	}

	return resolve(event);
}
