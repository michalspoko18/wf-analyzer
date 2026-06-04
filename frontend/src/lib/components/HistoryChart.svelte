<script lang="ts">
	import { onDestroy } from 'svelte';
	import { Chart, type ChartData } from 'chart.js/auto';
	import { api, type HourlyData } from '$lib/api';

	export let gymId: number;
	export let dow: number = new Date().getDay() === 0 ? 6 : new Date().getDay() - 1;

	const DOW_NAMES = ['Pon', 'Wt', 'Śr', 'Czw', 'Pt', 'Sob', 'Nd'];

	let canvas: HTMLCanvasElement;
	let chart: Chart | null = null;
	let rows: HourlyData[] = [];
	let error: string | null = null;
	let selectedDow = dow;

	async function load() {
		try {
			rows = await api.getHourly(gymId);
			error = null;
		} catch {
			error = 'Błąd pobierania danych';
		}
	}

	function buildChart() {
		const filtered = rows.filter((r) => r.dow === selectedDow);
		filtered.sort((a, b) => a.hour - b.hour);

		const labels = filtered.map((r) => `${r.hour}:00`);
		const data: ChartData = {
			labels,
			datasets: [
				{
					label: 'Średnia liczba osób',
					data: filtered.map((r) => r.avg_people),
					borderColor: '#6366f1',
					backgroundColor: 'rgba(99,102,241,0.15)',
					fill: true,
					tension: 0.3,
					pointRadius: 4
				},
				{
					label: 'Min',
					data: filtered.map((r) => r.min_people),
					borderColor: '#22c55e',
					borderDash: [4, 4],
					fill: false,
					pointRadius: 0
				},
				{
					label: 'Max',
					data: filtered.map((r) => r.max_people),
					borderColor: '#ef4444',
					borderDash: [4, 4],
					fill: false,
					pointRadius: 0
				}
			]
		};

		if (chart) {
			chart.data = data;
			chart.update();
		} else {
			chart = new Chart(canvas, {
				type: 'line',
				data,
				options: {
					responsive: true,
					plugins: {
						legend: { labels: { color: '#e2e8f0' } }
					},
					scales: {
						x: { ticks: { color: '#94a3b8' }, grid: { color: '#2a2d3a' } },
						y: {
							ticks: { color: '#94a3b8' },
							grid: { color: '#2a2d3a' },
							beginAtZero: true
						}
					}
				}
			});
		}
	}

	$: if (rows.length > 0) buildChart();
	$: selectedDow, rows.length > 0 && buildChart();

	$: gymId, load();
	onDestroy(() => chart?.destroy());
</script>

<div class="wrapper">
	<div class="dow-tabs">
		{#each DOW_NAMES as name, i}
			<button class:active={selectedDow === i} on:click={() => (selectedDow = i)}>{name}</button>
		{/each}
	</div>
	{#if error}
		<p class="error">{error}</p>
	{:else}
		<canvas bind:this={canvas}></canvas>
	{/if}
</div>

<style>
	.wrapper {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		padding: 1rem;
	}

	.dow-tabs {
		display: flex;
		gap: 0.25rem;
		margin-bottom: 1rem;
		flex-wrap: wrap;
	}

	button {
		background: none;
		border: 1px solid var(--color-border);
		color: var(--color-text-muted);
		border-radius: 6px;
		padding: 0.25rem 0.6rem;
		font-size: 0.8rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	button.active,
	button:hover {
		background: var(--color-accent);
		border-color: var(--color-accent);
		color: #fff;
	}

	.error {
		color: var(--color-text-muted);
		font-size: 0.85rem;
	}
</style>
