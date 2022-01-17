from parser_insruments import download_txt, download_cover, collect_book_info, get_book_page_content
from pathlib import Path
from bs4 import BeautifulSoup
from environs import Env
import argparse
import requests
import json


def write_book_info_to_json(book_info, json_path):
    file_path = Path(json_path, "books.json")
    with open(file=file_path, mode="a") as file:
        json.dump(book_info, file, ensure_ascii=False, indent=2)


def get_content(page):
    address = f"http://tululu.org/l55/{page}/"
    response = requests.get(address, verify=False, allow_redirects=False)
    response.raise_for_status()
    if response.is_redirect:
        raise requests.HTTPError

    page_content = BeautifulSoup(response.text, "lxml")

    return page_content


def get_last_page(page_content):
    last_page_index = -1
    last_page = page_content.select("#content > .center >.npage")[last_page_index].text
    return last_page


def get_books_ids(page_content):
    links = page_content.select("#content>table>tr:nth-child(2)>td>a", href=True)
    book_ids = ["".join(filter(str.isdigit, link["href"])) for link in links]

    return book_ids


def parse_tululu_category(book_path, covers_path, args, json_path):
    books = []
    if args.last_page:
        pages = range(args.start_page, int(args.last_page))

    else:
        page_content = get_content(args.start_page)
        last_page = get_last_page(page_content)
        pages = range(args.start_page, int(last_page))

    for page in pages:
        page_content = get_content(page)
        books_ids = get_books_ids(page_content)
        for book_id in books_ids:
            try:
                book_page_content = get_book_page_content(book_id)
                book_info = collect_book_info(book_page_content)
                title = book_info["title"]
                cover_link = book_info["cover_link"]
                if not args.skip_imgs:
                    download_cover(cover_link, covers_path)
                if not args.skip_txt:
                    download_txt(title, book_path, book_id)
                books.append(book_info)
            except requests.exceptions.HTTPError:
                continue

        write_book_info_to_json(books, json_path)


def main():

    env = Env()
    env.read_env()
    book_path = env.str("book_path", default="./books")
    covers_path = env.str("covers_path", default="./covers")
    json_path = env.str("json_path", defaul="./json")

    parser = argparse.ArgumentParser(
        description="Введите начальную и конечную страницу для скачивания")
    parser.add_argument("start_page",
                        help="Номер первой страницы",
                        type=int,
                        default=1,
                        nargs="?")
    parser.add_argument("last_page",
                        help="Номер последней страницы",
                        nargs="?")
    parser.add_argument('-book_path',
                        help='Вручную определить директорию для скачивания книг',
                        default=book_path,
                        nargs="?")
    parser.add_argument('-skip_imgs',
                        action="store_true",
                        help='не загружать картинки')
    parser.add_argument('-skip_txt',
                        action="store_true",
                        help='не загружить txt книг')
    parser.add_argument('-json_path',
                        help='вручную определить путь к *.json файлу',
                        default=json_path,
                        nargs="?")
    parser.add_argument('-covers_path',
                        help='вручную определить директорию для скачивания обложек книг',
                        default=covers_path,
                        nargs="?")

    args = parser.parse_args()

    Path(args.book_path).mkdir(parents=True, exist_ok=True)
    Path(args.covers_path).mkdir(parents=True, exist_ok=True)
    Path(args.json_path).mkdir(parents=True, exist_ok=True)

    parse_tululu_category(book_path, covers_path, args, json_path)


if __name__ == '__main__':
    main()
