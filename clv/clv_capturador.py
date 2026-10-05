#!/usr/bin/env python3
"""Capturador de cuotas de cierre para medir CLV en Betano, BetPlay y Betsson.

Lee tus picks (link + mercado + seleccion + cuota tomada), vigila cada partido
durante el dia y guarda la ultima cuota antes del inicio como cuota de cierre.

Uso:
  python clv_capturador.py validar                 revisa todos los picks ahora mismo
  python clv_capturador.py vigilar                 corre todo el dia capturando cierres
  python clv_capturador.py diagnosticar "<link>"   prueba un link y guarda lo que recibe
  python clv_capturador.py exportar                reescribe el CSV de salida

Opciones (todas opcionales):
  --picks RUTA_O_URL   archivo CSV de picks, o URL de un Google Sheet publicado como CSV
  --salida RUTA        CSV de CLV de cierre (por defecto clv_cierre.csv junto al script)
"""

import argparse
import csv
import difflib
import hashlib
import io
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

DIR = Path(__file__).resolve().parent
PICKS_DEFAULT = DIR / "picks.csv"
SALIDA_DEFAULT = DIR / "clv_cierre.csv"
ESTADO = DIR / "estado.json"
LOG_CAPTURAS = DIR / "capturas.csv"
DIAGNOSTICO = DIR / "diagnostico"

# Formato del CSV de salida. Para Excel en espanol usa SEPARADOR = ";" y DECIMAL = ",".
SEPARADOR = ","
DECIMAL = "."

# Una cuota de cierre tomada mas de esto antes del inicio se marca como "cierre_viejo".
MAX_MIN_CIERRE = 30

# BetPlay corre sobre Kambi. Si la deteccion automatica falla, ajusta estos valores
# con lo que muestre `diagnosticar`.
KAMBI_HOSTS = [
    "https://na-offering-api.kambicdn.net",
    "https://us1-offering-api.kambicdn.com",
    "https://eu-offering-api.kambicdn.com",
    "https://eu1.offering-api.kambicdn.com",
]
KAMBI_OFFERINGS = ["betplay", "betplayco"]

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")

LOCAL_TZ = datetime.now().astimezone().tzinfo


class CaptureError(Exception):
    pass


# --------------------------------------------------------------------------- HTTP

def http_get(url, referer=None):
    """Devuelve (codigo, texto). codigo 0 = error de red."""
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
        "Accept-Language": "es-CO,es;q=0.9,en;q=0.6",
    }
    if referer:
        headers["Referer"] = referer
    try:
        from curl_cffi import requests as creq  # opcional: imita un Chrome real
        try:
            r = creq.get(url, headers=headers, impersonate="chrome", timeout=25)
            return r.status_code, r.text
        except Exception as e:
            return 0, str(e)
    except ImportError:
        pass
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)


def a_json(texto):
    try:
        return json.loads(texto)
    except ValueError:
        return None


def json_embebido(html):
    """Objetos JSON que la pagina trae incrustados en el HTML."""
    patrones = [
        r'window\[["\']initial_state["\']\]\s*=\s*',
        r'window\.__INITIAL_STATE__\s*=\s*',
        r'window\.__PRELOADED_STATE__\s*=\s*',
        r'<script[^>]*id="__NEXT_DATA__"[^>]*>',
        r'<script[^>]*type="application/json"[^>]*>',
    ]
    dec = json.JSONDecoder()
    objs = []
    for pat in patrones:
        for m in re.finditer(pat, html):
            i = m.end()
            while i < len(html) and html[i].isspace():
                i += 1
            try:
                obj, _ = dec.raw_decode(html, i)
                objs.append(obj)
            except ValueError:
                pass
    return objs


# ------------------------------------------------------------------ utilidades

def fmt_num(x):
    return f"{x:g}"


