import BookForm from "@/app/books/_components/BookForm";
import type { BookFormData } from "@/types/book";

interface PageProps {
  searchParams: Promise<{
    [key: string]: string | string[] | undefined;
  }>;
}

export default async function ManualEntryPage({ searchParams }: PageProps) {
  const params = await searchParams;

  // URLパラメータからinitialDataを構築
  const initialData: BookFormData = {
    title: typeof params.title === "string" ? params.title : "",
    author: typeof params.author === "string" ? params.author : "",
    description:
      typeof params.description === "string" ? params.description : "",
    isbn: typeof params.isbn === "string" ? params.isbn : "",
    image_url: typeof params.image_url === "string" ? params.image_url : "",
    note: "",
  };

  return (
    <div className="container">
      <h2>書籍登録</h2>
      <BookForm initialData={initialData} submitLabel="登録" />
    </div>
  );
}
