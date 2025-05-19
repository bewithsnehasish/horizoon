import type { RequestEvent } from './$types';

export type RequestHandler = (event: RequestEvent) => Promise<Response>;
