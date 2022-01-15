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
from main import download_txt, download_cover, collect_book_info, get_book_page_content
import json


def write_book_info_to_json(book_info):
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


def download_txt_and_cover(book_id, book_info, covers_path, book_path):
    title = book_info["title"]
    cover_link = book_info["cover_link"]
    download_txt(title, book_path, book_id)
    download_cover(cover_link, covers_path)


def download_book_pack(book_path, covers_path, books_ids):

    for book_id in books_ids:
        try:
            book_page_content = get_book_page_content(book_id)
            book_info = collect_book_info(book_page_content)
            download_txt_and_cover(book_id, book_info, covers_path, book_path)
            write_book_info_to_json(book_info)
        except requests.exceptions.HTTPError:
            continue


def main():

    env = Env()
    env.read_env()
    book_path = env.str("book_path", default="./books")
    covers_path = env.str("covers_path", default="./covers")

    Path(book_path).mkdir(parents=True, exist_ok=True)
    Path(covers_path).mkdir(parents=True, exist_ok=True)

    pages = range(1, 2)
    for page in pages:
        page_content = get_content(page)
        books_ids = get_books_ids(page_content)
        download_book_pack(book_path, covers_path, books_ids)


if __name__ == '__main__':
    main()