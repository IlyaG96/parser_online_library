import requests
import pathlib
from environs import Env



def download_books(book_path):

    for id in range(10):
        url = f"http://tululu.org/txt.php?id={id}"
        response = requests.get(url, verify=False)
        book = response.content
        pathlib.Path(book_path).mkdir(parents=True, exist_ok=True)

        with open(file=f"./books/{id}.txt", mode="wb") as file:
            file.write(book)


def main():
    env = Env()
    env.read_env()
    book_path = env.str("book_path")

    download_books(book_path)
