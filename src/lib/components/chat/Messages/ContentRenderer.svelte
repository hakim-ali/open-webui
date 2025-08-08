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
		showOverview
	} from '$lib/stores';
	import FloatingButtons from '../ContentRenderer/FloatingButtons.svelte';
	import { createMessagesList } from '$lib/utils';

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

	// Function to collect links from markdown content
	function collectLinksFromContent(content) {
		const links = [];
		const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
		const urlRegex = /https?:\/\/[^\s]+/g;
		
		// Collect markdown links
		let match;
		while ((match = linkRegex.exec(content)) !== null) {
			links.push({
				href: match[2],
				text: match[1],
				title: match[1]
			});
		}
		
		// Collect plain URLs
		while ((match = urlRegex.exec(content)) !== null) {
			const url = match[0];
			// Skip if already collected as markdown link
			if (!links.some(link => link.href === url)) {
				links.push({
					href: url,
					text: url,
					title: url
				});
			}
		}
		
		return links;
	}

	// Function to get domain from URL
	function getDomain(url) {
		try {
			const urlObj = new URL(url);
			return urlObj.hostname.replace('www.', '');
		} catch {
			return url;
		}
	}

	// Function to get favicon URL
	function getFaviconUrl(url) {
		try {
			// Clean the URL by removing any trailing parentheses
			const cleanUrl = url.replace(/\)+$/, '');
			const urlObj = new URL(cleanUrl);
			return `https://www.google.com/s2/favicons?domain=${urlObj.hostname}&sz=64`;
		} catch {
			return '';
		}
	}

	$: {
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

		if (floatingButtonsElement) {
			// check if closeHandler is defined

			if (typeof floatingButtonsElement?.closeHandler === 'function') {
				// call the closeHandler function
				floatingButtonsElement?.closeHandler();
			}
		}
	};

	const keydownHandler = (e) => {
		if (e.key === 'Escape') {
			closeFloatingButtons();
		}
	};

	onMount(() => {
		if (floatingButtons) {
			contentContainerElement?.addEventListener('mouseup', updateButtonPosition);
			document.addEventListener('mouseup', updateButtonPosition);
			document.addEventListener('keydown', keydownHandler);
		}
	});

	onDestroy(() => {
		if (floatingButtons) {
			contentContainerElement?.removeEventListener('mouseup', updateButtonPosition);
			document.removeEventListener('mouseup', updateButtonPosition);
			document.removeEventListener('keydown', keydownHandler);
		}
	});
</script>

<div bind:this={contentContainerElement}>
	<Markdown
		{id}
		{content}
		{model}
		{save}
		{preview}
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
		<div class="inline-flex items-center gap-2 px-3 py-2 max-h-10 rounded-full transition-colors bg-[#E5EBF3] text-[#23282E]">
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
							on:click={(e) => {
								e.stopPropagation();
								window.open(link.href, '_blank', 'nofollow');
							}}
							on:error={(e) => {
								const target = e?.target;
								if (target) {
									target.style.display = 'none';
								}
							}}
						/>
					{/if}
				{/each}
			</div>
			<span class="text-sm font-medium">
				Sources
			</span>
		</div>
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
