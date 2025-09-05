<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '$lib/components/Button.svelte';
	import Card from '$lib/components/Card.svelte';
	import Heading from '$lib/components/Heading.svelte';

	let password = $state('');
	let confirmPassword = $state('');
	let loading = $state(false);
	let error = $state(null);
	let hasSessionToken = $state(true);

	const handleSetPassword = async () => {
		if (!password) {
			error = 'Please enter a password';
			return;
		}

		if (password.length < 8) {
			error = 'Password must be at least 8 characters long';
			return;
		}

		if (password !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}

		loading = true;
		error = null;

		try {
			const response = await fetch('http://localhost:8085/api/set-password', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				credentials: 'include',
				body: JSON.stringify({ password })
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail || 'Failed to set password');
			}

			// Password set successfully, redirect to login
			goto('/login');
			
		} catch (err) {
			console.error('Set password error:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	};

	const isPasswordValid = $derived(password.length >= 8);
	const doPasswordsMatch = $derived(password && confirmPassword && password === confirmPassword);
	
	// Enhanced password strength feedback
	const hasLowerCase = $derived(/[a-z]/.test(password));
	const hasUpperCase = $derived(/[A-Z]/.test(password));
	const hasDigit = $derived(/\d/.test(password));
	const hasSpecialChar = $derived(/[^a-zA-Z0-9]/.test(password));
	
	const strengthCriteria = $derived({
		length: password.length >= 8,
		lowercase: hasLowerCase,
		uppercase: hasUpperCase,
		digit: hasDigit,
		special: hasSpecialChar
	});
	
	const canSubmit = $derived(
		isPasswordValid && 
		doPasswordsMatch && 
		hasLowerCase && 
		hasUpperCase && 
		hasDigit && 
		hasSpecialChar
	);
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50">
	<div class="max-w-md w-full">
		<Card>
			<div class="w-full flex flex-col gap-6">
				<div class="text-center">
					<Heading>Set Your Password</Heading>
					<p class="mt-2 text-sm text-gray-600">
						Create a secure password to complete your account setup
					</p>
				</div>

				{#if hasSessionToken}
					<div class="flex flex-col gap-4">
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
							{#if password}
								<div class="mt-2 space-y-1">
									<div class="flex items-center text-sm">
										<span class={strengthCriteria.length ? 'text-green-600' : 'text-red-600'}>
											{strengthCriteria.length ? '✓' : '✗'} At least 8 characters
										</span>
									</div>
									<div class="flex items-center text-sm">
										<span class={strengthCriteria.lowercase ? 'text-green-600' : 'text-red-600'}>
											{strengthCriteria.lowercase ? '✓' : '✗'} One lowercase letter
										</span>
									</div>
									<div class="flex items-center text-sm">
										<span class={strengthCriteria.uppercase ? 'text-green-600' : 'text-red-600'}>
											{strengthCriteria.uppercase ? '✓' : '✗'} One uppercase letter
										</span>
									</div>
									<div class="flex items-center text-sm">
										<span class={strengthCriteria.digit ? 'text-green-600' : 'text-red-600'}>
											{strengthCriteria.digit ? '✓' : '✗'} One number
										</span>
									</div>
									<div class="flex items-center text-sm">
										<span class={strengthCriteria.special ? 'text-green-600' : 'text-red-600'}>
											{strengthCriteria.special ? '✓' : '✗'} One special character
										</span>
									</div>
								</div>
							{/if}
						</div>

						<div>
							<label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1">
								Confirm Password
							</label>
							<input
								id="confirmPassword"
								type="password"
								bind:value={confirmPassword}
								placeholder="Confirm your password"
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
								disabled={loading}
							/>
							{#if confirmPassword && !doPasswordsMatch}
								<p class="mt-1 text-sm text-red-600">
									Passwords do not match
								</p>
							{/if}
						</div>
					</div>

					{#if error}
						<div class="p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
							{error}
						</div>
					{/if}

					<Button onClick={handleSetPassword} {loading} disabled={loading || !canSubmit}>
						Set Password
					</Button>
				{:else}
					<div class="p-4 bg-yellow-50 border border-yellow-200 rounded text-yellow-700 text-center">
						<div class="font-medium mb-2">Invalid Session</div>
						<div class="text-sm">
							{error || 'Please sign up first to receive a magic link.'}
						</div>
					</div>
				{/if}
			</div>
		</Card>
	</div>
</div>