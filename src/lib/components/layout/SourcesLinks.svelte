<script lang="ts">
	import { onMount, getContext, createEventDispatcher } from 'svelte';
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';
	
	const i18n = getContext<Writable<i18nType>>('i18n');
	const dispatch = createEventDispatcher();

	import { showSourcesLinks, sourcesLinksMessageId, chatId, chats } from '$lib/stores';
	import { createMessagesList } from '$lib/utils';
	import { getChatById } from '$lib/apis/chats';

	import XMark from '../icons/XMark.svelte';
	import ExternalLinkModal from '../common/ExternalLinkModal.svelte';

	let extractedLinks: Array<{ 
		href: string; 
		text: string; 
		title: string; 
		domain: string; 
		favicon: string;
		websiteTitle?: string;
		websiteDescription?: string;
		loading?: boolean;
	}> = [];
	let messages: any[] = [];
	let showExternalModal = false;
	let externalUrl = '';

	function handleExternalLinkClick(e: Event, url: string) {
		e.preventDefault();
		externalUrl = url;
		showExternalModal = true;
	}

	// Function to fetch website metadata
	async function fetchWebsiteMetadata(url: string): Promise<{ title?: string; description?: string }> {
		try {
			// Use a reliable proxy service with timeout
			const proxyUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(url)}`;
			
			// Create a timeout promise
			const timeoutPromise = new Promise((_, reject) => {
				setTimeout(() => reject(new Error('Timeout')), 5000); // 5 second timeout
			});
			
			// Create the fetch promise
			const fetchPromise = fetch(proxyUrl, {
				method: 'GET',
				headers: {
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
				}
			});
			
			// Race between fetch and timeout
			const response = await Promise.race([fetchPromise, timeoutPromise]) as Response;
			
			if (!response.ok) {
				throw new Error(`HTTP ${response.status}`);
			}
			
			const data = await response.json();
			
			if (!data.contents) {
				throw new Error('No contents in response');
			}
			
			const html = data.contents;
			const parser = new DOMParser();
			const doc = parser.parseFromString(html, 'text/html');
			
			// Extract title (try multiple sources)
			let title = doc.querySelector('title')?.textContent?.trim();
			if (!title) {
				title = doc.querySelector('meta[property="og:title"]')?.getAttribute('content')?.trim();
			}
			if (!title) {
				title = doc.querySelector('meta[name="twitter:title"]')?.getAttribute('content')?.trim();
			}
			if (!title) {
				title = doc.querySelector('h1')?.textContent?.trim();
			}
			
			// Extract description (try multiple sources)
			let description = doc.querySelector('meta[name="description"]')?.getAttribute('content')?.trim();
			if (!description) {
				description = doc.querySelector('meta[property="og:description"]')?.getAttribute('content')?.trim();
			}
			if (!description) {
				description = doc.querySelector('meta[name="twitter:description"]')?.getAttribute('content')?.trim();
			}
			if (!description) {
				// Try to get first paragraph as description
				const firstP = doc.querySelector('p');
				if (firstP && firstP.textContent) {
					description = firstP.textContent.trim().substring(0, 200);
					if (description.length === 200) {
						description += '...';
					}
				}
			}
			
			// Clean up the title and description
			if (title) {
				title = title.replace(/\s+/g, ' ').trim();
			}
			if (description) {
				description = description.replace(/\s+/g, ' ').trim();
			}
			
			return { title, description };
		} catch (error) {
			console.warn('Error fetching metadata for:', url, error);
		}
		
		return {};
	}

	// Function to normalize URL for comparison
	function normalizeUrl(url: string): string {
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

	// Function to extract links from content (similar to ContentRenderer)
	function collectLinksFromContent(content: string) {
		const links: Array<{ href: string; text: string; title: string; domain: string; favicon: string }> = [];
		const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
		const urlRegex = /https?:\/\/[^\s]+/g;
		const seenUrls = new Set<string>();
		
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
				const domain = getDomain(href);
				const favicon = getFaviconUrl(href);
				
				links.push({
					href,
					text,
					title: text,
					domain,
					favicon
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
				const domain = getDomain(url);
				const favicon = getFaviconUrl(url);
				
				links.push({
					href: url,
					text: url,
					title: url,
					domain,
					favicon
				});
			}
		}
		
		// Final deduplication pass to ensure absolute uniqueness
		const finalUniqueLinks = [];
		const finalSeenUrls = new Set<string>();
		
		links.forEach((link) => {
			const normalizedUrl = normalizeUrl(link.href);
			if (!finalSeenUrls.has(normalizedUrl)) {
				finalSeenUrls.add(normalizedUrl);
				finalUniqueLinks.push(link);
			}
		});
		
		return finalUniqueLinks;
	}

	// Function to extract links from specific message
	async function extractLinksFromMessage() {
		extractedLinks = [];
		
		// Check if chatId and messageId are available
		if (!$chatId || !$sourcesLinksMessageId) {
			return;
		}

		try {
			// Fetch the current chat data
			const chat = await getChatById(localStorage.token, $chatId);
			if (!chat || !chat.chat) {
				return;
			}

			const chatContent = chat.chat;
			const history = chatContent.history || chatContent;
			
			if (!history || !history.messages) {
				return;
			}

			// Get the specific message
			const targetMessage = history.messages[$sourcesLinksMessageId];
			if (!targetMessage || !targetMessage.content) {
				return;
			}

			// Extract links from the specific message only
			const messageLinks = collectLinksFromContent(targetMessage.content);
			
			// Remove duplicates based on normalized URL
			const uniqueLinksMap = new Map<string, { href: string; text: string; title: string; domain: string; favicon: string }>();
			
			messageLinks.forEach((link) => {
				// Normalize the URL for comparison
				const normalizedUrl = normalizeUrl(link.href);
				
				// Only add if not already present
				if (!uniqueLinksMap.has(normalizedUrl)) {
					uniqueLinksMap.set(normalizedUrl, link);
				}
			});
		
		// Convert map back to array and add loading state
		extractedLinks = Array.from(uniqueLinksMap.values()).map(link => ({
			...link,
			loading: true
		}));

		console.log(`Found ${messageLinks.length} total links, ${extractedLinks.length} unique links for message ${$sourcesLinksMessageId}`);

		// Fetch metadata for each link
		await Promise.all(
			extractedLinks.map(async (link, index) => {
				try {
					const metadata = await fetchWebsiteMetadata(link.href);
					extractedLinks[index] = {
						...link,
						websiteTitle: metadata.title,
						websiteDescription: metadata.description,
						loading: false
					};
					extractedLinks = [...extractedLinks]; // Trigger reactivity
				} catch (error) {
					extractedLinks[index] = {
						...link,
						loading: false
					};
					extractedLinks = [...extractedLinks]; // Trigger reactivity
				}
			})
		);
		} catch (error) {
			console.warn('Error fetching chat or extracting links from message:', error);
			extractedLinks = [];
		}
	}

	// Function to get domain from URL
	function getDomain(url: string): string {
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
	function getFaviconUrl(url: string): string {
		try {
			const cleanUrl = url.replace(/[\s.,;!?)\]}>]+$/, '');
			const urlObj = new URL(cleanUrl);
			return `https://www.google.com/s2/favicons?domain=${urlObj.hostname}&sz=64`;
		} catch {
			return '';
		}
	}

	// Extract links whenever the sidebar is shown
	$: if ($showSourcesLinks && $chatId && $sourcesLinksMessageId) {
		extractLinksFromMessage();
	}

	onMount(() => {
		// Component mounted
	});
