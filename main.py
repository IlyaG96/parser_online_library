import requests

def download_book():
    url = "http://tululu.org/txt.php?id=32168"
    response = requests.get(url, verify=False)
    book = response.content

    with open(file="./books/file.txt", mode="wb") as file:
        file.write(book)


download_book()