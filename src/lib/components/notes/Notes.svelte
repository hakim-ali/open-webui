<script lang="ts">
	import { toast } from 'svelte-sonner';
	import fileSaver from 'file-saver';
	const { saveAs } = fileSaver;

	import jsPDF from 'jspdf';
	import html2canvas from 'html2canvas-pro';

	import dayjs from '$lib/dayjs';
	import duration from 'dayjs/plugin/duration';
	import relativeTime from 'dayjs/plugin/relativeTime';

	dayjs.extend(duration);
	dayjs.extend(relativeTime);

	async function loadLocale(locales) {
		for (const locale of locales) {
			try {
				dayjs.locale(locale);
				break; // Stop after successfully loading the first available locale
			} catch (error) {
				console.error(`Could not load locale '${locale}':`, error);
			}
		}
	}

	// Assuming $i18n.languages is an array of language codes
	$: loadLocale($i18n.languages);

	import { goto } from '$app/navigation';
	import { onMount, getContext, onDestroy } from 'svelte';
	import { WEBUI_NAME, config, prompts as _prompts, user, mobile } from '$lib/stores';

	import { createNewNote, deleteNoteById, getNotes } from '$lib/apis/notes';
	import { capitalizeFirstLetter } from '$lib/utils';

	import EllipsisVertical from '../icons/EllipsisVertical.svelte';
	import DeleteConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';
	import Search from '../icons/Search.svelte';
	import Plus from '../icons/Plus.svelte';
	import ChevronRight from '../icons/ChevronRight.svelte';
	import Spinner from '../common/Spinner.svelte';
	import Tooltip from '../common/Tooltip.svelte';
	import NoteMenu from './Notes/NoteMenu.svelte';
	import FilesOverlay from '../chat/MessageInput/FilesOverlay.svelte';
	import { marked } from 'marked';

	const i18n = getContext('i18n');
	let loaded = false;

	let importFiles = '';
	let query = '';

	let notes = [];
	let selectedNote = null;

	let showDeleteConfirm = false;

	const init = async () => {
		notes = await getNotes(localStorage.token);
	};

	const createNoteHandler = async () => {
		const res = await createNewNote(localStorage.token, {
			title: $i18n.t('New Note'),
			data: {
				content: {
					json: null,
					html: '',
					md: ''
				}
			},
			meta: null,
			access_control: null
		}).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			goto(`/notes/${res.id}`);
		}
	};

	const downloadHandler = async (type) => {
		console.log('downloadHandler', type);
		console.log('selectedNote', selectedNote);
		if (type === 'md') {
			const blob = new Blob([selectedNote.data.content.md], { type: 'text/markdown' });
			saveAs(blob, `${selectedNote.title}.md`);
		} else if (type === 'pdf') {
			await downloadPdf(selectedNote);
		}
	};

	const downloadPdf = async (note) => {
		try {
			// Define a fixed virtual screen size
			const virtualWidth = 1024; // Fixed width (adjust as needed)
			const virtualHeight = 1400; // Fixed height (adjust as needed)

			// STEP 1. Get a DOM node to render
			const html = note.data?.content?.html ?? '';
			let node;
			if (html instanceof HTMLElement) {
				node = html;
			} else {
				// If it's HTML string, render to a temporary hidden element
				node = document.createElement('div');
				node.innerHTML = html;
				document.body.appendChild(node);
			}

			// Render to canvas with predefined width
			const canvas = await html2canvas(node, {
				useCORS: true,
				scale: 2, // Keep at 1x to avoid unexpected enlargements
				width: virtualWidth, // Set fixed virtual screen width
				windowWidth: virtualWidth, // Ensure consistent rendering
				windowHeight: virtualHeight
			});

			// Remove hidden node if needed
			if (!(html instanceof HTMLElement)) {
				document.body.removeChild(node);
			}

			const imgData = canvas.toDataURL('image/png');

			// A4 page settings
			const pdf = new jsPDF('p', 'mm', 'a4');
			const imgWidth = 210; // A4 width in mm
			const pageHeight = 297; // A4 height in mm

			// Maintain aspect ratio
			const imgHeight = (canvas.height * imgWidth) / canvas.width;
			let heightLeft = imgHeight;
			let position = 0;

			pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
			heightLeft -= pageHeight;

			// Handle additional pages
			while (heightLeft > 0) {
				position -= pageHeight;
				pdf.addPage();

				pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
				heightLeft -= pageHeight;
			}

			pdf.save(`${note.title}.pdf`);
		} catch (error) {
			console.error('Error generating PDF', error);

			toast.error(`${error}`);
		}
	};

	const deleteNoteHandler = async (id) => {
		const res = await deleteNoteById(localStorage.token, id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			init();
		}
	};

	const inputFilesHandler = async (inputFiles) => {
		// Check if all the file is a markdown file and extract name and content

		for (const file of inputFiles) {
			if (file.type !== 'text/markdown') {
				toast.error($i18n.t('Only markdown files are allowed'));
				return;
			}

			const reader = new FileReader();
			reader.onload = async (event) => {
				const content = event.target.result;
				let name = file.name.replace(/\.md$/, '');

				if (typeof content !== 'string') {
					toast.error($i18n.t('Invalid file content'));
					return;
				}

				// Create a new note with the content
				const res = await createNewNote(localStorage.token, {
					title: name,
					data: {
						content: {
							json: null,
							html: marked.parse(content ?? ''),
							md: content
						}
					},
					meta: null,
					access_control: null
				}).catch((error) => {
					toast.error(`${error}`);
					return null;
				});

				if (res) {
					init();
				}
			};

			reader.readAsText(file);
		}
	};

	let dragged = false;

	const onDragOver = (e) => {
		e.preventDefault();

		// Check if a file is being dragged.
		if (e.dataTransfer?.types?.includes('Files')) {
			dragged = true;
		} else {
			dragged = false;
		}
	};

	const onDragLeave = () => {
		dragged = false;
	};

	const onDrop = async (e) => {
		e.preventDefault();
		console.log(e);

		if (e.dataTransfer?.files) {
			const inputFiles = Array.from(e.dataTransfer?.files);
			if (inputFiles && inputFiles.length > 0) {
				console.log(inputFiles);
				inputFilesHandler(inputFiles);
			}
		}

		dragged = false;
	};

	let scrollBox;
	function scrollToTop() {
		scrollBox.scrollTo({ top: 0, behavior: 'smooth' });
	}

	onDestroy(() => {
		console.log('destroy');
		const dropzoneElement = document.getElementById('notes-container');

		if (dropzoneElement) {
			dropzoneElement?.removeEventListener('dragover', onDragOver);
			dropzoneElement?.removeEventListener('drop', onDrop);
			dropzoneElement?.removeEventListener('dragleave', onDragLeave);
		}
	});

	onMount(async () => {
		await init();
		loaded = true;

		const dropzoneElement = document.getElementById('notes-container');

		dropzoneElement?.addEventListener('dragover', onDragOver);
		dropzoneElement?.addEventListener('drop', onDrop);
		dropzoneElement?.addEventListener('dragleave', onDragLeave);
	});
