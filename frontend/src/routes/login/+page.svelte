<script lang="ts">
    import { goto } from '$app/navigation';
    import { login } from '$lib/services/auth_service';

    let username = $state('');
    let password = $state('');
    let error = $state<string | null>(null);
    let isSubmitting = $state(false);

    async function handleSubmit(e: Event) {
        e.preventDefault();

        if (!username.trim() || !password.trim()) {
            error = 'Please enter both username and password';
            return;
        }

        isSubmitting = true;
        error = null;

        try {
            await login(username, password);

            // Redirect to home (login service already stores auth_response)
            goto('/');
        } catch (e) {
            error = e instanceof Error ? e.message : 'Login failed';
        } finally {
            isSubmitting = false;
        }
    }
</script>

<div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="w-full max-w-md">
        <div class="bg-white rounded-lg shadow-md p-8">
            <h1 class="text-3xl font-bold text-center mb-8">Login</h1>

            <form onsubmit={handleSubmit} class="space-y-6">
                <div>
                    <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
                        Username
                    </label>
                    <input
                        type="text"
                        id="username"
                        bind:value={username}
                        disabled={isSubmitting}
                        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter your username"
                    />
                </div>

                <div>
                    <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                        Password
                    </label>
                    <input
                        type="password"
                        id="password"
                        bind:value={password}
                        disabled={isSubmitting}
                        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter your password"
                    />
                </div>

                {#if error}
                    <p class="text-red-600 text-sm">{error}</p>
                {/if}

                <button
                    type="submit"
                    disabled={isSubmitting}
                    class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 rounded-md transition-colors"
                >
                    {isSubmitting ? 'Logging in...' : 'Login'}
                </button>
            </form>

            <p class="text-center mt-6 text-gray-600">
                Don't have an account?
                <a href="/register" class="text-blue-600 hover:text-blue-800 font-semibold">
                    Register
                </a>
            </p>
        </div>
    </div>
</div>
