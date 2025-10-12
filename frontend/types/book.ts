export type Book = {
  id: number;
  title: string;
  author?: string | null;
  description?: string | null;
  target_age?: string | null;
  isbn?: string | null;
  note?: string | null;
  image_url?: string | null;
};
