import requests
import pathlib
from environs import Env
from bs4 import BeautifulSoup


def download_books(book_path):

    for book_id in range(1, 11):
        url = f"http://tululu.org/txt.php?id={book_id}"
        response = requests.get(url, verify=False, allow_redirects=False)
        response.raise_for_status()
        if response.is_redirect:
            continue
        book = response.content
        pathlib.Path(book_path).mkdir(parents=True, exist_ok=True)

        with open(file=f"./books/{book_id}.txt", mode="wb") as file:
            file.write(book)


def parse_books_titles():
    for book_id in range(1, 11):
        url = f"http://tululu.org/b{book_id}/"
        response = requests.get(url, verify=False, allow_redirects=False)
        response.raise_for_status()

        if response.is_redirect:
            continue

        content = BeautifulSoup(response.text, 'lxml')
        header = content.find("div", {"id": "content"}).find('h1').text
        book_title = 0
        book_author = 1
        title = header.split("::")[book_title].strip()
        author = header.split("::")[book_author].strip()


def download_txt(url):


    pass

def parse_books_imgs():
    pass


def main():
    env = Env()
    env.read_env()
    book_path = env.str("book_path")

 #   download_books(book_path)

    parse_books_titles()

if __name__ == '__main__':
    main()