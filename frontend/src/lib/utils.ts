import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { fly, scale, type TransitionConfig } from 'svelte/transition';

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

// Add the flyAndScale utility function needed by shadcn-svelte components
export function flyAndScale(
	node: Element,
	options: { y: number; x?: number; start?: number; duration?: number }
): TransitionConfig {
	const style = getComputedStyle(node);
	const transform = style.transform === 'none' ? '' : style.transform;

	const scaleConf = {
		start: options.start ?? 0.95,
		opacity: 0,
		duration: options.duration ?? 300
	};

	const flyConf = {
		y: options.y ?? 0,
		x: options.x ?? 0,
		duration: options.duration ?? 300
	};

	return {
		duration: options.duration ?? 300,
		delay: 0,
		css: (t) => {
			const flyTransform = `translate(${(1 - t) * flyConf.x}px, ${(1 - t) * flyConf.y}px)`;
			const scaleTransform = `scale(${t * (1 - scaleConf.start) + scaleConf.start})`;

			return `
				transform: ${transform} ${flyTransform} ${scaleTransform};
				opacity: ${t};
			`;
		}
	};
}
