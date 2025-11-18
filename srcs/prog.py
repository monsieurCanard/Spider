import os
from Arachnida import Arachnida
import requests


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def download_images(scraper):
    for image in scraper.all_images:
        if image in scraper.images_downloaded:
            continue
        try:
            # Telechargement en flux
            response = requests.get(image, stream=True)

            # Jete une exception si le code != 200
            response.raise_for_status()

            image_name = os.path.basename(image)
            image_path = os.path.join(scraper.path, image_name)
            scraper.images_downloaded.add(image)
            with open(image_path, "wb") as img_file:
                # Ecriture par morceaux
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        img_file.write(chunk)

        except requests.RequestException as e:
            print(f"Failed to download {image}: {e}")


def loop(scraper, url, depth_level):
    if depth_level < 0:
        return
    if url in scraper.links_visited:
        return

    scraper.links_visited.add(url)
    scraper.url = url
    print(f"Recursing into: {url} | Depth level: {depth_level}")
    page_content = scraper._fetch_html_page()

    if page_content is None:
        return

    scraper._parse_html_page(page_content)
    create_directory(scraper.path)
    download_images(scraper)

    if scraper.recurse and depth_level > 0:
        depth_level -= 1
        for link in scraper.all_links:
            loop(scraper, link, depth_level - 1)


def main():
    scraper = Arachnida()

    scraper._parse_args()
    try:
        page_content = scraper._fetch_html_page()
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return

    if page_content is None:
        return

    scraper._parse_html_page(page_content)
    create_directory(scraper.path)
    download_images(scraper)

    if scraper.recurse and scraper.level > 0:
        print("Recursing into linked pages...")
        scraper.level -= 1
        for link in scraper.all_links:
            loop(scraper, link, scraper.level)


if __name__ == "__main__":
    main()
