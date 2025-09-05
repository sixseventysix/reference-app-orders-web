<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '$lib/components/Button.svelte';
	import Card from '$lib/components/Card.svelte';
	import Heading from '$lib/components/Heading.svelte';

	let name = $state('');
	let email = $state('');
	let loading = $state(false);
	let error = $state(null);
	let success = $state(false);

	const handleSignup = async () => {
		if (!email) {
			error = 'Please enter your email';
			return;
		}

		loading = true;
		error = null;

		try {
			const response = await fetch('http://localhost:8085/signup', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ 
					email,
					...(name && { name }) // Include name if provided
				})
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail || 'Signup failed');
			}

			const data = await response.json();
			success = true;
			
		} catch (err) {
			console.error('Signup error:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	};

	const handleLogin = () => {
		goto('/login');
	};
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50">
	<div class="max-w-md w-full">
		<Card>
			<div class="w-full flex flex-col gap-6">
				<div class="text-center">
					<Heading>Create Account</Heading>
					<p class="mt-2 text-sm text-gray-600">
						Sign up to get started with your account
					</p>
				</div>

				{#if success}
					<div class="p-4 bg-green-50 border border-green-200 rounded text-green-700 text-center">
						<div class="font-medium mb-2">Check your email!</div>
						<div class="text-sm">
							We've sent you a magic link to complete your signup. 
							Click the link in your email to set your password.
						</div>
					</div>
				{:else}
					<div class="flex flex-col gap-4">
						<div>
							<label for="name" class="block text-sm font-medium text-gray-700 mb-1">
								Name (Optional)
							</label>
							<input
								id="name"
								type="text"
								bind:value={name}
								placeholder="Enter your full name"
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
								disabled={loading}
							/>
						</div>

						<div>
							<label for="email" class="block text-sm font-medium text-gray-700 mb-1">
								Email
							</label>
							<input
								id="email"
								type="email"
								bind:value={email}
								placeholder="Enter your email address"
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
								disabled={loading}
							/>
						</div>
					</div>

					{#if error}
						<div class="p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
							{error}
						</div>
					{/if}

					<div class="flex flex-col gap-3">
						<Button onClick={handleSignup} {loading} disabled={loading || !email}>
							Create Account
						</Button>

						<div class="text-center">
							<button 
								type="button"
								onClick={handleLogin}
								class="text-sm text-blue-600 hover:text-blue-500 underline"
								disabled={loading}
							>
								Already have an account? Sign in
							</button>
						</div>
					</div>
				{/if}
			</div>
		</Card>
	</div>
</div>