<script lang="ts">
	import { onMount } from 'svelte';
	import { api, type Gym } from '$lib/api';
	import GymComparison from '$lib/components/GymComparison.svelte';
	import HistoryChart from '$lib/components/HistoryChart.svelte';
	import Heatmap from '$lib/components/Heatmap.svelte';
	import Recommendations from '$lib/components/Recommendations.svelte';

	let gyms: Gym[] = [];
	let selectedGymId: number | null = null;
	let activeTab: 'chart' | 'heatmap' = 'chart';
	let error: string | null = null;

	onMount(async () => {
		try {
			gyms = await api.getGyms();
			if (gyms.length > 0) selectedGymId = gyms[0].id;
		} catch {
			error = 'Nie można pobrać listy siłowni.';
		}
	});
</script>

<svelte:head>
	<title>WF Analyzer</title>
</svelte:head>

<main>
	<header>
		<h1>WF Analyzer</h1>
		<p class="subtitle">Aktualne obłożenie siłowni WellFitness</p>
	</header>

	{#if error}
		<div class="error-banner">{error}</div>
	{:else}
		<section class="section">
			<h2>Teraz</h2>
			<GymComparison {gyms} />
		</section>

		{#if gyms.length > 0}
			<section class="section">
				<div class="section-header">
					<h2>Szczegóły</h2>
					<div class="gym-tabs">
						{#each gyms as gym}
							<button
								class:active={selectedGymId === gym.id}
								on:click={() => (selectedGymId = gym.id)}
							>
								{gym.name.split(',')[1]?.trim() ?? gym.name}
							</button>
						{/each}
					</div>
				</div>

				<div class="view-tabs">
					<button class:active={activeTab === 'chart'} on:click={() => (activeTab = 'chart')}
						>Wykres</button
					>
					<button
						class:active={activeTab === 'heatmap'}
						on:click={() => (activeTab = 'heatmap')}>Heatmapa</button
					>
				</div>

				{#if selectedGymId}
					{#if activeTab === 'chart'}
						<HistoryChart gymId={selectedGymId} />
					{:else}
						<Heatmap gymId={selectedGymId} />
					{/if}
				{/if}
			</section>
		{/if}

		<section class="section">
			<Recommendations />
		</section>
	{/if}
</main>

<style>
	main {
		max-width: 1100px;
		margin: 0 auto;
		padding: 2rem 1rem;
	}

	header {
		margin-bottom: 2rem;
	}

	h1 {
		font-size: 1.8rem;
	}

	h2 {
		font-size: 1.1rem;
		margin-bottom: 0.75rem;
	}

	.subtitle {
		color: var(--color-text-muted);
		font-size: 0.9rem;
		margin-top: 0.25rem;
	}

	.section {
		margin-bottom: 2.5rem;
	}

	.section-header {
		display: flex;
		align-items: center;
		gap: 1rem;
		flex-wrap: wrap;
		margin-bottom: 0.75rem;
	}

	.gym-tabs,
	.view-tabs {
		display: flex;
		gap: 0.25rem;
		flex-wrap: wrap;
	}

	.view-tabs {
		margin-bottom: 0.75rem;
	}

	button {
		background: none;
		border: 1px solid var(--color-border);
		color: var(--color-text-muted);
		border-radius: 6px;
		padding: 0.3rem 0.75rem;
		font-size: 0.82rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	button.active,
	button:hover {
		background: var(--color-accent);
		border-color: var(--color-accent);
		color: #fff;
	}

	.error-banner {
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid var(--color-danger);
		color: var(--color-danger);
		border-radius: var(--radius);
		padding: 0.75rem 1rem;
		font-size: 0.9rem;
	}
</style>
