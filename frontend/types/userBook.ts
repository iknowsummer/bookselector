import type { BookStatus } from "@/types/book";

export type UserBook = {
  id: number;
  user_id: number;
  book_id: number;
  note?: string | null;
  status: BookStatus;
  shelf_id?: number | null;
  created_at: string;
  updated_at: string;
};

export type UserBookCreatePayload = {
  book_id: number;
  note?: string | null;
  shelf_id?: number | null;
  status?: BookStatus;
};

export type UserBookUpdatePayload = {
  note?: string | null;
  shelf_id?: number | null;
  status?: BookStatus;
};
