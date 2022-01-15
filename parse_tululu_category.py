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
from urllib.parse import urljoin

def get_page_content():

    address = f"http://tululu.org/l55/"
    response = requests.get(address, verify=False, allow_redirects=False)
    response.raise_for_status()

    if response.is_redirect:
        raise requests.HTTPError

    page_content = BeautifulSoup(response.text, "lxml")

    return page_content


def get_book_links(page_content):

    links = page_content.select("#content>table>tr:nth-child(2)>td>a", href=True)
    base_url = "http://tululu.org/"
    book_links = [urljoin(base_url, str(link["href"])) for link in links]
    pprint(book_links)
