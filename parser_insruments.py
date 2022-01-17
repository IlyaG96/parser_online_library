from pathvalidate import sanitize_filename
from pathlib import Path
from bs4 import BeautifulSoup
from lxml import html
import requests
import os


def download_cover(cover_link, covers_path):

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

    comments = page_content.select("#content > div.texts > span")
    if comments:
        comments = [html.document_fromstring(str(comment)).text_content() for comment in comments]

    genres = page_content.select("#content > span > a")
    genres = [html.document_fromstring(str(genre)).text_content() for genre in genres]

    header = page_content.select_one("#content > h1").text.split("::")
    title, author = [sanitize_filename(element.strip()) for element in header]

    cover_link = page_content.select_one("div.bookimage > a > img")["src"]
    cover_link = f"http://tululu.org{cover_link}"

    book_info = {
        "title": title,
        "author": author,
        "cover_link": cover_link,
        "comments": comments,
        "genres": genres
    }

    return book_info


def get_book_page_content(book_id):

    address = f"http://tululu.org/b{book_id}/"
    response = requests.get(address, verify=False, allow_redirects=False)
    response.raise_for_status()

    if response.is_redirect:
        raise requests.HTTPError

    page_content = BeautifulSoup(response.text, "lxml")

    return page_content
