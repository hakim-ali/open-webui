<script lang="ts">
	import ExternalLinkModal from '$lib/components/common/ExternalLinkModal.svelte';
	
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
		<div class="text-sm text-gray-600 dark:text-gray-400 space-y-2">
			{#each urls as url, index}
				<div 
					id="citation-{index}" 
					class="flex items-start gap-2 transition-colors duration-300 p-2 rounded {highlightedIndex === index ? 'bg-blue-100 dark:bg-blue-900/30' : ''}"
				>
					<span class="font-medium">[{index + 1}]</span>
					<button
						on:click={() => handleUrlClick(url, index)}
						class="inline-flex items-center gap-2 px-3 py-1.5 bg-[#CCDDFC4D] hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 rounded-full text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors no-underline cursor-pointer"
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