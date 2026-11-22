# Pisos Madrid

Proyecto de referencia del Módulo 10 (Casos de Uso de Data Analytics e IA, Máster en Business Analytics e IA de Inesdi, noviembre y diciembre de 2026).

Es el proyecto que el docente construye en directo en cada sesión, pieza a pieza. **No es un proyecto para copiar:** cada alumno aplica el mismo patrón a su propio proyecto, con sus datos y algo que predecir. Quien no tenga idea elige una de las temáticas de ejemplo de la Sesión 1, no este proyecto.

La pregunta que responde: "¿Está bien de precio este piso de Madrid? Avísame cuando aparezca un chollo."

## Estructura

| Carpeta | Qué hay | Sesión |
|---|---|---|
| `web/` | La página pública, publicada en Vercel (Root Directory `web`) | S1 |
| `data/` | Los datos y su licencia | S1 |
| `scripts/` | Scripts de datos | S1 |
| `api/` | El modelo que estima el precio, servido como API | S3 (llegará) |
| `mcp/` | El servidor MCP para hablar con los datos y el modelo | S4 (llegará) |
| `agente/` | El agente de "chollos del día" | S5 (llegará) |

`AGENTS.md` explica el proyecto al agente de programación (`CLAUDE.md` lo importa para Claude Code).

## Datos

Pisos en venta en Madrid capital (2018) de idealista18, bajo la Open Database License 1.0. Detalle, columnas y atribución en [data/README.md](data/README.md).

Datos: idealista18 (Rey-Blanco, Arbués, López y Páez, 2024), https://github.com/paezha/idealista18. Contiene información de la base de datos idealista18, disponible bajo la Open Database License (ODbL) 1.0. Ni idealista ni los autores avalan este proyecto.

Para regenerarlos:

```bash
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements-datos.txt
.venv/bin/python scripts/preparar_datos.py
```

## Licencias

- **Código:** MIT ([LICENSE](LICENSE)).
- **Datos** (`data/`): ODbL 1.0 ([data/LICENSE](data/LICENSE)). Los CSV son una base de datos derivada y se distribuyen bajo la misma licencia.
