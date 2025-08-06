<script lang="ts">
	import { documentsArray } from '$lib/stores';
	import { onMount, getContext } from 'svelte';
	import { isRTL } from '$lib/i18n';
	import ChevronUp from '$lib/components/icons/ChevronUp.svelte';
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import FolderIcon from '$lib/components/icons/FolderIcon.svelte';
	import GovKno from '$lib/components/icons/GovKno.svelte';
	import KnoDocs from '$lib/components/icons/KnoDocs.svelte';

	const i18n = getContext('i18n');

	let receivedStoreData = [];
	let documents = [];
	let loading = true;

	// Subscribe to store data
	documentsArray.subscribe(value => {
		receivedStoreData = value;
		if (value && value.documents) {
			documents = value.documents;
			loading = false;
		}
	});

	// Sorting state
	let orderBy: string = 'title';
	let direction: 'asc' | 'desc' = 'asc';

	function setSortKey(key: string) {
		if (orderBy === key) {
			direction = direction === 'asc' ? 'desc' : 'asc';
		} else {
			orderBy = key;
			direction = 'asc';
		}
	}

	$: sortedDocuments = [...documents].sort((a, b) => {
		let aVal, bVal;

		switch (orderBy) {
			case 'title':
				aVal = a.title || '';
				bVal = b.title || '';
				return direction === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
			case 'summary':
				aVal = $isRTL ? (a.summaryAr || '') : (a.summaryEn || '');
				bVal = $isRTL ? (b.summaryAr || '') : (b.summaryEn || '');
				return direction === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
			default:
				return 0;
		}
	});

</script>

<div class="mt-0.5 mb-2 gap-2 flex flex-row py-6">
	<div class="flex md:self-center px-0.5">
		<GovKno />
	</div>
	<div class="flex md:self-center text-lg font-medium px-0.5">
		{$i18n?.t('Whole of Knowledge Repository') || 'Whole of Knowledge Repository'}
	</div>
</div>
<div class="mb-3 gap-2 flex flex-row">
	<div class="flex md:self-center  font-normal px-0.5">
		{$i18n?.t('Government Entities') || 'Government Entities'}
	</div>
</div>

{#if loading}
	<div class="text-center text-sm text-gray-500 dark:text-gray-400 py-8">
		{$i18n?.t('Loading documents...') || 'Loading documents...'}
	</div>
{:else if documents.length === 0}
	<div class="text-center text-sm text-gray-500 dark:text-gray-400 py-8">
		{$i18n?.t('No documents found') || 'No documents found'}
	</div>
{:else}
	<div
		class="scrollbar-hidden relative whitespace-nowrap overflow-x-auto max-w-full rounded-sm pt-0.5"
	>
		<table
			class="w-full text-sm text-left text-gray-500 dark:text-gray-400 table-auto max-w-full rounded-sm"
		>
			<thead
				class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-850 dark:text-gray-400 -translate-y-0.5"
			>
				<tr class="">
					<th
						scope="col"
						class="px-3 py-1.5 cursor-pointer select-none"
						on:click={() => setSortKey('title')}
					>
						<div class="flex gap-1.5 items-center">
							{$i18n?.t('Name') || 'Name'}
							{#if orderBy === 'title'}
								<span class="font-normal">
									{#if direction === 'asc'}
										<ChevronUp className="size-3" />
									{:else}
										<ChevronDown className="size-3" />
									{/if}
								</span>
							{:else}
								<span class="invisible">
									<ChevronUp className="size-3" />
								</span>
							{/if}
						</div>
					</th>

					<th
						scope="col"
						class="px-3 py-1.5 cursor-pointer select-none"
						on:click={() => setSortKey('summary')}
					>
						<div class="flex gap-1.5 items-center">
							{$i18n?.t('Description') || 'Description'}
							{#if orderBy === 'summary'}
								<span class="font-normal">
									{#if direction === 'asc'}
										<ChevronUp className="size-3" />
									{:else}
										<ChevronDown className="size-3" />
									{/if}
								</span>
							{:else}
								<span class="invisible">
									<ChevronUp className="size-3" />
								</span>
							{/if}
						</div>
					</th>
				</tr>
			</thead>
			<tbody class="">
				{#each sortedDocuments as document (document.title)}
					<tr
						class="bg-white dark:bg-gray-900 dark:border-gray-850 text-xs cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition"
					>
						<td class="py-3 pl-3 flex flex-col">
							<div class="flex flex-col items-start gap-0.5 h-full">
								<div class="flex flex-col h-full">
									<div class="font-semibold text-gray-600 dark:text-gray-400 flex-1 flex items-center gap-4">
										<KnoDocs />
										{document.title}
									</div>
								</div>
							</div>
						</td>

						<td class="px-3 py-3 text-left font-medium text-gray-900 dark:text-white ">
							<Tooltip  content={$isRTL ? document.summaryAr : document.summaryEn}>
								<div class="max-w-md truncate">
									{$isRTL ? document.summaryAr : document.summaryEn}
								</div>
							</Tooltip>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}