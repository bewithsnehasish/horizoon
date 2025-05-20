<!-- src/routes/cars/categories/+page.svelte -->
<script>
	export let data = {}; // ✅ Default to empty object to avoid undefined error
	let categories = data.categories ?? [
		'SUV',
		'Sedan',
		'Electric',
		'Luxury',
		'Hatchback',
		'Convertible'
	];
</script>

<h1>Car Categories</h1>
<ul>
	{#each categories as category (category)}
		<li>{category}</li>
	{/each}
</ul>