def parse_time(v):
    """Fecha desde ISO o epoch (s/ms). Solo acepta fechas cercanas a hoy."""
    dt = None
    if isinstance(v, bool):
        return None
    if isinstance(v, str) and v.strip().isdigit():
        v = int(v.strip())
    if isinstance(v, (int, float)):
        if v > 1e12:
            v = v / 1000
        if v > 1e9:
            dt = datetime.fromtimestamp(v, tz=timezone.utc)
    elif isinstance(v, str) and re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", v):
        try:
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            dt = None
    if dt is None:
        return None
    ahora = datetime.now(timezone.utc)
    if ahora - timedelta(days=2) <= dt <= ahora + timedelta(days=15):
        return dt
    return None


def parse_inicio_usuario(texto):
    """'2026-10-05 19:30' o '19:30' (hoy), hora local."""
    texto = (texto or "").strip()
    if not texto:
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%H:%M"):
        try:
            dt = datetime.strptime(texto, fmt)
        except ValueError:
            continue
        if fmt == "%H:%M":
            hoy = datetime.now(LOCAL_TZ)
            dt = dt.replace(year=hoy.year, month=hoy.month, day=hoy.day)
        return dt.replace(tzinfo=LOCAL_TZ).astimezone(timezone.utc)
    return None


def a_float(v):
    if v is None:
        return None
    try:
        return float(str(v).strip().replace(",", "."))
    except ValueError:
        return None


# ------------------------------------------------------- extraccion de mercados

NAME_KEYS = ("name", "label", "title", "selectionName", "outcomeName", "fullName",
             "shortName", "marketName", "displayName")
PRICE_KEYS = ("price", "odds", "odd", "decimalOdds", "oddsDecimal", "decimal",
              "coefficient", "cuota", "value")
SEL_LIST_KEYS = ("selections", "outcomes", "odds", "runners", "selectionList",
                 "options", "bets")
LINE_KEYS = ("handicap", "line", "points", "hcp", "specialValue", "spread")
START_KEYS = ("start", "startTime", "startDate", "startDateTime", "eventStartTime",
              "kickoff", "kickOffTime", "startsAt", "eventDate")
TYPE_ALIASES = {"OT_ONE": ["1"], "OT_CROSS": ["x"], "OT_TWO": ["2"],
                "OT_OVER": ["mas"], "OT_UNDER": ["menos"],
                "OT_YES": ["si"], "OT_NO": ["no"]}


def primer_texto(d, claves):
    for k in claves:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def precio(d):
    for k in PRICE_KEYS:
        v = d.get(k)
        if isinstance(v, dict):
            for k2 in ("decimal", "value", "price"):
                if isinstance(v.get(k2), (int, float, str)):
                    v = v[k2]
                    break
            else:
                continue
        if isinstance(v, str):
            v = a_float(v)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        if isinstance(v, int) and v >= 1000:  # Kambi: cuotas en milesimas
            v = v / 1000
        if 1.0 < v < 1000:
            return float(v)
    return None


def linea(d):
    for k in LINE_KEYS:
        v = d.get(k)
        if isinstance(v, str):
            v = a_float(v)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        if isinstance(v, int) and abs(v) >= 1000:  # Kambi: lineas en milesimas
            v = v / 1000
        return float(v)
    return None


def con_linea(texto, ln):
    if ln is None or not texto:
        return texto
    n = fmt_num(ln)
    return texto if n in texto else f"{texto} {n}"


def como_seleccion(d):
    nombre = primer_texto(d, NAME_KEYS)
    p = precio(d)
    if not nombre or p is None:
        return None
    ln = linea(d)
    aliases = [con_linea(d[k], ln) for k in NAME_KEYS + ("participant",)
               if isinstance(d.get(k), str) and d[k].strip()]
    aliases += [con_linea(a, ln) for a in TYPE_ALIASES.get(d.get("type"), [])]
    if ln is None:
        m = re.search(r"[-+]?\d+\.\d+", nombre)
        ln = float(m.group()) if m else None
    estado = d.get("status") or ("SUSPENDED" if d.get("suspended") else "")
    return {"name": con_linea(nombre, ln), "aliases": aliases, "price": p,
            "line": ln, "status": str(estado)}


