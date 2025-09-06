<script lang="ts">
	import { generateOrders, type Order, type OrderItem } from '$lib/types/order';
	import Button from '$lib/components/Button.svelte';
	import { goto } from '$app/navigation';
	import ItemDetails from '$lib/components/ItemDetails.svelte';
	import Card from '$lib/components/Card.svelte';
	import Heading from '$lib/components/Heading.svelte';

	const orders = generateOrders(20);
	let order: Order = $state(orders[0]);
	let loading = $state(false);
	let error = $state(null);

	const onItemClick = async (item: Order) => {
		order = item;
	};

	// Client-side form submission
	const submitOrder = async () => {
		if (!order) return;
		
		loading = true;
		error = null;
		
		try {
			// Call your Go backend API to create the order
			const response = await fetch('http://localhost:8085/api/order-workflow', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Flow-ID': order.id,
				},
				credentials: 'include',
				body: JSON.stringify({ input: order })
			});

			if (!response.ok) {
				throw new Error(`Failed to create order: ${response.status}`);
			}

			const result = await response.json();
			
			// Simulate processing delay
			await new Promise((resolve) => setTimeout(resolve, 1000));
			
			// Navigate to the created order
			goto(`/orders/${order.id}`);
		} catch (err) {
			console.error('Error creating order:', err);
			error = err.message;
			loading = false;
		}
	};
</script>

{#snippet orderDetails(item: OrderItem)}
	<Card>
		<ItemDetails items={[item]} />
		{#snippet actionButtons()}
			<div class="text-xs text-gray-600/80 px-4">{item.description}</div>
		{/snippet}
	</Card>
{/snippet}

<Heading>New Order</Heading>
<div class="flex flex-col gap-2">
	<div class="flex flex-wrap gap-0.5">
		{#each orders as item, index}
			<button
				onclick={() => onItemClick(item)}
				type="button"
				class="relative cursor-pointer inline-flex items-center {order.id === item.id
					? 'bg-blue-500 hover:bg-blue-600 text-white'
					: 'bg-white hover:bg-gray-50'} px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-gray-200 ring-inset focus:z-10"
				>Package {index + 1}</button
			>
		{/each}
	</div>
	
	<!-- Convert form to client-side handling -->
	<div class="flex w-full flex-col gap-2 items-end">
		{#each order.items as item}
			{@render orderDetails(item)}
		{/each}
		
		{#if error}
			<div class="w-full p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
				Error: {error}
			</div>
		{/if}
		
		<Button onClick={submitOrder} {loading} disabled={!order}>Submit</Button>
	</div>
</div>