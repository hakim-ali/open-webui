<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';

	import { WEBUI_NAME, mobile, showSidebar, user } from '$lib/stores';
	import MenuLines from '$lib/components/icons/MenuLines.svelte';
	import { page } from '$app/stores';
	import MaterialIcon from '$lib/components/common/MaterialIcon.svelte';
	import GovKno from '$lib/components/icons/GovKno.svelte';

	const i18n = getContext('i18n');

	let loaded = false;

	onMount(async () => {
		// Add any authentication/authorization logic here if needed
		loaded = true;
	});
</script>

<svelte:head>
	<title>
		{$i18n?.t('Knowledge Repository') || 'Knowledge Repository'} • {$WEBUI_NAME}
	</title>
</svelte:head>

{#if loaded}
	<div
		class="flex flex-col w-full h-screen max-h-[100dvh] transition-width duration-200 ease-in-out {$showSidebar
			? 'md:max-w-[calc(100%-300px)]'
			: 'md:max-w-[calc(100%-80px)]'} max-w-full"
	>
		<nav class="px-2.5 pt-2 backdrop-blur-xl drag-region">
			<div class="flex justify-between items-center gap-1">
				<div class="{!$mobile ? 'md:hidden' : ''} self-center flex flex-none items-center">
					<button
						class="flex items-center justify-center rounded-lg size-10 hover:bg-gray-100 dark:hover:bg-gray-850 transition"
						aria-label="Toggle Sidebar"
						on:click={() => showSidebar.set(!$showSidebar)}
					>
						<MaterialIcon name="menu" className="w-6 h-6" />
					</button>
				</div>

				<div
					class="mt-0.5 {$mobile
						? 'me-4'
						: 'ms-6'} gap-2 item-center flex flex-row py-1 dark:bg-transparent"
				>
					<div class="flex md:self-center text-lg font-medium px-0.5 mt-1">
						<GovKno />
					</div>
					<div class="flex md:self-center text-lg font-medium px-0.5">
						{$i18n?.t('Gov Government Repository') || 'Gov Government Repository'}
					</div>
				</div>

				<div />
			</div>
		</nav>
		<div class="h-[calc(100vh-2rem)] max-h-[100dvh] dark:bg-transparent">
			<div class="p-[16px] {$mobile ? '' : 'px-8'} flex-1 max-h-full overflow-y-auto">
				<slot />
			</div>
		</div>
	</div>
{/if}
