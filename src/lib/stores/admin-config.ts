import { writable, derived } from 'svelte/store';
import type { AdminPanelConfig, AdminFeatures } from '$lib/apis/admin-config';
import { getAdminPanelConfig, getAdminFeatures } from '$lib/apis/admin-config';
import { user } from './index';

interface AdminConfigState {
	config: AdminPanelConfig | null;
	features: AdminFeatures | null;
	loading: boolean;
	error: string | null;
}

function createAdminConfigStore() {
	const { subscribe, set, update } = writable<AdminConfigState>({
		config: null,
		features: null,
		loading: false,
		error: null
	});

	return {
		subscribe,
		set,
		update,
		
		// Load admin configuration
		async loadConfig() {
			update(state => ({ ...state, loading: true, error: null }));
			
			try {
				const currentUser = user.get();
				if (!currentUser?.token) {
					throw new Error('No authentication token available');
				}
				
				const [config, features] = await Promise.all([
					getAdminPanelConfig(currentUser.token),
					getAdminFeatures(currentUser.token)
				]);
				
				update(state => ({
					...state,
					config,
					features,
					loading: false,
					error: null
				}));
			} catch (error) {
				update(state => ({
					...state,
					loading: false,
					error: error instanceof Error ? error.message : 'Failed to load admin configuration'
				}));
			}
		},
		
		// Reset store
		reset() {
			set({
				config: null,
				features: null,
				loading: false,
				error: null
			});
		}
	};
}

export const adminConfig = createAdminConfigStore();

// Derived stores for easy access to specific configuration values
export const adminFeatures = derived(adminConfig, ($adminConfig) => $adminConfig.features);
export const adminConfigData = derived(adminConfig, ($adminConfig) => $adminConfig.config);
export const adminConfigLoading = derived(adminConfig, ($adminConfig) => $adminConfig.loading);
export const adminConfigError = derived(adminConfig, ($adminConfig) => $adminConfig.error);

// Helper functions for checking feature availability
export const isFeatureEnabled = (featureName: keyof AdminFeatures): boolean => {
	const features = adminFeatures.get();
	return features?.[featureName] ?? false;
};

export const isTabEnabled = (tabName: keyof AdminFeatures): boolean => {
	return isFeatureEnabled(tabName);
};
