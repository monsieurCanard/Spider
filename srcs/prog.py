from Arachnida import Arachnida
import requests
from Worker import Worker


def main():
    scraper = Arachnida()

    scraper._parse_args()
    try:
        print(f"Scraping URL: {scraper.url}")
        page_content = scraper._fetch_html_page()
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return

    if page_content is None:
        return

    scraper._parse_html_page(page_content)
    scraper.create_directory(scraper.path)
    scraper.download_images()

    if scraper.recurse and scraper.level > 0:
        scraper.level -= 1
        for link in scraper.all_links:
            worker = Worker(scraper, link, scraper.level)
            fut = scraper.executor.submit(worker.run)
            scraper.threads.append(fut)

    for thread in scraper.threads:
        thread.result()

    print(f"Downloaded {scraper.counter} images.")


if __name__ == "__main__":
    main()
