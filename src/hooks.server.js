import { redirect } from '@sveltejs/kit';

/** @type {import('@sveltejs/kit').Handle} */
export async function handle({ event, resolve }) {
	// Check if the route is admin-related and redirect to root
	if (event.url.pathname.startsWith('/admin')) {
		throw redirect(302, '/');
	}

	// Check if the route is admin-related API and redirect to root
	if (event.url.pathname.startsWith('/api/v1/functions') || 
		event.url.pathname.startsWith('/api/v1/pipelines') ||
		event.url.pathname.startsWith('/api/v1/evaluations')) {
		throw redirect(302, '/');
	}

	return resolve(event);
}
