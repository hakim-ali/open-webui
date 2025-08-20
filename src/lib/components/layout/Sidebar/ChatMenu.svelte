<script lang="ts">
	import { DropdownMenu } from 'bits-ui';
	import { flyAndScale } from '$lib/utils/transitions';
	import { getContext, createEventDispatcher, onMount, onDestroy } from 'svelte';

	import fileSaver from 'file-saver';
	const { saveAs } = fileSaver;

	import jsPDF from 'jspdf';
	import html2canvas from 'html2canvas-pro';

	const dispatch = createEventDispatcher();

	import Dropdown from '$lib/components/common/Dropdown.svelte';
	import GarbageBin from '$lib/components/icons/GarbageBin.svelte';
	import Pencil from '$lib/components/icons/Pencil.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Tags from '$lib/components/chat/Tags.svelte';
	import Share from '$lib/components/icons/Share.svelte';
	import ArchiveBox from '$lib/components/icons/ArchiveBox.svelte';
	import DocumentDuplicate from '$lib/components/icons/DocumentDuplicate.svelte';
	import Bookmark from '$lib/components/icons/Bookmark.svelte';
	import BookmarkSlash from '$lib/components/icons/BookmarkSlash.svelte';
	import {
		getChatById,
		getChatPinnedStatusById,
		toggleChatPinnedStatusById
	} from '$lib/apis/chats';
	import { chats, settings, theme, user } from '$lib/stores';
	import { createMessagesList } from '$lib/utils';
	import { downloadChatAsPDF } from '$lib/apis/utils';
	import Download from '$lib/components/icons/Download.svelte';
	import { isRTL } from '$lib/i18n';
	const i18n = getContext('i18n');

	export let shareHandler: Function;
	export let cloneChatHandler: Function;
	export let archiveChatHandler: Function;
	export let renameHandler: Function;
	export let deleteHandler: Function;
	export let onClose: Function;
	export let triggerElement: HTMLElement | null = null;

	export let chatId = '';

	let show = false;
	let pinned = false;
	let scrollContainer: HTMLElement | null = null;

	const pinHandler = async () => {
		await toggleChatPinnedStatusById(localStorage.token, chatId);
		dispatch('change');
	};

	const checkPinned = async () => {
		pinned = await getChatPinnedStatusById(localStorage.token, chatId);
	};

	const getChatAsText = async (chat) => {
		const history = chat.chat.history;
		const messages = createMessagesList(history, history.currentId);
		const chatText = messages.reduce((a, message, i, arr) => {
			return `${a}### ${message.role.toUpperCase()}\n${message.content}\n\n`;
		}, '');

		return chatText.trim();
	};

	const downloadTxt = async () => {
		const chat = await getChatById(localStorage.token, chatId);
		if (!chat) {
			return;
		}

		const chatText = await getChatAsText(chat);
		let blob = new Blob([chatText], {
			type: 'text/plain'
		});

		saveAs(blob, `chat-${chat.chat.title}.txt`);
	};

	const downloadPdf = async () => {
		try {
			const chat = await getChatById(localStorage.token, chatId);
			if (!chat || !chat.chat) {
				console.error('Chat not found');
				return;
			}

			const isDarkMode = document.documentElement.classList.contains('dark');
			const virtualWidth = 800;
			const messages = chat.chat.messages || [];

			const containerElement = document.createElement('div');
			containerElement.style.width = `${virtualWidth}px`;
			containerElement.style.position = 'absolute';
			containerElement.style.left = '-9999px';
			containerElement.style.top = '0';
			containerElement.style.backgroundColor = isDarkMode ? '#000' : '#fff';
			containerElement.style.fontFamily = 'Arial, sans-serif';
			containerElement.style.padding = '20px';
			containerElement.style.boxSizing = 'border-box';

			const MAX_BUBBLE_CHARS = 800; // split long messages

			messages.forEach((msg) => {
				const segments = (msg.content || '').split(/\n\s*\n/); // split paragraphs
				const bubbles = [];

				segments.forEach((seg) => {
					if (seg.length > MAX_BUBBLE_CHARS) {
						// Break long segments into chunks
						for (let i = 0; i < seg.length; i += MAX_BUBBLE_CHARS) {
							bubbles.push(seg.slice(i, i + MAX_BUBBLE_CHARS));
						}
					} else {
						bubbles.push(seg);
					}
				});

				bubbles.forEach((bubbleText, idx) => {
					const wrapper = document.createElement('div');
					wrapper.style.display = 'flex';
					wrapper.style.margin = '8px 0';
					wrapper.style.width = '100%';

					const bubble = document.createElement('div');
					bubble.style.maxWidth = '70%';
					bubble.style.padding = '10px 14px';
					bubble.style.borderRadius = '12px';
					bubble.style.wordWrap = 'break-word';
					bubble.style.whiteSpace = 'pre-wrap';
					bubble.style.fontSize = '14px';
					bubble.style.lineHeight = '20px';

					if (msg.role === 'user') {
						wrapper.style.justifyContent = 'flex-end';
						bubble.style.backgroundColor = isDarkMode ? '#007bff' : '#d1e7ff';
						bubble.style.color = isDarkMode ? '#fff' : '#000';
					} else {
						wrapper.style.justifyContent = 'flex-start';
						bubble.style.backgroundColor = isDarkMode ? '#333' : '#f1f1f1';
						bubble.style.color = isDarkMode ? '#fff' : '#000';
					}

					bubble.innerHTML = bubbleText;
					wrapper.appendChild(bubble);
					containerElement.appendChild(wrapper);

					// Only attach sources to last bubble of AI message
					if (msg.role !== 'user' && idx === bubbles.length - 1 && msg.sources?.length) {
						const sourceWrapper = document.createElement('div');
						sourceWrapper.style.display = 'flex';
						sourceWrapper.style.flexWrap = 'wrap';
						sourceWrapper.style.marginTop = '6px';
						sourceWrapper.style.marginLeft = '10px';
						sourceWrapper.style.gap = '6px';

						msg.sources.forEach((src) => {
							const sourceDiv = document.createElement('div');
							sourceDiv.style.display = 'flex';
							sourceDiv.style.alignItems = 'center';
							sourceDiv.style.backgroundColor = isDarkMode ? '#222' : '#eee';
							sourceDiv.style.borderRadius = '6px';
							sourceDiv.style.padding = '4px 6px';

							const icon = document.createElement('img');
							icon.src = `https://www.google.com/s2/favicons?domain=${new URL(src.url).hostname}&sz=16`;
							icon.style.width = '16px';
							icon.style.height = '16px';
							icon.style.marginRight = '4px';

							const text = document.createElement('span');
							text.style.fontSize = '12px';
							text.style.color = isDarkMode ? '#fff' : '#000';
							text.textContent = src.title || src.url;

							sourceDiv.appendChild(icon);
							sourceDiv.appendChild(text);
							sourceWrapper.appendChild(sourceDiv);
						});

						containerElement.appendChild(sourceWrapper);
					}
				});
			});

			document.body.appendChild(containerElement);

			// Capture entire chat in one go
			const canvas = await html2canvas(containerElement, {
				backgroundColor: isDarkMode ? '#000' : '#fff',
				useCORS: true,
				scale: 2,
				width: virtualWidth,
				height: containerElement.scrollHeight,
				windowWidth: virtualWidth
			});

			const imgData = canvas.toDataURL('image/png');
			const pdf = new jsPDF('p', 'mm', 'a4');
			const imgWidth = 210;
			const pageHeight = 297;
			const imgHeight = (canvas.height * imgWidth) / canvas.width;
			let heightLeft = imgHeight;
			let position = 0;

			pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
			heightLeft -= pageHeight;

			while (heightLeft > 0) {
				position = heightLeft - imgHeight;
				pdf.addPage();
				pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
				heightLeft -= pageHeight;
			}

			pdf.save(`chat-${chat.chat.title}.pdf`);
			document.body.removeChild(containerElement);
		} catch (error) {
			console.error('Error generating PDF', error);
		}
	};

	const downloadJSONExport = async () => {
		const chat = await getChatById(localStorage.token, chatId);

		if (chat) {
			let blob = new Blob([JSON.stringify([chat])], {
				type: 'application/json'
			});
			saveAs(blob, `chat-export-${Date.now()}.json`);
		}
	};

	const handleScroll = () => {
		if (scrollContainer && triggerElement && show) {
			const containerRect = scrollContainer.getBoundingClientRect();
			const triggerRect = triggerElement.getBoundingClientRect();
			
			// Check if trigger button is above the top of the sidebar viewport
			const isAboveTop = triggerRect.bottom < containerRect.top;
			// Check if trigger button is below the bottom of the sidebar viewport  
			const isBelowBottom = triggerRect.top > containerRect.bottom;
			
			if (isAboveTop || isBelowBottom) {
				show = false;
			}
		}
	};

	onMount(() => {
		// Find the sidebar scroll container
		scrollContainer = document.querySelector('.sidebar__top');
		if (scrollContainer) {
			scrollContainer.addEventListener('scroll', handleScroll);
		}
	});

	onDestroy(() => {
		if (scrollContainer) {
			scrollContainer.removeEventListener('scroll', handleScroll);
		}
	});

	$: if (show) {
		checkPinned();
	}
