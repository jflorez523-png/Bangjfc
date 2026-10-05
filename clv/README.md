# Capturador de cuotas de cierre (CLV)

Vigila tus picks de Betano, BetPlay y Betsson durante el día. La última cuota
antes de que empiece cada partido queda como **cuota de cierre**, y con ella el
script calcula el CLV en `clv_cierre.csv`, listo para tu sistema.

Corre en un **celular Android (Termux)** o en un **PC que se quede encendido**.
Tiene que correr en Colombia, porque las casas bloquean las conexiones de fuera.

## 1. Tus picks

Una fila por pick. Sirve un CSV o un Google Sheet; ver `picks_ejemplo.csv`.

| columna | qué va | ejemplo |
|---|---|---|
| `link` | link del partido en la casa (copiado del navegador) | `https://betplay.com.co/apuestas#event/1021234567` |
| `mercado` | nombre del mercado | `1X2`, `Total de goles`, `Ambos marcan` |
| `seleccion` | lo que apostaste | `Millonarios`, `1`, `Empate`, `Más de 2.5`, `Sí` |
| `cuota` | cuota tomada | `2,30` |
| `inicio` | *(opcional)* hora del partido, si el script no la detecta | `19:30` |

El script entiende sinónimos: `Over`/`Más de`, `Local`/`1`, `Empate`/`X`,
`BTTS`/`Ambos marcan`. Si un pick no se encuentra o es ambiguo, el CSV de salida
muestra los mercados disponibles para que lo corrijas.

**Desde el celular:** la forma más cómoda es un Google Sheet con esas columnas.
Ve a *Archivo → Compartir → Publicar en la web*, elige la hoja y el formato CSV,
y usa ese link con `--picks`. El script lo relee cada minuto, así que puedes
agregar picks durante el día. Ojo: cualquiera que tenga ese link puede ver la hoja.

## 2. Instalar

**Android (Termux)**
1. Instala Termux desde F-Droid. La versión de Play Store está desactualizada.
2. En Termux:
   ```
   pkg update && pkg install python
   termux-setup-storage
   ```
3. Copia la carpeta `clv` al celular, por ejemplo a `Download/clv`, y entra:
   `cd ~/storage/shared/Download/clv`
4. En Ajustes de Android, quita la optimización de batería para Termux.
   Si no, Android lo cierra en segundo plano.

**PC (Windows)**
1. Instala Python 3 desde python.org y marca "Add to PATH".
2. Opcional, pero recomendado: `pip install curl_cffi`. Ayuda a no ser bloqueado.
3. Opcional, para Betsson o si una casa bloquea: `pip install playwright` y luego `playwright install chromium`.

## 3. Primera vez: diagnóstico (una vez por casa)

El script no se ha probado contra las casas reales, porque desde fuera de Colombia
no es posible. Antes del primer día, corre el diagnóstico con un partido de cada casa:

```
python clv_capturador.py diagnosticar "LINK_DE_BETPLAY"
python clv_capturador.py diagnosticar "LINK_DE_BETANO"
python clv_capturador.py diagnosticar "LINK_DE_BETSSON"
```

Si sale `OK` con la lista de mercados y cuotas, esa casa funciona. Si sale
`fallo`, envía lo que imprimió y la carpeta `diagnostico/` para ajustar el lector.

## 4. Uso diario

```
python clv_capturador.py validar      # justo después de cargar los picks: confirma que encuentra cada uno
python clv_capturador.py vigilar      # déjalo corriendo todo el día
```

En Termux, corre `termux-wake-lock` antes de `vigilar`.

Con Google Sheet y la salida en una carpeta que llegue a tu PC:

```
python clv_capturador.py vigilar --picks "URL_CSV_DEL_SHEET" --salida ~/storage/shared/Download/clv_cierre.csv
```

Cada cuánto consulta un pick: cada hora cuando faltan más de 3 h para el partido,
cada 20 min cuando falta más de 1 h, cada 5 min cuando faltan más de 20 min, y cada
2 min en los últimos 20 min. Al empezar el partido deja de consultar y fija el cierre.

## 5. Salida: `clv_cierre.csv`

| columna | significado |
|---|---|
| `cuota_cierre` | última cuota capturada antes del inicio (se prefieren las abiertas, no las suspendidas) |
| `min_antes_inicio` | cuántos minutos antes del inicio se tomó esa cuota |
| `clv_pct` | `(cuota_tomada / cuota_cierre − 1) × 100` |
| `clv_sin_margen_pct` | `(cuota_tomada × prob_justa_cierre − 1) × 100`. Quita el margen de la casa usando las otras opciones del mismo mercado |
| `margen_cierre_pct` | margen de la casa en ese mercado al cierre |
| `estado` | `pendiente`, `cerrado`, `cierre_viejo` (la última captura fue más de 30 min antes del inicio) o `sin_captura` |

`capturas.csv` guarda todas las capturas, por si quieres ver cómo se movió la línea.

Para Excel en español, cambia al inicio del script `SEPARADOR = ";"` y `DECIMAL = ","`.

## Limitaciones

- Las casas no tienen API oficial. El script lee los datos de sus propias páginas,
  y si cambian el formato hay que ajustarlo. Para eso está `diagnosticar`.
- Betsson probablemente necesita el modo navegador (Playwright), que solo corre en PC, no en Termux.
- Las condiciones de uso de las casas suelen prohibir el acceso automatizado. El
  script solo lee cuotas públicas, sin iniciar sesión y con pocas consultas.
