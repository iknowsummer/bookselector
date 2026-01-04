export type Shelf = {
  id: number;
  user_id: number;
  name: string;
  memo: string | null;
  created_at: string;
};

export type ShelfFormData = {
  name: string;
  memo: string | null;
};
