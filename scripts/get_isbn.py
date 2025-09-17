import requests
import pandas as pd


# Google Books APIで書籍情報（タイトル・著者・出版日・ISBN-13・画像URL）を取得
def get_book_info_from_googlebooks(title, count=10):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"intitle:{title}",
        "maxResults": count,
        "printType": "books",
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("APIリクエスト失敗:", response.status_code)
        return None
    data = response.json()
    items = data.get("items", [])
    if not items:
        return None
    # 最初にISBN-13があるものを優先
    for item in items:
        volume_info = item.get("volumeInfo", {})
        title_text = volume_info.get("title", "")
        authors = ", ".join(volume_info.get("authors", []))
        date_text = volume_info.get("publishedDate", "")
        image_url = None
        if "imageLinks" in volume_info:
            img = volume_info["imageLinks"]
            for key in [
                "extraLarge",
                "large",
                "medium",
                "small",
                "thumbnail",
                "smallThumbnail",
            ]:
                if key in img:
                    image_url = img[key]
                    break

        isbn13 = None
        for idinfo in volume_info.get("industryIdentifiers", []):
            if idinfo.get("type") == "ISBN_13":
                isbn13 = idinfo.get("identifier")
                break
        if isbn13:
            return {
                "title": title_text,
                "authors": authors,
                "publishedDate": date_text,
                "isbn13": isbn13,
                "image_url": image_url,
            }
    # ISBN-13がなければ最初の書籍情報を返す
    item = items[0]
    volume_info = item.get("volumeInfo", {})
    title_text = volume_info.get("title", "")
    authors = ", ".join(volume_info.get("authors", []))
    date_text = volume_info.get("publishedDate", "")
    image_url = None
    if "imageLinks" in volume_info:
        img = volume_info["imageLinks"]
        for key in [
            "extraLarge",
            "large",
            "medium",
            "small",
            "thumbnail",
            "smallThumbnail",
        ]:
            if key in img:
                image_url = img[key]
                break
    isbn13 = None
    for idinfo in volume_info.get("industryIdentifiers", []):
        if idinfo.get("type", "").startswith("ISBN"):
            isbn13 = idinfo.get("identifier")
            break
    return {
        "title": title_text,
        "authors": authors,
        "publishedDate": date_text,
        "isbn13": isbn13,
        "image_url": image_url,
    }


def process_csv_and_save(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    isbn_list = []
    image_url_list = []
    description_list = []
    for title in df["title"]:
        print(title)
        info = get_book_info_from_googlebooks(title)
        if info:
            isbn_list.append(info.get("isbn13"))
            image_url_list.append(info.get("image_url"))
            description_list.append(info.get("description"))
        else:
            isbn_list.append(None)
            image_url_list.append(None)
            description_list.append(None)
    df["isbn13"] = isbn_list
    df["image_url"] = image_url_list
    df.to_csv(output_csv, index=False)


# 使用例
if __name__ == "__main__":
    # input_csv = "scripts/sample-books.csv"
    input_csv = "scripts/japanese_picture_books_50.csv"
    output_csv = "scripts/sample-books_with_isbn_image.csv"
    process_csv_and_save(input_csv, output_csv)
