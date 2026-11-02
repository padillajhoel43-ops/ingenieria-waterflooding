"""Calculadora educativa de OOIP. Python 3.9+, sin dependencias externas."""

import argparse
import csv
import math
from dataclasses import asdict, dataclass
from pathlib import Path

VERSION = "0.1.0"
BARRILES_POR_ACRE_PIE = 7758.0  # Factor convencional redondeado.


@dataclass(frozen=True)
class DatosYacimiento:
    area_acres: float
    espesor_neto_ft: float
    porosidad: float
    saturacion_agua_inicial: float
    boi_rb_stb: float

    def validar(self):
        for nombre, valor in asdict(self).items():
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                raise ValueError(f"{nombre}: debe ser un número.")
            if not math.isfinite(valor):
                raise ValueError(f"{nombre}: debe ser finito.")
        if self.area_acres <= 0 or self.espesor_neto_ft <= 0:
            raise ValueError("El área y el espesor neto deben ser mayores que cero.")
        if not 0 < self.porosidad <= 1:
            raise ValueError("La porosidad debe estar entre 0 (excluido) y 1.")
        if not 0 <= self.saturacion_agua_inicial <= 1:
            raise ValueError("La saturación de agua debe estar entre 0 y 1.")
        if self.boi_rb_stb <= 0:
            raise ValueError("Boi debe ser mayor que cero, en rb/STB.")


@dataclass(frozen=True)
class Resultado:
    volumen_bruto_acre_ft: float
    volumen_poroso_rb: float
    volumen_petroleo_inicial_rb: float
    ooip_stb: float
    ooip_mmstb: float


def calcular_ooip(datos):
    """Modelo volumétrico inicial sin gas libre: Soi = 1 - Swi.

    N [STB] = 7758 * A [acre] * h [ft] * phi * (1-Swi) / Boi [rb/STB].
    Swi es saturación inicial de agua; no se supone que sea irreducible.
    """
    datos.validar()
    bruto = datos.area_acres * datos.espesor_neto_ft
    poroso = BARRILES_POR_ACRE_PIE * bruto * datos.porosidad
    petroleo = poroso * (1 - datos.saturacion_agua_inicial)
    ooip = petroleo / datos.boi_rb_stb
    resultado = Resultado(bruto, poroso, petroleo, ooip, ooip / 1_000_000)
    if not all(math.isfinite(v) for v in asdict(resultado).values()):
        raise ValueError("Los datos producen desbordamiento numérico; revise su magnitud.")
    return resultado


# Escenario exclusivamente sintético. No corresponde a un campo real.
EJEMPLO = DatosYacimiento(40.0, 40.0, 0.20, 0.25, 1.23)


def exportar_csv(ruta, datos, resultado):
    """Exporta entradas y salidas; la CLI exige un archivo nuevo."""
    unidades = {
        "area_acres": "acre", "espesor_neto_ft": "ft",
        "porosidad": "fracción", "saturacion_agua_inicial": "fracción",
        "boi_rb_stb": "rb/STB", "volumen_bruto_acre_ft": "acre.ft",
        "volumen_poroso_rb": "rb", "volumen_petroleo_inicial_rb": "rb",
        "ooip_stb": "STB", "ooip_mmstb": "MMSTB",
    }
    with Path(ruta).open("x", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.writer(archivo, delimiter=";")
        escritor.writerow(["tipo", "variable", "valor", "unidad"])
        for tipo, objeto in (("entrada", datos), ("resultado", resultado)):
            for nombre, valor in asdict(objeto).items():
                escritor.writerow([tipo, nombre, valor, unidades[nombre]])


def leer_numero(etiqueta):
    # Permite coma decimal, sin separadores de miles.
    while True:
        texto = input(etiqueta + ": ").strip().replace(",", ".")
        try:
            valor = float(texto)
            if not math.isfinite(valor):
                raise ValueError
            return valor
        except ValueError:
            print("Escribe un número finito, sin separadores de miles.")


def main(argv=None):
    parser = argparse.ArgumentParser(description="OOIP educativo por método volumétrico.")
    parser.add_argument("--version", action="version", version=VERSION)
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument("--ejemplo", action="store_true", help="Usar escenario sintético.")
    modo.add_argument("--datos", nargs=5, type=float,
                      metavar=("A", "H", "PHI", "SWI", "BOI"),
                      help="Área acre, espesor ft, phi fracción, Swi fracción, Boi rb/STB.")
    parser.add_argument("--csv", type=Path, help="Guardar CSV en un archivo que no exista.")
    args = parser.parse_args(argv)
    print("OOIP | Ingeniería Waterflooding | v" + VERSION)
    print("Modelo educativo inicial de petróleo y agua, sin gas libre.")
    try:
        if args.ejemplo:
            datos = EJEMPLO
            print("DATOS SINTÉTICOS: A=40 acre; h=40 ft; phi=0.20; Swi=0.25; Boi=1.23.")
        elif args.datos is not None:
            datos = DatosYacimiento(*args.datos)
        else:
            print("Usa fracciones: 20 % = 0.20. Boi se evalúa a condiciones iniciales.")
            datos = DatosYacimiento(
                leer_numero("Área [acre]"), leer_numero("Espesor neto [ft]"),
                leer_numero("Porosidad [fracción]"),
                leer_numero("Saturación inicial de agua [fracción]"),
                leer_numero("Boi [rb/STB]"),
            )
        resultado = calcular_ooip(datos)
        print(f"Volumen bruto: {resultado.volumen_bruto_acre_ft:,.3f} acre.ft")
        print(f"Volumen poroso: {resultado.volumen_poroso_rb:,.3f} rb")
        print(f"Petróleo inicial a condiciones de yacimiento: {resultado.volumen_petroleo_inicial_rb:,.3f} rb")
        print(f"OOIP: {resultado.ooip_stb:,.3f} STB = {resultado.ooip_mmstb:.6f} MMSTB")
        print("Formato de salida: coma para miles y punto decimal.")
        print("OOIP no equivale a reservas recuperables ni predice el comportamiento de la inyección.")
        if args.csv:
            exportar_csv(args.csv, datos, resultado)
            print(f"CSV guardado: {args.csv}")
        return 0
    except (ValueError, OSError, OverflowError) as error:
        print(f"Error: {error}")
        return 2
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada cancelada.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
