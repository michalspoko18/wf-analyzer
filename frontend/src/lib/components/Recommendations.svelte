<script lang="ts">
	import { onMount } from 'svelte';
	import { api, type GymBestTimes } from '$lib/api';

	const DOW_PL: Record<string, string> = {
		Monday: 'poniedziałek',
		Tuesday: 'wtorek',
		Wednesday: 'środa',
		Thursday: 'czwartek',
		Friday: 'piątek',
		Saturday: 'sobota',
		Sunday: 'niedziela'
	};

	const DOW_SHORT = ['Pon', 'Wt', 'Śr', 'Czw', 'Pt', 'Sob', 'Nd'];
	const HOUR_OPTIONS = Array.from({ length: 24 }, (_, i) => i);

	let data: GymBestTimes[] = [];
	let error: string | null = null;
	let loading = false;
	let selectedDows = new Set([0, 1, 2, 3, 4, 5, 6]);
	let hourFrom = 0;
	let hourTo = 23;
	let maxPeople = 80;

	function toggleDow(d: number) {
		if (selectedDows.has(d)) {
			if (selectedDows.size > 1) selectedDows.delete(d);
		} else {
			selectedDows.add(d);
		}
		selectedDows = new Set(selectedDows);
	}

	async function load() {
		loading = true;
		error = null;
		try {
			data = await api.getBestTimes({
				dows: [...selectedDows],
				hourFrom,
				hourTo,
				maxPeople
			});
		} catch {
			error = 'Błąd pobierania rekomendacji';
		} finally {
			loading = false;
		}
	}

	$: selectedDows, hourFrom, hourTo, maxPeople, load();

	onMount(load);
</script>

<div class="wrapper">
	<h3>Najlepsze godziny</h3>
	{#if error}
		<p class="error">{error}</p>
	{:else}
		<div class="filters">
			<div class="dow-tabs">
				{#each DOW_SHORT as name, i}
					<button class:active={selectedDows.has(i)} on:click={() => toggleDow(i)}>{name}</button>
				{/each}
			</div>
			<div class="hour-range">
				<label>
					Od
					<select bind:value={hourFrom} on:change={() => { if (hourFrom > hourTo) hourTo = hourFrom; }}>
						{#each HOUR_OPTIONS as h}
							<option value={h}>{h}:00</option>
						{/each}
					</select>
				</label>
				<label>
					Do
					<select bind:value={hourTo} on:change={() => { if (hourTo < hourFrom) hourFrom = hourTo; }}>
						{#each HOUR_OPTIONS as h}
							<option value={h}>{h}:00</option>
						{/each}
					</select>
				</label>
				<label class="max-people">
					Maks. osób
					<input
						type="number"
						bind:value={maxPeople}
						min="1"
						max="999"
					/>
				</label>
			</div>
		</div>
		{#if loading}
			<p class="muted">Ładowanie…</p>
		{:else if data.length === 0}
			<p class="muted">Brak wystarczającej ilości danych — wróć po kilku dniach.</p>
		{:else}
			<div class="gyms">
				{#each data as gym}
					{#if gym.best_times.length > 0}
						<div class="gym-block">
							<div class="gym-name">{gym.gym_name}</div>
							<ol>
								{#each gym.best_times as slot}
									<li>
										<span class="slot"
											>{DOW_PL[slot.dow_name] ?? slot.dow_name}, {slot.hour}:00–{slot.hour +
												1}:00</span
										>
										<span class="avg">śr. {slot.avg_people} os.</span>
									</li>
								{/each}
							</ol>
						</div>
					{/if}
				{/each}
				{#if data.every((g) => g.best_times.length === 0)}
					<p class="muted">Brak wyników dla wybranych filtrów.</p>
				{/if}
			</div>
		{/if}
	{/if}
</div>

<style>
	.wrapper {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		padding: 1.25rem;
	}

	h3 {
		font-size: 1rem;
		margin-bottom: 1rem;
	}

	.filters {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.75rem;
		margin-bottom: 1.25rem;
	}

	.dow-tabs {
		display: flex;
		gap: 0.25rem;
		flex-wrap: wrap;
	}

	.dow-tabs button {
		background: none;
		border: 1px solid var(--color-border);
		color: var(--color-text-muted);
		border-radius: 6px;
		padding: 0.25rem 0.6rem;
		font-size: 0.8rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	.dow-tabs button.active,
	.dow-tabs button:hover {
		background: var(--color-accent);
		border-color: var(--color-accent);
		color: #fff;
	}

	.hour-range {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		font-size: 0.8rem;
		color: var(--color-text-muted);
	}

	.hour-range label {
		display: flex;
		align-items: center;
		gap: 0.35rem;
	}

	.hour-range select {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 6px;
		color: var(--color-text-muted);
		padding: 0.2rem 0.4rem;
		font-size: 0.8rem;
		cursor: pointer;
	}

	.hour-range select:focus {
		outline: 1px solid var(--color-accent);
	}

	.max-people input {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 6px;
		color: var(--color-text-muted);
		padding: 0.2rem 0.4rem;
		font-size: 0.8rem;
		width: 5rem;
	}

	.max-people input:focus {
		outline: 1px solid var(--color-accent);
	}

	.gyms {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		gap: 1.5rem;
	}

	.gym-name {
		font-size: 0.8rem;
		color: var(--color-text-muted);
		margin-bottom: 0.5rem;
		font-weight: 600;
	}

	ol {
		padding-left: 1.2rem;
	}

	li {
		font-size: 0.85rem;
		display: flex;
		justify-content: space-between;
		gap: 0.5rem;
		padding: 0.15rem 0;
	}

	.avg {
		color: var(--color-text-muted);
		white-space: nowrap;
	}

	.muted,
	.error {
		color: var(--color-text-muted);
		font-size: 0.85rem;
	}
</style>
