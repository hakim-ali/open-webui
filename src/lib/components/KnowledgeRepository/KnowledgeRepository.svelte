<script lang="ts">
	import { onMount, getContext, setContext } from 'svelte';
	import { isRTL } from '$lib/i18n';
	import dayjs from 'dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';

	dayjs.extend(relativeTime);

	const i18n = getContext('i18n');

	import ChevronUp from '$lib/components/icons/ChevronUp.svelte';
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import GovKno from '$lib/components/icons/GovKno.svelte';
	import { getKnowledgeRepos } from '$lib/apis/govRepository';
	import { goto } from '$app/navigation';
	import { documentsArray, mobile } from '$lib/stores';
	import KnoFolder from '../icons/knoFolder.svelte';
	import Paper from '$lib/components/icons/Paper.svelte';

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
				repositories = departments.map((dept, index) => ({
					id: index + 1, // Using name as ID for now
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
	const onClickDepartment = (e: any, repository: any) => {
		e.preventDefault();
		documentsArray.set(repository);
		goto(`/knowledgeRepository/${repository.id}`);
	};
	let page = 1;
	$: paginatedRepositories = repositories.slice((page - 1) * 10, page * 10);

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

<div class="my-5 gap-2 flex flex-row">
	<div class="flex md:self-center text-md font-bold px-0.5">
		{$i18n?.t('Government Entities') || 'Government Entities'}
	</div>
</div>

{#if loading}
	<div class="text-center text-sm text-gray-500 dark:text-gray-400 py-8">
		{$i18n?.t('Loading repositories...') || 'Loading repositories...'}
	</div>
{:else if error}
	<div class="text-center text-sm text-red-500 dark:text-red-400 py-8">
		{$i18n?.t(error)}
	</div>
{:else}
	<div
		class="h-[calc(100dvh-200px)] bg-white dark:bg-[#072D5A4D] scrollbar-hidden relative whitespace-nowrap overflow-x-auto max-w-full rounded-lg pt-0.5"
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
					class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-[#072D5A4D] dark:text-gray-400 -translate-y-0.5"
				>
					<tr class="">
						<th
							scope="col"
							class="px-3 py-3 cursor-pointer select-none w-1/3 p-2 text-left"
							on:click={() => setSortKey('name')}
						>
							<div class="flex gap-1.5 items-center ml-3 capitalize {$mobile ? 'gap-2' : 'gap-6'}">
								<Paper />
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
							class="px-3 py-1.5 cursor-pointer select-none w-2/3 p-2 text-left"
							on:click={() => setSortKey('totalFiles')}
						>
							<div class="flex gap-1.5 items-center justify-start capitalize">
								{$mobile
									? $i18n?.t('Files') || 'Total Files'
									: $i18n?.t('Total Files') || 'Total Files'}
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
							class="bg-white dark:bg-[#072D5A4D] dark:border-gray-850 text-xs cursor-pointer hover:bg-gradient-bg-2 dark:hover:bg-gray-850 transition"
							on:click={(e) => onClickDepartment(e, repository)}
						>
							<td class="py-1 pl-3 flex flex-col">
								<div class="flex flex-col items-start gap-0.5 h-full">
									<div class="flex flex-col h-full">
										<div
											class="tex-[14px] text-gray-600 dark:text-gray-400 flex-1 flex items-center {$mobile
												? 'gap-2'
												: 'gap-4'}"
										>
											<KnoFolder />
											{$isRTL ? repository.nameAr : repository.name}
										</div>
									</div>
								</div>
							</td>

							<td class="px-3 py-1 {$isRTL ? 'text-right' : 'text-left'}  font-medium">
								{repository.totalFiles}
								{$i18n?.t('Items')}
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
