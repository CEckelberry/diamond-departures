import type { Session, SupabaseClient } from '@supabase/supabase-js';

declare global {
	namespace App {
		interface Locals {
			supabase: SupabaseClient;
			session: Session | null;
		}
		interface PageData {
			user: {
				id: string;
				email: string;
				name: string | null;
				avatar_url: string | null;
				is_premium: boolean;
			} | null;
		}
	}
}

export {};
