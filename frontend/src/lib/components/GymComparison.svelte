<script lang="ts">
	import { api, type Gym } from '$lib/api';
	import CurrentOccupancy from './CurrentOccupancy.svelte';

	export let gyms: Gym[];
</script>

<div class="grid">
	{#each gyms as gym}
		<CurrentOccupancy gymId={gym.id} gymName={gym.name} />
	{/each}
</div>

<style>
	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
	}
</style>
