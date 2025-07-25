<script lang="ts">
	import { DropdownMenu } from 'bits-ui';
	import { getContext, onMount } from 'svelte';

	import { flyAndScale } from '$lib/utils/transitions';
	import { fade, slide } from 'svelte/transition';

	import { showSettings, mobile, showSidebar, user } from '$lib/stores';

	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import ArchiveBox from '$lib/components/icons/ArchiveBox.svelte';
	import Download from '$lib/components/icons/Download.svelte';
	import Trash from '$lib/components/icons/Trash.svelte';
	import DocumentDuplicate from '$lib/components/icons/DocumentDuplicate.svelte';
	import Share from '$lib/components/icons/Share.svelte';

	const i18n = getContext('i18n');

	export let show = false;
	export let className = 'max-w-[180px]';

	export let onDownload = (type) => {};
	export let onDelete = () => {};
	export let onCopyToClipboard = () => {};

	export let onChange = () => {};
</script>

<DropdownMenu.Root
	bind:open={show}
	onOpenChange={(state) => {
		onChange(state);
	}}
>
	<DropdownMenu.Trigger>
		<slot />
	</DropdownMenu.Trigger>

	<slot name="content">
		<DropdownMenu.Content
			class="w-full {className} rounded-[8px] border border-neutrals-50 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-custom"
			sideOffset={6}
			side="bottom"
			align="start"
			transition={(e) => fade(e, { duration: 100 })}
		>
			<DropdownMenu.Sub>
				<DropdownMenu.SubTrigger
					class="p-[8px] flex items-center text-neutrals-800 gap-[8px] text-[16px] leading-[24px] font-medium  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md"
				>
					<Download strokeWidth="2" />

					<div class="flex items-center">{$i18n.t('Download')}</div>
				</DropdownMenu.SubTrigger>
				<DropdownMenu.SubContent
					class="w-full rounded-xl px-1 py-1.5 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-lg"
					transition={flyAndScale}
					sideOffset={8}
				>
					<DropdownMenu.Item
						class="p-[8px] flex items-center text-neutrals-800 gap-[8px] text-[16px] leading-[24px] font-medium  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md"
						on:click={() => {
							onDownload('md');
						}}
					>
						<div class="flex items-center line-clamp-1">{$i18n.t('Plain text (.md)')}</div>
					</DropdownMenu.Item>

					<DropdownMenu.Item
						class=" p-[8px] flex items-center text-neutrals-800 gap-[8px] text-[16px] leading-[24px] font-medium cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md"
						on:click={() => {
							onDownload('pdf');
						}}
					>
						<div class="flex items-center line-clamp-1">{$i18n.t('PDF document (.pdf)')}</div>
					</DropdownMenu.Item>
				</DropdownMenu.SubContent>
			</DropdownMenu.Sub>

			<DropdownMenu.Sub>
				<DropdownMenu.SubTrigger
					class="p-[8px] flex items-center text-neutrals-800 gap-[8px] text-[16px] leading-[24px] font-medium cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md"
				>
					<Share strokeWidth="2" />

					<div class="flex items-center">{$i18n.t('Share')}</div>
				</DropdownMenu.SubTrigger>
				<DropdownMenu.SubContent
					class="w-full rounded-xl px-1 py-1.5 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-lg"
					transition={flyAndScale}
					sideOffset={8}
				>
					<DropdownMenu.Item
						class="flex items-center text-neutrals-800 gap-[8px] text-[16px] leading-[24px] font-medium cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md"
						on:click={() => {
							onCopyToClipboard();
						}}
					>
						<DocumentDuplicate strokeWidth="2" />
						<div class="flex items-center">{$i18n.t('Copy to clipboard')}</div>
					</DropdownMenu.Item>
				</DropdownMenu.SubContent>
			</DropdownMenu.Sub>

			<DropdownMenu.Item
				class="p-[8px] flex items-center text-neutrals-800 gap-[8px] text-[16px] leading-[24px] font-medium cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md"
				on:click={() => {
					onDelete();
				}}
			>
				<Trash strokeWidth="2" />
				<div class="flex items-center text-[#C2451E]">{$i18n.t('Delete')}</div>
			</DropdownMenu.Item>
		</DropdownMenu.Content>
	</slot>
</DropdownMenu.Root>
