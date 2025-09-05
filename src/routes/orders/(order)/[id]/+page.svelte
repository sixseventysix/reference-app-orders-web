<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Fulfillment from '$lib/components/Fullfillment.svelte';
	import Button from '$lib/components/Button.svelte';
	import { page } from '$app/state';
	import type { Action } from '$lib/types/order';
	import Card from '$lib/components/Card.svelte';
	import Heading from '$lib/components/Heading.svelte';
	import StatusBadge from '$lib/components/StatusBadge.svelte';

	// Client-side state management
	let order = $state(null);
	let loading = $state(true);
	let actionLoading = $state(false);
	let error = $state(null);
	let id = $derived(page.params.id);
	let pollInterval = null;

	// Load order data
	const loadOrder = async () => {
		// Don't try to load if id is undefined
		if (!id || id === 'undefined') {
			console.log('Order ID not available yet, skipping load');
			return;
		}
		
		try {
			const response = await fetch(`http://localhost:8085/api/orders/${id}`, {
				method: 'GET',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include'
			});
			if (!response.ok) {
				throw new Error(`Failed to fetch order: ${response.status}`);
			}
			const outer = await response.json();                       // { id, result: "<json>" }
			const inner = typeof outer.result === 'string' ? JSON.parse(outer.result) : outer.result;
			const arr = Array.isArray(inner?.order) ? inner.order : [];
			order = arr.find((o: any) => o.id === id) ?? arr[0] ?? null;

			if (!order) throw new Error('Order not found');
			error = null;
		} catch (err) {
			console.error('Error loading order:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	};

	onMount(async () => {
		// Wait for id to be available
		if (id && id !== 'undefined') {
			await loadOrder();
		} else {
			loading = false;
			error = "Invalid order ID";
			return;
		}
		
		// Set up polling for real-time updates (optional)
		const finalStatuses = ['completed', 'failed', 'cancelled', 'timedOut'];
		pollInterval = setInterval(async () => {
			if (order && !finalStatuses.includes(order.status)) {
				await loadOrder();
			} else if (pollInterval) {
				clearInterval(pollInterval);
			}
		}, 2000); // Poll every 2 seconds instead of 500ms

		// Cleanup on component destroy
		return () => {
			if (pollInterval) {
				clearInterval(pollInterval);
			}
		};
	});

	const sendAction = async (action: Action) => {
		actionLoading = true;
		try {
			// Call your Go backend API for order actions
			const response = await fetch('/api/order-action', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ id, action })
			});

			if (!response.ok) {
				throw new Error(`Action failed: ${response.status}`);
			}

			// Wait a moment for the action to process
			setTimeout(async () => {
				actionLoading = false;
				if (action === 'cancel') {
					goto('/orders');
				} else {
					// Reload the order data to show updated status
					await loadOrder();
				}
			}, 1000);
		} catch (err) {
			console.error('Error sending action:', err);
			actionLoading = false;
			// You might want to show an error message to the user
		}
	};

	const actionRequired = $derived(order?.status === 'customerActionRequired');
</script>

{#if loading}
	<div class="flex justify-center items-center p-8">
		<p>Loading order...</p>
	</div>
{:else if error}
	<div class="flex justify-center items-center p-8">
		<p class="text-red-600">Error: {error}</p>
	</div>
{:else if order}
	<Card>
		<div class="w-full flex flex-col gap-2">
			<div class="flex flex-row items-center gap-2 w-full">
				<StatusBadge status={order.status} />
				<Heading>{order.id}</Heading>
			</div>
			<Fulfillment {order} />
		</div>
		{#snippet actionButtons()}
			{#if actionRequired}
				<div class="flex items-center justify-end gap-2">
					<Button loading={actionLoading} onClick={() => sendAction('amend')}>Amend</Button>
					<Button loading={actionLoading} onClick={() => sendAction('cancel')}>Cancel</Button>
				</div>
			{:else}
				<p class="px-4 py-2 text-sm font-light"><i>Customer {order.customerId}</i></p>
			{/if}
		{/snippet}
	</Card>
{:else}
	<div class="flex justify-center items-center p-8">
		<p>Order not found</p>
	</div>
{/if}