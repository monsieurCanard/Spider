import argparse
import re
import requests
from urllib.parse import urljoin, urlparse


class Arachnida:
    regex_image = re.compile(
        r'<img[^>]+src=["\'](.*?)["\'][^>]*/?>', re.IGNORECASE | re.MULTILINE
    )

    regex_external_link = re.compile(
        r'<a[^>]+href=["\'](http[s]?://[^"\']+)["\'][^>]*/?>',
        re.IGNORECASE | re.MULTILINE,
    )

    def __init__(self):
        self.url = ""
        self.recurse = False
        self.level = 5

        self.all_links = []
        self.all_images = []
        self.images_downloaded = set()
        self.links_visited = set()
        self._init_parser_args()

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
            description="A simple web scraper to extract images and external links from a webpage.",
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
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                },
            )
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            print("An error occurred during the request: ", e)
            # TODO: Handle different http response code
            return None

    def _parse_url_path(self, urls, images=True):
        verified_urls = []
        for url in urls:
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = urljoin(self.url, url)

            if images and parsed_url.path.endswith(
                (".jpg", ".jpeg", ".png", ".gif", ".bmp")
            ):
                verified_urls.append(url)
            elif not images:
                verified_urls.append(url)

        return verified_urls

    def _parse_html_page(self, response):
        all_images = self.regex_image.findall(response.text)
        all_links = self.regex_external_link.findall(response.text)

        self.all_images = self._parse_url_path(all_images)
        self.all_links = self._parse_url_path(all_links, images=False)

        print(self)
