<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import type { AuthResponse } from '$lib/services/auth_service';
    import { logout } from '$lib/services/auth_service';
    import ProjectDashboard from '$lib/components/ProjectDashboard.svelte';

    let user = $state<AuthResponse | null>(null);

    onMount(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            user = JSON.parse(storedUser);
        } else {
            goto('/login');
        }
    });

    async function handleLogout() {
        await logout();
        goto('/login');
    }
</script>

{#if user}
    <div class="flex flex-col items-center gap-8 min-h-screen mt-8 px-4">
        <div class="w-full max-w-4xl flex justify-between items-center">
            <h1 class="text-3xl font-bold">Demo UCU TODO</h1>
            <button
                onclick={handleLogout}
                class="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-4 rounded transition-colors"
            >
                Logout
            </button>
        </div>

        <p class="text-lg">Bienvenido {user.username}</p>

        <ProjectDashboard userId={Number(user.id)} />
    </div>
{:else}
    <div class="flex items-center justify-center min-h-screen">
        <p class="text-gray-600">Loading...</p>
    </div>
{/if}

