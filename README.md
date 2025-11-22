**Arachnida**

Arachnida est un petit scraper web (en Python) conçu pour parcourir un site web, extraire les images et les télécharger localement. Il supporte la récursivité, un niveau de profondeur configurable, et un logger pour suivre l'activité (fichier `spider.log`).

**Principaux objectifs**
- **Facile** : interface CLI simple pour lancer un crawl d'un site.
- **Récursif** : possibilité de suivre les liens et d'aller en profondeur.
- **Robuste** : téléchargements multi-threadés avec gestion basique des duplicatas et des erreurs.

**Contenu du dépôt**
- **`srcs/`** : code source principal.
	- `prog.py` : point d'entrée principal (boucle, barre de progression, orchestration).
	- `Scraper.py` : logique du scraper (récupération des pages, parsing, stockage des URL).
	- `Parser.py` : extrait images et liens d'une page HTML (utilise `argparse` pour la CLI).
	- `Worker.py` : tâches exécutées par les threads (crawl récursif, téléchargement d'images).
	- `Logger.py` : configuration du logger (fichier `spider.log`).
	- `utils.py` : utilitaires (par ex. calcul de la taille du dossier `data`).
	- `print.py` : fonctions d'affichage pour bannières centrées.
- **`data/`** : dossier où les images seront enregistrées (généré à l'exécution).
- `spider.log` : fichier de log produit par `Logger.get_logger()`.

**Installation (rapide)**
Prerequis : Python 3.8+ recommandé. Installer les dépendances (requests, tqdm).

```bash
python3 -m pip install -r requirements.txt || python3 -m pip install requests tqdm
```

Si vous préférez ne pas utiliser `requirements.txt`, installez manuellement :

```bash
python3 -m pip install requests tqdm
```

**Utilisation**
Lancer le scraper depuis la racine du repository (zsh / terminal) :

```bash
python3 srcs/prog.py <URL> [options]
```

Exemples :

```bash
# Crawl simple (sans récursivité)
python3 srcs/prog.py https://example.com

# Crawl récursif jusqu'à 2 niveaux, enregistrer dans data_custom et logs en INFO
python3 srcs/prog.py https://example.com -r -l 2 -p data_custom --log INFO
```

Notes : l'argument positionnel `url` est requis. Les options sont définies dans `Parser.py` (`-r`, `-l`, `-p`, `--log`).

**Options CLI**
- **`url`** : URL cible (ex : `https://example.com`). Si le schéma est absent, `https://` est préfixé.
- **`-r`, `--recurse`** : activer la récursivité sur les liens trouvés.
- **`-l`, `--level`** : profondeur maximale de récursivité (par défaut 5).
- **`-p`, `--path`** : dossier de destination pour les images (par défaut `data`).
- **`--log`** : niveau de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).

**Logging**
- Le logger écrit dans le fichier `spider.log` (créé au démarrage si nécessaire) et affiche les messages `INFO+` sur la console.
- Si vous ne voyez pas de logs dans `spider.log` :
	- vérifiez que vous exécutez le script depuis le répertoire du projet (cwd), car le `FileHandler` utilise le chemin relatif `spider.log`.
	- utilisez l'option `--log INFO` pour forcer un niveau d'information visible.

Conseil (débogage) : ouvrez `spider.log` pour suivre l'activité détaillée (DEBUG) et surveillez la console pour les messages INFO/ERROR.

**Architecture et flux d'exécution**
- `prog.py` crée un objet `Scraper`.
- `Scraper` lit les arguments via `Parser.parse_args(self)` et configure le logger.
- `prog.py` récupère la page principale (`_fetch_html_page`) et appelle `_parse_html_page` qui alimente `Scraper.all_images` et `Scraper.all_links`.
- Si la récursivité est activée, `Worker.run` est soumis au `ThreadPoolExecutor` pour parcourir les liens.
- Pour les images, `Worker.download_images` télécharge en streaming et stocke les fichiers sous `data/<netloc>/<path>`.

**Warning**
- Ne pas lancer des crawls massifs sans autorisation : respectez le `robots.txt` et la charge serveur.
- Timeout et gestion des erreurs sont basiques : certaines pages lentes ou serveurs stricts peuvent produire des erreurs.
- La logique d'unicité des images se base sur le chemin/dossier final ; si deux images différentes ont le même nom/location relative, elles peuvent être considérées comme duplicatas.


Si vous voulez, je peux :
- ajouter un `requirements.txt` propre,
- corriger le problème du niveau de logger dans `Scraper.py` et proposer un patch,
- fournir des exemples plus détaillés ou des tests unitaires simples.

Faites-moi savoir ce que vous préférez que je fasse ensuite.

# Exemple d'exécution (avec log activé)

```bash
2025-11-22 09:19:32,485 [INFO] Arachnida Spider started.
    ========================================
          Arachnida - Web Scraper
    ========================================
           ____                      ,
          /---.'.__             ____//
               '--.\           /.---'
          _______  \         //
        /.------.\  \|      .'/  ______
       //  ___  \ \ ||/|\  //  _/_----.\__
      |/  /.-.\  \ \:|< >|// _/.'..\   '--'
         //   \'. | \'.|.'/ /_/ /  \
        //     \ \_\/" ' ~\-'.-'    \
       //       '-._| :H: |'-.__     \
      //           (/'==='\)'-._\     ||
      ||                        \\    \|
      ||                         \\    '
      |/                          \\
                                   ||
                                   ||
                                   \
    ========================================
        TARGET URL: https://clubic.com
        RECURSION: True
        DEPTH LEVEL: 1
    ========================================
        LET'S GET ALL THE IMAGES!
    ++++++++++++++++++++++++++++++++++++++++

2025-11-22 09:19:32,486 [INFO] Fetching main page: https://clubic.com
2025-11-22 09:19:32,486 [INFO] Fetching URL: https://clubic.com
2025-11-22 09:19:32,691 [INFO] Found 6 images and 461 links on the page.
2025-11-22 09:19:32,697 [INFO] Directory created or already exists: data
2025-11-22 09:19:32,726 [INFO] Initial size of data directory 'data': 38245474 bytes.
2025-11-22 09:19:32,726 [INFO] Starting crawl with recursion level 1.
2025-11-22 09:19:32,727 [INFO] Fetching URL: https://www.clubic.com/
2025-11-22 09:19:32,739 [INFO] Starting crawl loop with 461 workers.

# --- Progression simulée de la phase "crawl" (tqdm)
# note : tqdm met à jour la même ligne ; ici on montre plusieurs étapes successives
Spider charging caffeine… crawling faster…:  12%|███▏       | 56/461 [00:05<00:36, 11.2it/s]
Spider charging caffeine… crawling faster…:  34%|███████▎   | 157/461 [00:16<00:30, 10.6it/s]
Spider charging caffeine… crawling faster…:  62%|████████████▋ | 286/461 [00:28<00:13, 12.0it/s]
Spider charging caffeine… crawling faster…: 100%|████████████████████| 461/461 [00:42<00:00, 10.9it/s]

2025-11-22 09:19:32,954 [INFO] Found 1 images and 146 links on the page.
2025-11-22 09:19:32,977 [INFO] Found 1 images and 159 links on the page.
2025-11-22 09:19:33,000 [INFO] Found 1 images and 139 links on the page.
... (logs de pages trouvées) ...

# Après crawl : confirmation du nombre d'images
                     Total images to download: 123 images.

# Demande utilisateur (input)
                     Do you want to download the images? (y/n):

# L'utilisateur répond 'y' et commence la phase de téléchargement

                     Starting image download...

2025-11-22 09:20:15,120 [INFO] Starting download of 123 images.

# --- Progression simulée de la phase "download" (tqdm)
Negotiating with TCP like it’s a hostage situation.:   0%|          | 0/123 [00:00<?, ?it/s]
Negotiating with TCP like it’s a hostage situation.:  25%|███▍      | 31/123 [00:04<00:13, 7.00it/s]
Negotiating with TCP like it’s a hostage situation.:  50%|████████▌ | 62/123 [00:10<00:09, 6.75it/s]
Negotiating with TCP like it’s a hostage situation.: 100%|████████████| 123/123 [00:22<00:00, 5.45it/s]

2025-11-22 09:20:37,350 [INFO] Downloading image: https://www.clubic.com/images/sample1.jpg
2025-11-22 09:20:37,435 [INFO] Downloading image: https://www.clubic.com/images/sample2.jpg
2025-11-22 09:20:39,102 [INFO] Duplicate image found, skipping download: data/www.clubic.com/images/sample3.jpg
2025-11-22 09:20:45,600 [ERROR] Error downloading image https://...: ConnectionError('...')

2025-11-22 09:21:00,123 [INFO] Final size of data directory 'data': 38900482 bytes.

    ========================================
          Arachnida - Scraping Complete
    ========================================
    ++ 100 downloaded ( ~ 6.25 MB)
    -----------------------------------      
    -- 20 duplicates
    -----------------------------------      
    -- 3 errors.
    -----------------------------------
    ===================================
      Spider returning to the shadows…
            As all spiders do.
    ===================================
```

