<script lang="ts">
	import { onMount, getContext, setContext } from 'svelte';
	import { isRTL } from '$lib/i18n';
	import dayjs from 'dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';

	dayjs.extend(relativeTime);

	const i18n = getContext('i18n');

	import ChevronUp from '$lib/components/icons/ChevronUp.svelte';
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import GovKno from '$lib/components/icons/GovKno.svelte';
	import { getKnowledgeRepos } from '$lib/apis/gov-repository';
	import FolderIcon from '$lib/components/icons/FolderIcon.svelte';
	import { goto } from '$app/navigation';
	import { documentsArray } from '$lib/stores';

	// Types for the government departments data
	type Document = {
		title: string;
		summaryEn: string;
		summaryAr: string;
	};

	type Department = {
		name: string;
		nameAr: string;
		documents: Document[];
	};

	// Data state
	let departments: Department[] = [];
	let repositories = [];
	let loading = true;
	let error = null;

	// Load data on component mount
	onMount(async () => {
		try {
			loading = true;
			error = null;
			
			// Get token from localStorage or context
			const token = localStorage.getItem('token') || '';
			
			// Call the API - using a default ID for now, adjust as needed
			const data = await getKnowledgeRepos(token, 'default');
			
			if (data) {
				// Parse the data and transform it for the table
				departments = data;
				repositories = departments.map(dept => ({
					id: dept.name.replace(/\s+/g, ""), // Using name as ID for now
					name: dept.name,
					nameAr: dept.nameAr,
					lastModified: Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000, // Random date within last 30 days
					totalFiles: dept.documents.length,
					documents: dept.documents
				}));
			} else {
				error = 'Failed to load repositories';
			}
		} catch (err) {
			console.error('Error loading repositories:', err);
			error = err.message || 'Failed to load repositories';
		} finally {
			loading = false;
		}
	});
	const onClickDepartment= (e: any, repository: any)=> {
		e.preventDefault();
		documentsArray.set(repository);
		goto(`/knowledgeRepository/${repository.id}`)}
	let page = 1;
	$: paginatedRepositories = sortedRepositories.slice((page - 1) * 10, page * 10);

	let orderBy: string = 'lastModified';
	let direction: 'asc' | 'desc' = 'desc';

	function setSortKey(key: string) {
		if (orderBy === key) {
			direction = direction === 'asc' ? 'desc' : 'asc';
		} else {
			orderBy = key;
			if (key === 'name') {
				direction = 'asc';
			} else {
				direction = 'desc';
			}
		}
		page = 1;
	}
	$: sortedRepositories = [...repositories].sort((a, b) => {
		let aVal, bVal;

		switch (orderBy) {
			case 'name':
				aVal = a.name || '';
				bVal = b.name || '';
				return direction === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
			case 'lastModified':
				aVal = a.lastModified;
				bVal = b.lastModified;
				return direction === 'asc' ? aVal - bVal : bVal - aVal;
			case 'totalFiles':
				aVal = a.totalFiles;
				bVal = b.totalFiles;
				return direction === 'asc' ? aVal - bVal : bVal - aVal;
			default:
				return 0;
		}
	});
</script>

<div class="mt-0.5 mb-2 gap-2 flex flex-row py-6">
	<div class="flex md:self-center text-lg font-medium px-0.5">
		<GovKno />
	</div>
	<div class="flex md:self-center text-lg font-medium px-0.5">
		{$i18n?.t('Whole of Knowledge Repository') || 'Whole of Knowledge Repository'}
	</div>
</div>
<div class="mb-3 gap-2 flex flex-row">
	<div class="flex md:self-center text-lg font-bold px-0.5">
		{$i18n?.t('Government Entities') || 'Government Entities'}
	</div>
</div>

{#if loading}
	<div class="text-center text-sm text-gray-500 dark:text-gray-400 py-8">
		{$i18n?.t('Loading repositories...') || 'Loading repositories...'}
	</div>
{:else if error}
	<div class="text-center text-sm text-red-500 dark:text-red-400 py-8">
		{error}
	</div>
{:else}
	<div
		class="scrollbar-hidden relative whitespace-nowrap overflow-x-auto max-w-full rounded-sm pt-0.5"
	>
		{#if (repositories ?? []).length === 0}
			<div class="text-center text-xs text-gray-500 dark:text-gray-400 py-1">
				{$i18n?.t('No repositories found') || 'No repositories found'}
			</div>
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
							on:click={() => setSortKey('name')}
						>
							<div class="flex gap-1.5 items-center">
								{$i18n?.t('Name') || 'Name'}
								{#if orderBy === 'name'}
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
							class="px-3 py-1.5 text-right cursor-pointer select-none w-fit"
							on:click={() => setSortKey('lastModified')}
						>
							<div class="flex gap-1.5 items-center justify-end">
								{$i18n?.t('Last Modified') || 'Last Modified'}
								{#if orderBy === 'lastModified'}
									<span class="font-normal">
										{#if direction === 'asc'}
											<ChevronUp className="size-3" />
										{:else}
											<ChevronDown className="size-3" />
										{/if}
									</span>
								{:else}
									<span class="invisible">
										<ChevronUp className="size-2" />
									</span>
								{/if}
							</div>
						</th>

						<th
							scope="col"
							class="px-3 py-1.5 text-right cursor-pointer select-none w-0"
							on:click={() => setSortKey('totalFiles')}
						>
							<div class="flex gap-1.5 items-center justify-end">
								{$i18n?.t('Total Files') || 'Total Files'}
								{#if orderBy === 'totalFiles'}
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
					{#each paginatedRepositories as repository (repository.id)}
						<tr
							class="bg-white dark:bg-gray-900 dark:border-gray-850 text-xs cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition"
						on:click={(e)=>onClickDepartment(e, repository) }
						>
							<td class="py-1 pl-3 flex flex-col">
								<div class="flex flex-col items-start gap-0.5 h-full">
									<div class="flex flex-col h-full">
										<div class="font-semibold text-gray-600 dark:text-gray-400 flex-1">
											  {$isRTL ?repository.nameAr :repository.name}
										</div>
									</div>
								</div>
							</td>

							<td class="px-3 py-1 text-right font-medium text-gray-900 dark:text-white w-max">
								{dayjs(repository.lastModified).fromNow()}
							</td>

							<td class="px-3 py-1 text-right font-medium">
								{repository.totalFiles} items
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{/if}
	</div>

	{#if repositories.length > 10}
		<div class="mt-4">
			<!-- Pagination component can be added here if needed -->
		</div>
	{/if}
{/if}