// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}
/// <reference types="vite/client" />

interface ImportMetaEnv {
	VITE_API_URL: string
  }

export {};
