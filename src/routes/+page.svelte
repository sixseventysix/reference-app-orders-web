<script>
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  
  onMount(() => {
    goto('/role');
  });
</script>

<p>Redirecting to role selection...</p>