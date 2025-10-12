export type Book = {
  id: number;
  title: string;
  author: string;
  description?: string | null;
  note?: string | null;
  image_url?: string;
};
