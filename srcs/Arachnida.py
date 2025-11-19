import os
import requests
import threading
from urllib.parse import urljoin, urlparse
from Parser import Parser
from concurrent.futures import ThreadPoolExecutor


class Arachnida:
    def __init__(self):
        self.lock = threading.Lock()
        
        self.url = ""
        self.parser = Parser()
        self.threads = []
        
        
        self.recurse = False
        self.level = 5
        
        self.total = 0
        self.duplicates = 0
        
        self.all_links = []
        self.all_images = []

        self.links_visited = set()

        self.executor = ThreadPoolExecutor(max_workers=50)
        self.parser.parse_args(self)

    def __str__(self):
        images = "\n".join(str(img) for img in self.all_images)
        links = "\n".join(str(link) for link in self.all_links)
        return f"Images:\n{images}\n\nLinks:\n{links}"

    def _fetch_html_page(self, url):
        try:
            with self.lock:
                self.links_visited.add(url)
                response = requests.get(
                    url,
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
            print("An error occurred during the request: ", e)
            # TODO: Handle different http response code
            return None

   
    def _parse_html_page(self, response, worker=None):
            parser = Parser()
            parser.feed(response.text)
            parser.close()

            all_images = parser.images
            self.total += len(all_images)
            all_links = parser.links

            with self.lock:
                self.all_images.add(self.parser._parse_url_path(self, all_images, images=True))

                if worker is None:
                    self.all_links = self.parser._parse_url_path(self, all_links, images=False)
                else:
                    worker.all_links = self.parser._parse_url_path(self, all_links, images=False)

    def create_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    # def download_images(self):
    #     for image in self.all_images:
    #         try:
    #             image_name = os.path.basename(image)
    #             if os.path.exists(os.path.join(self.path, image_name)):
    #                 print(f"Image {image_name} already exists. Skipping download.")
    #                 continue

    #             # Telechargement en flux
    #             response = requests.get(
    #                 image,
    #                 stream=True,
    #                 timeout=5,
    #                 headers={
    #                     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
    #                     "Connection": "keep-alive",
    #                 },
    #             )

    #             # Jete une exception si le code != 200
    #             response.raise_for_status()

    #             image_path = os.path.join(self.path, image_name)

    #             # self.images_downloaded.add(image)
    #             print(f"Downloading image: {image_name}")
    #             with open(image_path, "wb") as img_file:
    #                 for chunk in response.iter_content(chunk_size=8192):
    #                     if chunk:
    #                         img_file.write(chunk)

    #             # self.counter += 1

    #         except requests.RequestException as e:
    #             print(f"Failed to download image: {image}. Error: {e}")
    #             # print(f"Failed to download {image}: {e}")
    #         # print(self)
