import type { Shelf, ShelfFormData } from "@/types/shelf";
import { getApiBaseUrl } from "./client";

export const fetchShelves = async (): Promise<Shelf[]> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/shelves/`);
  if (!res.ok) {
    throw new Error("棚情報の取得に失敗しました");
  }
  return await res.json();
};

export const fetchShelf = async (id: number): Promise<Shelf> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/shelves/${id}`);
  if (!res.ok) {
    if (res.status === 404) {
      throw new Error("棚が見つかりません");
    }
    throw new Error("棚情報の取得に失敗しました");
  }
  return await res.json();
};

export const createShelf = async (formData: ShelfFormData): Promise<Shelf> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/shelves/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  });
  if (!res.ok) {
    throw new Error("棚の登録に失敗しました");
  }
  return await res.json();
};

export const updateShelf = async (
  id: number,
  formData: Partial<ShelfFormData>
): Promise<Shelf> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/shelves/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  });
  if (!res.ok) {
    if (res.status === 404) {
      throw new Error("棚が見つかりません");
    }
    throw new Error("棚の更新に失敗しました");
  }
  return await res.json();
};

export const deleteShelf = async (id: number): Promise<void> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/shelves/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    if (res.status === 404) {
      throw new Error("棚が見つかりません");
    }
    throw new Error("棚の削除に失敗しました");
  }
};
