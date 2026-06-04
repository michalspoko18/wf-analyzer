<script lang="ts">
	import { onMount } from 'svelte';
	import { api, type HourlyData } from '$lib/api';

	export let gymId: number;

	const DOW_NAMES = ['Pon', 'Wt', 'Śr', 'Czw', 'Pt', 'Sob', 'Nd'];
	const HOURS = Array.from({ length: 18 }, (_, i) => i + 5); // 5–22

	let rows: HourlyData[] = [];
	let error: string | null = null;
	let maxVal = 1;

	async function load() {
		try {
			rows = await api.getHourly(gymId);
			maxVal = Math.max(1, ...rows.map((r) => r.avg_people));
			error = null;
		} catch {
			error = 'Błąd pobierania danych';
		}
	}

	function getCell(dow: number, hour: number): HourlyData | undefined {
		return rows.find((r) => r.dow === dow && r.hour === hour);
	}

	function hue(val: number): string {
		// green (120) → yellow (60) → red (0) based on fill ratio
		const ratio = val / maxVal;
		const h = Math.round((1 - ratio) * 120);
		return `hsl(${h}, 70%, 35%)`;
	}

	$: gymId, load();
</script>

<div class="wrapper">
	{#if error}
		<p class="error">{error}</p>
	{:else}
		<div class="grid" style="--cols: {HOURS.length + 1}">
			<!-- Header row: hours -->
			<div class="cell header corner"></div>
			{#each HOURS as h}
				<div class="cell header">{h}</div>
			{/each}

			<!-- Data rows: one per day -->
			{#each DOW_NAMES as day, dow}
				<div class="cell header dow">{day}</div>
				{#each HOURS as hour}
					{@const cell = getCell(dow, hour)}
					<div
						class="cell data"
						style={cell ? `background:${hue(cell.avg_people)}` : ''}
						title={cell
							? `${day} ${hour}:00 — śr. ${cell.avg_people.toFixed(0)} osób`
							: 'brak danych'}
					>
						{#if cell}
							<span>{cell.avg_people.toFixed(0)}</span>
						{/if}
					</div>
				{/each}
			{/each}
		</div>
	{/if}
</div>

<style>
	.wrapper {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		padding: 1rem;
		overflow-x: auto;
	}

	.grid {
		display: grid;
		grid-template-columns: 2.5rem repeat(calc(var(--cols) - 1), 1fr);
		gap: 2px;
		min-width: 480px;
	}

	.cell {
		height: 2rem;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.7rem;
		border-radius: 4px;
	}

	.cell.header {
		color: var(--color-text-muted);
		font-weight: 600;
	}

	.cell.corner {
		background: none;
	}

	.cell.data {
		background: var(--color-border);
		color: #fff;
		cursor: default;
		transition: opacity 0.15s;
	}

	.cell.data:hover {
		opacity: 0.8;
	}

	.error {
		color: var(--color-text-muted);
		font-size: 0.85rem;
	}
</style>
