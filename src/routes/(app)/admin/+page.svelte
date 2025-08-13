<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { config, user } from '$lib/stores';

	onMount(() => {
		// Check if user is admin and admin functionality is enabled
		if ($user?.role !== 'admin' || !($config?.features?.enable_admin_functionality ?? true)) {
			goto('/');
		} else {
			goto('/admin/users');
		}
	});
</script>
