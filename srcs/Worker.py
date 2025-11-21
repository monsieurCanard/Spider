import threading
from concurrent.futures import ThreadPoolExecutor
import os
from urllib.parse import urlparse
import requests


class Worker:
    lock = threading.Lock()

    def __init__(self, depth_level):
        super().__init__()
        self.depth_level = depth_level
        self.workers = []
        self.all_links = []

    def run(self, url, scraper):
        try:
            if self.depth_level < 0:
                return

            self.all_links = []

            page_content = scraper._fetch_html_page(url)
            if page_content is None:
                return

            scraper._parse_html_page(page_content, self)

            self.depth_level -= 1
            for link in self.all_links:
                worker = Worker(self.depth_level)
                fut = scraper.executor.submit(worker.run, link, scraper)
                with scraper.lock:
                    scraper.threads.append(fut)
        except Exception as e:
            pass

    def download_images(self, scraper, imageUrl):
        try:
            with scraper.lock:
                url = (
                    scraper.path
                    + "/"
                    + urlparse(imageUrl).netloc
                    + "/"
                    + urlparse(imageUrl).path
                )
                os.makedirs(os.path.dirname(url), exist_ok=True)
                dest_path = os.path.abspath(url)
                if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
                    scraper.duplicates += 1
                    return

            response = requests.get(
                imageUrl,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
                    "Connection": "keep-alive",
                    "accept": "image/jpeg, image/png, image/gif, image/bmp, image/jpg, image/apng",
                },
                stream=True,
                timeout=5,
            )
            response.raise_for_status()

            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            with scraper.lock:
                if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
                    scraper.total_download_size += os.path.getsize(dest_path)
                    scraper.download += 1

        except Exception as e:
            with scraper.lock:
                scraper.error += 1

            # print(f"Error downloading image {imageUrl}: {e}")
