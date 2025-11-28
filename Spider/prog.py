import random
import tqdm
from Scraper import Scraper
import requests
from concurrent.futures import as_completed
from utils import get_dir_size
from Worker import Worker
from print import print_centered, print_completion_banner, print_launch_banner


def loop(scraper, list_workers, type):
    scraper.logger.info(f"Starting {type} loop with {len(list_workers)} workers.")
    progress_bar_desc = (
        (type == "download")
        and [
            "Negotiating with TCP like it’s a hostage situation.",
            "TLS handshake took it personally.",
            "HTTP/1.1 keep-alive because who closes connections anyway?",
        ]
        or [
            "Spider charging caffeine… crawling faster…",
            "Eight legs, zero mercy… scraping everything…",
            "Spider learning parkour on hyperlinks…",
            "Spider opening forbidden doors…",
        ]
    )

    progress_bar_color = (type == "download") and "green" or "blue"
    unit = (type == "download") and "images" or "links"
    while True:
        with scraper.lock:
            pending = [f for f in list_workers if not f.done()]
        if not pending:
            break
        for fut in tqdm.tqdm(
            as_completed(pending),
            total=len(pending),
            desc=random.choice(progress_bar_desc),
            colour=progress_bar_color,
            unit=unit,
            ncols=100,
            leave=False,
        ):
            try:
                fut.result()
            except Exception as e:
                scraper.logger.error(f"Worker error while {type} link: {e}")


def main():
    scraper = Scraper()
    scraper.logger.info("Arachnida Spider started.")
    print_launch_banner(scraper)

    scraper.logger.info(f"Fetching main page: {scraper.url}")
    page_content = scraper._fetch_html_page(scraper.url, main=True)
    if page_content is None:
        return

    scraper._parse_html_page(page_content)
    scraper.create_directory(scraper.path)

    previous_size_data = get_dir_size(scraper.path, scraper)
    scraper.logger.info(
        f"Initial size of data directory '{scraper.path}': {previous_size_data} bytes."
    )

    if scraper.recurse and scraper.level > 0:
        scraper.logger.info(f"Starting crawl with recursion level {scraper.level}.")
        for link in scraper.all_links:
            worker = Worker(scraper.level)
            fut = scraper.executor.submit(worker.run, link, scraper)
            scraper.threads.append(fut)

        loop(scraper, scraper.threads, "crawl")

    print_centered(f"Total images to download: {len(scraper.all_images)} images.")
    print_centered("Do you want to download the images? (y/n): ")

    choice = input().strip().lower()
    if choice == "n":
        return
    print_centered("\nStarting image download...\n")

    download_fut = []
    for imageUrl in scraper.all_images:
        fut = scraper.executor.submit(worker.download_images, scraper, imageUrl)
        download_fut.append(fut)

    scraper.logger.info(f"Starting download of {len(download_fut)} images.")
    loop(scraper, download_fut, "download")

    total_download_Size = get_dir_size(scraper.path, scraper)
    scraper.logger.info(
        f"Final size of data directory '{scraper.path}': {total_download_Size} bytes."
    )
    print_completion_banner(scraper, total_download_Size - previous_size_data)


if __name__ == "__main__":
    main()
