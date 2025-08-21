<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Button from '$lib/components/Button.svelte';
	import Link from '$lib/components/Link.svelte';
	import StatusBadge from '$lib/components/StatusBadge.svelte';
	import TableWithHeader from '$lib/components/TableWithHeader.svelte';

	// Client-side state management
	let orders = $state([]);
	let loading = $state(true);
	let error = $state(null);

	// Load data on component mount
	onMount(async () => {
		try {
			// Call your Go backend API instead of server-side load
			const response = await fetch('/api/orders'); // This will be handled by your Python server for now, later your Go server
			if (!response.ok) {
				throw new Error(`Failed to fetch orders: ${response.status}`);
			}
			const data = await response.json();
			orders = data.orders || data; // Handle different response formats
		} catch (err) {
			console.error('Error loading orders:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	});

	const columns = [
		{
			title: 'Order ID',
			key: 'id',
			formatter: (value: string) => ({
				type: Link,
				props: { value, href: `/orders/${value}` }
			})
		},
		{
			title: 'Date & Time',
			key: 'receivedAt',
			formatter: (value: string) => {
				return `${new Date(value).toLocaleDateString()} ${new Date(value).toLocaleTimeString()}`;
			}
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
		<p>Loading orders...</p>
	</div>
{:else if error}
	<div class="flex justify-center items-center p-8">
		<p class="text-red-600">Error: {error}</p>
	</div>
{:else}
	<TableWithHeader title="Orders" {columns} data={orders}>
		{#snippet action()}
			<Button onClick={() => goto('/orders/new')}>New Order</Button>
		{/snippet}
	</TableWithHeader>
{/if}