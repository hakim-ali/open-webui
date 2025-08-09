<script lang="ts">
	import ExternalLinkModal from '$lib/components/common/ExternalLinkModal.svelte';
	import ArrowDigonal from '$lib/components/icons/ArrowDigonal.svelte';

	export let urls: string[] = [];
	export let onCitationClick: (index: number) => void = () => {};

	let showConfirmModal = false;
	let urlToOpen = '';
	let highlightedIndex = -1;

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

	function handleUrlClick(url: string, index: number) {
		urlToOpen = url;
		showConfirmModal = true;
		onCitationClick(index);
	}

	function openExternalUrl() {
		window.open(urlToOpen, '_blank');
		urlToOpen = '';
	}

	function cancelNavigation() {
		urlToOpen = '';
	}

	export function highlightCitation(index: number) {
		highlightedIndex = index;
		// Scroll to the citation
		const citationElement = document.getElementById(`citation-${index}`);
		if (citationElement) {
			citationElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
		}
		// Remove highlight after 2 seconds
		setTimeout(() => {
			highlightedIndex = -1;
		}, 2000);
	}
</script>

{#if urls.length > 0}
	<div class="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
		<div class="flex flex-row justify-start text-sm text-gray-600 dark:text-gray-400 space-y-2">
			{#each urls as url, index}
				<div
					id="citation-{index}"
					class="flex items-start gap-2 transition-colors duration-300 p-1 rounded {highlightedIndex ===
					index
						? 'bg-blue-100 dark:bg-blue-900/30'
						: ''}"
				>
					<button
						on:click={() => handleUrlClick(url, index)}
						class="inline-flex items-center gap-2 px-3 bg-[#CCDDFC4D] hover:bg-gray-200 dark:bg-[#072D5A] dark:hover:bg-gray-700 rounded-full text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors no-underline cursor-pointer"
					>
						<span class="font-medium px-2 rounded-md bg-[#CCDDFC] dark:bg-blue-900"
							>{index + 1}</span
						>
						<img
							src={getFaviconUrl(url)}
							alt=""
							class="w-4 h-4 rounded-sm flex-shrink-0"
							loading="lazy"
							on:error={(e) => {
								if (e.target instanceof HTMLElement) {
									e.target.style.display = 'none';
								}
							}}
						/>
						<span class="truncate max-w-[300px]">
							{extractDomain(url)}
						</span>
						<ArrowDigonal />
					</button>
				</div>
			{/each}
		</div>
	</div>
{/if}

<ExternalLinkModal
	bind:show={showConfirmModal}
	url={urlToOpen}
	onConfirm={openExternalUrl}
	onCancel={cancelNavigation}
/>
