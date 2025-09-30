<script lang="ts">
    import { onMount } from 'svelte';
    import type { Task, TaskCreate } from '$lib/models';
    import { getTasks, createTask, toggleTaskComplete as toggleComplete } from '$lib/services/task_service';

    interface Props {
        projectId: number;
    }

    let { projectId }: Props = $props();

    let tasks = $state<Task[]>([]);
    let loading = $state(true);
    let error = $state<string | null>(null);
    let newTaskDetalle = $state('');
    let isSubmitting = $state(false);

    async function loadTasks() {
        loading = true;
        error = null;
        try {
            tasks = await getTasks(projectId);
        } catch (e) {
            error = e instanceof Error ? e.message : 'Failed to load tasks';
        } finally {
            loading = false;
        }
    }

    onMount(async () => {
        await loadTasks();
    });

    async function handleAddTask(e: Event) {
        e.preventDefault();

        if (!newTaskDetalle.trim()) return;

        isSubmitting = true;
        error = null;

        try {
            const taskData: TaskCreate = {
                detalle: newTaskDetalle.trim(),
                project_id: projectId,
            };

            await createTask(taskData);
            newTaskDetalle = '';
            await loadTasks();
        } catch (e) {
            error = e instanceof Error ? e.message : 'Error al crear la tarea';
        } finally {
            isSubmitting = false;
        }
    }

    async function toggleTaskComplete(task: Task) {
        try {
            await toggleComplete(task.id!);
            await loadTasks();
        } catch (e) {
            error = e instanceof Error ? e.message : 'Error al actualizar la tarea';
        }
    }
</script>

<div class="w-full">
    <h2 class="text-2xl font-semibold mb-4">Tareas</h2>

    <!-- Add Task Form -->
    <form onsubmit={handleAddTask} class="mb-6">
        <div class="flex gap-2">
            <input
                type="text"
                bind:value={newTaskDetalle}
                disabled={isSubmitting}
                placeholder="Nueva tarea..."
                class="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
                type="submit"
                disabled={isSubmitting || !newTaskDetalle.trim()}
                class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-2 px-6 rounded transition-colors"
            >
                {isSubmitting ? 'Agregando...' : 'Agregar'}
            </button>
        </div>
    </form>

    {#if error}
        <p class="text-red-600 mb-4">{error}</p>
    {/if}

    <!-- Tasks List -->
    {#if loading}
        <p class="text-gray-600">Cargando tareas...</p>
    {:else if tasks.length === 0}
        <p class="text-gray-600">No hay tareas todavía. ¡Agrega una para comenzar!</p>
    {:else}
        <div class="space-y-2">
            {#each tasks as task}
                <div class="flex items-center gap-3 p-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                    <input
                        type="checkbox"
                        checked={task.completed}
                        onchange={() => toggleTaskComplete(task)}
                        class="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                    <span class={task.completed ? 'flex-1 line-through text-gray-500' : 'flex-1'}>
                        {task.detalle}
                    </span>
                    {#if task.created_at}
                        <span class="text-sm text-gray-400">
                            {new Date(task.created_at).toLocaleDateString()}
                        </span>
                    {/if}
                </div>
            {/each}
        </div>
    {/if}
</div>
