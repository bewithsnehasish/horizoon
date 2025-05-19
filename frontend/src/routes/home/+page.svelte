<script lang="ts">
	import { goto } from '$app/navigation';
	import { AvatarFallback, AvatarImage, Root } from '$lib/components/ui/avatar';
	import Avatar from '$lib/components/ui/avatar/avatar.svelte';
	import Button from '$lib/components/ui/button/button.svelte';
	import Input from '$lib/components/ui/input/input.svelte';
	import Label from '$lib/components/ui/label/label.svelte';
	import * as Select from '$lib/components/ui/select';
	import { ArrowLeft, Pencil, UserCircle2 } from 'lucide-svelte';

	// Shadcn UI imports
	let name: string = '';
	let phoneNumber: string = '';
	let selectedCountryCode: string | undefined = '+91'; // Default country code, allow undefined for initial placeholder
	let selectedGender: string | undefined = undefined;
	let profilePictureUrl: string | null = null;
	let fileInput: HTMLInputElement | null = null;

	const countryCodes = [
		{ value: '+91', label: '+91 (India)' },
		{ value: '+1', label: '+1 (USA)' },
		{ value: '+44', label: '+44 (UK)' }
		// Add more as needed
	];

	const genders = [
		{ value: 'male', label: 'Male' },
		{ value: 'female', label: 'Female' },
		{ value: 'other', label: 'Other' },
		{ value: 'prefer_not_to_say', label: 'Prefer not to say' }
	];

	function goBack() {
		if (window.history.length > 1) {
			window.history.back();
		} else {
			goto('/');
		}
	}

	function triggerFileInput() {
		fileInput?.click();
	}

	function handleProfilePictureChange(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];
		if (file) {
			const reader = new FileReader();
			reader.onload = (e) => {
				profilePictureUrl = e.target?.result as string;
			};
			reader.readAsDataURL(file);
		}
	}

	async function handleSubmitProfile() {
		if (!name || !phoneNumber || !selectedGender) {
			alert('Please fill in all required fields.');
			return;
		}
		console.log('Submitting profile:', {
			name,
			countryCode: selectedCountryCode,
			phoneNumber,
			gender: selectedGender,
			profilePicture: profilePictureUrl ? 'Image selected' : 'No image'
		});
		alert('Profile submitted (mock)!');
		goto('/dashboard');
	}
Select.
</script>

<svelte:head>
	<title>Complete Your Profile</title>
</svelte:head>

<div class="flex min-h-screen flex-col bg-white font-['Inter',sans-serif] text-gray-800">
	<header class="sticky top-0 z-10 bg-white px-4 pb-2 pt-4">
		<Button
			variant="ghost"
			size="icon"
			class="rounded-full p-2 text-gray-700 hover:bg-gray-100"
			on:click={goBack}
			aria-label="Go back"
		>
			<ArrowLeft class="h-6 w-6" />
		</Button>
	</header>

	<main class="flex flex-grow flex-col items-center px-6 py-4">
		<div class="w-full max-w-sm space-y-8">
			<div>
				<h1 class="text-center text-2xl font-semibold text-gray-900 md:text-3xl">
					Complete Your Profile
				</h1>
				<p class="mt-2 text-center text-sm text-gray-500">
					Don't worry, only you can see your personal data. No one else will be able to see it.
				</p>
			</div>

			<div class="flex justify-center">
				<div class="relative">
					<Avatar class="h-32 w-32 border-2 border-gray-200">
						<AvatarImage src={profilePictureUrl} alt="Profile picture" />
						<AvatarFallback class="bg-gray-200">
							<UserCircle2 class="h-20 w-20 text-gray-400" />
						</AvatarFallback>
					</Avatar>
					<Button
						variant="secondary"
						size="icon"
						class="absolute -bottom-1 -right-1 h-9 w-9 rounded-full bg-gray-700 text-white shadow-md hover:bg-gray-600"
						on:click={triggerFileInput}
						aria-label="Edit profile picture"
					>
						<Pencil class="h-4 w-4" />
					</Button>
					<input
						type="file"
						class="hidden"
						accept="image/*"
						bind:this={fileInput}
						on:change={handleProfilePictureChange}
					/>
				</div>
			</div>

			<form on:submit|preventDefault={handleSubmitProfile} class="space-y-6">
				<div>
					<Label for="name" class="mb-1 block text-sm font-medium text-gray-700">Name</Label>
					<Input
						id="name"
						type="text"
						bind:value={name}
						placeholder="Ex: John Doe"
						class="focus:border-primary-500 border-gray-300 bg-gray-100 text-gray-800 placeholder-gray-400 focus:bg-white"
						required
					/>
				</div>

				<div>
					<Label for="phone" class="mb-1 block text-sm font-medium text-gray-700"
						>Phone Number</Label
					>
					<div
						class="focus-within:ring-primary-500 focus-within:border-primary-500 flex items-center space-x-0.5 rounded-md border border-gray-300 bg-gray-100 focus-within:bg-white focus-within:ring-1"
					>
						<Select.Root
							value={selectedCountryCode}
							onValueChange={(v) => {
								selectedCountryCode = v;
							}}
						>
							<Select.Trigger
								aria-label="Country code"
								class="w-[90px] rounded-l-md border-0 bg-transparent py-2.5 pl-3 pr-2 text-gray-700 focus:ring-0"
							>
								<Select.Value placeholder="Code" />
							</Select.Trigger>
							<Select.Content class="bg-white">
								<Select.Group>
									{#each countryCodes as code (code.value)}
										<Select.Item value={code.value} class="text-gray-700"
											>{code.label.split(' ')[0]}</Select.Item
										>
									{/each}
								</Select.Group>
							</Select.Content>
						</Select.Root>
						<div class="mx-1 h-6 border-l border-gray-300" />
						<Input
							id="phone"
							type="tel"
							bind:value={phoneNumber}
							placeholder="Enter the Phone Number"
							class="flex-1 rounded-r-md border-0 bg-transparent py-2.5 text-gray-800 placeholder-gray-400 focus:ring-0"
							pattern="[0-9]*"
							required
						/>
					</div>
				</div>

				<div>
					<Label for="gender" class="mb-1 block text-sm font-medium text-gray-700">Gender</Label>
					<Select.Root
						value={selectedGender}
						onValueChange={(v) => {
							selectedGender = v;
						}}
					>
						<SelectTrigger
							id="gender"
							class="focus:ring-primary-500 focus:border-primary-500 w-full border-gray-300 bg-gray-100 text-gray-800 placeholder-gray-400 focus:bg-white focus:ring-1"
						>
							<SelectValue placeholder="Select" />
						</SelectTrigger>
						<SelectContent class="bg-white">
							<SelectGroup>
								{#each genders as gender (gender.value)}
									<SelectItem value={gender.value} class="text-gray-700">{gender.label}</SelectItem>
								{/each}
							</SelectGroup>
						</SelectContent>
					</Select.Root>
				</div>

				<Button
					type="submit"
					class="!mt-10 w-full rounded-xl bg-gray-600 py-3 text-base font-semibold text-white hover:bg-gray-700"
				>
					Complete Profile
				</Button>
			</form>
		</div>
	</main>
</div>

<style>
	:global(
		.font-\[\'Inter\'\,sans-serif\]
			[data-state='closed']
			[data-radix-select-trigger][role='combobox']
			> span
	) {
		color: hsl(var(--foreground)) !important;
	}
	:global(
		.font-\[\'Inter\'\,sans-serif\]
			[data-state='open']
			[data-radix-select-trigger][role='combobox']
			> span
	) {
		color: hsl(var(--foreground)) !important;
	}
</style>
