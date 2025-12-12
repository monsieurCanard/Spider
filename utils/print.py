import shutil


def print_centered(text):
    width = shutil.get_terminal_size((80, 20)).columns
    for line in text.splitlines():
        print(line.center(width))


def print_launch_banner(scraper):
    banner = r"""\
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
        Press Ctrl+C to stop (please wait)
        LET'S GET ALL THE IMAGES!
    ++++++++++++++++++++++++++++++++++++++++
        """
    banner = banner.format(
        url=scraper.url, recurse=scraper.recurse, level=scraper.level
    )
    print_centered(banner)


def print_completion_banner(scraper, total_size_downloaded):
    banner = f"""\
    ===================================
       Arachnida - Scraping Complete   
    ===================================
    ++ {scraper.download} downloaded ( ~ {total_size_downloaded / (1024**2):.2f} MB)
    -----------------------------------
    -- {scraper.duplicates} duplicates
    -----------------------------------
    -- {scraper.error} errors.
    ===================================
      Spider returning to the shadows…
            As all spiders do.
    ===================================
    """
    print_centered(banner)
