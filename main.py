import requests
import pathlib
from environs import Env
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def get_page_content(book_id, url):

    address = f"{url}/b{book_id}/"
    response = requests.get(address, verify=False, allow_redirects=False)
    response.raise_for_status()

    if response.is_redirect:
        raise requests.HTTPError

    page_content = BeautifulSoup(response.text, 'lxml')

    return page_content


def parse_book_author(page_content):
    header = page_content.find("div", {"id": "content"}).find('h1').text.split("::")
    book_author = 1
    author = header[book_author].strip()

    return author


def parse_book_title(page_content):

    header = page_content.find("div", {"id": "content"}).find('h1').text.split("::")
    book_title = 0
    title = header[book_title].strip()

    return title


def parse_cover_link(page_content, url):

    picture_link = page_content.find("div", {"class": "bookimage"}).find('img')['src']

    return f"{url}{picture_link}"


def download_txt(url, filename, book_path, book_id):
    filename = sanitize_filename(filename)

    address = f"{url}/txt.php?id={book_id}"
    response = requests.get(address, verify=False, allow_redirects=False)
    response.raise_for_status()
    if response.is_redirect:
        raise requests.HTTPError
    book = response.content
    pathlib.Path(book_path).mkdir(parents=True, exist_ok=True)

    with open(file=f"./books/{filename}.txt", mode="wb") as file:
        file.write(book)


def download_books_covers(cover_link, book_path, book_id):

    response = requests.get(cover_link)
    response.raise_for_status()

    with open(file=f"{book_path}/{book_id}.jpg", mode="wb") as file:
        file.write(response.content)


def main():
    env = Env()
    env.read_env()
    book_path = env.str("book_path")
    url = "http://tululu.org"

    for book_id in range(1, 11):
        try:
            page_content = get_page_content(book_id, url)
            title = parse_book_title(page_content)
            author = parse_book_author(page_content)
            cover_link = parse_cover_link(page_content, url)
#           download_txt(url, filename, book_path, book_id)
            download_books_covers(cover_link, book_path, book_id)
        except requests.HTTPError:
            continue


if __name__ == '__main__':
    main()