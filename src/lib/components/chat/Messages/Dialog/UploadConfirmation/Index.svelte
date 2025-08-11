<script lang="ts">
	import DOMPurify from 'dompurify';

	import { onMount, getContext, createEventDispatcher, onDestroy } from 'svelte';
	import * as FocusTrap from 'focus-trap';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	import { fade } from 'svelte/transition';
	import { flyAndScale } from '$lib/utils/transitions';
	import MaterialIcon from '$lib/components/common/MaterialIcon.svelte';

	export let message = '';

	export let onConfirm = () => {};

	export let input = false;
	export let inputPlaceholder = '';
	export let inputValue = '';
	export let option = '';
	export let options = {};

	export let show = false;

	let modalElement = null;
	let mounted = false;

	let focusTrap: FocusTrap.FocusTrap | null = null;

	const handleKeyDown = (event: KeyboardEvent) => {
		if (event.key === 'Escape') {
			console.log('Escape');
			show = false;
		}

		if (event.key === 'Enter') {
			console.log('Enter');
			addFileHandler();
		}
	};

	const addFileHandler = () => {
		show = false;
		dispatch('addFiles');
	};

	const newChatHandler = () => {
		show = false;
		dispatch('initNewChat');
	};

	onMount(() => {
		mounted = true;
	});

	$: if (mounted) {
		if (show && modalElement) {
			document.body.appendChild(modalElement);
			focusTrap = FocusTrap.createFocusTrap(modalElement);
			focusTrap.activate();

			window.addEventListener('keydown', handleKeyDown);
			document.body.style.overflow = 'hidden';
		} else if (modalElement) {
			focusTrap.deactivate();

			window.removeEventListener('keydown', handleKeyDown);
			document.body.removeChild(modalElement);

			document.body.style.overflow = 'unset';
		}
	}

	onDestroy(() => {
		show = false;
		if (focusTrap) {
			focusTrap.deactivate();
		}
		if (modalElement) {
			document.body.removeChild(modalElement);
		}
	});
</script>

{#if show}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div
		bind:this={modalElement}
		class=" fixed top-0 right-0 left-0 bottom-0 bg-white/25 backdrop-blur-md w-full h-screen max-h-[100dvh] flex justify-center z-99999999 overflow-hidden overscroll-contain"
		in:fade={{ duration: 10 }}
		on:mousedown={() => {
			show = false;
		}}
	>
		<div
			class="p-[16px] m-auto rounded-[16px] max-w-full w-[32rem] mx-2 bg-gray-50 dark:bg-[#0F1924] max-h-[100dvh] shadow-custom"
			in:flyAndScale
			on:mousedown={(e) => {
				e.stopPropagation();
			}}
		>
			<div class="flex flex-col">
				<div
					class="flex gap-[10px] items-center pb-[20px] text-neutrals-800 text-[18px] leading-[26px] font-bold dark:text-gray-200"
				>
					<MaterialIcon iconClass="material-symbols-outlined" name="description" />
					Uploading files to this chat?
				</div>

				<div>
					All files uploaded to this chat will be considered while responding. In case you are
					looking for a fresh analysis, start a new chat.
				</div>

				<div class="flex justify-start gap-[6px] mt-[20px]">
					<button
						class="px-[12px] py-[8px] bg-[#004280] hover:bg-gray-850 text-gray-100 dark:bg-[#F1C9CF] dark:hover:bg-white dark:text-gray-800 font-medium rounded-lg transition"
						on:click={() => {
							addFileHandler();
						}}
						type="button"
					>
						{$i18n.t('Add Files')}
					</button>
					<button
						class="px-[12px] py-[8px] text-gray-100 dark:bg-[#F1C9CF] dark:hover:bg-white dark:text-gray-800 font-medium rounded-lg transition"
						on:click={() => {
							newChatHandler();
						}}
						type="button"
					>
						{$i18n.t('Start New Chat')}
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	.modal-content {
		animation: scaleUp 0.1s ease-out forwards;
	}

	@keyframes scaleUp {
		from {
			transform: scale(0.985);
			opacity: 0;
		}
		to {
			transform: scale(1);
			opacity: 1;
		}
	}
</style>
