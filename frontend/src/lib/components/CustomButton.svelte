<script lang="ts">
	import { cn } from '../utils'; // Utility to merge class names
	import Button from './ui/button/button.svelte';

	export let variant: 'primary' | 'secondary' | 'outline' = 'primary';
	export let className = '';
	export let type: 'button' | 'submit' | 'reset' = 'button';
	export let disabled = false;

	// Compute classes based on variant
	const variantClasses = {
		primary: 'bg-blue-500 text-white hover:bg-blue-600',
		secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
		outline: 'border-2 border-gray-200 bg-transparent text-gray-900 hover:bg-gray-50'
	};

	$: buttonClass = cn(
		'h-12 px-6 rounded-full font-medium transition-colors',
		variantClasses[variant],
		className
	);
</script>

<Button class={buttonClass} {type} {disabled} {...$$restProps}>
	<slot />
</Button>
