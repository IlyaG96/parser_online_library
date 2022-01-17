from parser_insruments import download_txt, download_cover, collect_book_info, get_book_page_content
from pathlib import Path
from environs import Env
from pprint import pprint
from tqdm import tqdm
import argparse
import requests


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
            page_content = get_book_page_content(book_id)
            book_info = collect_book_info(page_content)
            title = book_info["title"]
            cover_link = book_info["cover_link"]
            download_txt(title, book_path, book_id)
            download_cover(cover_link, covers_path)
            if args.v:
                pprint(book_info, width=150)
        except requests.HTTPError:
            continue


if __name__ == "__main__":
    main()
