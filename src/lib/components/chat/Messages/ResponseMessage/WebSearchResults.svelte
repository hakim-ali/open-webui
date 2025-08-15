<script lang="ts">
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import ChevronUp from '$lib/components/icons/ChevronUp.svelte';
	import MagnifyingGlass from '$lib/components/icons/MagnifyingGlass.svelte';
	import Collapsible from '$lib/components/common/Collapsible.svelte';
	import ExternalLinkModal from '$lib/components/common/ExternalLinkModal.svelte';
	import { getContext } from 'svelte';

	export let status = { urls: [], query: '' };
	export let state = true;

	const i18n = getContext('i18n');
	let showExternalModal = false;
	let externalUrl = '';

	function handleUrlClick(url: string) {
		externalUrl = url;
		showExternalModal = true;
	}

	function extractDomain(url: string): string {
		try {
			const urlObj = new URL(url);
			return urlObj.hostname.replace('www.', '');
		} catch {
			return url;
		}
	}

	function getFaviconUrl(url: string): string {
		try {
			const urlObj = new URL(url);
			return `https://www.google.com/s2/favicons?domain=${urlObj.hostname}&sz=64`;
		} catch {
			return '';
		}
	}
</script>

<Collapsible bind:open={state} className="w-full space-y-1">
	<div
		class="flex items-center gap-2 text-gray-500 dark:text-gray-200 hover:text-gray-700 dark:hover:text-gray-300 transition"
	>
		<!-- {#if state}
			<ChevronUp strokeWidth="3.5" className="size-3.5 " />
		{:else}
			<ChevronDown strokeWidth="3.5" className="size-3.5 " />
		{/if} -->
	</div>
	<div class="text-sm rounded-xl mb-1.5" slot="content">
		<slot />
		{#if status?.query}
			<button
				on:click={() => handleUrlClick(`https://www.google.com/search?q=${status.query}`)}
				class="flex w-full items-center p-3 px-4 border-b border-gray-300/30 dark:border-gray-700/50 group/item justify-between font-normal text-gray-800 dark:text-gray-300 no-underline cursor-pointer"
			>
				<div class="flex gap-2 items-center">
					<MagnifyingGlass />

					<div class=" line-clamp-1">
						{status.query}
					</div>
				</div>

				<div
					class=" ml-1 text-white dark:text-gray-900 group-hover/item:text-gray-600 dark:group-hover/item:text-white transition"
				>
					<!--  -->
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 16 16"
						fill="currentColor"
						class="size-4"
					>
						<path
							fill-rule="evenodd"
							d="M4.22 11.78a.75.75 0 0 1 0-1.06L9.44 5.5H5.75a.75.75 0 0 1 0-1.5h5.5a.75.75 0 0 1 .75.75v5.5a.75.75 0 0 1-1.5 0V6.56l-5.22 5.22a.75.75 0 0 1-1.06 0Z"
							clip-rule="evenodd"
						/>
					</svg>
				</div>
			</button>
		{/if}
		<div class="flex flex-wrap gap-2 py-3">
			{#if status?.urls}
				{#each status.urls as url}
					<button
						on:click={() => handleUrlClick(url)}
						class="max-h-10 inline-flex items-center gap-2 px-3 py-1.5 bg-[#CCDDFC4D] hover:bg-gray-200 dark:bg-[#072D5A] dark:hover:bg-menu-hover rounded-full text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors no-underline cursor-pointer"
					>
						<img
							src={getFaviconUrl(url)}
							alt=""
							class="w-4 h-4 rounded-sm flex-shrink-0"
							loading="lazy"
							on:error={(e) => (e.target.style.display = 'none')}
						/>
						<span class="truncate max-w-[200px]">
							{extractDomain(url)}
						</span>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 16 16"
							fill="currentColor"
							class="w-3 h-3 flex-shrink-0 opacity-60"
						>
							<path
								fill-rule="evenodd"
								d="M4.22 11.78a.75.75 0 0 1 0-1.06L9.44 5.5H5.75a.75.75 0 0 1 0-1.5h5.5a.75.75 0 0 1 .75.75v5.5a.75.75 0 0 1-1.5 0V6.56l-5.22 5.22a.75.75 0 0 1-1.06 0Z"
								clip-rule="evenodd"
							/>
						</svg>
					</button>
				{/each}
			{:else}
				{#each Array(3) as _, i}
					<div
						class="max-h-10 inline-flex items-center gap-2 px-3 py-3 bg-[#CCDDFC4D] dark:bg-[#072D5A] rounded-full text-sm font-medium animate-pulse"
					>
						<div class="w-4 h-4 rounded-full flex-shrink-0 bg-gray-300 dark:bg-gray-600"></div>
						<div class="w-24 h-4 bg-gray-300 dark:bg-gray-600 rounded"></div>
					</div>
				{/each}
			{/if}
		</div>
	</div>
</Collapsible>

<!-- External Link Modal -->
<ExternalLinkModal bind:show={showExternalModal} url={externalUrl} />
