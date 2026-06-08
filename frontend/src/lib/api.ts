const API_BASE = '/api';

export interface Gym {
	id: number;
	name: string;
	address: string;
}

export interface CurrentOccupancy {
	gym: Gym;
	people_count: number | null;
	measured_at: string | null;
}

export interface HourlyData {
	dow: number;
	hour: number;
	avg_people: number;
	min_people: number;
	max_people: number;
	samples_count: number;
}

export interface DailyData {
	dow: number;
	avg_people: number;
	min_people: number;
	max_people: number;
	peak_hour: number | null;
	samples_count: number;
}

export interface BestTime {
	dow: number;
	dow_name: string;
	hour: number;
	avg_people: number;
	samples_count: number;
}

export interface GymBestTimes {
	gym_id: number;
	gym_name: string;
	best_times: BestTime[];
}

async function get<T>(path: string): Promise<T> {
	const res = await fetch(`${API_BASE}${path}`);
	if (!res.ok) throw new Error(`HTTP ${res.status}: ${path}`);
	return res.json() as Promise<T>;
}

export const api = {
	getGyms: () => get<Gym[]>('/gyms'),
	getCurrentOccupancy: (gymId: number) =>
		get<CurrentOccupancy>(`/gyms/${gymId}/current`),
	getHourly: (gymId: number) => get<HourlyData[]>(`/gyms/${gymId}/hourly`),
	getDaily: (gymId: number) => get<DailyData[]>(`/gyms/${gymId}/daily`),
	getBestTimes: (params?: {
		dows?: number[];
		hourFrom?: number;
		hourTo?: number;
		maxPeople?: number;
		limit?: number;
	}) => {
		const p = new URLSearchParams();
		(params?.dows ?? [0, 1, 2, 3, 4, 5, 6]).forEach((d) => p.append('dows', String(d)));
		p.set('hour_from', String(params?.hourFrom ?? 0));
		p.set('hour_to', String(params?.hourTo ?? 23));
		p.set('max_people', String(params?.maxPeople ?? 80));
		p.set('limit', String(params?.limit ?? 5));
		return get<GymBestTimes[]>(`/analytics/best-times?${p.toString()}`);
	},
};
