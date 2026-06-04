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

	let data: GymBestTimes[] = [];
	let error: string | null = null;

	onMount(async () => {
		try {
			data = await api.getBestTimes();
		} catch {
			error = 'Błąd pobierania rekomendacji';
		}
	});
</script>

<div class="wrapper">
	<h3>Najlepsze godziny</h3>
	{#if error}
		<p class="error">{error}</p>
	{:else if data.length === 0}
		<p class="muted">Brak wystarczającej ilości danych — wróć po kilku dniach.</p>
	{:else}
		<div class="gyms">
			{#each data as gym}
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
			{/each}
		</div>
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
