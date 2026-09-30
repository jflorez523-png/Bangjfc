#!/usr/bin/env python3
"""Pliego de carpintería del Apto 901 para pedir cotizaciones (un solo HTML con imágenes incrustadas)."""
import base64
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_obra_blanca_901 as B  # noqa: E402  (genera también la página principal)

BASE = HERE.parent
OUT = BASE / 'descarga' / 'carpinteria-apto-901.html'
esc = B.esc


def img64(name):
    return 'data:image/jpeg;base64,' + base64.b64encode((BASE / 'img' / name).read_bytes()).decode('ascii')


# ---------------------------------------------------------------- plano de ubicación con códigos
TAGS = [
    ('COC-01', 150, 205), ('COC-02', 290, 150), ('COC-03', 385, 34), ('COC-04', 190, 34),
    ('CLO-01', 455, -309), ('CLO-02', -173, -135), ('CLO-03', -168, 60),
    ('BAN-01', 490, 55), ('BAN-02', -55, 55), ('SAL-01', 24, -230),
    ('PUE-01', 300, -55), ('PUE-02', -55, -128), ('PUE-03', -175, -50), ('PUE-04', 455, 22),
]


def tag_plan():
    d = B.D('tg', (-385, -470, 960, 790), 0.84, 10.5)
    B.plan_content(d, 'full')
    fsz = d.fs * 0.74
    for code, x, y in TAGS:
        w = len(code) * fsz * 0.66 + 10
        h = fsz * 1.55
        d.a(f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h / 2:.1f}" class="tag-r"/>')
        d.a(f'<text x="{x}" y="{y + fsz * 0.36:.1f}" font-size="{fsz:.2f}" text-anchor="middle" class="tag-t">{code}</text>')
    return d.svg('Plano del Apto 901 con la ubicación de cada mueble a cotizar: cocina, península, closets, muebles de baño, panel de TV y puertas interiores.', cls='dw crop')


TAG_PLAN = tag_plan()


# ---------------------------------------------------------------- piezas
def sec(id_, kicker, title, body, sub=''):
    s = f'<p class="sub">{sub}</p>' if sub else ''
    return f'<section class="sec" id="{id_}"><div class="wrap"><div class="kicker">{kicker}</div><h2>{title}</h2>{s}{body}</div></section>'


