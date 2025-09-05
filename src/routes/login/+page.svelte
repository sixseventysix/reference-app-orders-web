<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '$lib/components/Button.svelte';
	import Card from '$lib/components/Card.svelte';
	import Heading from '$lib/components/Heading.svelte';

	let email = $state('');
	let password = $state('');
	let loading = $state(false);
	let error = $state(null);

	const handleLogin = async () => {
		if (!email || !password) {
			error = 'Please enter both email and password';
			return;
		}

		loading = true;
		error = null;

		try {
			const response = await fetch('http://localhost:8085/login', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				credentials: 'include', // Important for cookies
				body: JSON.stringify({ email, password })
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail || 'Login failed');
			}

			// Login successful, cookies are set automatically
			goto('/role');
		} catch (err) {
			console.error('Login error:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	};

	const handleSignup = () => {
		goto('/signup');
	};
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50">
	<div class="max-w-md w-full">
		<Card>
			<div class="w-full flex flex-col gap-6">
				<div class="text-center">
					<Heading>Sign In</Heading>
					<p class="mt-2 text-sm text-gray-600">
						Enter your credentials to access your account
					</p>
				</div>

				<div class="flex flex-col gap-4">
					<div>
						<label for="email" class="block text-sm font-medium text-gray-700 mb-1">
							Email
						</label>
						<input
							id="email"
							type="email"
							bind:value={email}
							placeholder="Enter your email"
							class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							disabled={loading}
						/>
					</div>

					<div>
						<label for="password" class="block text-sm font-medium text-gray-700 mb-1">
							Password
						</label>
						<input
							id="password"
							type="password"
							bind:value={password}
							placeholder="Enter your password"
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
					<Button onClick={handleLogin} {loading} disabled={loading || !email || !password}>
						Sign In
					</Button>

					<div class="text-center">
						<button 
							type="button"
							onClick={handleSignup}
							class="text-sm text-blue-600 hover:text-blue-500 underline"
							disabled={loading}
						>
							Don't have an account? Sign up
						</button>
					</div>
				</div>
			</div>
		</Card>
	</div>
</div>