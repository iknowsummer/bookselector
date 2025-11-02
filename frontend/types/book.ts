export type BookStatus = "unread" | "picked" | "read";

export type Book = {
  id: number;
  title: string;
  author?: string | null;
  description?: string | null;
  target_age?: string | null;
  isbn?: string | null;
  note?: string | null;
  image_url?: string | null;
  status: BookStatus;
  created_at: string;
};

export type BookFormData = {
  title: string;
  author: string;
  description: string;
  isbn: string;
  note: string;
};