def mods(rows):
    body = ''.join(f'<tr><td class="z">{a}</td><td class="num">{b}</td><td>{c}</td></tr>' for a, b, c in rows)
    return (f'<div class="tbl"><table><thead><tr><th>Módulo</th><th class="num">Ancho × alto × fondo (cm)</th><th>Qué lleva</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


def item(code, title, where, rows, notes=''):
    n = f'<ul class="bul">{"".join(f"<li>{x}</li>" for x in notes)}</ul>' if notes else ''
    return (f'<div class="item" id="{code.lower()}"><div class="ihead"><span class="code">{code}</span><h3>{title}</h3>'
            f'<span class="where">{where}</span></div>{mods(rows)}{n}</div>')


def shot(src, alt, cap):
    return (f'<figure class="shot"><div class="shot-img"><img src="{src}" width="1600" height="1000" alt="{esc(alt)}" loading="lazy" decoding="async">'
            f'<span class="shot-tag">Render ilustrativo</span></div><figcaption>{cap}</figcaption></figure>')


def sample(sid, el, name):
    return (f'<figure class="mcard"><img src="{img64(f"m-{sid}.jpg")}" width="640" height="480" alt="Muestra: {esc(name)}" loading="lazy">'
            f'<figcaption><span class="mel">{el}</span><b>{name}</b></figcaption></figure>')


fig = B.fig
PAGE_CSS = B.page.split('<style>', 1)[1].split('</style>', 1)[0]
note = B.note

# ---------------------------------------------------------------- contenido
ITEMS = [
    ('COC-01', 'Mueble bajo del muro sur', 'Cocina · 2,03 m lineales', 1, 'gl'),
    ('COC-02', 'Muebles altos del muro sur', 'Cocina y ropas · 2,63 m lineales', 1, 'gl'),
    ('COC-03', 'Frente norte: módulo bajo y torre', 'Cocina · 0,70 m más hueco de nevera', 1, 'gl'),
    ('COC-04', 'Península con frente en WPC', 'Cocina hacia la sala · 1,50 × 0,90 m', 1, 'gl'),
    ('COC-05', 'Mesones (si los suministran)', 'Cocina y península · ≈2,7 m²', 1, 'gl'),
    ('CLO-01', 'Closet alcoba principal', '1,50 × 2,40 × 0,60 m', 1, 'und'),
    ('CLO-02', 'Closet alcoba 2', '1,45 × 2,40 × 0,60 m', 1, 'und'),
    ('CLO-03', 'Closet alcoba 3, corredizo', '1,20 × 2,40 × 0,60 m', 1, 'und'),
    ('BAN-01', 'Mueble flotante baño principal', '0,60 × 0,38 × 0,45 m', 1, 'und'),
    ('BAN-02', 'Mueble flotante baño auxiliar', '0,60 × 0,38 × 0,45 m', 1, 'und'),
    ('SAL-01', 'Panel de TV y repisa flotante', 'Sala · 1,20 m', 1, 'gl'),
    ('PUE-01 a 04', 'Puertas interiores con marco y chapa', '3 alcobas y baño principal', 4, 'und'),
]
ALTS = [
    ('ALT-01', 'Muebles altos y torre hasta el techo (90 cm en vez de 75)', 'COC-02 y COC-03'),
    ('ALT-02', 'Alacena sobre la nevera con panel lateral', 'COC-03'),
    ('ALT-03', 'Espejo de cuerpo entero en la puerta central del closet', 'CLO-01'),
    ('ALT-04', 'Tira LED con sensor de movimiento dentro de los tres closets', 'CLO-01 a 03'),
    ('ALT-05', 'Tapa de mesón sobre la lavadora (solo si es de carga frontal)', 'COC-02'),
    ('ALT-06', 'Puertas corredizas en espejo en lugar de melamina', 'CLO-03'),
    ('ALT-07', 'Cajones con correderas telescópicas de bolas en lugar de caja metálica (para comparar)', 'COC-01 y COC-04'),
]

resumen_rows = ''.join(f'<tr><td class="z"><a href="#{c.split()[0].lower()}">{c}</a></td><td>{t}</td><td>{w}</td></tr>' for c, t, w, q, u in ITEMS)

MAT_CARDS = '''<div class="grid2">
  <div class="card"><h3>Tableros y cantos</h3><ul>
    <li><b>Tablero:</b> aglomerado o MDP RH (resistente a la humedad) de 18 mm en cuerpos, frentes y entrepaños. Indique marca (por ejemplo Tablemac/Pelikano, Duratex o Masisa).</li>
    <li><b>Fondos:</b> 9 mm RH en cocina y baños; mínimo 6 mm en closets.</li>
    <li><b>Cantos:</b> PVC de 2 mm en frentes y bordes vistos; 0,45 mm en bordes ocultos. Cola PUR en el mueble del lavaplatos y en los de baño.</li>
    <li><b>Textura:</b> supermate o antihuella en frentes, si la marca la tiene.</li>
  </ul></div>
  <div class="card"><h3>Herrajes</h3><ul>
    <li><b>Bisagras:</b> cierre suave de marca con garantía (Blum, Hettich, Grass o equivalente). Dos por puerta hasta 1 m, tres hasta 2 m.</li>
    <li><b>Cajones de cocina y península:</b> sistema de caja metálica con cierre suave y extensión total, mínimo 40 kg en el cajón de ollas.</li>
    <li><b>Cajones de closet:</b> correderas ocultas con cierre suave y extensión total.</li>
    <li><b>Sin manijas:</b> perfil de aluminio tipo gola en bajos; en altos, puertas 2 cm más largas por debajo para abrir.</li>
    <li><b>Patas y zócalo:</b> patas plásticas regulables y zócalo de aluminio removible.</li>
    <li>Indique marca y referencia de cada herraje en la cotización.</li>
  </ul></div>
</div>'''
CLO_CARD = '''<div class="card"><h3>Para los tres closets</h3><ul>
  <li>Fondo total de 60 cm, del piso al techo (≈2,40 m, confirmar), sobre zócalo de 8 cm. Melamina RH roble natural.</li>
  <li>Puertas en dos alturas: hoja de 2,00 m y puerta de maletero arriba (≈38 cm), para evitar que se pandeen. Si cotiza una sola hoja piso-techo, use 4 bisagras y enderezador de aluminio.</li>
  <li>Perfil de aluminio vertical como tirador; rejillas de ventilación en las puertas de maletero.</li>
  <li>Barras ovaladas de aluminio con soportes metálicos; entrepaños regulables.</li>
</ul></div>'''

S = []
S.append(sec('alcance', '01 · Alcance', 'Qué se va a cotizar', f'''
<p class="lead2">Carpintería completa del apartamento 901, Torre 1, Alto Tramonti (Girón), que hoy está en obra gris con 2,40 m de altura libre. Incluye cocina con península, tres closets, dos muebles de baño, un panel de TV y cuatro puertas interiores. Cada mueble tiene un código; úselo en la cotización.</p>
<div class="tbl"><table><thead><tr><th>Código</th><th>Mueble</th><th>Dónde y cuánto</th></tr></thead><tbody>{resumen_rows}</tbody></table></div>
{note('blue', 'i', '<b>Cotización preliminar.</b> Las medidas vienen del plano comercial y son aproximadas. Cotice con ellas y confirme con visita y medición láser antes de la cotización definitiva. No fabrique sin plano de despiece aprobado.')}
'''))

S.append(sec('plano', '02 · Ubicación', 'Dónde va cada mueble', f'''
<div class="figs">{fig(TAG_PLAN, '<b>Planta del Apto 901.</b> Norte arriba, con el balcón; la entrada es por el sur. Las etiquetas naranjas son los códigos de este pliego.', 'panel')}</div>
'''))

S.append(sec('materiales', '03 · Materiales y herrajes', 'Lo que aplica a todos los muebles', f'''
{MAT_CARDS}
<h3 class="h3s">Colores</h3>
<div class="mgrid2">
{sample('upper-b', 'Muebles altos', 'Melamina RH blanco cálido')}
{sample('lower-b', 'Bajos, península y torre', 'Melamina RH gris piedra suave')}
{sample('clo-b', 'Closets, baños y panel TV', 'Melamina RH roble natural')}
{sample('wpc-b', 'Frente de la península', 'WPC acanalado roble natural')}
{sample('ctr-b', 'Mesones (COC-05)', 'Granito de primera o superficie compacta')}
{sample('metal-b', 'Herrajes', 'Inoxidable y perfil de aluminio')}
</div>
<p class="disc">Muestras generadas por computador: los colores son aproximados. Traiga muestras físicas de los colores de su catálogo más cercanos.</p>
'''))

# (título, dónde, módulos, notas)
CARP = {
    'COC-01': ('Mueble bajo del muro sur', 'Entre la puerta de entrada y ropas · alto total 90 cm con mesón, fondo 60 cm', [
    ('Lavaplatos', '60 × 78 × 58', '2 puertas; bandeja antiderrame de aluminio; caneca de reciclaje extraíble de 2 compartimentos; fondo RH 9 mm; perforaciones para desagüe y llaves con el sifón accesible.'),
    ('Cajonero', '60 × 78 × 58', '3 cajones de caja metálica (≈16, 26 y 36 cm); organizador de cubiertos en el primero; el inferior para ollas, carga reforzada.'),
    ('Estufa y horno', '60 × 78 × 58', 'Hueco para horno empotrado de 60 cm con ventilación, según el modelo que se compre; cajón inferior de 16 cm; soporte para la cubierta a gas de 4 puestos.'),
    ('Remate', '23 × 78 × 58', 'Especiero o botellero extraíble de 20 cm con herraje de marca.'),
    ('Zócalo', '203 × 10', 'Aluminio removible sobre patas regulables.'),
], ['El lavaplatos y la estufa quedan donde Inacar deja el desagüe y el gas: no se mueven redes.', 'Espacios de 60 cm para la lavadora y de 50 cm para el lavadero bajo la ventana de ropas (no llevan mueble bajo).']),
    'COC-02': ('Muebles altos del muro sur', 'Desde el lavaplatos hasta la lavadora · a 1,47 m del piso, fondo 33 cm, alto 75 cm', [
    ('Sobre lavaplatos', '60 × 75 × 33', '2 puertas; escurreplatos interno con bandeja recogegotas.'),
    ('Sobre cajonero', '60 × 75 × 33', '2 puertas y 1 entrepaño regulable.'),
    ('Sobre estufa', '60 × 42 × 33', 'Alacena corta sobre la campana. Respetar la distancia a la cubierta que pida el fabricante de la campana (suministro aparte).'),
    ('Sobre remate y lavadora', '83 × 75 × 33', '2 puertas y 1 entrepaño; guarda detergentes de ropas.'),
    ('Iluminación', '263 lineales', 'Perfil de aluminio para tira LED bajo los altos, con paso de cable oculto. El electricista instala la luz.'),
]),
    'COC-03': ('Frente norte: módulo bajo y torre', 'Contra el muro de la alcoba principal, frente al mesón', [
    ('Módulo bajo', '30 × 78 × 58', 'Bandejero vertical con divisores para tablas y bandejas; mesón encima, continuo con la península.'),
    ('Hueco de nevera', '70 de ancho', 'Sin mueble. Dejar 5 cm de ventilación a los lados y arriba; confirmar con el modelo de nevera.'),
    ('Torre', '40 × 222 × 60', '3 puertas. Arriba despensa con entrepaños regulables; abajo zona de aseo de 1,20 m de alto con ganchos para escoba y trapero.'),
]),
    'COC-04': ('Península con frente en WPC', 'Límite entre cocina y sala, unida al módulo bajo de COC-03', [
    ('Cuerpo', '150 × 78 × 60', 'Sobre zócalo retrocedido de 10 cm. Hacia la cocina: puerta de 50, cajonero de 50 con 3 cajones de caja metálica y puerta de 50.'),
    ('Frente y costado', '150 + 60 × 78', 'Panel WPC acanalado de interior, color roble natural, con fijación oculta, hacia la sala y en el costado occidental.'),
    ('Voladizo', '100 × 30', 'Solo en el tramo de los bancos, para no estorbar la puerta de la alcoba principal (lo da el mesón, COC-05).'),
    ('Toma', '—', 'Perforación para toma doble en el costado hacia la cocina (la instala el electricista).'),
], ['Anclar el cuerpo al piso y al módulo bajo de COC-03.', 'Si prefiere más espacio para las rodillas: cuerpo de 55 cm y voladizo de 35 cm, con el mismo total de 90 cm. Indique si cambia el precio.', 'Los bancos no se incluyen.']),
    'COC-05': ('Mesones (si los suministran)', 'Si no los suministran, indíquelo: se cotizan con marmolería', [
    ('Muro sur', '203 × 63,5 × 2', 'Granito de primera o superficie compacta con ficha técnica; recortes para lavaplatos y cubierta; borde pulido y sellado; silicona neutra antihongos.'),
    ('Península y módulo', '100 × 94 + 80 × 64', 'Una pieza en L: 100 × 94 cm en el tramo con voladizo y 80 × 64 cm en el resto de la península y el módulo de 30.'),
    ('Salpicadero', '—', 'No es de carpintería: cerámica 30 × 60 que coloca el enchapador.'),
]),
    'CLO-01': ('Closet alcoba principal', 'Muro norte, junto a la ventana · 150 × 240 × 60', [
    ('Cuerpo 1', '50', 'Doble colgado con barras a 1,96 y 1,06 m.'),
    ('Cuerpo 2', '50', '4 cajones con correderas ocultas y 2 entrepaños arriba.'),
    ('Cuerpo 3', '50', 'Zapatero con 3 entrepaños abajo y colgado medio arriba.'),
    ('Maletero', '150 × 35', 'Corrido arriba, con puertas y rejillas.'),
    ('Puertas', '3 × 50', 'Batientes en dos alturas.'),
]),
    'CLO-02': ('Closet alcoba 2', 'Muro sur, junto a la puerta · 145 × 240 × 60', [
    ('Cuerpo 1', '48', 'Colgado largo.'),
    ('Cuerpo 2', '48', '3 cajones y entrepaños.'),
    ('Cuerpo 3', '48', 'Doble colgado.'),
    ('Maletero', '145 × 35', 'Corrido arriba.'),
    ('Puertas', '3 × 48', 'Batientes en dos alturas.'),
]),
    'CLO-03': ('Closet alcoba 3, corredizo', 'Muro oriental · 120 × 240 × 60', [
    ('Cuerpo 1', '60', 'Colgado con entrepaño arriba.'),
    ('Cuerpo 2', '60', '2 cajones y entrepaños.'),
    ('Maletero', '120 × 35', 'Con puertas abatibles o corredizas.'),
    ('Puertas', '2 × 60', 'Corredizas con marco de aluminio y panel de melamina de 9 mm, riel superior e inferior.'),
], ['Con cama de 0,90 m quedan 50 cm de paso frente al closet; por eso las puertas son corredizas.']),
    'BAN-01': ('Mueble flotante baño principal', 'Muro oriental, junto a la puerta', [
    ('Mueble', '60 × 38 × 45', 'Melamina RH roble natural con cantos en cola PUR; 1 puerta o cajón con recorte para el sifón; anclaje oculto al muro, a 47 cm del piso.'),
], ['El lavamanos o la cubierta con lavamanos se suministra aparte; confirme medidas antes de fabricar.']),
    'BAN-02': ('Mueble flotante baño auxiliar', 'Igual a BAN-01', [
    ('Mueble', '60 × 38 × 45', 'Igual a BAN-01. El baño auxiliar ya viene terminado: cotícelo aparte porque puede que no se haga.'),
]),
    'SAL-01': ('Panel de TV y repisa flotante', 'Muro occidental de la sala, frente al sofá', [
    ('Panel', '120 × 100 × 3', 'Melamina roble natural, fijo al muro entre 0,95 y 1,95 m, con paso de cables oculto.'),
    ('Repisa', '110 × 18 × 32', 'Flotante, a 36 cm del piso, con soportes ocultos.'),
], ['El soporte del TV va anclado al muro, no al panel.']),
}

COC = f'''
<div class="shots2">
{shot(img64('cocina-b.jpg'), 'Render de la cocina desde la sala con la península, dos bancos y el mueble sobre el muro sur.', '<b>Desde la sala.</b> Península con frente en WPC y, al fondo, el mueble del muro sur.')}
{shot(img64('ropas-b.jpg'), 'Render de la cocina desde la entrada con el mesón, la península, la nevera, la torre y ropas.', '<b>Desde la entrada.</b> Mesón a la derecha, península a la izquierda y torre al fondo.')}
</div>
<div class="figs">{fig(B.PLAN_COCINA, '<b>Planta de la cocina.</b> Mesón de 60 cm sobre el muro sur, pasillo de 1,10 m y península hacia la sala. La nevera y la lavadora son del propietario.', 'panel')}</div>
<div class="figs">{fig(B.KE, '<b>Muro sur visto desde la cocina.</b> COC-01 abajo y COC-02 arriba. Lavaplatos y estufa van donde están el desagüe y el gas actuales.', 'panel')}</div>
<div class="figs">{fig(B.PE, '<b>Península (COC-04).</b> Hacia la sala, frente en WPC; en corte, cuerpo de 60 cm y voladizo de 30 cm a 90 cm de altura; hacia la cocina, puerta, cajonero y puerta.', 'panel')}</div>
{item('COC-01', *CARP['COC-01'])}
{item('COC-02', *CARP['COC-02'])}
{item('COC-03', *CARP['COC-03'])}
{item('COC-04', *CARP['COC-04'])}
{item('COC-05', *CARP['COC-05'])}
'''
S.append(sec('cocina', '04 · Cocina y península', 'COC-01 a COC-05', COC,
             'La cocina se abre a la sala. El mueble del muro sur mide 2,03 m entre la puerta de entrada y ropas; al frente van el módulo bajo, la nevera y la torre, y hacia la sala la península.'))

CLO = f'''
{shot(img64('alcoba-b.jpg'), 'Render de la alcoba principal con el closet en roble natural junto a la ventana.', '<b>Closet de la alcoba principal (CLO-01)</b>, junto a la ventana.')}
<div class="figs panel">
  {fig(B.PLAN_AP, '<b>Alcoba principal.</b> Closet de 1,50 m junto a la ventana norte.')}
  {fig(B.PLAN_A2, '<b>Alcoba 2.</b> Closet de 1,45 m sobre el muro sur.')}
  {fig(B.PLAN_A3, '<b>Alcoba 3.</b> Closet corredizo de 1,20 m.')}
</div>
<div class="figs">{fig(B.CE, '<b>Interior de CLO-01</b>, sin puertas: doble colgado, cajones, zapatero con colgado medio y maletero con rejillas.', 'panel')}</div>
{CLO_CARD}
{item('CLO-01', *CARP['CLO-01'])}
{item('CLO-02', *CARP['CLO-02'])}
{item('CLO-03', *CARP['CLO-03'])}
'''
S.append(sec('closets', '05 · Closets', 'CLO-01 a CLO-03', CLO,
             'En el plano real caben unos 4,15 m lineales entre las tres alcobas.'))

OTROS = f'''
<div class="figs">{fig(B.BE, '<b>Muro de aparatos de los baños.</b> El mueble flotante de 60 cm va junto a la puerta, bajo el espejo.', 'panel')}</div>
{item('BAN-01', *CARP['BAN-01'])}
{item('BAN-02', *CARP['BAN-02'])}
{item('SAL-01', *CARP['SAL-01'])}
'''
S.append(sec('otros', '06 · Baños y sala', 'BAN-01, BAN-02 y SAL-01', OTROS))

PUE = f'''
<div class="tbl"><table><thead><tr><th>Código</th><th>Dónde</th><th class="num">Vano aprox. (m)</th><th>Chapa</th></tr></thead><tbody>
<tr><td class="z">PUE-01</td><td>Alcoba principal</td><td class="num">0,80 × 2,10</td><td>Manija con llave</td></tr>
<tr><td class="z">PUE-02</td><td>Alcoba 2</td><td class="num">0,80 × 2,10</td><td>Manija con llave</td></tr>
<tr><td class="z">PUE-03</td><td>Alcoba 3</td><td class="num">0,80 × 2,10</td><td>Manija con llave</td></tr>
<tr><td class="z">PUE-04</td><td>Baño principal</td><td class="num">0,70 × 2,10</td><td>De baño con seguro</td></tr>
</tbody></table></div>
<ul class="bul">
  <li>Puerta entamborada con marco nuevo y chambrana por las dos caras, tres bisagras de acero, chapa y tope.</li>
  <li>Acabado igual al de la puerta principal que entrega la constructora (Duratex Lana). Si ofrece roble natural para que combine con los closets, cotícelo como opción.</li>
  <li>Medir los vanos en obra: los del plano son aproximados.</li>
</ul>
'''
S.append(sec('puertas', '07 · Puertas interiores', 'PUE-01 a PUE-04', PUE,
             'La constructora no entrega las puertas de las tres alcobas ni la del baño principal.'))

alt_rows = ''.join(f'<tr><td class="z">{c}</td><td>{t}</td><td>{w}</td></tr>' for c, t, w in ALTS)
S.append(sec('alternativas', '08 · Alternativas', 'Cotizar por separado', f'''
<p class="sub">No van en el total. Dé un valor para cada una, para decidir después.</p>
<div class="tbl"><table><thead><tr><th>Código</th><th>Alternativa</th><th>Afecta a</th></tr></thead><tbody>{alt_rows}</tbody></table></div>
'''))

S.append(sec('condiciones', '09 · Condiciones', 'Cómo presentar la cotización', '''
<div class="grid2">
  <div class="card"><h3>La cotización debe traer</h3><ul>
    <li>Valor por código (COC-01, CLO-01…) y total, con IVA aparte.</li>
    <li>Materiales, herrajes (marca y referencia), transporte, instalación y retiro de escombros separados o claramente incluidos.</li>
    <li>Marca del tablero y de los herrajes que ofrece.</li>
    <li>Tiempo de fabricación, tiempo de instalación y fecha posible de inicio.</li>
    <li>Garantía de muebles y de herrajes, en años.</li>
    <li>Fotos de tres trabajos terminados y validez de la oferta.</li>
  </ul></div>
  <div class="card"><h3>Reglas de la obra</h3><ul>
    <li>Visita y medición láser antes de la cotización definitiva.</li>
    <li>Plano de despiece aprobado antes de cortar: módulos, anchos, fondos, apertura de puertas y electrodomésticos.</li>
    <li>La carpintería se instala después de pisos, pintura y enchapes.</li>
    <li>Pagos contra avance verificable: anticipo moderado, pagos por hitos y 10% retenido hasta la entrega y la corrección de pendientes.</li>
    <li>Cualquier adicional se aprueba por escrito antes de hacerlo.</li>
    <li>Proteger zonas comunes, retirar escombros y entregar limpio.</li>
  </ul></div>
</div>
<div class="grid2">
  <div class="card"><h3>No incluye</h3><ul>
    <li>Electrodomésticos, campana, lavaplatos, griferías, lavamanos y lavadero.</li>
    <li>Instalaciones eléctricas, hidráulicas y de gas.</li>
    <li>Salpicadero y enchapes.</li>
    <li>Mesones, si no los suministra (COC-05).</li>
    <li>Bancos y mobiliario suelto.</li>
  </ul></div>
  <div class="card"><h3>Se coordina con</h3><ul>
    <li><b>Electricista:</b> tomas del mesón y la península, LED bajo altos y en closets.</li>
    <li><b>Plomero:</b> lavaplatos, lavamanos y sifones accesibles.</li>
    <li><b>Gasista:</b> conexión de la cubierta de la estufa.</li>
    <li><b>Marmolería:</b> mesones y recortes, si no los suministra.</li>
  </ul></div>
</div>
'''))

# ---------------------------------------------------------------- cuadro de cotización
qrows = ''.join(
    f'<tr><td class="z">{c}</td><td>{t}</td><td class="num">{q}</td><td>{u}</td>'
    f'<td class="num"><input class="money" data-q="{q}" id="u-{i}" inputmode="numeric" aria-label="Valor unitario {c}" placeholder="$"></td>'
    f'<td class="num tot" id="t-{i}">—</td></tr>'
    for i, (c, t, w, q, u) in enumerate(ITEMS))
arows = ''.join(
    f'<tr><td class="z">{c}</td><td>{t}</td><td class="num"><input class="money alt" id="a-{i}" inputmode="numeric" aria-label="Valor {c}" placeholder="$"></td></tr>'
    for i, (c, t, w) in enumerate(ALTS))
FIELDS = [('Proponente o empresa', 'f-nom'), ('NIT o cédula', 'f-nit'), ('Teléfono', 'f-tel'), ('Correo', 'f-mail'),
          ('Marca de tablero', 'f-tab'), ('Marca de herrajes', 'f-her'), ('Tiempo de fabricación', 'f-fab'), ('Tiempo de instalación', 'f-ins'),
          ('Garantía de muebles', 'f-gm'), ('Garantía de herrajes', 'f-gh'), ('Forma de pago', 'f-pago'), ('Validez de la oferta', 'f-val')]
ftags = ''.join(f'<label class="fld" for="{i}"><span>{n}</span><input id="{i}" type="text"></label>' for n, i in FIELDS)
S.append(sec('cotizacion', '10 · Cuadro de cotización', 'Para llenar y devolver', f'''
<p class="sub">Escriba los valores en pesos. Los totales se calculan solos. Al terminar, use el botón para imprimir o guardar como PDF y envíe ese PDF.</p>
<div class="fields">{ftags}</div>
<div class="tbl qform"><table><thead><tr><th>Código</th><th>Mueble</th><th class="num">Cant.</th><th>Und.</th><th class="num">Valor unitario</th><th class="num">Total</th></tr></thead>
<tbody>{qrows}</tbody>
<tfoot>
<tr><td colspan="5">Subtotal</td><td class="num" id="sub">—</td></tr>
<tr><td colspan="4">IVA</td><td class="num"><input class="money" id="iva" inputmode="numeric" aria-label="Valor del IVA" placeholder="$"></td><td class="num" id="ivat">—</td></tr>
<tr class="big"><td colspan="5">Total</td><td class="num" id="tot">—</td></tr>
</tfoot></table></div>
<h3 class="h3s">Alternativas (no suman al total)</h3>
<div class="tbl qform"><table><thead><tr><th>Código</th><th>Alternativa</th><th class="num">Valor</th></tr></thead><tbody>{arows}</tbody></table></div>
<label class="fld wide" for="f-obs"><span>Observaciones</span><textarea id="f-obs" rows="4"></textarea></label>
<div class="actions noprint"><button type="button" id="print">Imprimir o guardar como PDF</button></div>
'''))

toc = ''.join(f'<a href="#{i}">{t}</a>' for i, t in [('alcance', 'Alcance'), ('plano', 'Ubicación'), ('materiales', 'Materiales'), ('cocina', 'Cocina'),
                                                     ('closets', 'Closets'), ('otros', 'Baños y sala'), ('puertas', 'Puertas'),
                                                     ('alternativas', 'Alternativas'), ('condiciones', 'Condiciones'), ('cotizacion', 'Cotización')])

EXTRA = r'''
.lead2{font-size:1rem;max-width:70ch;margin:14px 0 0}
.toc{display:flex;flex-wrap:wrap;gap:6px 8px;margin-top:18px}
.toc a{font:600 .8rem/1 var(--f-body);color:var(--ink);text-decoration:none;border:1px solid var(--line-strong);background:var(--card);padding:8px 11px;border-radius:999px}
.toc a:hover{border-color:var(--accent);color:var(--accent)}
.sec{padding-block:30px 36px;border-top:1px solid var(--line)}
.item{margin-top:26px}
.ihead{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 12px;margin-bottom:4px}
.ihead h3{margin:0;font-size:1.1rem}
.code{font-family:var(--f-mono);font-weight:600;font-size:.78rem;color:var(--on-s);background:var(--accent);padding:4px 9px;border-radius:999px}
.where{font-size:.84rem;color:var(--muted)}
.bul{margin:10px 0 0;padding-left:18px;font-size:.9rem}
.bul li{margin:4px 0}
.h3s{margin:24px 0 0}
.tbl td a{color:var(--accent);font-weight:600}
.tag-r{fill:var(--accent);stroke:var(--card);stroke-width:1.5}
.tag-t{fill:var(--on-s);font-family:var(--f-mono);font-weight:600}
.fields{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px 14px;margin-top:18px}
.fld{display:flex;flex-direction:column;gap:4px;font-size:.78rem;color:var(--muted);font-weight:600}
.fld.wide{margin-top:18px}
.fld input,.fld textarea,.qform input{font:500 .9rem/1.3 var(--f-body);color:var(--ink);background:var(--paper);border:1px solid var(--line-strong);border-radius:8px;padding:8px 10px;width:100%}
.qform input{text-align:right;font-family:var(--f-mono);max-width:170px}
.qform td{vertical-align:middle}
.qform .tot,#sub,#ivat,#tot{font-weight:600}
.qform tfoot td{border-top:1px solid var(--line-strong)}
.qform tr.big td{background:var(--accent-soft)}
.actions{margin-top:20px}
.actions button{appearance:none;border:0;background:var(--accent);color:var(--on-s);font:600 .95rem/1 var(--f-body);padding:13px 18px;border-radius:10px;cursor:pointer}
@media print{
  :root{--paper:#fff;--card:#fff;--ink:#111;--muted:#444;--line:#ccc;--line-strong:#999;color-scheme:light}
  body{background:#fff}
  .noprint,.toc{display:none!important}
  .panel,.card,.shot-img,.mcard{box-shadow:none!important}
  .sec{break-inside:auto}
  .item,.figs,.shot,.card,tr{break-inside:avoid}
  .scroll{overflow:visible}
  input,textarea{border:none!important;background:none!important;padding:0!important}
}
'''

JS = r'''
(function(){
  function num(v){var d=(v||'').replace(/\D/g,'');return d?parseInt(d,10):0}
  function fmt(n){return n?'$'+n.toString().replace(/\B(?=(\d{3})+(?!\d))/g,'.'):'—'}
  function calc(){
    var sub=0;
    document.querySelectorAll('input.money[data-q]').forEach(function(inp){
      var i=inp.id.slice(2),t=num(inp.value)*parseInt(inp.dataset.q,10);
      document.getElementById('t-'+i).textContent=fmt(t);sub+=t;
    });
    var iva=num(document.getElementById('iva').value);
    document.getElementById('sub').textContent=fmt(sub);
    document.getElementById('ivat').textContent=fmt(iva);
    document.getElementById('tot').textContent=fmt(sub+iva);
  }
  document.querySelectorAll('input.money').forEach(function(inp){
    inp.addEventListener('input',function(){var n=num(inp.value);inp.value=n?n.toString().replace(/\B(?=(\d{3})+(?!\d))/g,'.'):'';calc();});
  });
  var b=document.getElementById('print');if(b)b.addEventListener('click',function(){window.print()});
  calc();
})();
'''

page = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Carpintería Apto 901</title>
<meta name="description" content="Pliego de carpintería del Apto 901, Torre 1, Alto Tramonti (Girón) para solicitar cotizaciones: cocina con península, closets, muebles de baño, panel de TV y puertas.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap">
<style>:root{{color-scheme:light}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}
{PAGE_CSS}
{EXTRA}</style>
</head>
<body>
<header><div class="wrap top">
  <div class="eyebrow">Solicitud de cotización · Carpintería</div>
  <h1>Carpintería Apto 901</h1>
  <p class="lede">Torre 1, Alto Tramonti VIS, Girón (Santander). Pliego con todo lo que se quiere fabricar e instalar, para cotizar por mueble.</p>
  <dl class="ficha">
    <div><dt>Estado</dt><dd>Obra gris<small>Altura libre ≈ 2,40 m</small></dd></div>
    <div><dt>Cocina</dt><dd>2,03 + 2,63 m<small>Bajos + altos, torre y península</small></dd></div>
    <div><dt>Península</dt><dd>1,50 × 0,90 m<small>Frente en WPC acanalado</small></dd></div>
    <div><dt>Closets</dt><dd>4,15 m lineales<small>3 alcobas, piso a techo</small></dd></div>
    <div><dt>Otros</dt><dd>2 + 1 + 4<small>Muebles de baño, panel TV, puertas</small></dd></div>
  </dl>
  <nav class="toc noprint" aria-label="Contenido">{toc}</nav>
</div></header>
<main>{''.join(S)}</main>
<footer><div class="wrap">
  <p class="disc">Pliego elaborado a partir del plano comercial del Apto 901 y la propuesta de acabados (Opción B con península). Las vistas y renders son conceptuales; las medidas se confirman en obra antes de fabricar.</p>
</div></footer>
<script>{JS}</script>
</body>
</html>
'''
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(page, encoding='utf-8')
print(OUT, f'{OUT.stat().st_size / 1024 / 1024:.2f} MB')
