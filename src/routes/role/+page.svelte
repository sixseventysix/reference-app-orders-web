<script lang="ts">
	import Link from '$lib/components/Link.svelte';
	import TableWithHeader from '$lib/components/TableWithHeader.svelte';
	import type { TableColumns } from '$lib/types/ui';
	
	// Move the server data directly into the component
	const personas = [
		{
			role: 'Customer',
			description: 'Someone who orders products from the store',
			link: '/orders'
		},
		{
			role: 'Courier',
			description: 'Someone who delivers products to the customer',
			link: '/shipments'
		},
		{
			role: 'Store Manager',
			description: 'Someone who performs administrative functions',
			link: '/admin'
		},
		{
			role: 'Operator',
			description: "Someone who manages deployments and tests the system's performance",
			link: '/operator'
		}
	];
	
	const columns: TableColumns = [
		{
			title: 'Role',
			key: 'role',
			formatter: (value, row: Record<string, string>) => ({
				type: Link,
				props: { value, href: row.link }
			})
		},
		{
			title: 'Description',
			key: 'description'
		}
	];
</script>

<TableWithHeader title="Select Your Role" {columns} data={personas} />