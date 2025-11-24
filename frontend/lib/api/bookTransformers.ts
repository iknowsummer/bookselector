import type { Book, BookFormData } from "@/types/book";

/**
 * Book型からBookFormData型へ変換
 * null/undefinedを空文字列に変換してフォーム表示用データを作成
 */
export function bookToFormData(book: Book): BookFormData {
  return {
    title: book.title,
    author: book.author ?? "",
    description: book.description ?? "",
    isbn: book.isbn ?? "",
    image_url: book.image_url ?? "",
    note: book.note ?? "",
    shelf_id: book.shelf_id ?? null,
  };
}

/**
 * BookFormDataをAPI更新用のデータ形式に変換
 * 空文字列をnullに変換してバックエンドの期待する形式にする
 */
export function formDataToBookUpdate(formData: BookFormData): {
  title: string;
  author: string | null;
  description: string | null;
  isbn: string | null;
  image_url: string | null;
  note: string | null;
  shelf_id: number | null;
} {
  return {
    title: formData.title,
    author: formData.author || null,
    description: formData.description || null,
    isbn: formData.isbn || null,
    image_url: formData.image_url || null,
    note: formData.note || null,
    shelf_id: formData.shelf_id ?? null,
  };
}

/**
 * BookFormDataをAPI作成用のBook形式に変換
 * 新規作成時に必要なフィールドを追加
 */
export function formDataToBookCreate(formData: BookFormData): Omit<Book, "id"> {
  return {
    ...formDataToBookUpdate(formData),
    status: "unread",
    created_at: new Date().toISOString(),
  };
}
