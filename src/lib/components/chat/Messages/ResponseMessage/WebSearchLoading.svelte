<script lang="ts">
	import { onDestroy, getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';

	const i18n = getContext<Writable<i18nType>>('i18n');

	export let text: string = '';
	export let stage: number = 0; // 0 none, 1 just-a-sec, 2 searching, 3 results

	// Local visual state
	const FADE_OUT_MS = 800;
	const GAP_NEXT_MS = 120;

	let displayText = '';
	let fadeState: 'in' | 'out' = 'out';
	let fadeHandle: ReturnType<typeof setTimeout> | null = null;

	$: if (text && text !== displayText) {
		if (!displayText) {
			displayText = text;
			fadeState = 'in';
		} else {
			fadeState = 'out';
			if (fadeHandle) clearTimeout(fadeHandle);
			const next = text;
			fadeHandle = setTimeout(() => {
				displayText = next;
				fadeState = 'in';
			}, FADE_OUT_MS + GAP_NEXT_MS);
		}
	}

	$: if (!text && displayText) {
		fadeState = 'out';
		if (fadeHandle) {
			clearTimeout(fadeHandle);
			fadeHandle = null;
		}
		displayText = '';
	}

	onDestroy(() => {
		if (fadeHandle) clearTimeout(fadeHandle);
	});
</script>

{#if text}
	<div class="status {fadeState}" aria-live="polite" aria-atomic="true">
		<span
			class="shimmer-text"
			style="color: {text.includes('Searched') && text.includes('Shortlisted')
				? '#23282E'
				: '#666D7A'}"
		>
			{#if text === 'Just a sec...'}
				🕒 {$i18n.t('Just a sec...')}
			{:else if text === 'Searching on web...' || text === 'Searching the web'}
				🔎 {$i18n.t('Searching the web')}
			{:else}
				{text}
			{/if}
		</span>
	</div>
{/if}

<style>
	@keyframes shimmer {
		from {
			background-position: -200% 0;
		}
		to {
			background-position: 200% 0;
		}
	}

	.shimmer-text {
		position: relative;
		background: linear-gradient(90deg, #8e96ab 0%, #cbd2e3 50%, #8e96ab 100%);
		background-size: 200% 100%;
		-webkit-background-clip: text;
		background-clip: text;
		-webkit-text-fill-color: transparent;
		animation: shimmer 2.2s linear infinite;
	}

	.status {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		opacity: 0;
	}
	.status.in {
		opacity: 1;
		transition: opacity 180ms ease;
	}
	.status.out {
		opacity: 0;
		transition: opacity 800ms ease;
	}
</style>
