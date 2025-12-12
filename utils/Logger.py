import logging
from logging.handlers import RotatingFileHandler

from utils.utils import create_directory
def get_logger():
	logger = logging.getLogger()
	create_directory(logger, "logs")


	if not logger.handlers:
		# Format commun
		formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
		
		# File handler
		fh = RotatingFileHandler("logs/spider.log", maxBytes=5*1024*1024, backupCount=3)
		fh.setFormatter(formatter)
		fh.setLevel(logging.DEBUG)  # fichier enregistre tout

		# Stream handler
		sh = logging.StreamHandler()
		sh.setFormatter(formatter)
		sh.setLevel(logging.INFO)   # console affiche info+

		logger.addHandler(fh)
		logger.addHandler(sh)
	return logger