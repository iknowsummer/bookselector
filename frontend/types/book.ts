export type Book = {
  id: number;
  title: string;
  author?: string | null;
  description?: string | null;
  note?: string | null;
  image_url?: string | null;
};
