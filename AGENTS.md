# Pisos Madrid

Proyecto de referencia del Módulo 10. La pregunta: "¿Está bien de precio este piso de Madrid? Avísame cuando aparezca un chollo."

## Datos
- `data/pisos.csv`: 75.455 pisos en venta en Madrid capital en 2018 (idealista18, licencia ODbL 1.0). Columnas y atribución en `data/README.md`.
- Histórico: trimestres 2018-T1 a 2018-T3 (44.191 anuncios). Cola: 2018-T4, que se "publica" a 50 pisos por día desde el 24/11/2026.
- Para cualquier cifra y para entrenar modelos, usa solo el histórico (`trimestre` distinto de `2018-T4`).
- Lo que queremos predecir: el precio (`precio`).

## Estructura
- `web/`: la página pública, publicada en Vercel con Root Directory `web`. Por ahora, HTML estático.
- `scripts/`: scripts de datos.
- Vendrán: `api/` (modelo, S3), `mcp/` (servidor MCP, S4) y `agente/` (S5).

## Reglas para el agente
- Habla en español.
- Las cifras se calculan con código, nunca de memoria. Guarda el script en `scripts/` y enséñame el resultado antes de usarlo.
- Pasos pequeños: dime el plan antes de crear o cambiar archivos.
- Ninguna clave ni contraseña en el código.
- Toda página que muestre datos lleva el pie de atribución de `data/README.md`.
- En `web/`, sin frameworks por ahora: un archivo HTML con el CSS dentro.
