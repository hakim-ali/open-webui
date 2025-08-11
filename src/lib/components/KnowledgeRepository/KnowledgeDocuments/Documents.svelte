<script lang="ts">
	import { documentsArray, mobile } from '$lib/stores';
	import { onMount, getContext } from 'svelte';
	import { isRTL } from '$lib/i18n';
	import ChevronUp from '$lib/components/icons/ChevronUp.svelte';
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import GovKno from '$lib/components/icons/GovKno.svelte';
	import KnoDocs from '$lib/components/icons/KnoDocs.svelte';
	import { goto } from '$app/navigation';
	import Info from '$lib/components/icons/Info.svelte';
	import Paper from '$lib/components/icons/Paper.svelte';
	import Collapsible from '$lib/components/common/Collapsible.svelte';

	const i18n = getContext('i18n');

	let receivedStoreData: any = [];
	let documents: any = [];
	let loading = true;

	// Subscribe to store data
	documentsArray.subscribe((value) => {
		receivedStoreData = value;
		if (value && value.documents) {
			documents = value.documents;
			loading = false;
		}
	});
	let openStates = Array(documents.length).fill(false);
	function toggle(index) {
		openStates = openStates.map((_, i) => (i === index ? !openStates[i] : false));
	}
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
				aVal = $isRTL ? a.summaryAr || '' : a.summaryEn || '';
				bVal = $isRTL ? b.summaryAr || '' : b.summaryEn || '';
				return direction === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
			default:
				return 0;
		}
	});
</script>

<!-- <div class="mt-0.5 mb-2 gap-2 flex flex-row py-6">
	<div class="flex md:self-center px-0.5">
		<GovKno />
	</div>
	<div class="flex md:self-center text-lg font-medium px-0.5">
		{$i18n?.t('Gov Knowledge Repository') || 'Gov Knowledge Repository'}
	</div>
</div> -->
<div class="my-5 flex flex-row">
	<div
		class="flex md:self-center text-sm text-gray-500 font-normal px-0.5 cursor-pointer"
		on:click={() => goto('/knowledgeRepository')}
	>
		{$i18n?.t('Government Entities') || 'Government Entities'} >
	</div>
	<div class="flex md:self-center text-sm text-gray-1000 font-normal px-0.5 dark:text-white">
		{receivedStoreData?.name}
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
		class="h-[calc(100dvh-200px)] bg-white dark:bg-[#072D5A4D] scrollbar-hidden relative whitespace-nowrap overflow-x-auto max-w-full rounded-md pt-0.5 flex-col gap-10"
	>
		{#if $mobile}
			<table
				class="table-fixed w-full text-sm text-left text-gray-500 dark:text-gray-400 table-auto max-w-full rounded-sm"
			>
				<thead
					class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-[#072D5A4D] dark:text-gray-400 -translate-y-0.5"
				>
					<tr class="">
						<th
							scope="col"
							class="px-3 py-3 cursor-pointer select-none"
							on:click={() => setSortKey('title')}
						>
							<div class="flex gap-1.5 items-center ml-2 gap-3 capitalize">
								<Paper />
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
					</tr>
				</thead>
				<tbody class="w-full">
					{#each sortedDocuments as document, i (document.title)}
						<tr
							class="bg-white dark:bg-[#072D5A4D] dark:border-gray-850 text-xs cursor-pointer hover:bg-gradient-bg-2 dark:hover:bg-gray-850 transition"
						>
							<td class="py-3 pl-3">
								<!--							<div class="flex flex-col gap-0.5 h-full w-full">-->
								<Collapsible bind:open={openStates[i]} className="w-full space-y-1 gap-4">
									<!-- Header: Flex row for title + chevron -->
									<div
										class="flex items-center justify-between w-full font-semibold text-gray-600 dark:text-gray-400 gap-1"
									>
										<!-- Left: Icon + Title -->
										<div class="flex items-center space-x-2 truncate">
											<KnoDocs />
											<div class="truncate max-w-[250px]">
												{document.title}
											</div>
										</div>

										<!-- Right: Chevron -->
										<div class="flex items-center">
											{#if openStates[i]}
												<ChevronUp strokeWidth="3.5" className="size-3.5" />
											{:else}
												<ChevronDown strokeWidth="3.5" className="size-3.5" />
											{/if}
										</div>
									</div>

									<!-- Collapsible content -->
									<div slot="content">
										<div
											class="mt-2 p-[12px] justify-center gap-4 text-wrap font-semibold text-gray-600 dark:text-gray-400 flex-1 flex items-center dark:bg-[#072D5A4D] rounded-[6px] border border-[color:var(--Outline-Outline-default,#E5EBF3)] dark:border-[color:var(--Outline-Outline-default,#2D3642)] bg-[var(--Background-background,#FBFCFC)] shadow-[0_8px_8px_0_rgba(0,0,0,0.08)]"
										>
											{$isRTL ? document.summaryAr : document.summaryEn}
										</div>
									</div>
								</Collapsible>
								<!--							</div>-->
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{:else}
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
							<div class="flex gap-1.5 items-center ml-2.5 gap-5 capitalize">
								<Paper />
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
							<div class="flex gap-1.5 items-center capitalize">
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
							class="bg-white dark:bg-[#072D5A4D] dark:border-gray-850 text-xs cursor-pointer hover:bg-gradient-bg-2 dark:hover:bg-gray-850 transition"
						>
							<td class="py-3 pl-3 flex flex-col">
								<div class="flex flex-col items-start gap-0.5 h-full">
									<div class="flex flex-col h-full">
										<div
											class="font-semibold text-gray-600 dark:text-gray-400 flex-1 flex items-center gap-4"
										>
											<KnoDocs />
											{document.title}
										</div>
									</div>
								</div>
							</td>

							<td class="px-3 py-3 text-left font-medium text-gray-900 dark:text-white">
								<Tooltip
									content={$isRTL ? document.summaryAr : document.summaryEn}
									placement="bottom"
								>
									<div class="max-w-md truncate">
										{$isRTL ? document.summaryAr : document.summaryEn}
									</div>
								</Tooltip>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{/if}
	</div>
{/if}
