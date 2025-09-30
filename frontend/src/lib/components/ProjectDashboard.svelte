<script lang="ts">
    import { onMount } from 'svelte';
    import type { Project } from "$lib/models";
    import { getProjects } from '$lib/services/project_service';
    import ProjectForm from './ProjectForm.svelte';

    interface Props {
        userId: number;
    }

    let { userId }: Props = $props();

    let projects = $state<Project[]>([]);
    let loading = $state(true);
    let error = $state<string | null>(null);

    async function loadProjects() {
        loading = true;
        error = null;
        try {
            const allProjects = await getProjects();
            // Filter projects for the specified user
            projects = allProjects.filter(p => p.user_id === userId);
        } catch (e) {
            error = e instanceof Error ? e.message : 'Failed to load projects';
        } finally {
            loading = false;
        }
    }

    onMount(async () => {
        await loadProjects();
    });

    function handleProjectCreated() {
        loadProjects();
    }
</script>

<div class="w-full max-w-4xl">
    <h2 class="text-2xl font-semibold mb-4">Mis Proyectos</h2>

    <ProjectForm userId={userId} onSuccess={handleProjectCreated} />

    {#if loading}
        <p class="text-gray-600">Cargando proyectos...</p>
    {:else if error}
        <p class="text-red-600">Error: {error}</p>
    {:else if projects.length === 0}
        <p class="text-gray-600">No tienes proyectos todavía</p>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each projects as project}
                <a href="/project/{project.id}" class="border border-gray-300 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer block">
                    <h3 class="text-xl font-semibold mb-2">{project.nombre}</h3>
                    {#if project.description}
                        <p class="text-gray-700 mb-3">{project.description}</p>
                    {/if}
                    {#if project.created_at}
                        <p class="text-sm text-gray-500">
                            Creado: {new Date(project.created_at).toLocaleDateString()}
                        </p>
                    {/if}
                </a>
            {/each}
        </div>
    {/if}
</div>
