<script lang="ts">
    import type { ProjectCreate } from "$lib/models";
    import { createProject } from '$lib/services/project_service';

    interface Props {
        userId: number;
        onSuccess?: () => void;
    }

    let { userId, onSuccess }: Props = $props();

    let nombre = $state('');
    let description = $state('');
    let isSubmitting = $state(false);
    let error = $state<string | null>(null);
    let showForm = $state(false);

    async function handleSubmit(e: Event) {
        e.preventDefault();

        if (!nombre.trim()) {
            error = 'El nombre del proyecto es requerido';
            return;
        }

        isSubmitting = true;
        error = null;

        try {
            const projectData: ProjectCreate = {
                nombre: nombre.trim(),
                description: description.trim() || undefined,
            };

            await createProject(projectData, userId);

            // Reset form
            nombre = '';
            description = '';
            showForm = false;

            // Call success callback
            if (onSuccess) {
                onSuccess();
            }
        } catch (e) {
            error = e instanceof Error ? e.message : 'Error al crear el proyecto';
        } finally {
            isSubmitting = false;
        }
    }

    function toggleForm() {
        showForm = !showForm;
        if (!showForm) {
            // Reset form when closing
            nombre = '';
            description = '';
            error = null;
        }
    }
</script>

<div class="mb-6">
    {#if !showForm}
        <button
            onclick={toggleForm}
            class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded transition-colors"
        >
            + Nuevo Proyecto
        </button>
    {:else}
        <div class="border border-gray-300 rounded-lg p-4 bg-white shadow-sm">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-semibold">Crear Nuevo Proyecto</h3>
                <button
                    onclick={toggleForm}
                    class="text-gray-500 hover:text-gray-700 text-2xl leading-none"
                    disabled={isSubmitting}
                >
                    &times;
                </button>
            </div>

            <form onsubmit={handleSubmit} class="space-y-4">
                <div>
                    <label for="nombre" class="block text-sm font-medium text-gray-700 mb-1">
                        Nombre del Proyecto *
                    </label>
                    <input
                        type="text"
                        id="nombre"
                        bind:value={nombre}
                        disabled={isSubmitting}
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Ingrese el nombre del proyecto"
                    />
                </div>

                <div>
                    <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
                        Descripción
                    </label>
                    <textarea
                        id="description"
                        bind:value={description}
                        disabled={isSubmitting}
                        rows="3"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Ingrese una descripción (opcional)"
                    ></textarea>
                </div>

                {#if error}
                    <p class="text-red-600 text-sm">{error}</p>
                {/if}

                <div class="flex gap-2">
                    <button
                        type="submit"
                        disabled={isSubmitting}
                        class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded transition-colors"
                    >
                        {isSubmitting ? 'Creando...' : 'Crear Proyecto'}
                    </button>
                    <button
                        type="button"
                        onclick={toggleForm}
                        disabled={isSubmitting}
                        class="bg-gray-300 hover:bg-gray-400 disabled:bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded transition-colors"
                    >
                        Cancelar
                    </button>
                </div>
            </form>
        </div>
    {/if}
</div>
