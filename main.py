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

    page_content = BeautifulSoup(response.text, 'lxml')

    return page_content


def parse_book_title(page_content):

    header = page_content.find("div", {"id": "content"}).find('h1').text.split("::")
    book_title = 0
    title = header[book_title].strip()

    return title


def parse_cover_link(page_content):

    cover_link = page_content.find("div", {"class": "bookimage"}).find('img')['src']

    return f"http://tululu.org{cover_link}"


def download_books_covers(cover_link, covers_path):

    book_title_index = 1
    response = requests.get(cover_link)
    response.raise_for_status()
    cover_name = os.path.split(cover_link)[book_title_index]
    path_to_file = Path(covers_path, cover_name)

    if not Path(path_to_file).is_file():
        with open(file=path_to_file, mode="wb") as file:
            file.write(response.content)


def download_txt(filename, book_path, book_id):

    filename = sanitize_filename(filename)
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
    book = response.content

    path_to_file = Path(book_path, filename)
    with open(file=f"{path_to_file}.txt", mode="wb") as file:
        file.write(book)


def collect_book_info(title, cover_link, page_content):

    comments = page_content.find("div", {"id": "content"}).find_all("span", {"class": "black"})
    if comments:
        comments = [html.document_fromstring(str(comment)).text_content() for comment in comments]

    genres = page_content.select("#content > span >a")
    genres = [html.document_fromstring(str(genre)).text_content() for genre in genres]

    header = page_content.find("div", {"id": "content"}).find('h1').text.split("::")
    book_author = 1
    author = header[book_author].strip()

    book_info = {
        title: {
            "author": author,
            "cover_link": cover_link,
            "comments": comments,
            "genres": genres
        }
    }

    return book_info


def main():
    env = Env()
    env.read_env()
    book_path = env.str("book_path", default="./books")
    covers_path = env.str("covers_path", default="./covers")

    Path(book_path).mkdir(parents=True, exist_ok=True)
    Path(covers_path).mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(description='Введите id книг (начальный и конечный)')
    parser.add_argument('start_id',
                        help='Номер (id) первой книги',
                        type=int,
                        default=1,
                        nargs='?')
    parser.add_argument('stop_id',
                        help='Номер (id) последней книги',
                        type=int,
                        default=11,
                        nargs='?')
    parser.add_argument('show_info',
                        help='отображение информации о книге (любое число)',
                        type=int,
                        default=0,
                        nargs='?')
    args = parser.parse_args()
    progress_bar = tqdm(total=args.stop_id-args.start_id)
    for book_id in range(args.start_id, args.stop_id):
        progress_bar.update(1)
        try:
            page_content = get_page_content(book_id)
            title = parse_book_title(page_content)
            cover_link = parse_cover_link(page_content)
            download_txt(title, book_path, book_id)
            download_books_covers(cover_link, covers_path)
            if args.show_info:
                pprint(collect_book_info(title, cover_link, page_content), width=150)
        except requests.HTTPError:
            continue


if __name__ == '__main__':
    main()
