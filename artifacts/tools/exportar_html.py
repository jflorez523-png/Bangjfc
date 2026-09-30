#!/usr/bin/env python3
"""Exporta la página como un solo archivo HTML con las imágenes incrustadas, para descargar y compartir."""
import base64
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / 'obra-blanca-901.html'
OUT = BASE / 'descarga' / 'obra-blanca-apto-901.html'

page = SRC.read_text(encoding='utf-8')


def inline(match):
    path = BASE / match.group(1)
    data = base64.b64encode(path.read_bytes()).decode('ascii')
    return f'src="data:image/jpeg;base64,{data}"'


page = re.sub(r'src="(img/[^"]+\.jpg)"', inline, page)
title = re.search(r'<title>.*?</title>', page, re.S).group(0)
page = page.replace(title, '', 1)

doc = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{title}
<style>:root{{color-scheme:light}}body{{margin:0;font:14px system-ui,sans-serif}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
</head>
<body>
{page}
</body>
</html>
'''
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(doc, encoding='utf-8')
left = re.findall(r'src="img/', doc)
print(OUT, f'{OUT.stat().st_size / 1024 / 1024:.2f} MB', 'imágenes sin incrustar:', len(left))
