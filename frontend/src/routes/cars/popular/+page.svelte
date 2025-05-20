<!-- src/routes/cars/popular/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	export let data;
	let popularCars = data.cars;

	function navigateToCarDetail(carId) {
		goto(`/cars/${carId}`);
	}
</script>

<h1>Popular Cars</h1>
<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
	{#each popularCars as car (car.id)}
		<div
			on:click={() => navigateToCarDetail(car.id)}
			on:keydown={(e) => e.key === 'Enter' && navigateToCarDetail(car.id)}
			role="button"
			tabindex="0"
			class="rounded-lg border bg-slate-800 p-4 text-gray-200"
		>
			<h2>{car.name}</h2>
			<p>{car.brand}</p>
			<p>${car.pricePerDay}/day</p>
		</div>
	{/each}
</div>
