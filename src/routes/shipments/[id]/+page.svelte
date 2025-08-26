<script lang="ts">
	import { onMount } from 'svelte';
	import Card from '$lib/components/Card.svelte';
	import Button from '$lib/components/Button.svelte';
	import Heading from '$lib/components/Heading.svelte';
	import ItemDetails from '$lib/components/ItemDetails.svelte';
	import ShipmentProgress from '$lib/components/ShipmentProgress.svelte';
	import { page } from '$app/state';
	import type { Shipment } from '$lib/types/order';

	// Client-side state management
	let shipment: Shipment | null = $state(null);
	let loading = $state(true);
	let actionLoading = $state(false);
	let error = $state(null);
	let id = $derived(page.params.id);
	let status = $derived(shipment?.status);
	let broadcaster: BroadcastChannel | null = null;

	// Load shipment data
	const loadShipment = async () => {
		// Don't try to load if id is undefined
		if (!id || id === 'undefined') {
			console.log('Shipment ID not available yet, skipping load');
			return;
		}
		
		try {
			const response = await fetch('http://localhost:8085/api/shipment', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ shipment_id: id })
			});
			if (!response.ok) {
				throw new Error(`Failed to fetch shipment: ${response.status}`);
			}
			const outer = await response.json();                       // { id, result: "<json>" }
			const inner = typeof outer.result === 'string' ? JSON.parse(outer.result) : outer.result;
			const arr = Array.isArray(inner?.shipment) ? inner.shipment : [];
			shipment = arr.find((o: any) => o.id === id) ?? arr[0] ?? null;

			if (!shipment) throw new Error('shipment not found');
			error = null;
		} catch (err) {
			console.error('Error loading shipment:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	};

	onMount(async () => {
		// Wait for id to be available
		if (id && id !== 'undefined') {
			await loadShipment();
		} else {
			loading = false;
			error = "Invalid shipment ID";
			return;
		}
		
		// Set up BroadcastChannel for real-time updates (if shipment loaded successfully)
		if (shipment?.id) {
			broadcaster = new BroadcastChannel(`shipment-${shipment.id}`);
			broadcaster.addEventListener('message', (event) => {
				if (shipment) {
					shipment.status = event.data;
				}
			});
		}

		// Cleanup on component destroy
		return () => {
			if (broadcaster) {
				broadcaster.close();
			}
		};
	});

	const dispatchShipment = async (shipment: Shipment) => {
		if (!shipment) return;
		
		actionLoading = true;
		try {
			const orderId = shipment.id;
			const shipmentId = 'shipment:' + orderId;
			const url = new URL(`/flow/${encodeURIComponent(shipmentId)}`, 'http://localhost:8085');
			const response = await fetch(url, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					signal_name: 'update_shipment_status_signal',
					input: {
						id: orderId,
						status: 'dispatched'
					}
				})
			});

			if (!response.ok) {
				throw new Error(`Failed to dispatch shipment: ${response.status}`);
			}

			// Update local state
			shipment.status = 'dispatched';
			
			// Broadcast the status change
			if (broadcaster) {
				broadcaster.postMessage('dispatched');
			}
		} catch (err) {
			console.error('Error dispatching shipment:', err);
			// You might want to show an error message to the user
		} finally {
			actionLoading = false;
		}
	};

	const deliverShipment = async (shipment: Shipment) => {
		if (!shipment) return;
		
		actionLoading = true;
		try {
			const orderId = shipment.id;
			const shipmentId = 'shipment:' + orderId;
			const url = new URL(`/flow/${encodeURIComponent(shipmentId)}`, 'http://localhost:8085');
			const response = await fetch(url, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					signal_name: 'update_shipment_status_signal',
					input: {
						id: orderId,
						status: 'delivered'
					}
				})
			});

			if (!response.ok) {
				throw new Error(`Failed to deliver shipment: ${response.status}`);
			}

			// Update local state
			shipment.status = 'delivered';
			
			// Broadcast the status change
			if (broadcaster) {
				broadcaster.postMessage('delivered');
			}
		} catch (err) {
			console.error('Error delivering shipment:', err);
			// You might want to show an error message to the user
		} finally {
			actionLoading = false;
		}
	};
</script>

{#if loading}
	<div class="flex justify-center items-center p-8">
		<p>Loading shipment...</p>
	</div>
{:else if error}
	<div class="flex justify-center items-center p-8">
		<p class="text-red-600">Error: {error}</p>
	</div>
{:else if shipment}
	<Card>
		<div class="w-full flex flex-col gap-2">
			<div class="flex flex-col md:flex-row items-center justify-between gap-2 w-full">
				<Heading>{shipment.id}</Heading>
				<ShipmentProgress {status} />
			</div>
			<ItemDetails items={shipment.items} />
		</div>
		{#snippet actionButtons()}
			<Button 
				disabled={status !== 'booked' || actionLoading} 
				loading={actionLoading}
				onClick={() => dispatchShipment(shipment)}
			>
				Dispatch
			</Button>
			<Button 
				disabled={status !== 'dispatched' || actionLoading} 
				loading={actionLoading}
				onClick={() => deliverShipment(shipment)}
			>
				Deliver
			</Button>
		{/snippet}
	</Card>
{:else}
	<div class="flex justify-center items-center p-8">
		<p>Shipment not found</p>
	</div>
{/if}