</script>

{#if $showSourcesLinks}
	<div class="fixed inset-0 z-50 flex">
		<!-- Backdrop -->
		<div 
			class="absolute inset-0 bg-black/20 dark:bg-black/40"
			on:click={() => {
				showSourcesLinks.set(false);
				sourcesLinksMessageId.set(null);
			}}
		></div>
		
		<!-- Sidebar -->
		<div class="relative ml-auto w-full max-w-md bg-white dark:bg-gray-850 shadow-xl">
			<div class="flex h-full flex-col">
				<!-- Header -->
				<div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-700 px-6 py-4">
					<div>
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
							{$i18n.t('Citations')}
						</h3>
					</div>
					<button
						class="rounded-full p-1 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
						on:click={() => {
							showSourcesLinks.set(false);
							sourcesLinksMessageId.set(null);
						}}
					>
						<XMark className="w-5 h-5" />
					</button>
				</div>

				<!-- Content -->
				<div class="flex-1 overflow-y-auto">
					{#if extractedLinks.length > 0}
						<div class="p-6 space-y-4">
							<!-- Citations -->
							{#each extractedLinks as link, index}
								<div class="flex items-start gap-3 group">
									<!-- Favicon -->
									<div class="flex-shrink-0 w-6 h-6 rounded-full overflow-hidden bg-transparent flex items-center justify-center">
										<img 
											src={link.favicon} 
											alt={link.domain}
											class="w-6 h-6 rounded-full"
											on:error={(e) => {
												const target = e?.target;
												if (target && target instanceof HTMLImageElement) {
													target.style.display = 'none';
												}
											}}
										/>
									</div>
									
									<!-- Link Content -->
									<div class="flex-1 min-w-0">
										<div class="text-sm font-medium text-gray-900 dark:text-white mb-1">
											{link.domain}
										</div>
										<a
											href={link.href}
											class="block text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline transition-colors mb-1 line-clamp-2 cursor-pointer"
											title={link.websiteTitle || link.title}
											on:click={(e) => handleExternalLinkClick(e, link.href)}
										>
											{#if link.loading}
												<div class="animate-pulse">
													<div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-1"></div>
													<div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
												</div>
											{:else if link.websiteTitle}
												{link.websiteTitle}
											{:else}
												{link.text || link.title}
											{/if}
										</a>
										{#if link.websiteDescription && !link.loading}
											<div class="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mb-1">
												{link.websiteDescription}
											</div>
										{/if}
										<div class="text-xs text-gray-500 dark:text-gray-400">
											{link.domain}
										</div>
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<div class="flex-1 flex items-center justify-center p-6">
							<div class="text-center text-gray-500 dark:text-gray-400">
								<div class="w-12 h-12 mx-auto mb-4 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
									<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
										<path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>
									</svg>
								</div>
								<p class="text-sm font-medium">{$i18n.t('No citations found')}</p>
								<p class="text-xs mt-1">{$i18n.t('Links from your conversation will appear here')}</p>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}

<!-- External Link Modal -->
<ExternalLinkModal bind:show={showExternalModal} url={externalUrl} /> 