# Motor de reels de Me Dejó en Visto

Cada reel es un HTML de 1080x1920 que define sus escenas con atributos `data-in` y `data-out` (segundos) y un efecto `data-fx`
(`up`, `down`, `pop`, `stamp`, `left`, `right`, `bubble-in`, `bubble-out`, `type`, `cut`, `fade`). `common.js` expone `render(t)`;
`render.py` lo captura cuadro a cuadro a 30 fps con Playwright y `audio.py` sintetiza una pista original (sin derechos de terceros).

    ./make.sh halloween 24 musicbox "whoosh:2.9,pop:3.2,boom:17"

Ejemplos incluidos: halloween (historia de miedo), tipos (cortes al ritmo), mito (cuenta regresiva y sello),
frases (chat con hojas de otoño), avion (celular en primera persona), tutorial (exportar el chat).
Reglas de marca: degradado #c2185b a #4a148c, fuente Inter, marca "✓✓ ME DEJÓ EN VISTO" arriba, texto clave entre y=300 y y=1450
(abajo y a la derecha lo tapan los botones de Instagram y TikTok), nunca el logo ni el verde de WhatsApp, pareja siempre ficticia.
Revisa fotogramas con `python3 render.py archivo.html carpeta keys 1.5,5,10` antes de renderizar completo.
Sube el mp4 a social/ y prográmalo en Metricool con la URL de GitHub Pages.
