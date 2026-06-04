<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { api, type CurrentOccupancy } from '$lib/api';

	export let gymId: number;
	export let gymName: string;

	let data: CurrentOccupancy | null = null;
	let error: string | null = null;
	let interval: ReturnType<typeof setInterval>;

	async function load() {
		try {
			data = await api.getCurrentOccupancy(gymId);
			error = null;
		} catch {
			error = 'Błąd pobierania danych';
		}
	}

	onMount(() => {
		load();
		interval = setInterval(load, 5 * 60 * 1000);
	});

	onDestroy(() => clearInterval(interval));

	$: occupancyClass =
		data?.people_count == null
			? 'neutral'
			: data.people_count < 30
				? 'low'
				: data.people_count < 70
					? 'mid'
					: 'high';
</script>

<div class="card {occupancyClass}">
	<div class="gym-name">{gymName}</div>
	{#if error}
		<p class="error">{error}</p>
	{:else if data}
		<div class="count">{data.people_count ?? '—'}</div>
		<div class="label">osób teraz</div>
		{#if data.measured_at}
			<div class="time">
				{new Date(data.measured_at).toLocaleTimeString('pl-PL', {
					hour: '2-digit',
					minute: '2-digit'
				})}
			</div>
		{/if}
	{:else}
		<div class="loading">ładowanie…</div>
	{/if}
</div>

<style>
	.card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		padding: 1.5rem;
		text-align: center;
		transition: border-color 0.3s;
	}

	.card.low {
		border-color: var(--color-success);
	}

	.card.mid {
		border-color: var(--color-warning);
	}

	.card.high {
		border-color: var(--color-danger);
	}

	.gym-name {
		font-size: 0.85rem;
		color: var(--color-text-muted);
		margin-bottom: 0.5rem;
	}

	.count {
		font-size: 3rem;
		font-weight: 700;
		line-height: 1;
	}

	.label {
		font-size: 0.8rem;
		color: var(--color-text-muted);
		margin-top: 0.25rem;
	}

	.time {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		margin-top: 0.75rem;
	}

	.error,
	.loading {
		color: var(--color-text-muted);
		font-size: 0.85rem;
	}
</style>
