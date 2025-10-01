<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import type { Project } from '$lib/models';
    import { getProject } from '$lib/services/project_service';
    import TaskList from '$lib/components/TaskList.svelte';

    let projectId = $derived(Number($page.params.id));
    let project = $state<Project | null>(null);
    let loading = $state(true);
    let error = $state<string | null>(null);

    onMount(async () => {
        try {
            project = await getProject(projectId);
        } catch (e) {
            error = e instanceof Error ? e.message : 'Failed to load project';
        } finally {
            loading = false;
        }
    });
</script>

<div class="flex flex-col items-center gap-8 min-h-screen mt-8 px-4">
    <div class="w-full max-w-4xl">
        <a href="/" class="text-blue-600 hover:text-blue-800 mb-4 inline-block">
            ← Volver a proyectos
        </a>

        {#if loading}
            <p class="text-gray-600">Cargando proyecto...</p>
        {:else if error}
            <p class="text-red-600">Error: {error}</p>
        {:else if project}
            <div class="mb-8">
                <h1 class="text-3xl font-bold mb-2">{project.nombre}</h1>
                {#if project.description}
                    <p class="text-gray-700">{project.description}</p>
                {/if}
            </div>

            <TaskList projectId={projectId} />
        {/if}
    </div>
</div>
