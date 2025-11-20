import threading
from concurrent.futures import ThreadPoolExecutor
import os
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

            with scraper.lock:
                if url in scraper.links_visited:
                    return
                scraper.url = url
                self.all_links = []

            page_content = scraper._fetch_html_page(url)
            if page_content is None:
                return

            scraper._parse_html_page(page_content, self)

            # scraper.download_images()

            if self.depth_level > 0:
                self.depth_level -= 1
                for link in self.all_links:
                    worker = Worker(self.depth_level)

                    with scraper.lock:
                        fut = scraper.executor.submit(worker.run, link, scraper)

                    self.workers.append(fut)

        except Exception as e:
            pass
            # print(f"Error in worker for URL {self.url}: {e}")

        finally:
            for fut in self.workers:
                try:
                    fut.result()
                except Exception as e:
                    print(f"Error in thread for URL {self.url}: {e}")

    def download_images(self, scraper, imageUrl):
        try:
            image_name = os.path.basename(imageUrl.split("?")[0])

            with scraper.lock:
                dest_path = os.path.abspath(os.path.join(scraper.path, image_name))
                if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
                    scraper.duplicates += 1
                    return

            # Telechargement en flux
            response = requests.get(
                imageUrl,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
                    "Connection": "keep-alive",
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
            if os.path.exists(dest_path) and os.path.getsize(dest_path) == 0:
                os.remove(dest_path)
            # print(f"Error downloading image {imageUrl}: {e}")