def como_mercado(d):
    nombre = primer_texto(d, NAME_KEYS)
    if not nombre:
        crit = d.get("criterion")
        if isinstance(crit, dict):
            nombre = primer_texto(crit, ("label", "englishLabel"))
    if not nombre:
        return None
    for k in SEL_LIST_KEYS:
        lst = d.get(k)
        if isinstance(lst, list) and lst and all(isinstance(x, dict) for x in lst):
            sels = [s for s in (como_seleccion(x) for x in lst) if s]
            if sels and len(sels) * 2 >= len(lst):
                aliases = [nombre]
                for extra in ("criterion", "betOfferType"):
                    if isinstance(d.get(extra), dict):
                        aliases += [v for v in (d[extra].get("label"), d[extra].get("name"),
                                                d[extra].get("englishLabel"),
                                                d[extra].get("englishName")) if v]
                return {"name": nombre, "aliases": aliases, "selections": sels}
    return None


def enlazar(mercados, selecciones):
    """Estructura plana: markets[] y selections[] unidas por marketId."""
    por_id = {}
    for m in mercados:
        if isinstance(m, dict) and m.get("id") is not None:
            nombre = primer_texto(m, NAME_KEYS)
            if nombre:
                por_id[m["id"]] = {"name": nombre, "aliases": [nombre], "selections": []}
    for s in selecciones:
        if not isinstance(s, dict):
            continue
        mid = s.get("marketId", s.get("market_id"))
        sel = como_seleccion(s)
        if sel and mid in por_id:
            por_id[mid]["selections"].append(sel)
    return [m for m in por_id.values() if m["selections"]]


def extraer_generico(obj):
    """Busca mercados, nombre y hora del evento en cualquier JSON (recorrido en anchura)."""
    mercados, inicio, nombre_ev = [], None, None
    cola = [obj]
    vistos = 0
    while cola and vistos < 200000:
        o = cola.pop(0)
        vistos += 1
        if isinstance(o, dict):
            m = como_mercado(o)
            if m:
                mercados.append(m)
            if isinstance(o.get("markets"), list) and isinstance(o.get("selections"), list):
                mercados.extend(enlazar(o["markets"], o["selections"]))
            if inicio is None:
                for k in START_KEYS:
                    t = parse_time(o.get(k))
                    if t:
                        inicio = t
                        nombre_ev = primer_texto(o, ("name", "eventName", "title"))
                        break
            cola.extend(v for v in o.values() if isinstance(v, (dict, list)))
        elif isinstance(o, list):
            cola.extend(v for v in o if isinstance(v, (dict, list)))
    unicos, claves = [], set()
    for m in mercados:
        clave = (m["name"], tuple((s["name"], s["price"]) for s in m["selections"]))
        if clave not in claves:
            claves.add(clave)
            unicos.append(m)
    return {"name": nombre_ev or "", "start": inicio, "markets": unicos}


# --------------------------------------------------------------- por casa

def capturar_kambi(url, estado, diag):
    m = re.search(r"event/(\d+)", url) or re.search(r"(\d{8,})", url)
    if not m:
        raise CaptureError("no encontre el id del evento en el link de BetPlay")
    eid = m.group(1)
    combos = []
    if estado.get("kambi"):
        combos.append(tuple(estado["kambi"]))
    combos += descubrir_kambi(estado, diag)
    combos += [(h, o) for o in KAMBI_OFFERINGS for h in KAMBI_HOSTS]
    probados = set()
    for host, off in combos:
        if (host, off) in probados:
            continue
        probados.add((host, off))
        api = (f"{host}/offering/v2018/{off}/betoffer/event/{eid}.json"
               "?lang=es_CO&market=CO&includeParticipants=true")
        code, body = http_get(api, referer="https://betplay.com.co/")
        diag("kambi", api, code, body)
        data = a_json(body) if code == 200 else None
        if not data:
            continue
        ev = extraer_generico(data)
        evs = data.get("events") or []
        if evs:
            ev["start"] = parse_time(evs[0].get("start")) or ev["start"]
            ev["name"] = evs[0].get("name") or ev["name"]
        if ev["markets"]:
            estado["kambi"] = [host, off]
            return ev
    raise CaptureError("Kambi no devolvio mercados para este evento")


