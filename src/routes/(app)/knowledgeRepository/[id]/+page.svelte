<script lang="ts">
	import { page } from '$app/stores';

	import Documents from '$lib/components/KnowledgeRepository/KnowledgeDocuments/Documents.svelte';
</script>

<Documents documentIdProp={$page.params.id} />
