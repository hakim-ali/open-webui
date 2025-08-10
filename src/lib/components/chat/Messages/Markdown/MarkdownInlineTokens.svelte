<script lang="ts">
	import DOMPurify from 'dompurify';
	import { toast } from 'svelte-sonner';

	import type { Token } from 'marked';
	import { getContext } from 'svelte';

	const i18n = getContext('i18n');

	import { WEBUI_BASE_URL } from '$lib/constants';
	import { copyToClipboard, unescapeHtml } from '$lib/utils';

	import Image from '$lib/components/common/Image.svelte';
	import KatexRenderer from './KatexRenderer.svelte';
	import Source from './Source.svelte';
	import HtmlToken from './HTMLToken.svelte';
	import ExternalLinkModal from '$lib/components/common/ExternalLinkModal.svelte';

	export let id: string;
	export let tokens: Token[];
	export let onSourceClick: Function = () => {};
	export let getCitationNumber: Function = () => {};

	let showExternalModal = false;
	let externalUrl = '';

	function handleExternalLinkClick(e: Event, url: string) {
		e.preventDefault();
		externalUrl = url;
		showExternalModal = true;
	}
</script>

{#each tokens as token}
	{#if token.type === 'escape'}
		{unescapeHtml(token.text)}
	{:else if token.type === 'html'}
		<HtmlToken {id} {token} {onSourceClick} />
	{:else if token.type === 'link'}
		<span
			class="inline-flex items-start justify-center leading-[1rem] min-w-[1.2rem] px-1 text-[10px] font-medium bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-md border border-blue-200 dark:border-blue-700 cursor-pointer hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
			title={token.title || token.href}
			role="button"
			tabindex="0"
			on:click={(e) => handleExternalLinkClick(e, token.href)}
			on:keydown={(e) => {
				if (e.key === 'Enter' || e.key === ' ') {
					e.preventDefault();
					handleExternalLinkClick(e, token.href);
				}
			}}
		>
			{getCitationNumber(token.href)}
		</span>
	{:else if token.type === 'image'}
		<Image src={token.href} alt={token.text} />
	{:else if token.type === 'strong'}
		<strong
			><svelte:self
				id={`${id}-strong`}
				tokens={token.tokens}
				{onSourceClick}
				{getCitationNumber}
			/></strong
		>
	{:else if token.type === 'em'}
		<em
			><svelte:self id={`${id}-em`} tokens={token.tokens} {onSourceClick} {getCitationNumber} /></em
		>
	{:else if token.type === 'codespan'}
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
		<code
			class="codespan cursor-pointer"
			on:click={() => {
				copyToClipboard(unescapeHtml(token.text));
				toast.success('Copied to clipboard');
			}}>{unescapeHtml(token.text)}</code
		>
	{:else if token.type === 'br'}
		<br />
	{:else if token.type === 'del'}
		<del
			><svelte:self
				id={`${id}-del`}
				tokens={token.tokens}
				{onSourceClick}
				{getCitationNumber}
			/></del
		>
	{:else if token.type === 'inlineKatex'}
		{#if token.text}
			<KatexRenderer content={token.text} displayMode={false} />
		{/if}
	{:else if token.type === 'iframe'}
		<iframe
			src="{WEBUI_BASE_URL}/api/v1/files/{token.fileId}/content"
			title={token.fileId}
			width="100%"
			frameborder="0"
		></iframe>
	{:else if token.type === 'text'}
		{token.raw}
	{/if}
{/each}

<!-- External Link Modal -->
<ExternalLinkModal bind:show={showExternalModal} url={externalUrl} />
