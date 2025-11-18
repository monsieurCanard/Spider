import threading
from concurrent.futures import ThreadPoolExecutor


class Worker:
    lock = threading.Lock()

    def __init__(self, scraper, url, depth_level):
        super().__init__()
        self.scraper = scraper
        self.url = url
        self.depth_level = depth_level
        self.threads = []
        self.executor = ThreadPoolExecutor(max_workers=1)

    def run(self):
        try:
            if self.depth_level < 0:
                return

            with Worker.lock:
                if self.url in self.scraper.links_visited:
                    return
                self.scraper.links_visited.add(self.url)
                self.scraper.url = self.url

            page_content = self.scraper._fetch_html_page()

            if page_content is None:
                return

            self.scraper._parse_html_page(page_content)
            self.scraper.create_directory(self.scraper.path)

            print(f"{len(self.scraper.all_images)} images to download.")
            self.scraper.download_images()

            if self.scraper.recurse and self.depth_level > 0:
                self.depth_level -= 1
                for link in self.scraper.all_links:
                    worker = Worker(self.scraper, link, self.depth_level)
                    fut = self.executor.submit(worker.run)
                    self.threads.append(fut)

        except Exception as e:
            print(f"Error in worker for URL {self.url}: {e}")

        finally:
            for fut in self.threads:
                try:
                    fut.result()
                except Exception as e:
                    print(f"Error in thread for URL {self.url}: {e}")
