<script lang="ts">
	import { onMount } from 'svelte';
	import Link from '$lib/components/Link.svelte';
	import TableWithHeader from '$lib/components/TableWithHeader.svelte';
	import StatusBadge from '$lib/components/StatusBadge.svelte';

	// Client-side state management
	let shipments = $state([]);
	let loading = $state(true);
	let error = $state(null);

	// Load data on component mount
	onMount(async () => {
		try {
			// Call your Go backend API instead of server-side load
			const response = await fetch('http://localhost:8085/api/shipments', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({})
			});
			if (!response.ok) {
				throw new Error(`Failed to fetch shipments: ${response.status}`);
			}
			const outer = await response.json();
			const inner = typeof outer.result === 'string' ? JSON.parse(outer.result) : outer.result;

			// inner.shipments is expected to be an array
			shipments = Array.isArray(inner?.shipments)
			? inner.shipments
			: (inner?.shipments && typeof inner.shipments === 'object'
				? Object.values(inner.shipments) // fallback if it’s a dict
				: []);

			error = null;
		} catch (err) {
			console.error('Error loading shipments:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	});

	const columns = [
		{
			title: 'Shipment ID',
			key: 'id',
			formatter: (value: string) => ({
				type: Link,
				props: { value, href: `/shipments/${value}` }
			})
		},
		{
			title: 'Status',
			key: 'status',
			formatter: (value: string) => ({
				type: StatusBadge,
				props: { status: value }
			})
		}
	];
</script>

{#if loading}
	<div class="flex justify-center items-center p-8">
		<p>Loading shipments...</p>
	</div>
{:else if error}
	<div class="flex justify-center items-center p-8">
		<p class="text-red-600">Error: {error}</p>
	</div>
{:else}
	<TableWithHeader title="Shipments" {columns} data={shipments} />
{/if}