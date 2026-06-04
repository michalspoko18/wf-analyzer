import { describe, it, expect, vi, beforeEach } from 'vitest';

// Must mock import.meta.env before importing api
vi.stubGlobal('import', { meta: { env: { VITE_API_URL: '' } } });

// Mock fetch globally
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

// Dynamically import api so the stub is in place
const { api } = await import('./api');

beforeEach(() => {
	mockFetch.mockReset();
});

function mockOk(body: unknown) {
	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: async () => body,
	});
}

function mockError(status: number) {
	mockFetch.mockResolvedValueOnce({ ok: false, status });
}

describe('api.getGyms', () => {
	it('returns gym list on success', async () => {
		const gyms = [{ id: 1, name: 'Test Gym', address: 'Test St' }];
		mockOk(gyms);

		const result = await api.getGyms();

		expect(result).toEqual(gyms);
		expect(mockFetch).toHaveBeenCalledWith('/api/gyms');
	});

	it('throws on HTTP error', async () => {
		mockError(500);
		await expect(api.getGyms()).rejects.toThrow('HTTP 500');
	});
});

describe('api.getCurrentOccupancy', () => {
	it('fetches current occupancy for a gym', async () => {
		const payload = {
			gym: { id: 2, name: 'Hanza', address: 'Wyzwolenia 46' },
			people_count: 55,
			measured_at: '2026-06-04T10:00:00Z',
		};
		mockOk(payload);

		const result = await api.getCurrentOccupancy(2);

		expect(result.people_count).toBe(55);
		expect(mockFetch).toHaveBeenCalledWith('/api/gyms/2/current');
	});

	it('throws on 404', async () => {
		mockError(404);
		await expect(api.getCurrentOccupancy(99)).rejects.toThrow('HTTP 404');
	});
});

describe('api.getHourly', () => {
	it('fetches hourly data', async () => {
		const rows = [{ dow: 0, hour: 8, avg_people: 12, min_people: 5, max_people: 20, samples_count: 3 }];
		mockOk(rows);

		const result = await api.getHourly(1);

		expect(result).toEqual(rows);
		expect(mockFetch).toHaveBeenCalledWith('/api/gyms/1/hourly');
	});
});

describe('api.getBestTimes', () => {
	it('fetches best times', async () => {
		const payload = [{ gym_id: 1, gym_name: 'Test', best_times: [] }];
		mockOk(payload);

		const result = await api.getBestTimes();

		expect(result).toEqual(payload);
		expect(mockFetch).toHaveBeenCalledWith('/api/analytics/best-times');
	});
});
