"""Pruebas de ingeniería, límites físicos e integración de la CLI."""
import csv
import math
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from calculadora_ooip import DatosYacimiento, EJEMPLO, calcular_ooip, exportar_csv


class PruebasOOIP(unittest.TestCase):
    def test_caso_unitario(self):
        self.assertEqual(calcular_ooip(DatosYacimiento(1, 1, 1, 0, 1)).ooip_stb, 7758)

    def test_ejemplo_independiente(self):
        r = calcular_ooip(EJEMPLO)
        # Cálculo manual: 1600 acre.ft -> 2,482,560 rb porosos
        # -> 1,861,920 rb de petróleo -> dividir entre 1.23.
        self.assertEqual(r.volumen_bruto_acre_ft, 1600)
        self.assertEqual(r.volumen_poroso_rb, 2482560)
        self.assertEqual(r.volumen_petroleo_inicial_rb, 1861920)
        self.assertAlmostEqual(r.ooip_stb, 1513756.0975609757)
        self.assertAlmostEqual(r.ooip_mmstb, 1.5137560975609756)

    def test_doble_area(self):
        self.assertAlmostEqual(calcular_ooip(replace(EJEMPLO, area_acres=80)).ooip_stb,
                               2 * calcular_ooip(EJEMPLO).ooip_stb)

    def test_boi_inverso(self):
        self.assertAlmostEqual(calcular_ooip(replace(EJEMPLO, boi_rb_stb=2.46)).ooip_stb,
                               calcular_ooip(EJEMPLO).ooip_stb / 2)

    def test_saturacion_total_agua(self):
        self.assertEqual(calcular_ooip(replace(EJEMPLO, saturacion_agua_inicial=1)).ooip_stb, 0)

    def test_sin_agua(self):
        r = calcular_ooip(replace(EJEMPLO, saturacion_agua_inicial=0))
        self.assertAlmostEqual(r.ooip_stb, 2482560 / 1.23)

    def test_rechaza_limites_invalidos(self):
        for campo, valores in {
            "area_acres": [0, -1], "espesor_neto_ft": [0, -1],
            "porosidad": [0, -0.1, 20, 1.01],
            "saturacion_agua_inicial": [-0.1, 25, 1.01],
            "boi_rb_stb": [0, -1],
        }.items():
            for valor in valores:
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValueError):
                    calcular_ooip(replace(EJEMPLO, **{campo: valor}))

    def test_rechaza_no_finitos_y_tipos(self):
        for campo in EJEMPLO.__dataclass_fields__:
            for valor in [math.nan, math.inf, -math.inf, True, "20", None]:
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValueError):
                    calcular_ooip(replace(EJEMPLO, **{campo: valor}))

    def test_desbordamiento(self):
        with self.assertRaises(ValueError):
            calcular_ooip(replace(EJEMPLO, area_acres=1e308))

    def test_csv_y_no_sobrescribir(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "resultado.csv"
            exportar_csv(ruta, EJEMPLO, calcular_ooip(EJEMPLO))
            with ruta.open(encoding="utf-8-sig", newline="") as f:
                filas = list(csv.DictReader(f, delimiter=";"))
            self.assertEqual(len(filas), 10)
            fila = next(x for x in filas if x["variable"] == "ooip_stb")
            self.assertEqual(fila["unidad"], "STB")
            self.assertAlmostEqual(float(fila["valor"]), 1513756.0975609757)
            with self.assertRaises(FileExistsError):
                exportar_csv(ruta, EJEMPLO, calcular_ooip(EJEMPLO))

    def ejecutar(self, *args, entrada=None):
        script = Path(__file__).with_name("calculadora_ooip.py")
        return subprocess.run([sys.executable, str(script), *args], input=entrada,
                              capture_output=True, text=True, timeout=10)

    def test_cli_ejemplo(self):
        r = self.ejecutar("--ejemplo")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1.513756 MMSTB", r.stdout)

    def test_cli_datos_invalidos(self):
        self.assertEqual(self.ejecutar("--datos", "40", "40", "20", ".25", "1.23").returncode, 2)

    def test_cli_interactivo_coma_decimal(self):
        r = self.ejecutar(entrada="40\n40\n0,20\n0,25\n1,23\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1.513756 MMSTB", r.stdout)

    def test_cli_reintenta_entrada_invalida(self):
        r = self.ejecutar(entrada="abc\n40\n40\n.2\n.25\n1.23\n")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Escribe un número finito", r.stdout)

    def test_cli_csv(self):
        with tempfile.TemporaryDirectory() as d:
            destino = str(Path(d) / "salida.csv")
            self.assertEqual(self.ejecutar("--ejemplo", "--csv", destino).returncode, 0)
            self.assertTrue(Path(destino).is_file())
            self.assertEqual(self.ejecutar("--ejemplo", "--csv", destino).returncode, 2)


if __name__ == "__main__":
    unittest.main()
