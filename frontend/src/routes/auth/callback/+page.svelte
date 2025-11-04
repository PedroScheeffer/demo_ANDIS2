<script lang="ts">
  export const ssr = false;
  export const prerender = false;

  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  function parseFragment(hash: string) {
    const params = new URLSearchParams(hash.startsWith('#') ? hash.slice(1) : hash);
    return {
      access_token: params.get('access_token'),
      token_type: params.get('token_type') ?? 'bearer',
      user: {
        id: params.get('id'),
        username: params.get('username'),
        display_name: params.get('display_name') ?? params.get('username'),
        picture: params.get('picture')
      }
    };
  }

  onMount(() => {
    const auth = parseFragment(location.hash);
    if (auth?.access_token && auth?.user?.username) {
      localStorage.setItem('auth_response', JSON.stringify(auth));
      goto('/', { replaceState: true }); // redirige al dashboard principal
    } else {
      goto('/login', { replaceState: true });
    }
  });
</script>

<p>Procesando autenticación…</p>
