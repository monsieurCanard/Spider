from Arachnida import Arachnida
import requests
from Worker import Worker

def main():
    scraper = Arachnida()

    print(f"Scraping URL: {scraper.url}")

    try:
        page_content = scraper._fetch_html_page(scraper.url)
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return

    if page_content is None:
        return

    scraper._parse_html_page(page_content)
    scraper.create_directory(scraper.path)
    # scraper.download_images()
    print(f"Found {len(scraper.all_images)} images.")


    if scraper.recurse and scraper.level > 0:
        print(f"Recursing into links, level: {scraper.level}")
        scraper.level -= 1
        for link in scraper.all_links:
            worker = Worker(scraper.level)
            fut = scraper.executor.submit(worker.run, link, scraper)
            scraper.threads.append(fut)

    for thread in scraper.threads:
        thread.result()

    print(f"Downloaded {len(scraper.all_images)} images.")
    print(f"Total images found: {scraper.total}")


if __name__ == "__main__":
    main()
