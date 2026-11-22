# Datos de "Pisos Madrid"

**Datos: idealista18 (Rey-Blanco, Arbués, López y Páez, 2024), https://github.com/paezha/idealista18. Contiene información de la base de datos idealista18, disponible bajo la Open Database License (ODbL) 1.0. Precios y coordenadas anonimizados por sus autores; limpieza y asignación de barrio y distrito propias. Precios de 2018.**

Cita: Rey-Blanco, D., Arbués, P., López, F. y Páez, A. (2024). *A geo-referenced micro-data set of real estate listings for Spain's three largest cities*. Environment and Planning B, 51(6), 1369-1379. https://doi.org/10.1177/23998083241242844

## Ficheros

| Fichero | Qué es |
|---|---|
| `pisos.csv` | 75.455 pisos en venta en Madrid capital (2018): 44.191 de histórico (2018-T1 a T3) y 31.264 en cola (2018-T4) |
| `pisos_muestra_5000.csv` | 5.000 pisos del histórico, para importar en directo desde el panel de Supabase |
| `LICENSE` | Texto de la ODbL 1.0. **Estos CSV son una base de datos derivada y se distribuyen bajo la misma licencia.** |

Se generan con `scripts/preparar_datos.py` a partir del commit `e9ef806` del repositorio original. El script descarga los ficheros originales, asigna barrio y distrito por coordenadas, quita duplicados (un anuncio por `id_anuncio`) y valores extremos (más de 10 habitaciones, más de 6 baños o más de 3 M€).

## Columnas

| Columna | Tipo | Nota |
|---|---|---|
| `id_anuncio` | texto | único |
| `trimestre` | texto | `2018-T1` a `2018-T4` |
| `precio` | entero | euros de 2018, precio de oferta, anonimizado (±2,5 %) |
| `precio_m2` | entero | euros por m² construido |
| `superficie_m2` | entero | construida |
| `habitaciones`, `banos` | entero | |
| `planta` | entero | 0 = bajo, -1 = sótano; vacío en un 4 % |
| `exterior` | booleano | vacío en un 7 % |
| `estado` | texto | `obra_nueva`, `a_reformar` o `buen_estado` |
| `anio_construccion` | entero | del Catastro |
| `ascensor`, `terraza`, `aire_acondicionado`, `garaje`, `trastero`, `piscina`, `portero`, `jardin`, `duplex`, `estudio`, `ultima_planta` | booleano | |
| `dist_centro_km`, `dist_metro_km` | decimal | kilómetros |
| `latitud`, `longitud` | decimal | desplazadas 30 a 60 m por anonimato, siempre dentro de su barrio |
| `barrio` | texto | 135 zonas de idealista (basadas en los barrios oficiales, retocadas) |
| `distrito` | texto | los 21 distritos oficiales |
| `publicado_en` | fecha y hora | **simulada**, ver abajo |

## `publicado_en`: cómo "aparecen" pisos nuevos cada día

Los datos son de 2018 y no cambian, así que la novedad se simula:

- **Histórico (2018-T1 a T3):** fecha al azar en los 30 días anteriores al 24/11/2026. Ya está publicado.
- **Cola (2018-T4):** 50 pisos por día, a las 07:00 (hora de Madrid), desde el 24/11/2026.

La app, el MCP y el agente leen solo lo publicado (`where publicado_en <= now()`), así que cada mañana aparecen 50 pisos sin que nada se ejecute.

**Regla para el modelo:** entrenar **solo con el histórico**. Si el modelo ve la cola, ya conoce esos precios y los "chollos" son falsos (fuga de datos).

## Avisos

- Precios **de oferta de 2018**, no de venta ni actuales. Decirlo en la app.
- Ni idealista ni los autores avalan este proyecto.
