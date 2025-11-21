import tqdm
from Arachnida import Arachnida
import requests
from concurrent.futures import as_completed
from Worker import Worker
import os


def get_dir_size(path=".", scraper=None):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path, scraper)
    return total


def print_launch_banner(scraper):
    banner = """\
    ========================================
          Arachnida - Web Scraper
    ========================================
           ____                      ,
          /---.'.__             ____//
               '--.\           /.---'
          _______  \\         //
        /.------.\  \|      .'/  ______
       //  ___  \ \ ||/|\  //  _/_----.\__
      |/  /.-.\  \ \:|< >|// _/.'..\   '--'
         //   \'. | \'.|.'/ /_/ /  \\
        //     \ \_\/" ' ~\-'.-'    \\
       //       '-._| :H: |'-.__     \\
      //           (/'==='\)'-._\     ||
      ||                        \\    \|
      ||                         \\    '
      |/                          \\
                                   ||
                                   ||
                                   \\
    ========================================
        TARGET URL: {url}
        RECURSION: {recurse}
        DEPTH LEVEL: {level}
    ========================================
        LET'S GET ALL THE IMAGES!
    ++++++++++++++++++++++++++++++++++++++++
        """
    print(
        banner.format(
            url=scraper.url,
            recurse=scraper.recurse,
            level=scraper.level,
        )
    )


def main():
    scraper = Arachnida()

    print_launch_banner(scraper)

    page_content = scraper._fetch_html_page(scraper.url, main=True)
    if page_content is None:
        return

    scraper._parse_html_page(page_content)
    scraper.create_directory(scraper.path)

    previous_size_data = get_dir_size(scraper.path, scraper)

    if scraper.recurse and scraper.level > 0:
        for link in scraper.all_links:
            worker = Worker(scraper.level)
            fut = scraper.executor.submit(worker.run, link, scraper)
            scraper.threads.append(fut)

        while True:
            with scraper.lock:
                pending = [f for f in scraper.threads if not f.done()]
            if not pending:
                break
            for fut in tqdm.tqdm(
                as_completed(pending),
                total=len(pending),
                desc="Scrapping links",
            ):
                try:
                    fut.result()
                except Exception as e:
                    print(f"Worker error while scrapping link: {e}")

    print(f"Total images to download: {len(scraper.all_images)} images.")
    print("Do you want to download the images? (y/n): ", end="")

    choice = input().strip().lower()
    if choice == "y":
        print("\nStarting image download...\n")

        download_fut = []
        for image in scraper.all_images:
            worker = Worker(scraper.level)
            fut = scraper.executor.submit(worker.download_images, scraper, image)
            download_fut.append(fut)

        for fut in tqdm.tqdm(
            as_completed(download_fut),
            total=len(download_fut),
            desc="Downloading images",
        ):
            try:
                fut.result()
            except Exception as e:
                print(f"Worker error while downloading image: {e}")
        total_download_Size = get_dir_size(scraper.path, scraper)

        print(f"Scrapper path: {scraper.path}\n")
        print(f"""
-----------------------------------
    Download complete
-----------------------------------
++ {scraper.download} downloaded ( ~ {(total_download_Size - previous_size_data) / (1024**2):.2f} MB)
-----------------------------------      
-- {scraper.duplicates} duplicates
-----------------------------------      
-- {scraper.error} errors.
-----------------------------------
        """)


if __name__ == "__main__":
    main()
