<script>
	import { onDestroy, onMount, tick, getContext } from 'svelte';
	const i18n = getContext('i18n');

	import Markdown from './Markdown.svelte';
	import {
		artifactCode,
		chatId,
		mobile,
		settings,
		showArtifacts,
		showControls,
		showOverview,
		showSourcesLinks,
		sourcesLinksMessageId
	} from '$lib/stores';
	import FloatingButtons from '../ContentRenderer/FloatingButtons.svelte';
	import { createMessagesList } from '$lib/utils';
	import ExternalLinkModal from '$lib/components/common/ExternalLinkModal.svelte';

	export let id;
	export let content;
	export let history;
	export let model = null;
	export let sources = null;

	export let save = false;
	export let preview = false;
	export let floatingButtons = true;

	export let onSave = () => {};
	export let onSourceClick = () => {};
	export let onTaskClick = () => {};

	export let onAddMessages = () => {};

	let contentContainerElement;
	let floatingButtonsElement;
	let collectedLinks = [];
	let showExternalModal = false;
	let externalUrl = '';
	
	// Citation numbering system
	let citationMap = new Map(); // URL -> citation number
	let citationCounter = 0;
	
	// Function to get or assign citation number
	function getCitationNumber(url) {
		// Normalize URL for consistent numbering
		function normalizeUrl(url) {
			let normalized = url.toLowerCase().trim();
			normalized = normalized.replace(/[\s.,;!?)\]}>]+$/, '');
			normalized = normalized.replace(/\?.*$/, '');
			normalized = normalized.replace(/#.*$/, '');
			normalized = normalized.replace(/\/$/, '');
			normalized = normalized.replace(/^https?:\/\/www\./, 'https://');
			normalized = normalized.replace(/^http:\/\//, 'https://');
			return normalized;
		}
		
		const normalizedUrl = normalizeUrl(url);
		
		if (citationMap.has(normalizedUrl)) {
			return citationMap.get(normalizedUrl);
		} else {
			citationCounter++;
			citationMap.set(normalizedUrl, citationCounter);
			return citationCounter;
		}
	}

	function handleExternalLinkClick(e, url) {
		e.preventDefault();
		e.stopPropagation();
		externalUrl = url;
		showExternalModal = true;
	}

	// Function to collect links from markdown content
	function collectLinksFromContent(content) {
		const links = [];
		const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
		const urlRegex = /https?:\/\/[^\s]+/g;
		const seenUrls = new Set();
		
		// Function to normalize URL for comparison
		function normalizeUrl(url) {
			let normalized = url.toLowerCase().trim();
			
			// Remove multiple trailing punctuation marks and whitespace
			normalized = normalized.replace(/[\s.,;!?)\]}>]+$/, '');
			
			// Remove common URL parameters that don't affect the core URL
			normalized = normalized.replace(/\?.*$/, '');
			normalized = normalized.replace(/#.*$/, '');
			
			// Remove trailing slash after cleaning parameters
			normalized = normalized.replace(/\/$/, '');
			
			// Remove www prefix for better deduplication
			normalized = normalized.replace(/^https?:\/\/www\./, 'https://');
			
			// Ensure protocol consistency (prefer https)
			normalized = normalized.replace(/^http:\/\//, 'https://');
			
			return normalized;
		}
		
		// Collect markdown links first
		let match;
		while ((match = linkRegex.exec(content)) !== null) {
			let href = match[2].trim();
			const text = match[1].trim();
			
			// Clean the href from trailing punctuation and whitespace
			href = href.replace(/[\s.,;!?)\]}>]+$/, '');
			
			// Skip invalid URLs
			if (!href || !href.match(/^https?:\/\//)) {
				continue;
			}
			
			const normalizedUrl = normalizeUrl(href);
			
			if (!seenUrls.has(normalizedUrl)) {
				seenUrls.add(normalizedUrl);
				links.push({
					href,
					text,
					title: text
				});
			}
		}
		
		// Collect plain URLs (skip if already collected as markdown link)
		while ((match = urlRegex.exec(content)) !== null) {
			let url = match[0].trim();
			
			// Clean the URL from trailing punctuation and whitespace
			url = url.replace(/[\s.,;!?)\]}>]+$/, '');
			
			// Skip invalid URLs
			if (!url || !url.match(/^https?:\/\//)) {
				continue;
			}
			
			const normalizedUrl = normalizeUrl(url);
			
			// Skip if already collected as markdown link or plain URL
			if (!seenUrls.has(normalizedUrl)) {
				seenUrls.add(normalizedUrl);
				links.push({
					href: url,
					text: url,
					title: url
				});
			}
		}
		
		// Final deduplication pass to ensure absolute uniqueness
		const finalUniqueLinks = [];
		const finalSeenUrls = new Set();
		
		links.forEach((link) => {
			const normalizedUrl = normalizeUrl(link.href);
			if (!finalSeenUrls.has(normalizedUrl)) {
				finalSeenUrls.add(normalizedUrl);
				finalUniqueLinks.push(link);
			}
		});
		
		return finalUniqueLinks;
	}

	// Function to get domain from URL
	function getDomain(url) {
		try {
			const cleanUrl = url.replace(/[\s.,;!?)\]}>]+$/, '');
			const urlObj = new URL(cleanUrl);
			return urlObj.hostname.replace(/^www\./, '');
		} catch {
			// Extract domain manually if URL parsing fails
			const match = url.match(/https?:\/\/(?:www\.)?([^\/\s.,;!?)\]}>]+)/);
			return match ? match[1] : url;
		}
	}

	// Function to get favicon URL
	function getFaviconUrl(url) {
		try {
			const cleanUrl = url.replace(/[\s.,;!?)\]}>]+$/, '');
			const urlObj = new URL(cleanUrl);
			return `https://www.google.com/s2/favicons?domain=${urlObj.hostname}&sz=64`;
		} catch {
			return '';
		}
	}

	$: {
		// Reset citation counter when content changes
		citationMap.clear();
		citationCounter = 0;
		collectedLinks = collectLinksFromContent(content || '');
	}

	const updateButtonPosition = (event) => {
		const buttonsContainerElement = document.getElementById(`floating-buttons-${id}`);
		if (
			!contentContainerElement?.contains(event.target) &&
			!buttonsContainerElement?.contains(event.target)
		) {
			closeFloatingButtons();
			return;
		}

		setTimeout(async () => {
			await tick();

			if (!contentContainerElement?.contains(event.target)) return;

			let selection = window.getSelection();

			if (selection && selection.toString().trim().length > 0) {
				const range = selection.getRangeAt(0);
				const rect = range.getBoundingClientRect();

				const parentRect = contentContainerElement.getBoundingClientRect();

				// Adjust based on parent rect
				const top = rect.bottom - parentRect.top;
				const left = rect.left - parentRect.left;

				if (buttonsContainerElement) {
					buttonsContainerElement.style.display = 'block';

					// Calculate space available on the right
					const spaceOnRight = parentRect.width - left;
					let halfScreenWidth = $mobile ? window.innerWidth / 2 : window.innerWidth / 3;

					if (spaceOnRight < halfScreenWidth) {
						const right = parentRect.right - rect.right;
						buttonsContainerElement.style.right = `${right}px`;
						buttonsContainerElement.style.left = 'auto'; // Reset left
					} else {
						// Enough space, position using 'left'
						buttonsContainerElement.style.left = `${left}px`;
						buttonsContainerElement.style.right = 'auto'; // Reset right
					}
					buttonsContainerElement.style.top = `${top + 5}px`; // +5 to add some spacing
				}
			} else {
				closeFloatingButtons();
			}
		}, 0);
	};

	const closeFloatingButtons = () => {
		const buttonsContainerElement = document.getElementById(`floating-buttons-${id}`);
		if (buttonsContainerElement) {
			buttonsContainerElement.style.display = 'none';
		}
	};

	onMount(() => {
		document.addEventListener('click', updateButtonPosition);
	});

	onDestroy(() => {
		document.removeEventListener('click', updateButtonPosition);
	});
