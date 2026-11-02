# Ingeniería Waterflooding

Herramientas educativas en Python para cálculos de ingeniería de yacimientos, con documentación en español. Proyecto emergente impulsado por Jhoel José Padilla Choquevillca, estudiante de Ingeniería en Gas y Petróleo e Ingeniería Civil, Bolivia.

## Versión 0.1.0: calculadora de petróleo original en sitio

Esta versión estima el **OOIP** mediante el método volumétrico. Muestra el volumen bruto, el volumen poroso, el volumen inicial de petróleo a condiciones de yacimiento y el OOIP a condiciones de tanque. Permite introducir datos por consola y exportar entradas y resultados a CSV.

Es el primer módulo del proyecto. **No simula waterflooding**, no calcula barrido, presiones de inyección, ruptura de agua ni reservas recuperables.

## Ejecutar en Windows

Necesitas Python 3.9 o posterior. No requiere instalar paquetes externos.

1. Descarga el repositorio con **Code → Download ZIP** y extrae los archivos.
2. Abre esa carpeta en el Explorador de Windows.
3. Escribe `cmd` en su barra de direcciones y presiona Enter.
4. Ejecuta el ejemplo:

```bat
py -3 calculadora_ooip.py --ejemplo
```

Para ingresar tus propios datos, ejecuta:

```bat
py -3 calculadora_ooip.py
```

Si `py` no está disponible, prueba `python`. En Linux o macOS, usa `python3`.

## Fundamento y unidades

```text
N = 7758 × A × h × phi × (1 − Swi) / Boi
```

| Variable | Significado | Unidad de entrada |
|---|---|---|
| A | Área del sector evaluado | acre |
| h | Espesor neto petrolífero promedio | ft |
| phi | Porosidad efectiva representativa | fracción, por ejemplo 0.20 |
| Swi | Saturación inicial de agua | fracción, por ejemplo 0.25 |
| Boi | Factor volumétrico del petróleo a condiciones iniciales | rb/STB |
| N | Petróleo original en sitio | STB |

El factor convencional redondeado 7758 convierte acre.ft a barriles. Un MMSTB equivale a un millón de STB. El modelo supone petróleo y agua en el volumen poroso inicial, sin gas libre: Soi = 1 − Swi. **Swi significa inicial; no necesariamente irreducible.** Boi debe corresponder a la presión y temperatura iniciales, no sustituirse automáticamente por el Bo de otra etapa.

Se utilizan propiedades promedio representativas del sector y espesor ya neto: no se aplica una segunda reducción por net-to-gross. Para un yacimiento heterogéneo, la selección de promedios y la integración espacial requieren una evaluación adicional.

Referencia técnica para la ecuación: AAPG Wiki, [Predicting hydrocarbon recovery](https://wiki.aapg.org/Predicting_hydrocarbon_recovery), sección sobre volumen original de hidrocarburos. La referencia sustenta el método; no valida los datos sintéticos ni este software.

## Ejemplo sintético reproducible

**Todos estos valores son ilustrativos. No son datos de campo ni un conjunto validado de una monografía.**

| Entrada | Valor |
|---|---:|
| Área | 40 acre |
| Espesor neto | 40 ft |
| Porosidad | 0.20 |
| Saturación inicial de agua | 0.25 |
| Boi | 1.23 rb/STB |

Comprobación manual:

1. Volumen bruto = 40 × 40 = **1600 acre.ft**.
2. Volumen poroso = 7758 × 1600 × 0.20 = **2 482 560 rb**.
3. Petróleo inicial en yacimiento = 2 482 560 × 0.75 = **1 861 920 rb**.
4. OOIP = 1 861 920 / 1.23 = **1 513 756.098 STB**, aproximadamente **1.513756 MMSTB**.

La consola utiliza coma para miles y punto decimal. En modo interactivo acepta punto o coma decimal, sin separadores de miles. Introduce 20 % como 0.20, no como 20. En los argumentos de línea de comandos utiliza punto decimal.

## Exportar y automatizar

```bat
py -3 calculadora_ooip.py --ejemplo --csv resultado_ooip.csv
py -3 calculadora_ooip.py --datos 40 40 0.20 0.25 1.23
```

El CSV utiliza punto decimal y punto y coma como separador; para abrirlo en Excel, importa el archivo y selecciona esos formatos. Incluye entradas, resultados y unidades. Por protección frente a pérdidas accidentales, el programa rechaza un nombre CSV que ya exista: elige uno nuevo.

También se puede importar la función desde otro programa:

```python
from calculadora_ooip import DatosYacimiento, calcular_ooip

datos = DatosYacimiento(40, 40, 0.20, 0.25, 1.23)
resultado = calcular_ooip(datos)
print(resultado.ooip_mmstb)
```

## Verificar

```bat
py -3 -m unittest -v
```

La suite verifica un caso unitario, el ejemplo manual, proporcionalidad con área, dependencia inversa de Boi, límites de saturación, rechazo de entradas inválidas y no finitas, desbordamiento, CSV y funcionamiento de la consola. Estas pruebas comprueban la implementación; no constituyen validación de un yacimiento real.

## Estado y próximos pasos

Disponible: módulo volumétrico, consola, exportación y pruebas. Pendiente: revisión técnica externa, ejemplos adicionales y futuros módulos de productividad y análisis de sensibilidad. No se afirma una base de usuarios, descargas ni resultados de campo.

Para colaborar, abre un issue con el problema o una propuesta. En cambios de cálculo, incluye ecuación, unidades, referencia y ejemplo comprobado. Utiliza únicamente datos sintéticos, públicos o autorizados.

## Autoría y licencia

Impulsor del proyecto: Jhoel José Padilla Choquevillca. Primera versión preparada con asistencia de IA y pruebas automatizadas; revisión técnica independiente pendiente. El repositorio utiliza licencia MIT; conserva el archivo LICENSE creado en GitHub.
