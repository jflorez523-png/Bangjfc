"""Pruebas sin red: python -m unittest test_clv.py"""

import csv
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

import clv_capturador as c

INICIO = (datetime.now(timezone.utc) + timedelta(hours=3)).replace(microsecond=0)

KAMBI = {
    "events": [{"id": 1021, "name": "Millonarios - Atlético Nacional",
                "start": INICIO.strftime("%Y-%m-%dT%H:%M:%SZ")}],
    "betOffers": [
        {"criterion": {"label": "Tiempo reglamentario"}, "betOfferType": {"name": "Partido"},
         "outcomes": [
             {"label": "1", "participant": "Millonarios", "type": "OT_ONE", "odds": 2150, "status": "OPEN"},
             {"label": "X", "type": "OT_CROSS", "odds": 3200, "status": "OPEN"},
             {"label": "2", "participant": "Atlético Nacional", "type": "OT_TWO", "odds": 3500, "status": "OPEN"}]},
        {"criterion": {"label": "Descanso"}, "betOfferType": {"name": "Partido"},
         "outcomes": [
             {"label": "1", "participant": "Millonarios", "type": "OT_ONE", "odds": 2900},
             {"label": "X", "type": "OT_CROSS", "odds": 2000},
             {"label": "2", "participant": "Atlético Nacional", "type": "OT_TWO", "odds": 4000}]},
        {"criterion": {"label": "Total de goles"}, "betOfferType": {"name": "Más/Menos"},
         "outcomes": [
             {"label": "Más de", "line": 2500, "type": "OT_OVER", "odds": 2050},
             {"label": "Menos de", "line": 2500, "type": "OT_UNDER", "odds": 1780}]},
        {"criterion": {"label": "Total de goles"}, "betOfferType": {"name": "Más/Menos"},
         "outcomes": [
             {"label": "Más de", "line": 1500, "type": "OT_OVER", "odds": 1350},
             {"label": "Menos de", "line": 1500, "type": "OT_UNDER", "odds": 3100}]},
    ],
}

BETANO_HTML = """<html><script>window["initial_state"]={"data":{"event":{"name":"Millonarios - Nacional",
"startTime":%d,"markets":[{"name":"Resultado Final","selections":[{"name":"1","price":2.10},
{"name":"X","price":3.25},{"name":"2","price":3.60}]},{"name":"Total de Goles Más/Menos",
"selections":[{"name":"Más de 2.5","price":2.02,"handicap":2.5},{"name":"Menos de 2.5","price":1.80,"handicap":2.5},
{"name":"Más de 3.5","price":3.40,"handicap":3.5},{"name":"Menos de 3.5","price":1.30,"handicap":3.5}]}]}}}</script></html>
""" % int(INICIO.timestamp() * 1000)


def pick(mercado, seleccion, cuota=2.2):
    return {"mercado": mercado, "seleccion": seleccion, "cuota": cuota}


class Kambi(unittest.TestCase):
    def setUp(self):
        self.ev = c.extraer_generico(KAMBI)

    def test_evento(self):
        self.assertEqual(self.ev["start"], INICIO)
        self.assertEqual(len(self.ev["markets"]), 4)

    def test_1x2_por_equipo_y_por_codigo(self):
        for sel in ("Millonarios", "1", "local"):
            m, s = c.emparejar(pick("1X2", sel), self.ev)
            self.assertEqual((m["name"], s["price"]), ("Tiempo reglamentario", 2.15), sel)

    def test_empate(self):
        _, s = c.emparejar(pick("Resultado final", "Empate"), self.ev)
        self.assertEqual(s["price"], 3.2)

    def test_over_linea_correcta(self):
        _, s = c.emparejar(pick("Total de goles", "Over 2.5"), self.ev)
        self.assertEqual(s["price"], 2.05)
        _, s = c.emparejar(pick("Total goles", "Menos de 1,5"), self.ev)
        self.assertEqual(s["price"], 3.1)

    def test_sin_margen(self):
        m, s = c.emparejar(pick("Total de goles", "Más de 2.5"), self.ev)
        justa, margen = c.sin_margen(m, s)
        self.assertAlmostEqual(justa, (1 / 2.05) / (1 / 2.05 + 1 / 1.78))
        self.assertGreater(margen, 0)

    def test_no_encontrado(self):
        with self.assertRaises(c.CaptureError):
            c.emparejar(pick("Total de goles", "Más de 4.5"), self.ev)


class Betano(unittest.TestCase):
    def setUp(self):
        self.ev = c.extraer_generico(c.json_embebido(BETANO_HTML))

    def test_evento(self):
        self.assertEqual(self.ev["start"], INICIO)
        self.assertEqual(self.ev["name"], "Millonarios - Nacional")

    def test_picks(self):
        _, s = c.emparejar(pick("1X2", "2"), self.ev)
        self.assertEqual(s["price"], 3.6)
        m, s = c.emparejar(pick("Más/Menos", "Más de 3.5"), self.ev)
        self.assertEqual(s["price"], 3.4)
        justa, _ = c.sin_margen(m, s)
        self.assertAlmostEqual(justa, (1 / 3.4) / (1 / 3.4 + 1 / 1.3))


class Planos(unittest.TestCase):
    def test_markets_y_selections_enlazados(self):
        data = {"data": {"markets": [{"id": "m1", "label": "Ambos equipos marcan"}],
                         "selections": [{"marketId": "m1", "label": "Sí", "odds": 1.9},
                                        {"marketId": "m1", "label": "No", "odds": 1.85}]}}
        ev = c.extraer_generico(data)
        _, s = c.emparejar(pick("BTTS", "Si"), ev)
        self.assertEqual(s["price"], 1.9)


class Salida(unittest.TestCase):
    def test_clv(self):
        antes = (INICIO - timedelta(minutes=3)).isoformat()
        estado = {"picks": {"a": {
            "link": "https://betplay.com.co/apuestas#event/1021", "cuota": 2.30,
            "inicio": INICIO.isoformat(), "cerrado": True, "evento": "x",
            "capturas": [{"ts": antes, "cuota": 2.10, "justa": 0.46, "margen": 0.05, "estado": "OPEN"}]}}}
        with tempfile.TemporaryDirectory() as d:
            ruta = f"{d}/out.csv"
            c.exportar(estado, ruta)
            with open(ruta, encoding="utf-8-sig") as fh:
                filas = list(csv.DictReader(fh))
        self.assertEqual(filas[0]["cuota_cierre"], "2.100")
        self.assertEqual(filas[0]["clv_pct"], "9.52")
        self.assertEqual(filas[0]["clv_sin_margen_pct"], "5.80")
        self.assertEqual(filas[0]["min_antes_inicio"], "3")
        self.assertEqual(filas[0]["estado"], "cerrado")


if __name__ == "__main__":
    unittest.main()
