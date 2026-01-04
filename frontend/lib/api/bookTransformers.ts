import type { Book, BookCreatePayload, BookFormData } from "@/types/book";
import type { UserBookCreatePayload, UserBookUpdatePayload } from "@/types/userBook";

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
export function formDataToBookCreate(formData: BookFormData): BookCreatePayload {
  return {
    isbn: formData.isbn || "",
  };
}

/**
 * BookFormDataをuser_books作成用データに変換
 */
export function formDataToUserBookCreate(
  formData: BookFormData,
  bookId: number
): UserBookCreatePayload {
  return {
    book_id: bookId,
    note: formData.note || null,
    shelf_id: formData.shelf_id ?? null,
  };
}

/**
 * BookFormDataをuser_books更新用データに変換
 */
export function formDataToUserBookUpdate(
  formData: BookFormData
): UserBookUpdatePayload {
  return {
    note: formData.note || null,
    shelf_id: formData.shelf_id ?? null,
  };
}
