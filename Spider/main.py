from Scraper import Scraper
from utils.utils import get_dir_size
from Worker import Worker
from utils.print import print_centered, print_completion_banner, print_launch_banner
from utils.utils import create_directory
from loop import loop
import sys



def main():
    scraper = Scraper()
    scraper.logger.info("Arachnida Spider started.")
    print_launch_banner(scraper)

    scraper.logger.info(f"Fetching main page: {scraper.url}")
    page_content = scraper._fetch_html_page(scraper.url, main=True)
    if page_content is None:
        return

    scraper._parse_html_page(page_content)
    create_directory(scraper.logger, scraper.path)

    previous_size_data = get_dir_size(scraper.path, scraper)
    scraper.logger.info(
        f"Initial size of data directory '{scraper.path}': {previous_size_data} bytes."
    )

    if scraper.recurse and scraper.level > 0:
        scraper.logger.info(f"Starting crawl with recursion level {scraper.level}.")
        for link in scraper.all_links:
            worker = Worker(scraper.level)
            fut = scraper.executor.submit(worker._run, link, scraper)
            scraper.threads.append(fut)
    try:
        loop(scraper, scraper.threads, "crawl")
    except KeyboardInterrupt:
        scraper.logger.info("Crawl interrupted by user.")
        scraper.executor.shutdown(wait=False, cancel_futures=True)
        sys.exit(0)

    print_centered(f"Total images to download: {len(scraper.all_images)} images.")
    print_centered("Do you want to download the images? (y/n): ")

    choice = input().strip().lower()
    if choice == "n":
        return
    print_centered("\nStarting image download...\n")

    download_fut = []
    for imageUrl in scraper.all_images:
        fut = scraper.executor.submit(worker._download_images, scraper, imageUrl)
        download_fut.append(fut)

    scraper.logger.info(f"Starting download of {len(download_fut)} images.")

    try:
        loop(scraper, download_fut, "download")
    except KeyboardInterrupt:
        scraper.logger.info("Download interrupted by user.")
        scraper.executor.shutdown(wait=False, cancel_futures=True)
        sys.exit(0)

    total_download_Size = get_dir_size(scraper.path, scraper)
    scraper.logger.info(
        f"Final size of data directory '{scraper.path}': {total_download_Size} bytes."
    )
    print_completion_banner(scraper, total_download_Size - previous_size_data)

    scraper.executor.shutdown(wait=True)


if __name__ == "__main__":
    main()
