<script>
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  
  onMount(() => {
    goto('/signup');
  });
</script>

<p>Redirecting to signup...</p>