def descubrir_kambi(estado, diag):
    if estado.get("kambi_descubierto") is not None:
        return [tuple(c) for c in estado["kambi_descubierto"]]
    code, html = http_get("https://betplay.com.co/apuestas")
    diag("betplay-home", "https://betplay.com.co/apuestas", code, html)
    hosts = set(re.findall(r"https://[a-z0-9.-]*offering-api\.kambicdn\.[a-z]+", html))
    offs = set(re.findall(r'["\']?offering["\']?\s*[:=]\s*["\']([a-z0-9]+)["\']', html))
    combos = [[h, o] for o in offs for h in hosts or KAMBI_HOSTS]
    estado["kambi_descubierto"] = combos
    return [tuple(c) for c in combos]


def capturar_betano(url, estado, diag):
    p = urlsplit(url)
    api = f"{p.scheme}://{p.netloc}/api{p.path}" + (f"?{p.query}" if p.query else "")
    for u in (api, url):
        code, body = http_get(u, referer=url)
        diag("betano", u, code, body)
        if code != 200:
            continue
        data = a_json(body)
        objs = [data] if data is not None else json_embebido(body)
        ev = extraer_generico(objs)
        if ev["markets"]:
            return ev
    raise CaptureError("Betano no devolvio mercados (posible bloqueo o cambio de formato)")


def capturar_html(url, estado, diag):
    code, body = http_get(url)
    diag("html", url, code, body)
    if code != 200:
        raise CaptureError(f"la pagina respondio {code}")
    data = a_json(body)
    ev = extraer_generico([data] if data is not None else json_embebido(body))
    if not ev["markets"]:
        raise CaptureError("la pagina no trae las cuotas en el HTML")
    return ev


