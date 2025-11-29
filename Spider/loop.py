import random
import tqdm
from concurrent.futures import as_completed


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
