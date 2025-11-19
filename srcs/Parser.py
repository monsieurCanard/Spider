from html.parser import HTMLParser
import argparse
from urllib.parse import urlparse, urljoin

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.links = []
        self._init_parser_args()

    def _init_parser_args(self):
      self.arg_parser = argparse.ArgumentParser(
          prog="Arachnida",
          description="A simple web self to extract images and external links from a webpage.",
      )
      self.arg_parser.add_argument("url")

      self.arg_parser.add_argument(
          "-r",
          "--recurse",
          action="store_true",
          help="Recursively scrape linked pages",
      )
      self.arg_parser.add_argument(
          "-l",
          "--level",
          type=int,
          default=5,
          help="Depth of recursion for scraping linked pages",
      )
      self.arg_parser.add_argument(
          "-p", "--path", type=str, help="Directory to save images"
      )

            
    def parse_args(self, scraper):
      args = self.arg_parser.parse_args()

      scraper.url = args.url
      scraper.recurse = args.recurse
      scraper.level = args.level if args.level else 0
      scraper.path = args.path if args.path else "data"

      # Ensure the URL has a scheme
      url_parsed = urlparse(scraper.url)
      if not url_parsed.scheme:
          scraper.url = "https://" + scraper.url

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "img" and "src" in attrs_dict:
            self.images.append(attrs_dict["src"])
        elif tag == "a" and "href" in attrs_dict:
            self.links.append(attrs_dict["href"])
    
    def _parse_url_path(self, scraper, urls, images=True):
      verified_urls = []

      for url in urls:
          parsed_url = urlparse(url)
          url = urljoin(scraper.url, url)
          if images and parsed_url.path.endswith(
              (".jpg", ".jpeg", ".png", ".gif", ".bmp")
          ):
              verified_urls.append(url)
          elif not images:
              verified_urls.append(url)

      return verified_urls