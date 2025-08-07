<script lang="ts">
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import ChevronUp from '$lib/components/icons/ChevronUp.svelte';
	import MagnifyingGlass from '$lib/components/icons/MagnifyingGlass.svelte';
	import Collapsible from '$lib/components/common/Collapsible.svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import { getContext } from 'svelte';
	import Warning from '$lib/components/icons/Warning.svelte';

	export let status = { urls: [], query: '' };
	export let state = true;

	const i18n = getContext('i18n');
	let showConfirmModal = false;
	let urlToOpen = '';

	function handleUrlClick(url: string) {
		urlToOpen = url;
		showConfirmModal = true;
	}

	function openExternalUrl() {
		window.open(urlToOpen, '_blank');
		showConfirmModal = false;
		urlToOpen = '';
	}

	function cancelNavigation() {
		showConfirmModal = false;
		urlToOpen = '';
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
			return `https://www.google.com/s2/favicons?domain=${urlObj.hostname}&sz=16`;
		} catch {
			return '';
		}
	}
</script>

<Collapsible bind:open={state} className="w-full space-y-1">
	<div
		class="flex items-center gap-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition"
	>
		<slot />

		{#if state}
			<ChevronUp strokeWidth="3.5" className="size-3.5 " />
		{:else}
			<ChevronDown strokeWidth="3.5" className="size-3.5 " />
		{/if}
	</div>
	<div
		class="text-sm rounded-xl mb-1.5"
		slot="content"
	>
		{#if status?.query}
			<a
				href="https://www.google.com/search?q={status.query}"
				target="_blank"
				class="flex w-full items-center p-3 px-4 border-b border-gray-300/30 dark:border-gray-700/50 group/item justify-between font-normal text-gray-800 dark:text-gray-300 no-underline"
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
			</a>
		{/if}

		<div class="flex flex-wrap gap-2 py-3">
			{#each status.urls as url}
				<button
					on:click={() => handleUrlClick(url)}
					class="inline-flex items-center gap-2 px-3 py-1.5 bg-[#CCDDFC4D] hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 rounded-full text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors no-underline cursor-pointer"
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
		</div>
	</div>
</Collapsible>

<Modal bind:show={showConfirmModal} size="sm">
	<div>
		<div class="flex justify-between px-4 py-4">
			<Warning />
			<button
				class="self-start flex items-center justify-center size-[18px] cursor-pointer text-gray-400 hover:text-gray-800 dark:hover:text-gray-100 transition"
				on:click={cancelNavigation}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="18"
					height="18"
					viewBox="0 0 18 18"
					fill="none"
				>
					<path
						d="M14.4608 13.6648C14.513 13.7171 14.5545 13.7792 14.5828 13.8474C14.6111 13.9157 14.6256 13.9889 14.6256 14.0628C14.6256 14.1367 14.6111 14.2099 14.5828 14.2782C14.5545 14.3465 14.513 14.4085 14.4608 14.4608C14.4085 14.513 14.3465 14.5545 14.2782 14.5828C14.2099 14.6111 14.1367 14.6256 14.0628 14.6256C13.9889 14.6256 13.9157 14.6111 13.8474 14.5828C13.7792 14.5545 13.7171 14.513 13.6648 14.4608L9.00031 9.79555L4.33578 14.4608C4.23023 14.5663 4.08708 14.6256 3.93781 14.6256C3.78855 14.6256 3.64539 14.5663 3.53984 14.4608C3.4343 14.3552 3.375 14.2121 3.375 14.0628C3.375 13.9135 3.4343 13.7704 3.53984 13.6648L8.20508 9.00031L3.53984 4.33578C3.4343 4.23023 3.375 4.08708 3.375 3.93781C3.375 3.78855 3.4343 3.64539 3.53984 3.53984C3.64539 3.4343 3.78855 3.375 3.93781 3.375C4.08708 3.375 4.23023 3.4343 4.33578 3.53984L9.00031 8.20508L13.6648 3.53984C13.7704 3.4343 13.9135 3.375 14.0628 3.375C14.2121 3.375 14.3552 3.4343 14.4608 3.53984C14.5663 3.64539 14.6256 3.78855 14.6256 3.93781C14.6256 4.08708 14.5663 4.23023 14.4608 4.33578L9.79555 9.00031L14.4608 13.6648Z"
						fill="currentColor"
					/>
				</svg>
			</button>
		</div>

		<div class="px-4 py-2">
			
			<div class="text-lg font-medium text-gray-800 dark:text-gray-200">
				{$i18n.t('You’re leaving GovGPT')}
			</div>

			<div class="text-sm text-typography-subtext dark:text-gray-400 mb-4">
				{$i18n.t('Verify the link before you choose to proceed.')}
			</div>
			<div class="bg-[#CCDDFC4D] dark:bg-gray-800 p-3 rounded-lg mb-4">
				<div class="text-sm font-medium text-gray-800 dark:text-gray-200 break-all">
					{urlToOpen}
				</div>
			</div>
		</div>

		<div class="flex justify-end gap-2 px-4 py-4">
			<button
				class="px-[12px] py-[8px] bg-white border border-neutrals-100 hover:bg-gray-200 text-gray-800 dark:bg-transparent dark:hover:bg-gray-800 dark:text-white font-medium rounded-lg transition"
				on:click={cancelNavigation}
			>
				{$i18n.t('Cancel')}
			</button>
			<button
				class="px-4 py-2 text-sm font-medium bg-[#004280] hover:bg-blue-700 text-white rounded-lg transition"
				on:click={openExternalUrl}
			>
				{$i18n.t('Open link')}
			</button>
		</div>
	</div>
</Modal>
