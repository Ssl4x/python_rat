pyinstaller --onefile -w -i explorer.ico client.py --exclude-module=_bz2 --exclude-module=_hashlib --exclude-module=_lzma --exclude-module=_ssl --exclude-module=PyQt5 --exclude-module=cv2 --exclude-module=sqlite3 --exclude-module=xml --exclude-module=beautifulsoup4 