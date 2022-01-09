from pathvalidate import sanitize_filename
from pathlib import Path
from bs4 import BeautifulSoup
from environs import Env
from lxml import html
from pprint import pprint
from tqdm import tqdm
import argparse
import requests
import os


def get_page_content(book_id):

    address = f"http://tululu.org/b{book_id}/"
    response = requests.get(address, verify=False, allow_redirects=False)
    response.raise_for_status()

    if response.is_redirect:
        raise requests.HTTPError

    page_content = BeautifulSoup(response.text, "lxml")

    return page_content


def download_covers(cover_link, covers_path):

    response = requests.get(cover_link)
    response.raise_for_status()

    cover_name = os.path.split(cover_link)[1]
    path_to_file = Path(covers_path, cover_name)

    if not path_to_file.is_file():
        with open(file=path_to_file, mode="wb") as file:
            file.write(response.content)


def download_txt(title, book_path, book_id):

    payload = {
        "id": book_id
    }
    address = f"http://tululu.org/txt.php"
    response = requests.get(address,
                            params=payload,
                            verify=False,
                            allow_redirects=False)
    response.raise_for_status()
    if response.is_redirect:
        raise requests.HTTPError

    book = response.text
    book_title = f"{title}.txt"
    path_to_file = Path(book_path, book_title)

    if not path_to_file.is_file():
        with open(file=path_to_file, mode="w") as file:
            file.write(book)


def collect_book_info(page_content):

    comments = page_content.find("div", {"id": "content"}).find_all("span", {"class": "black"})
    if comments:
        comments = [html.document_fromstring(str(comment)).text_content() for comment in comments]

    genres = page_content.select("#content > span >a")
    genres = [html.document_fromstring(str(genre)).text_content() for genre in genres]

    header = page_content.find("div", {"id": "content"}).find("h1").text.split("::")
    title, author = [sanitize_filename(element.strip()) for element in header]

    cover_link = page_content.find("div", {"class": "bookimage"}).find("img")["src"]
    cover_link = f"http://tululu.org{cover_link}"

    book_info = {
            "title": title,
            "author": author,
            "cover_link": cover_link,
            "comments": comments,
            "genres": genres

    }
    return book_info


def main():
    env = Env()
    env.read_env()
    book_path = env.str("book_path", default="./books")
    covers_path = env.str("covers_path", default="./covers")

    Path(book_path).mkdir(parents=True, exist_ok=True)
    Path(covers_path).mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(description="Введите id книг (начальный и конечный)")
    parser.add_argument("start_id",
                        help="Номер (id) первой книги",
                        type=int,
                        default=1,
                        nargs="?")
    parser.add_argument("stop_id",
                        help="Номер (id) последней книги",
                        type=int,
                        default=11,
                        nargs="?")
    parser.add_argument('-v', action="store_true",
                        help='отображение информации о книге',
                        default=False)
    args = parser.parse_args()
    progress_bar = tqdm(total=args.stop_id-args.start_id)
    for book_id in range(args.start_id, args.stop_id):
        progress_bar.update(1)
        try:
            page_content = get_page_content(book_id)
            book_info = collect_book_info(page_content)
            title = book_info["title"]
            cover_link = book_info["cover_link"]
            download_txt(title, book_path, book_id)
            download_covers(cover_link, covers_path)
            if args.v:
                pprint(book_info, width=150)
        except requests.HTTPError:
            continue


if __name__ == "__main__":
    main()