</script>

<svelte:head>
	<title>
		{$i18n.t('Notes')} • {$WEBUI_NAME}
	</title>
</svelte:head>

<FilesOverlay show={dragged} />

<div id="notes-container" class="relative w-full min-h-full h-full">
	{#if loaded}
		<DeleteConfirmDialog
			bind:show={showDeleteConfirm}
			title={$i18n.t('Delete note?')}
			on:confirm={() => {
				deleteNoteHandler(selectedNote.id);
				showDeleteConfirm = false;
			}}
		>
			<div class="pb-[16px] text-neutrals-700 text-[16px] leading-[24px]">
				{$i18n.t('This will delete')} <span class="  font-bold">{selectedNote.title}</span>.
			</div>
		</DeleteConfirmDialog>

		<div
			class="pt-[136px] max-w-[800px] mx-auto @container h-full overflow-y-auto"
			bind:this={scrollBox}
		>
			{#if Object.keys(notes).length > 0}
				<div>
					{#each Object.keys(notes) as timeRange}
						<!--<div class="w-full text-xs text-gray-500 dark:text-gray-500 font-medium pb-2.5">
							{$i18n.t(timeRange)}
						</div>-->

						<div
							class="gap-[12px] grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 px-[48px] sm:px-[16px] lg:px-[0px]"
						>
							{#each notes[timeRange] as note, idx (note.id)}
								<div
									class=" flex cursor-pointer w-full p-[16px] mb-[12px] bg-white/88 dark:bg-gray-850 dark:hover:bg-white/5 hover:bg-black/5 rounded-[12px] transition"
								>
									<div class=" flex flex-1 space-x-4 cursor-pointer w-full">
										<a href={`/notes/${note.id}`} class="w-full flex flex-col justify-between">
											<div class="flex-1">
												<div class="flex items-center gap-2 self-center justify-between">
													<div
														class="mb-[12px] font-bold text-[14px] leading-[22px] text-neutrals-800 capitalize"
													>
														{note.title}
													</div>

													<div>
														<NoteMenu
															onDownload={(type) => {
																selectedNote = note;

																downloadHandler(type);
															}}
															onDelete={() => {
																selectedNote = note;
																showDeleteConfirm = true;
															}}
														>
															<button
																class="self-center w-fit text-sm p-1 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
																type="button"
															>
																<EllipsisVertical className="size-5" />
															</button>
														</NoteMenu>
													</div>
												</div>

												<div
													class="font-medium font-bold text-[14px] leading-[22px] mb-[24px] text-neutrals-500 line-clamp-5"
												>
													{#if note.data?.content?.md}
														{note.data?.content?.md}
													{:else}
														{$i18n.t('No content')}
													{/if}
												</div>
											</div>

											<div class="font-medium text-[12px] leading-[20px] text-neutrals-500">
												<div>
													{dayjs(note.updated_at / 1000000).fromNow()}
												</div>
												<!--<Tooltip
													content={note?.user?.email ?? $i18n.t('Deleted User')}
													className="flex shrink-0"
													placement="top-start"
												>
													<div class="shrink-0 text-gray-500">
														{$i18n.t('By {{name}}', {
															name: capitalizeFirstLetter(
																note?.user?.name ?? note?.user?.email ?? $i18n.t('Deleted User')
															)
														})}
													</div>
												</Tooltip>-->
											</div>
										</a>
									</div>
								</div>
							{/each}
						</div>
					{/each}
				</div>
			{:else}
				<div class="w-full h-full flex flex-col items-center justify-center">
					<div class="pb-20 text-center">
						<div class=" text-xl font-medium text-gray-400 dark:text-gray-600">
							{$i18n.t('No Notes')}
						</div>

						<div class="mt-1 text-sm text-gray-300 dark:text-gray-700">
							{$i18n.t('Create your first note by clicking on the plus button below.')}
						</div>
					</div>
				</div>
			{/if}
		</div>

		<div
			class="pb-[48px] pt-[20px] absolute left-0 bottom-0 w-full flex justify-center background-gradient-bg2"
		>
			<button
				class="cursor-pointer relative z-50 flex justify-center items-center border border-neutrals-100 rounded-full w-[32px] h-[32px]"
				on:click={scrollToTop}
				><svg
					xmlns="http://www.w3.org/2000/svg"
					width="18"
					height="18"
					viewBox="0 0 18 18"
					fill="none"
				>
					<path
						d="M8.43737 16.1243V4.0075L4.7783 7.65512L3.99512 6.87194L8.99987 1.86719L14.0046 6.87194L13.2214 7.67387L9.56237 4.01463V16.1243H8.43737Z"
						fill="#36383B"
					/>
				</svg></button
			>
		</div>
		<!-- {#if $user?.role === 'admin'}
		<div class=" flex justify-end w-full mb-3">
			<div class="flex space-x-2">
				<input
					id="notes-import-input"
					bind:files={importFiles}
					type="file"
					accept=".md"
					hidden
					on:change={() => {
						console.log(importFiles);

						const reader = new FileReader();
						reader.onload = async (event) => {
							console.log(event.target.result);
						};

						reader.readAsText(importFiles[0]);
					}}
				/>

				<button
					class="flex text-xs items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-gray-200 transition"
					on:click={() => {
						const notesImportInputElement = document.getElementById('notes-import-input');
						if (notesImportInputElement) {
							notesImportInputElement.click();
						}
					}}
				>
					<div class=" self-center mr-2 font-medium line-clamp-1">{$i18n.t('Import Notes')}</div>

					<div class=" self-center">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 16 16"
							fill="currentColor"
							class="w-4 h-4"
						>
							<path
								fill-rule="evenodd"
								d="M4 2a1.5 1.5 0 0 0-1.5 1.5v9A1.5 1.5 0 0 0 4 14h8a1.5 1.5 0 0 0 1.5-1.5V6.621a1.5 1.5 0 0 0-.44-1.06L9.94 2.439A1.5 1.5 0 0 0 8.878 2H4Zm4 9.5a.75.75 0 0 1-.75-.75V8.06l-.72.72a.75.75 0 0 1-1.06-1.06l2-2a.75.75 0 0 1 1.06 0l2 2a.75.75 0 1 1-1.06 1.06l-.72-.72v2.69a.75.75 0 0 1-.75.75Z"
								clip-rule="evenodd"
							/>
						</svg>
					</div>
				</button>
			</div>
		</div>
	{/if} -->
	{:else}
		<div class="w-full h-full flex justify-center items-center">
			<Spinner />
		</div>
	{/if}
</div>
<div class="absolute z-50 bottom-0 right-0 p-5 w-[50px] flex justify-end">
	<div class="flex gap-0.5 justify-end w-full">
		<Tooltip content={$i18n.t('Create Note')}>
			<button
				class="cursor-pointer p-2.5 flex rounded-full border border-gray-50 bg-primary-400 dark:border-none dark:bg-gray-850 hover:bg-gray-50 dark:hover:bg-gray-800 transition shadow-xl"
				type="button"
				on:click={async () => {
					createNoteHandler();
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="18"
					height="18"
					viewBox="0 0 18 18"
					fill="none"
				>
					<path
						d="M8.4375 9.5625H4.125V8.4375H8.4375V4.125H9.5625V8.4375H13.875V9.5625H9.5625V13.875H8.4375V9.5625Z"
						fill="white"
					/>
				</svg>
			</button>
		</Tooltip>

		<!-- <button
				class="cursor-pointer p-2.5 flex rounded-full hover:bg-gray-100 dark:hover:bg-gray-850 transition shadow-xl"
			>
				<SparklesSolid className="size-4" />
			</button> -->
	</div>
</div>
