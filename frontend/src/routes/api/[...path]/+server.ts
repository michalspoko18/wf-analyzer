import type { RequestHandler } from '@sveltejs/kit';

const API_INTERNAL_URL = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
const API_KEY = process.env.API_KEY ?? '';

async function proxy(request: Request, path: string): Promise<Response> {
	const url = `${API_INTERNAL_URL}/api/${path}${request.url.includes('?') ? '?' + new URL(request.url).search.slice(1) : ''}`;

	const headers = new Headers(request.headers);
	headers.set('X-API-Key', API_KEY);
	// Remove hop-by-hop headers
	headers.delete('host');
	headers.delete('connection');

	const upstream = await fetch(url, {
		method: request.method,
		headers,
		body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
	});

	return new Response(upstream.body, {
		status: upstream.status,
		headers: upstream.headers,
	});
}

export const GET: RequestHandler = async ({ request, params }) => {
	return proxy(request, params.path ?? '');
};
