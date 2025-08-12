import { goto } from '$app/navigation';
import { config } from '$lib/stores';
import { get } from 'svelte/store';

/**
 * Route guard to block admin routes when admin functionality is disabled
 */
export function checkAdminRoute(pathname: string): boolean {
	const currentConfig = get(config);
	const adminEnabled = currentConfig?.features?.enable_admin_functionality ?? true;
	
	// If admin is enabled, allow all routes
	if (adminEnabled) {
		return true;
	}
	
	// Block admin routes
	if (pathname.startsWith('/admin')) {
		goto('/');
		return false;
	}
	
	// Block admin API routes (these should be handled by backend, but just in case)
	if (pathname.startsWith('/api/v1/functions') ||
		pathname.startsWith('/openai') || 
		pathname.startsWith('/api/v1/pipelines') ||
		pathname.startsWith('/api/v1/evaluations')) {
		goto('/');
		return false;
	}
	
	return true;
}

/**
 * Check if current user can access admin routes
 */
export function canAccessAdmin(userRole: string | undefined): boolean {
	const currentConfig = get(config);
	const adminEnabled = currentConfig?.features?.enable_admin_functionality ?? true;
	
	return adminEnabled && userRole === 'admin';
}
