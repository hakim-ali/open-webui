<script lang="ts">
	import { getAdminDetails } from '$lib/apis/auths';
	import { onMount, tick, getContext } from 'svelte';
	import { config } from '$lib/stores';

	const i18n = getContext('i18n');

	let adminDetails = null;

	onMount(async () => {
		adminDetails = await getAdminDetails(localStorage.token).catch((err) => {
			console.error(err);
			return null;
		});
	});
</script>

<div class=" dark login min-h-screen w-full flex justify-center relative">
	<div class="relative w-full h-full flex flex-col">
		<!-- Login using Credentials button in top right corner -->

		<div id="splash-screen" class="login">
			<div class="relative w-full h-full flex flex-col">
				<div class="splash-content">
					<div class="logo-container">
						<img src="/splash.svg" alt="GovGPT Logo" class="logo-image" />
					</div>
					<div class="title-container">
						<h1 class="govgpt-title">GovGPT</h1>
					</div>
					<div class="tagline-container">
						<p class="tagline">Amplifying Government Potential</p>
					</div>
					<p class="mb-[30px] text-typography-titles text-[28px] leading-[36px]">
						Welcome to the future of Government Intelligence
					</p>

					<p class="text-typography-subtext text-[14px] leading-[24px]">
						You’re on the GovGPT waitlist!  We’re unlocking access in phases. We’ll let you know by email  as soon as it’s your turn.
					</p>
					<div class=" mt-6 mx-auto relative group w-fit">
						<button
							class="text-xs text-center w-full mt-2 text-gray-400 underline"
							on:click={async () => {
								localStorage.removeItem('token');
								location.href = '/auth';
							}}>{$i18n.t('Sign Out')}</button
						>
					</div>
				</div>
			</div>
			<div
				class="p-[16px] hidden sm:block fixed bottom-0 left-0 right-0 text-center text-typography-subtext text-[10px] leading-[16px] bg-[#072D5A] z-50"
			>
				<span class="text-typography-titles">Disclaimer:</span>
				GovGPT is powered by artificial intelligence and may occasionally produce incorrect or outdated
				responses. Please verify critical information from official sources or consult your department
				head for confirmation.
			</div>
		</div>
	</div>
</div>

<!-- <div class="fixed w-full h-full flex z-999">
	<div
		class="absolute w-full h-full backdrop-blur-lg bg-white/10 dark:bg-gray-900/50 flex justify-center"
	>
		<div class="m-auto pb-10 flex flex-col justify-center">
			<div class="max-w-md">
				<div
					class="text-center dark:text-white text-2xl font-medium z-50"
					style="white-space: pre-wrap;"
				>
					{#if ($config?.ui?.pending_user_overlay_title ?? '').trim() !== ''}
						{$config.ui.pending_user_overlay_title}
					{:else}
						{$i18n.t('Account Activation Pending')}<br />
						{$i18n.t('Contact Admin for WebUI Access')}
					{/if}
				</div>

				<div
					class=" mt-4 text-center text-sm dark:text-gray-200 w-full"
					style="white-space: pre-wrap;"
				>
					{#if ($config?.ui?.pending_user_overlay_content ?? '').trim() !== ''}
						{$config.ui.pending_user_overlay_content}
					{:else}
						{$i18n.t('Your account status is currently pending activation.')}{'\n'}{$i18n.t(
							'To access the WebUI, please reach out to the administrator. Admins can manage user statuses from the Admin Panel.'
						)}
					{/if}
				</div>

				{#if adminDetails}
					<div class="mt-4 text-sm font-medium text-center">
						<div>{$i18n.t('Admin')}: {adminDetails.name} ({adminDetails.email})</div>
					</div>
				{/if}

				<div class=" mt-6 mx-auto relative group w-fit">
					<button
						class="relative z-20 flex px-5 py-2 rounded-full bg-white border border-gray-100 dark:border-none hover:bg-gray-100 text-gray-700 transition font-medium text-sm"
						on:click={async () => {
							location.href = '/';
						}}
					>
						{$i18n.t('Check Again')}
					</button>

					<button
						class="text-xs text-center w-full mt-2 text-gray-400 underline"
						on:click={async () => {
							localStorage.removeItem('token');
							location.href = '/auth';
						}}>{$i18n.t('Sign Out')}</button
					>
				</div>
			</div>
		</div>
	</div>
</div> -->
