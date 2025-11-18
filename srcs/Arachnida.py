import argparse
import os
import requests
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "img" and "src" in attrs_dict:
            self.images.append(attrs_dict["src"])
        elif tag == "a" and "href" in attrs_dict:
            self.links.append(attrs_dict["href"])


class Arachnida:
    def __init__(self):
        self.url = ""
        self.recurse = False
        self.level = 5
        self.counter = 0
        self.threads = []

        self.all_links = []
        self.all_images = []

        self.links_visited = set()
        self._init_parser_args()

        self.executor = ThreadPoolExecutor(max_workers=5)

    def __str__(self):
        images = "\n".join(str(img) for img in self.all_images)
        links = "\n".join(str(link) for link in self.all_links)
        return f"Images:\n{images}\n\nLinks:\n{links}"

    def _parse_args(self):
        args = self.parser.parse_args()
        self.url = args.url
        self.recurse = args.recurse
        self.level = args.level if args.level else 5
        self.path = args.path if args.path else "data"

        # Ensure the URL has a scheme
        url_parsed = urlparse(self.url)
        if not url_parsed.scheme:
            self.url = "https://" + self.url

    def _init_parser_args(self):
        self.parser = argparse.ArgumentParser(
            prog="Arachnida",
            description="A simple web self to extract images and external links from a webpage.",
        )
        self.parser.add_argument("url")

        self.parser.add_argument(
            "-r",
            "--recurse",
            action="store_true",
            help="Recursively scrape linked pages",
        )
        self.parser.add_argument(
            "-l",
            "--level",
            type=int,
            default=5,
            help="Depth of recursion for scraping linked pages",
        )
        self.parser.add_argument(
            "-p", "--path", type=str, help="Directory to save images"
        )

    def _fetch_html_page(self):
        try:
            self.links_visited.add(self.url)
            response = requests.get(
                self.url,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
                    "Connection": "keep-alive",
                },
                timeout=5,
            )
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            pass
            # print("An error occurred during the request: ", e)
            # TODO: Handle different http response code
            return None

    def _parse_url_path(self, urls, images=True):
        verified_urls = []

        for url in urls:
            parsed_url = urlparse(url)
            url = urljoin(self.url, url)
            # TODO: Regarder pourquoi j'ai ce genre de fichier 1024px-The_Photographer_User_in_Humboldt_Peak
            if images and parsed_url.path.endswith(
                (".jpg", ".jpeg", ".png", ".gif", ".bmp")
            ):
                verified_urls.append(url)
            elif not images:
                verified_urls.append(url)

        return verified_urls

    def _parse_html_page(self, response):
        parser = Parser()
        parser.feed(response.text)
        parser.close()

        all_images = parser.images
        all_links = parser.links

        self.all_images = self._parse_url_path(all_images)
        self.all_links = self._parse_url_path(all_links, images=False)

    def create_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def download_images(self):
        for image in self.all_images:
            try:
                image_name = os.path.basename(image)
                if os.path.exists(os.path.join(self.path, image_name)):
                    print(f"Image {image_name} already exists. Skipping download.")
                    continue

                # Telechargement en flux
                response = requests.get(
                    image,
                    stream=True,
                    timeout=5,
                    headers={
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
                        "Connection": "keep-alive",
                    },
                )

                # Jete une exception si le code != 200
                response.raise_for_status()

                image_path = os.path.join(self.path, image_name)

                # self.images_downloaded.add(image)
                print(f"Downloading image: {image_name}")
                with open(image_path, "wb") as img_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            img_file.write(chunk)

                # self.counter += 1

            except requests.RequestException as e:
                print(f"Failed to download image: {image}. Error: {e}")
                # print(f"Failed to download {image}: {e}")
            # print(self)
