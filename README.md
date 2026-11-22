# Pisos Madrid

Proyecto de referencia del Módulo 10 (Casos de Uso de Data Analytics e IA, Máster en Business Analytics e IA de Inesdi, noviembre 2026). Cada sesión añade una pieza: la app con datos, el modelo que estima el precio, el servidor MCP y el agente de "chollos del día".

## Datos

Pisos en venta en Madrid capital (2018) de idealista18, bajo la Open Database License 1.0. Detalle, columnas y atribución en [data/README.md](data/README.md).

Para regenerarlos:

```bash
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements-datos.txt
.venv/bin/python scripts/preparar_datos.py
```