</script>

<div class="relative">
	<div bind:this={contentContainerElement}>
		<Markdown
			{id}
			{content}
			{model}
			{save}
			{preview}
			getCitationNumber={getCitationNumber}
			sourceIds={(sources ?? []).reduce((acc, s) => {
				let ids = [];
				s.document.forEach((document, index) => {
					if (model?.info?.meta?.capabilities?.citations == false) {
						ids.push('N/A');
						return ids;
					}

					const metadata = s.metadata?.[index];
					const id = metadata?.source ?? 'N/A';

					if (metadata?.name) {
						ids.push(metadata.name);
						return ids;
					}

					if (id.startsWith('http://') || id.startsWith('https://')) {
						ids.push(id);
					} else {
						ids.push(s?.source?.name ?? id);
					}

					return ids;
				});

				acc = [...acc, ...ids];

				// remove duplicates
				return acc.filter((item, index) => acc.indexOf(item) === index);
			}, [])}
			{onSourceClick}
			{onTaskClick}
			{onSave}
			onUpdate={(token) => {
				const { lang, text: code } = token;

				if (
					($settings?.detectArtifacts ?? true) &&
					(['html', 'svg'].includes(lang) || (lang === 'xml' && code.includes('svg'))) &&
					!$mobile &&
					$chatId
				) {
					showArtifacts.set(true);
					showControls.set(true);
				}
			}}
			onPreview={async (value) => {
				console.log('Preview', value);
				await artifactCode.set(value);
				await showControls.set(true);
				await showArtifacts.set(true);
				await showOverview.set(false);
			}}
		/>
	</div>

	{#if collectedLinks.length > 0}
		<div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
			<button 
				class="inline-flex items-center gap-2 px-3 py-2 max-h-10 rounded-full transition-colors bg-[#E5EBF3] text-[#23282E] hover:bg-[#D1D9E6] cursor-pointer"
				on:click={() => {
					sourcesLinksMessageId.set(id);
					showSourcesLinks.set(true);
				}}
				aria-label="View all sources and links"
				title="Click to view all sources and links in detail"
			>
				<div class="flex -space-x-2">
					{#each collectedLinks.slice(0, 5) as link, index}
						{#if getFaviconUrl(link.href)}
							<img
								src={getFaviconUrl(link.href)}
								alt=""
								class="w-6 h-6 rounded-[16px] shadow-sm hover:scale-110 transition-transform cursor-pointer bg-transparent hover:bg-white object-cover"
								style="border-radius:16px"
								loading="lazy"
								title={link.text || getDomain(link.href)}
								on:click={(e) => handleExternalLinkClick(e, link.href)}
								on:error={(e) => {
									const target = e?.target;
									if (target && target instanceof HTMLImageElement) {
										target.style.display = 'none';
									}
								}}
							/>
						{/if}
					{/each}
				</div>
				<span class="text-sm font-medium">
					{$i18n.t('Sources')}
				</span>
			</button>
		</div>
	{/if}

	{#if floatingButtons && model}
		<FloatingButtons
			bind:this={floatingButtonsElement}
			{id}
			model={model?.id}
			messages={createMessagesList(history, id)}
			onAdd={({ modelId, parentId, messages }) => {
				console.log(modelId, parentId, messages);
				onAddMessages({ modelId, parentId, messages });
				closeFloatingButtons();
			}}
		/>
	{/if}
</div>

<!-- External Link Modal -->
<ExternalLinkModal bind:show={showExternalModal} url={externalUrl} />
