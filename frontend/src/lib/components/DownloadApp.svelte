<div class="flex h-screen bg-gray-900 text-white">
	<!-- Left Side: Title and Description -->
	<div class="flex flex-1 flex-col items-start justify-center p-10">
		<h1 class="mb-4 text-6xl font-bold">Project CC Laundry</h1>
		<p class="text-2xl text-gray-400">
			Your ultimate laundry solution. Download the app now to get started!
		</p>
	</div>

	<!-- Right Side: Download Icons -->
	<div class="flex flex-1 flex-col items-center justify-center bg-gray-800 p-10">
		<h2 class="mb-8 text-3xl font-bold">Download the App</h2>
		<div class="space-y-4">
			<a
				href="https://play.google.com/store/apps/details?id=com.example.myapp"
				target="_blank"
				rel="noopener noreferrer"
				class="flex w-64 items-center justify-center rounded-lg bg-blue-600 px-6 py-3 text-white transition duration-300 hover:bg-blue-700"
			>
				<img
					src="https://cdn-icons-png.flaticon.com/512/300/300221.png"
					alt="Google Play"
					class="mr-2 h-8 w-8"
				/>
				<span>Google Play</span>
			</a>
			<a
				href="https://apps.apple.com/app/id123456789"
				target="_blank"
				rel="noopener noreferrer"
				class="flex w-64 items-center justify-center rounded-lg bg-gray-700 px-6 py-3 text-white transition duration-300 hover:bg-gray-800"
			>
				<img
					src="https://cdn-icons-png.flaticon.com/512/300/300218.png"
					alt="App Store"
					class="mr-2 h-8 w-8"
				/>
				<span>App Store</span>
			</a>
		</div>
	</div>
</div>

<style>
	/* Tailwind classes are converted to equivalent CSS for scoped styles */
	.flex {
		display: flex;
	}
	.h-screen {
		height: 100vh;
	}
	.bg-gray-900 {
		background-color: #1f2937;
	}
	.text-white {
		color: #ffffff;
	}
	.flex-1 {
		flex: 1;
	}
	.flex-col {
		flex-direction: column;
	}
	.justify-center {
		justify-content: center;
	}
	.items-start {
		align-items: flex-start;
	}
	.items-center {
		align-items: center;
	}
	.p-10 {
		padding: 2.5rem;
	}
	.text-6xl {
		font-size: 3.75rem;
		line-height: 1;
	}
	.font-bold {
		font-weight: 700;
	}
	.mb-4 {
		margin-bottom: 1rem;
	}
	.mb-8 {
		margin-bottom: 2rem;
	}
	.text-2xl {
		font-size: 1.5rem;
		line-height: 2rem;
	}
	.text-gray-400 {
		color: #9ca3af;
	}
	.bg-gray-800 {
		background-color: #374151;
	}
	.text-3xl {
		font-size: 1.875rem;
		line-height: 2.25rem;
	}
	.space-y-4 > * + * {
		margin-top: 1rem;
	}
	.w-64 {
		width: 16rem;
	}
	.px-6 {
		padding-left: 1.5rem;
		padding-right: 1.5rem;
	}
	.py-3 {
		padding-top: 0.75rem;
		padding-bottom: 0.75rem;
	}
	.bg-blue-600 {
		background-color: #2563eb;
	}
	.rounded-lg {
		border-radius: 0.5rem;
	}
	.hover\:bg-blue-700:hover {
		background-color: #1d4ed8;
	}
	.hover\:bg-gray-800:hover {
		background-color: #1f2937;
	}
	.transition {
		transition-property: all;
		transition-duration: 300ms;
		transition-timing-function: ease;
	}
	.w-8 {
		width: 2rem;
	}
	.h-8 {
		height: 2rem;
	}
	.mr-2 {
		margin-right: 0.5rem;
	}
</style>
