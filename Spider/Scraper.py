import requests
import threading
from urllib.parse import urljoin
from Parser import Parser
from concurrent.futures import ThreadPoolExecutor

from Logger import get_logger


class Scraper:
    def __init__(self):
        self.lock = threading.Lock()

        self.url = ""
        self.parser = Parser()
        self.threads = []

        self.recurse = False
        self.level = 5
        self.log_level = None
        self.path = "data"

        self.total = 0
        self.duplicates = 0
        self.download = 0
        self.total_download_size = 0
        self.error = 0

        self.all_links = []
        self.all_images = set()

        self.links_visited = set()
        self.all_image_names = set()

        self.executor = ThreadPoolExecutor()
        self.parser._parse_args(self)
        self.logger = get_logger()
        if self.log_level is None:
            self.logger.setLevel(100)
        else:
            self.logger.setLevel(self.log_level)

    def __str__(self):
        images = "\n".join(str(img) for img in self.all_images)
        links = "\n".join(str(link) for link in self.all_links)
        return f"Images:\n{images}\n\nLinks:\n{links}"

    def _fetch_html_page(self, url, main=False):
        self.logger.info(f"Fetching URL: {url}")
        try:
            with self.lock:
                if url in self.links_visited:
                    self.logger.info(f"URL already visited: {url}")
                    return None
                self.links_visited.add(url)

            # self.links_visited.add(url)
            response = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
                    "Connection": "keep-alive",
                },
                timeout=5,
            )

            response.raise_for_status()

            if "text/html" not in response.headers.get("Content-Type"):
                self.logger.info(f"URL is not an HTML page: {url}")
                return None

            return response

        except requests.RequestException as e:
            self.logger.error(f"Error fetching URL {url}: {e}")
            return None

    def _parse_html_page(self, response, worker=None):
        parser = Parser()
        parser.feed(response.text)
        parser.close()

        all_images = parser.images
        all_links = parser.links
        self.logger.info(f"Found {len(all_images)} images and {len(all_links)} links on the page.")
        with self.lock:
            for img in all_images:
                url_dest = urljoin(self.url, img)
                if url_dest not in self.all_images:
                    self.all_images.add(url_dest)

            new_links = []
            for link in all_links:
                full_url = urljoin(response.url, link)
                if full_url not in self.links_visited:
                    new_links.append(full_url)

            if worker is None:
                self.all_links = self.parser._parse_url_path(
                    self,
                    new_links,
                    images=False,
                )
            else:
                worker.all_links = self.parser._parse_url_path(
                    self, new_links, images=False
                )

