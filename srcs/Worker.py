import threading
from concurrent.futures import ThreadPoolExecutor

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
                    print(f"URL already visited: {url}")
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
