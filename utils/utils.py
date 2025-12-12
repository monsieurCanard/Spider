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

def create_directory(logger, path):
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Directory created or already exists: {path}")
    else:
        logger.info(f"Skip directory creation, directory at {path} already exists.")