<script lang="ts">
  export const ssr = false;
  export const prerender = false;

  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import type { AuthResponse } from '$lib/services/auth_service';
  import { logout } from '$lib/services/auth_service';
  import ProjectDashboard from '$lib/components/ProjectDashboard.svelte';
  import type { User } from '$lib/models/user';

  let auth_response = $state<AuthResponse | null>(null);

  onMount(() => {
    const stored = localStorage.getItem('auth_response');
    if (stored) {
      auth_response = JSON.parse(stored);
    } else {
      goto('/login', { replaceState: true });
    }
  });

  async function handleLogout() {
    await logout();
    goto('/login', { replaceState: true });
  }

  let userId = $derived(auth_response ? Number(auth_response.user.id) : undefined);
  let username = $derived(auth_response?.user.username ?? '');
</script>

{#if auth_response}
  <div class="flex flex-col items-center gap-8 min-h-screen mt-8 px-4">
    <div class="w-full max-w-4xl flex justify-between items-center">
      <h1 class="text-3xl font-bold">Demo UCU TODO</h1>
      <button onclick={handleLogout}
        class="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-4 rounded transition-colors">
        Logout
      </button>
    </div>

    <p class="text-lg">Bienvenido {username}</p>

    {#if userId}
      <ProjectDashboard {userId} />
    {/if}
  </div>
{:else}
  <div class="flex items-center justify-center min-h-screen">
    <p class="text-gray-600">Loading...</p>
  </div>
{/if}