def capturar_navegador(url, estado, diag):
    """Abre el link en Chromium sin ventana y lee el JSON que la pagina descarga."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise CaptureError("modo navegador no disponible (pip install playwright && "
                           "playwright install chromium)")
    respuestas, textos = [], []
    with sync_playwright() as pw:
        nav = pw.chromium.launch(headless=True)
        ctx = nav.new_context(locale="es-CO", timezone_id="America/Bogota", user_agent=UA)
        pagina = ctx.new_page()
        pagina.on("response", lambda r: respuestas.append(r))
        try:
            pagina.goto(url, wait_until="domcontentloaded", timeout=45000)
            pagina.wait_for_timeout(9000)
            html = pagina.content()
            for r in respuestas:
                if "json" in (r.headers.get("content-type") or ""):
                    try:
                        textos.append((r.url, r.text()))
                    except Exception:
                        pass
        finally:
            nav.close()
    objs = []
    for u, t in textos:
        diag("navegador", u, 200, t)
        d = a_json(t)
        if d is not None:
            objs.append(d)
    objs += json_embebido(html)
    ev = extraer_generico(objs)
    if not ev["markets"]:
        raise CaptureError("el navegador no encontro cuotas en la pagina")
    return ev


CADENAS = {
    "betplay": [capturar_kambi, capturar_navegador],
    "betano": [capturar_betano, capturar_navegador],
    "betsson": [capturar_html, capturar_navegador],
    "otra": [capturar_html, capturar_navegador],
}


def casa_de(url):
    host = urlsplit(url).netloc.lower()
    for casa in ("betplay", "betano", "betsson"):
        if casa in host:
            return casa
    return "otra"


def capturar_evento(url, estado, diag=lambda *a: None):
    errores = []
    for fn in CADENAS[casa_de(url)]:
        try:
            return fn(url, estado, diag)
        except CaptureError as e:
            errores.append(str(e))
    raise CaptureError(" | ".join(errores))


# ------------------------------------------------------------------ emparejar

FRASES = [
    (r"\bmas de\b", "mas"), (r"\bmenos de\b", "menos"), (r"\bover\b", "mas"),
    (r"\bunder\b", "menos"), (r"\bempate\b", "x"), (r"\bdraw\b", "x"),
    (r"\blocal\b", "1"), (r"\bhome\b", "1"), (r"\bvisitante\b", "2"), (r"\baway\b", "2"),
    (r"\byes\b", "si"), (r"\bboth teams to score\b", "ambos marcan"),
    (r"\bambos equipos marcan\b", "ambos marcan"), (r"\bbtts\b", "ambos marcan"),
]
GRUPOS_MERCADO = [
    ["1x2", "resultado final", "resultado del partido", "ganador del partido",
     "tiempo reglamentario", "match result", "full time result", "final del partido",
     "resultado"],
    ["total de goles", "goles totales", "total goles", "mas menos", "total goals",
     "over under", "goles mas menos"],
    ["ambos marcan"],
    ["doble oportunidad", "double chance"],
    ["handicap asiatico", "asian handicap", "handicap"],
    ["empate no apuesta", "draw no bet", "apuesta sin empate"],
    ["moneyline", "money line", "ganador", "ganador incl prorroga"],
]
MITADES = {"parte", "mitad", "descanso", "half", "1a", "2a", "periodo", "cuarto",
           "set", "entrada", "inning"}


def norm(t):
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode()
    t = t.lower()
    t = re.sub(r"(\d),(\d)", r"\1.\2", t)
    t = re.sub(r"[^a-z0-9.+\-]+", " ", t)
    t = re.sub(r"(?<![\d])[.+\-](?![\d])", " ", t)
    t = " ".join(t.split())
    for pat, rep in FRASES:
        t = re.sub(pat, rep, t)
    return " ".join(t.split())


def numeros(t):
    return re.findall(r"[-+]?\d+(?:\.\d+)?", t)


def numeros_ok(q, c):
    cn = numeros(c)
    cabs = {abs(float(n)) for n in cn}
    cfull = {float(n) for n in cn}
    for n in numeros(q):
        if n[0] in "+-":
            if float(n) not in cfull:
                return False
        elif abs(float(n)) not in cabs:
            return False
    return True


def sim(q, c):
    if not q or not c:
        return 0.0
    if q == c:
        return 1.0
    tq, tc = set(q.split()), set(c.split())
    if tq <= tc or tc <= tq:
        chico, grande = sorted((len(tq), len(tc)))
        return 0.75 + 0.2 * chico / grande
    return difflib.SequenceMatcher(None, q, c).ratio()


def sin_lineas(t):
    """Quita las lineas (2.5, -1) pero no el 1 y el 2 de '1x2' ni el '1a' de '1a parte'."""
    return " ".join(re.sub(r"(?<![a-z0-9])[-+]?\d+(?:\.\d+)?(?![a-z0-9])", " ", norm(t)).split())


def sim_mercado(q, mercado):
    q = sin_lineas(q)
    aliases = [sin_lineas(a) for a in mercado["aliases"]]
    mejor = max((sim(q, a) for a in aliases), default=0.0)
    for grupo in GRUPOS_MERCADO:
        if q in grupo:
            for a in aliases:
                if a in grupo:
                    mejor = max(mejor, 0.92)
                elif any(re.search(rf"\b{re.escape(g)}\b", a) for g in grupo):
                    mejor = max(mejor, 0.85)
    tq = set(q.split())
    if any(set(a.split()) & MITADES and not tq & MITADES for a in aliases):
        mejor *= 0.7
    return mejor


def sim_seleccion(q, sel):
    q = norm(q)
    mejor = 0.0
    for a in [sel["name"]] + sel["aliases"]:
        a = norm(a)
        if numeros_ok(q, a):
            mejor = max(mejor, sim(q, a))
    return mejor


def emparejar(pick, ev, previo=None):
    if previo:
        for m in ev["markets"]:
            for s in m["selections"]:
                if m["name"] == previo[0] and s["name"] == previo[1]:
                    return m, s
    cands = []
    for m in ev["markets"]:
        ms = sim_mercado(pick["mercado"], m) if pick["mercado"] else 0.7
        if ms < 0.5:
            continue
        for s in m["selections"]:
            ss = sim_seleccion(pick["seleccion"], s)
            if ss >= 0.75:
                cands.append((0.35 * ms + 0.65 * ss, m, s))
    if not cands:
        nombres = ", ".join(sorted({m["name"] for m in ev["markets"]})[:25])
        raise CaptureError(f"no encontre '{pick['mercado']} / {pick['seleccion']}'. "
                           f"Mercados disponibles: {nombres}")
    cands.sort(key=lambda c: -c[0])
    mejor = cands[0]
    empates = [c for c in cands[1:] if c[0] >= mejor[0] - 0.02
               and c[2]["price"] != mejor[2]["price"]]
    if empates:
        opciones = "; ".join(f"{c[1]['name']} / {c[2]['name']} @ {c[2]['price']}"
                             for c in [mejor] + empates[:4])
        raise CaptureError(f"pick ambiguo, escribe el mercado mas exacto: {opciones}")
    return mejor[1], mejor[2]


def sin_margen(mercado, sel):
    """Probabilidad justa de la seleccion quitando el margen de la casa."""
    def misma_linea(x):
        if x["line"] is None or sel["line"] is None:
            return x["line"] is None and sel["line"] is None
        return abs(abs(x["line"]) - abs(sel["line"])) < 1e-9
    grupo = [x for x in mercado["selections"] if misma_linea(x)]
    if not 2 <= len(grupo) <= 3:
        return None, None
    total = sum(1 / x["price"] for x in grupo)
    if not 1.0 < total < 1.3:
        return None, None
    return (1 / sel["price"]) / total, total - 1


# ------------------------------------------------------------- picks y estado

def cargar_picks(fuente):
    fuente = str(fuente)
    if fuente.startswith("http"):
        code, texto = http_get(fuente)
        if code != 200:
            raise SystemExit(f"No pude leer los picks desde {fuente} (codigo {code})")
    else:
        ruta = Path(fuente)
        if not ruta.exists():
            raise SystemExit(f"No existe {ruta}. Copia picks_ejemplo.csv como picks.csv.")
        texto = ruta.read_text(encoding="utf-8-sig")
    primera = texto.splitlines()[0] if texto else ""
    delim = ";" if primera.count(";") > primera.count(",") else ","
    picks = []
    for fila in csv.DictReader(io.StringIO(texto), delimiter=delim):
        f = {norm(k).replace(" ", "_"): (v or "").strip() for k, v in fila.items() if k}
        link = f.get("link", "")
        if not link.startswith("http"):
            continue
        p = {
            "link": link,
            "mercado": f.get("mercado", ""),
            "seleccion": f.get("seleccion", ""),
            "cuota": a_float(f.get("cuota") or f.get("cuota_tomada")),
            "inicio": parse_inicio_usuario(f.get("inicio") or f.get("hora")),
        }
        clave = "|".join([link, p["mercado"], p["seleccion"], str(p["cuota"])])
        p["id"] = f.get("id") or hashlib.sha1(clave.encode()).hexdigest()[:8]
        picks.append(p)
    return picks


def cargar_estado():
    if ESTADO.exists():
        return json.loads(ESTADO.read_text(encoding="utf-8"))
    return {"picks": {}}


def guardar_estado(estado):
    tmp = ESTADO.with_suffix(".tmp")
    tmp.write_text(json.dumps(estado, ensure_ascii=False, indent=1, default=str),
                   encoding="utf-8")
    tmp.replace(ESTADO)


def iso(dt):
    return dt.isoformat() if dt else None


def desde_iso(t):
    return datetime.fromisoformat(t) if t else None


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def tomar_captura(pick, st, estado):
    ev = capturar_evento(pick["link"], estado)
    previo = (st.get("mercado_casa"), st.get("seleccion_casa")) if st.get("mercado_casa") else None
    m, s = emparejar(pick, ev, previo)
    justa, margen = sin_margen(m, s)
    st.update({"evento": ev["name"] or st.get("evento", ""),
               "mercado_casa": m["name"], "seleccion_casa": s["name"]})
    if ev["start"] and not pick["inicio"]:
        st["inicio"] = iso(ev["start"])
    snap = {"ts": iso(datetime.now(timezone.utc)), "cuota": s["price"], "justa": justa,
            "margen": margen, "estado": s["status"]}
    st["capturas"].append(snap)
    nuevo = not LOG_CAPTURAS.exists()
    with LOG_CAPTURAS.open("a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if nuevo:
            w.writerow(["hora", "pick", "casa", "evento", "mercado", "seleccion", "cuota",
                        "estado"])
        w.writerow([datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S"), pick["id"],
                    casa_de(pick["link"]), st["evento"], m["name"], s["name"], s["price"],
                    s["status"]])
    return snap


def intervalo(inicio, ahora):
    if inicio is None:
        return timedelta(minutes=30)
    falta = inicio - ahora
    if falta > timedelta(hours=3):
        return timedelta(minutes=60)
    if falta > timedelta(minutes=60):
        return timedelta(minutes=20)
    if falta > timedelta(minutes=20):
        return timedelta(minutes=5)
    return timedelta(minutes=2)


def estado_pick(pick, estado):
    st = estado["picks"].setdefault(pick["id"], {"capturas": []})
    st.update({"link": pick["link"], "mercado": pick["mercado"],
               "seleccion": pick["seleccion"], "cuota": pick["cuota"]})
    if pick["inicio"]:
        st["inicio"] = iso(pick["inicio"])
    return st


def ciclo(picks, estado, forzar=False):
    ahora = datetime.now(timezone.utc)
    for p in picks:
        st = estado_pick(p, estado)
        if st.get("cerrado"):
            continue
        inicio = desde_iso(st.get("inicio"))
        if inicio and ahora >= inicio:
            st["cerrado"] = True
            log(f"{p['id']} cerrado ({st.get('evento') or p['link']})")
            continue
        ultimo = desde_iso(st.get("ultimo_intento"))
        if not forzar and ultimo and ahora - ultimo < intervalo(inicio, ahora):
            continue
        st["ultimo_intento"] = iso(ahora)
        try:
            snap = tomar_captura(p, st, estado)
            st.pop("error", None)
            log(f"{p['id']} {st['evento']} | {st['mercado_casa']} / {st['seleccion_casa']}"
                f" @ {snap['cuota']}")
        except CaptureError as e:
            st["error"] = str(e)
            log(f"{p['id']} ERROR: {e}")
        guardar_estado(estado)


# --------------------------------------------------------------------- salida

def cierre(st):
    inicio = desde_iso(st.get("inicio"))
    validas = [c for c in st["capturas"]
               if not inicio or desde_iso(c["ts"]) < inicio]
    abiertas = [c for c in validas if c["estado"].upper() not in ("SUSPENDED", "CLOSED")]
    return (abiertas or validas or [None])[-1]


def num(x, dec):
    if x is None:
        return ""
    return f"{x:.{dec}f}".replace(".", DECIMAL)


def exportar(estado, salida, ids=None):
    filas = []
    for pid, st in estado["picks"].items():
        if ids is not None and pid not in ids:
            continue
        c = cierre(st)
        inicio = desde_iso(st.get("inicio"))
        cuota = st.get("cuota")
        fila = {
            "id": pid,
            "fecha": inicio.astimezone(LOCAL_TZ).strftime("%Y-%m-%d") if inicio else "",
            "hora_inicio": inicio.astimezone(LOCAL_TZ).strftime("%H:%M") if inicio else "",
            "casa": casa_de(st["link"]),
            "evento": st.get("evento", ""),
            "mercado": st.get("mercado_casa") or st.get("mercado", ""),
            "seleccion": st.get("seleccion_casa") or st.get("seleccion", ""),
            "cuota_tomada": num(cuota, 3),
            "cuota_cierre": "", "hora_captura_cierre": "", "min_antes_inicio": "",
            "clv_pct": "", "clv_sin_margen_pct": "", "margen_cierre_pct": "",
            "capturas": len(st["capturas"]),
            "estado": "",
            "link": st["link"],
        }
        if c:
            ts = desde_iso(c["ts"])
            fila["cuota_cierre"] = num(c["cuota"], 3)
            fila["hora_captura_cierre"] = ts.astimezone(LOCAL_TZ).strftime("%H:%M")
            if inicio:
                fila["min_antes_inicio"] = str(int((inicio - ts).total_seconds() // 60))
            if cuota:
                fila["clv_pct"] = num((cuota / c["cuota"] - 1) * 100, 2)
                if c.get("justa"):
                    fila["clv_sin_margen_pct"] = num((cuota * c["justa"] - 1) * 100, 2)
            if c.get("margen") is not None:
                fila["margen_cierre_pct"] = num(c["margen"] * 100, 2)
        if st.get("cerrado"):
            if not c:
                fila["estado"] = "sin_captura"
            elif inicio and (inicio - desde_iso(c["ts"])) > timedelta(minutes=MAX_MIN_CIERRE):
                fila["estado"] = "cierre_viejo"
            else:
                fila["estado"] = "cerrado"
        else:
            fila["estado"] = "pendiente"
        if st.get("error"):
            fila["estado"] += f" (error: {st['error'][:150]})"
        filas.append(fila)
    filas.sort(key=lambda f: (f["fecha"], f["hora_inicio"], f["id"]))
    if not filas:
        return
    tmp = Path(salida).with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]), delimiter=SEPARADOR)
        w.writeheader()
        w.writerows(filas)
    tmp.replace(salida)


# -------------------------------------------------------------------- comandos

def cmd_validar(args):
    picks = cargar_picks(args.picks)
    estado = cargar_estado()
    ciclo(picks, estado, forzar=True)
    guardar_estado(estado)
    exportar(estado, args.salida)
    ok = sum(1 for p in picks if not estado["picks"][p["id"]].get("error"))
    print(f"\n{ok}/{len(picks)} picks capturados bien. Revisa {args.salida}")


def cmd_vigilar(args):
    log(f"Vigilando picks de {args.picks}. Ctrl+C para salir.")
    estado = cargar_estado()
    while True:
        try:
            picks = cargar_picks(args.picks)
            ciclo(picks, estado)
            exportar(estado, args.salida)
        except SystemExit as e:
            log(str(e))
        except Exception as e:  # que un error raro no tumbe la vigilancia del dia
            log(f"error inesperado: {e!r}")
        time.sleep(60)


def cmd_diagnosticar(args):
    DIAGNOSTICO.mkdir(exist_ok=True)
    n = [0]

    def diag(etapa, url, code, body):
        n[0] += 1
        ruta = DIAGNOSTICO / f"{n[0]:02d}_{etapa}.txt"
        ruta.write_text(f"{url}\n{code}\n\n{body}", encoding="utf-8")
        print(f"  [{etapa}] {code} {url[:110]}  ({len(body or '')} bytes) -> {ruta.name}")

    estado = cargar_estado()
    print(f"Casa detectada: {casa_de(args.link)}")
    for fn in CADENAS[casa_de(args.link)]:
        print(f"\n== {fn.__name__}")
        try:
            ev = fn(args.link, estado, diag)
        except CaptureError as e:
            print(f"  fallo: {e}")
            continue
        inicio = ev["start"].astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M") if ev["start"] else "?"
        print(f"  OK: '{ev['name']}' inicio {inicio}, {len(ev['markets'])} mercados")
        for m in ev["markets"][:12]:
            sels = ", ".join(f"{s['name']} @ {s['price']}" for s in m["selections"][:6])
            print(f"    - {m['name']}: {sels}")
        guardar_estado(estado)
        return
    print("\nNinguna estrategia funciono. Envia la carpeta 'diagnostico' para ajustar el lector.")


def cmd_exportar(args):
    exportar(cargar_estado(), args.salida)
    print(f"Escrito {args.salida}")


def main():
    ap = argparse.ArgumentParser(description="Capturador de cuotas de cierre (CLV)")
    ap.add_argument("comando", choices=["validar", "vigilar", "diagnosticar", "exportar"])
    ap.add_argument("link", nargs="?", help="link del partido (solo para diagnosticar)")
    ap.add_argument("--picks", default=str(PICKS_DEFAULT))
    ap.add_argument("--salida", default=str(SALIDA_DEFAULT))
    args = ap.parse_args()
    if args.comando == "diagnosticar" and not args.link:
        ap.error("diagnosticar necesita el link del partido")
    try:
        {"validar": cmd_validar, "vigilar": cmd_vigilar,
         "diagnosticar": cmd_diagnosticar, "exportar": cmd_exportar}[args.comando](args)
    except KeyboardInterrupt:
        print("\nDetenido.")


if __name__ == "__main__":
    main()