</script>

<Dropdown
	bind:show
	on:change={(e) => {
		if (e.detail === false) {
			onClose();
		}
	}}
>
	<Tooltip content={$i18n.t('More')}>
		<slot />
	</Tooltip>

	<div slot="content">
		<DropdownMenu.Content
			class="w-full max-w-[228px] rounded-xl z-50 bg-light-bg text-label-primary dark:text-white shadow-custom "
			sideOffset={22}
			side={$isRTL ? 'left' : 'right'}
			align="start"
			transition={flyAndScale}
		>
			<DropdownMenu.Item
				class="flex flex-row-reverse justify-between px-[16px] py-[11px] flex items-center  gap-[8px]  text-[17px] leading-[22px]  cursor-pointer hover:bg-gradient-bg-2 dark:hover:bg-gray-800 rounded-md"
				on:click={() => {
					pinHandler();
				}}
			>
				{#if pinned}
					<BookmarkSlash strokeWidth="2" />
					<div class="flex items-center">{$i18n.t('Unpin')}</div>
				{:else}
					<Bookmark strokeWidth="2" />
					<div class="flex items-center">{$i18n.t('Pin')}</div>
				{/if}
			</DropdownMenu.Item>

			<DropdownMenu.Item
				class="flex flex-row-reverse justify-between px-[16px] py-[11px] flex items-center  gap-[8px]  text-[17px] leading-[22px] cursor-pointer hover:bg-neutrals-hover dark:hover:bg-gray-800 rounded-md"
				on:click={() => {
					renameHandler();
				}}
			>
				<Pencil strokeWidth="2" />
				<div class="flex items-center">{$i18n.t('Rename')}</div>
			</DropdownMenu.Item>

			<DropdownMenu.Item
				class="flex flex-row-reverse justify-between px-[16px] py-[11px] flex items-center  gap-[8px]  text-[17px] leading-[22px] cursor-pointer hover:bg-neutrals-hover dark:hover:bg-gray-800 rounded-md"
				on:click={() => {
					cloneChatHandler();
				}}
			>
				<DocumentDuplicate strokeWidth="2" />
				<div class="flex items-center">{$i18n.t('Duplicate')}</div>
			</DropdownMenu.Item>

			<DropdownMenu.Item
				class="flex flex-row-reverse justify-between px-[16px] py-[11px] flex items-center  gap-[8px]  text-[17px] leading-[22px] cursor-pointer hover:bg-neutrals-hover dark:hover:bg-gray-800 rounded-md"
				on:click={() => {
					archiveChatHandler();
				}}
			>
				<ArchiveBox strokeWidth="2" />
				<div class="flex items-center">{$i18n.t('Archive')}</div>
			</DropdownMenu.Item>

			<DropdownMenu.Sub>
				<DropdownMenu.SubTrigger
					class="flex flex-row-reverse justify-between px-[16px] py-[11px] flex items-center  gap-[8px]  text-[17px] leading-[22px] cursor-pointer hover:bg-neutrals-hover dark:hover:bg-gray-800 rounded-md"
				>
					<Download strokeWidth="2" />

					<div class="flex items-center">{$i18n.t('Download')}</div>
				</DropdownMenu.SubTrigger>
				<DropdownMenu.SubContent
					class="w-full rounded-xl px-1 py-1.5 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-lg"
					transition={flyAndScale}
					sideOffset={8}
				>
					{#if $user?.role === 'admin' || ($user.permissions?.chat?.export ?? true)}
						<DropdownMenu.Item
							class=" px-[16px] py-[11px] flex items-center  gap-[8px]  text-[17px] leading-[22px] cursor-pointer hover:bg-neutrals-hover dark:hover:bg-gray-800 rounded-md"
							on:click={() => {
								downloadJSONExport();
							}}
						>
							<div class="flex items-center line-clamp-1">{$i18n.t('Export chat (.json)')}</div>
						</DropdownMenu.Item>
					{/if}

					<DropdownMenu.Item
						class="px-[16px] py-[11px] flex items-center  gap-[8px]  text-[17px] leading-[22px] cursor-pointer hover:bg-neutrals-hover dark:hover:bg-gray-800 rounded-md"
						on:click={() => {
							downloadTxt();
						}}
					>
						<div class="flex items-center line-clamp-1">{$i18n.t('Plain text (.txt)')}</div>
					</DropdownMenu.Item>

					<DropdownMenu.Item
						class=" px-[16px] py-[11px] flex items-center  gap-[8px]  text-[17px] leading-[22px] cursor-pointer hover:bg-neutrals-hover dark:hover:bg-gray-800 rounded-md"
						on:click={() => {
							downloadPdf();
						}}
					>
						<div class="flex items-center line-clamp-1">{$i18n.t('PDF document (.pdf)')}</div>
					</DropdownMenu.Item>
				</DropdownMenu.SubContent>
			</DropdownMenu.Sub>
			{#if $user?.role === 'admin' || ($user.permissions?.chat?.share ?? true)}
				<DropdownMenu.Item
					class="flex flex-row-reverse justify-between px-[16px] py-[11px] flex items-center  gap-[8px]  text-[17px] leading-[22px] cursor-pointer hover:bg-neutrals-hover dark:hover:bg-gray-800  rounded-md"
					on:click={() => {
						shareHandler();
					}}
				>
					<Share />
					<div class="flex items-center">{$i18n.t('Share')}</div>
				</DropdownMenu.Item>
			{/if}
			<DropdownMenu.Item
				class="flex flex-row-reverse justify-between px-[16px] py-[11px] flex items-center  gap-[8px]  text-[17px] leading-[22px] cursor-pointer hover:bg-neutrals-hover dark:hover:bg-gray-800 rounded-md"
				on:click={() => {
					deleteHandler();
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="20"
					height="20"
					viewBox="0 0 20 20"
					fill="none"
				>
					<path
						d="M16.875 3.75H13.75V3.125C13.75 2.62772 13.5525 2.15081 13.2008 1.79917C12.8492 1.44754 12.3723 1.25 11.875 1.25H8.125C7.62772 1.25 7.15081 1.44754 6.79917 1.79917C6.44754 2.15081 6.25 2.62772 6.25 3.125V3.75H3.125C2.95924 3.75 2.80027 3.81585 2.68306 3.93306C2.56585 4.05027 2.5 4.20924 2.5 4.375C2.5 4.54076 2.56585 4.69973 2.68306 4.81694C2.80027 4.93415 2.95924 5 3.125 5H3.75V16.25C3.75 16.5815 3.8817 16.8995 4.11612 17.1339C4.35054 17.3683 4.66848 17.5 5 17.5H15C15.3315 17.5 15.6495 17.3683 15.8839 17.1339C16.1183 16.8995 16.25 16.5815 16.25 16.25V5H16.875C17.0408 5 17.1997 4.93415 17.3169 4.81694C17.4342 4.69973 17.5 4.54076 17.5 4.375C17.5 4.20924 17.4342 4.05027 17.3169 3.93306C17.1997 3.81585 17.0408 3.75 16.875 3.75ZM7.5 3.125C7.5 2.95924 7.56585 2.80027 7.68306 2.68306C7.80027 2.56585 7.95924 2.5 8.125 2.5H11.875C12.0408 2.5 12.1997 2.56585 12.3169 2.68306C12.4342 2.80027 12.5 2.95924 12.5 3.125V3.75H7.5V3.125ZM15 16.25H5V5H15V16.25ZM8.75 8.125V13.125C8.75 13.2908 8.68415 13.4497 8.56694 13.5669C8.44973 13.6842 8.29076 13.75 8.125 13.75C7.95924 13.75 7.80027 13.6842 7.68306 13.5669C7.56585 13.4497 7.5 13.2908 7.5 13.125V8.125C7.5 7.95924 7.56585 7.80027 7.68306 7.68306C7.80027 7.56585 7.95924 7.5 8.125 7.5C8.29076 7.5 8.44973 7.56585 8.56694 7.68306C8.68415 7.80027 8.75 7.95924 8.75 8.125ZM12.5 8.125V13.125C12.5 13.2908 12.4342 13.4497 12.3169 13.5669C12.1997 13.6842 12.0408 13.75 11.875 13.75C11.7092 13.75 11.5503 13.6842 11.4331 13.5669C11.3158 13.4497 11.25 13.2908 11.25 13.125V8.125C11.25 7.95924 11.3158 7.80027 11.4331 7.68306C11.5503 7.56585 11.7092 7.5 11.875 7.5C12.0408 7.5 12.1997 7.56585 12.3169 7.68306C12.4342 7.80027 12.5 7.95924 12.5 8.125Z"
						fill="#C2451E"
					/>
				</svg>
				<div class="flex items-center text-errorTone">{$i18n.t('Delete')}</div>
			</DropdownMenu.Item>

			<!--<hr class="border-gray-100 dark:border-gray-850 my-0.5" />

			<div class="flex p-1">
				<Tags
					{chatId}
					on:add={(e) => {
						dispatch('tag', {
							type: 'add',
							name: e.detail.name
						});

						show = false;
					}}
					on:delete={(e) => {
						dispatch('tag', {
							type: 'delete',
							name: e.detail.name
						});

						show = false;
					}}
					on:close={() => {
						show = false;
						onClose();
					}}
				/>
			</div>-->
		</DropdownMenu.Content>
	</div>
</Dropdown>
