from pathlib import Path
from bs4 import BeautifulSoup
from environs import Env
import argparse
import requests
from main import download_txt, download_cover, collect_book_info, get_book_page_content
import json


def write_book_info_to_json(book_info, json_path):
    with open(file="books.json", mode="a") as file:
        json.dump(book_info, file, ensure_ascii=False, indent=2)


def get_content(page):
    address = f"http://tululu.org/l55/{page}/"
    response = requests.get(address, verify=False, allow_redirects=False)
    response.raise_for_status()

    page_content = BeautifulSoup(response.text, "lxml")

    return page_content


def get_books_ids(page_content):
    links = page_content.select("#content>table>tr:nth-child(2)>td>a", href=True)
    book_links = ["".join(filter(str.isdigit, link["href"])) for link in links]

    return book_links


def download_txt_and_cover(book_id, book_info, covers_path, book_path, args):
    title = book_info["title"]
    cover_link = book_info["cover_link"]
    if not args.skip_imgs:
        download_cover(cover_link, covers_path)
    if not args.skip_txt:
        download_txt(title, book_path, book_id)


def start_parsing(book_path, covers_path, books_ids, args, json_path):

    for book_id in books_ids:
        try:
            book_page_content = get_book_page_content(book_id)
            book_info = collect_book_info(book_page_content)
            download_txt_and_cover(book_id, book_info, covers_path, book_path, args)
            write_book_info_to_json(book_info, json_path)
        except requests.exceptions.HTTPError:
            continue


def main():

    env = Env()
    env.read_env()
    book_path = env.str("book_path", default="./books")
    covers_path = env.str("covers_path", default="./covers")
    json_path = env.str("json_path", defaul="./json")

    parser = argparse.ArgumentParser(description="Введите id книг (начальный и конечный)")
    parser.add_argument("start_page",
                        help="Номер первой страницы",
                        type=int,
                        default=1,
                        nargs="?")
    parser.add_argument("stop_page",
                        help="Номер последней страницы",
                        type=int,
                        default=3,
                        nargs="?")
    parser.add_argument('-book_path',
                        help='Вручную определить директорию для скачивания книг',
                        default=book_path,
                        type=str,
                        nargs="?")
    parser.add_argument('-skip_imgs',
                        action="store_true",
                        help='не загружать картинки',
                        default=False)
    parser.add_argument('-skip_txt',
                        action="store_true",
                        help='не загружить txt книг',
                        default=False)
    parser.add_argument('-json_path',
                        help='вручную определить путь к *.json файлу',
                        default=json_path,
                        type=str,
                        nargs="?")
    parser.add_argument('-covers_path',
                        help='вручную определить путь к *.json файлу',
                        default=covers_path,
                        type=str,
                        nargs="?")

    args = parser.parse_args()
    print(args)

    pages = range(args.start_page, args.stop_page)

    Path(args.book_path).mkdir(parents=True, exist_ok=True)
    Path(args.covers_path).mkdir(parents=True, exist_ok=True)
    Path(args.json_path).mkdir(parents=True, exist_ok=True)

    for page in pages:
        page_content = get_content(page)
        books_ids = get_books_ids(page_content)
        start_parsing(book_path, covers_path, books_ids, args, json_path)


if __name__ == '__main__':
    main()