import logging

def get_logger():
	logger = logging.getLogger()

	if not logger.handlers:
		# Format commun
		formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
		
		# File handler
		fh = logging.FileHandler("spider.log")
		fh.setFormatter(formatter)
		fh.setLevel(logging.DEBUG)  # fichier enregistre tout

		# Stream handler
		sh = logging.StreamHandler()
		sh.setFormatter(formatter)
		sh.setLevel(logging.INFO)   # console affiche info+

		logger.addHandler(fh)
		logger.addHandler(sh)
	return logger