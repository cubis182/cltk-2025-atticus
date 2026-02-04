import sys

sys.path.append("C:/Users/T470s/Documents/GitHub/cltk-2025-atticus")
from pathlib import Path
import re

from postag_perseusDL import get_paths

paths: list[Path] = get_paths()

for p in paths:
    with open(p, "r+", encoding="utf-8") as f:
        orig = f.read()
        text = orig
        f.seek(0)
        text = text.replace("É", "E")
        text = text.replace("Á", "A")
        text = text.replace("Í", "I")
        text = text.replace("Ó", "O")
        text = text.replace("Ú", "U")
        text = text.replace("Ý", "Y")
        text = text.replace("á", "a")
        text = text.replace("é", "e")
        text = text.replace("í", "i")
        text = text.replace("ó", "o")
        text = text.replace("ú", "u")
        text = text.replace("ý", "y")
        f.write(text)
        f.truncate()
        if text != orig:
            print(f"Made a change to {p.as_uri()}!")
