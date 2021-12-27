import requests
import pathlib
from environs import Env
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def parse_books_description(book_id, url):

    address = f"{url}/b{book_id}/"
    response = requests.get(address, verify=False, allow_redirects=False)
    response.raise_for_status()

    if response.is_redirect:
        raise requests.HTTPError

    content = BeautifulSoup(response.text, 'lxml')
    header = content.find("div", {"id": "content"}).find('h1').text
    book_title = 0
    book_author = 1
    title = header.split("::")[book_title].strip()
    author = header.split("::")[book_author].strip()

    return f"'{title}'-{author}"


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



def parse_books_imgs():
    pass


def main():
    env = Env()
    env.read_env()
    book_path = env.str("book_path")
    url = "http://tululu.org"

    for book_id in range(1, 11):
        try:
            filename = parse_books_description(book_id, url)
            download_txt(url, filename, book_path, book_id)
        except requests.HTTPError:
            continue


if __name__ == '__main__':
    main()