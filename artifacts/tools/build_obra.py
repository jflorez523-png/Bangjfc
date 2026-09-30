#!/usr/bin/env python3
"""Pliego de toda la obra del Apto 901, sin valores, para pedir cotizaciones (un solo HTML con imágenes incrustadas)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_cocina as K  # noqa: E402  (regenera la página y los pliegos de carpintería y cocina)

C, B = K.C, K.B
BASE = HERE.parent
OUT = BASE / 'descarga' / 'obra-completa-apto-901.html'
fig, note, sec, shot, sample, img64, block = B.fig, B.note, C.sec, C.shot, C.sample, C.img64, K.block


# ---------------------------------------------------------------- ítems
ALT_OPC = {'la alternativa ALT-01': 'la opción OPC-03', 'la alternativa ALT-04': 'la opción OPC-07'}  # del pliego de cocina a este


def it(code, title=None, qty=None, unit=None, detail=None, bullets=None):
    """Ítem de obra; los de cocina toman por defecto el texto del pliego de cocina."""
    k = K.BYCODE.get(code, (code, '', 1, 'gl', 'Global', []))
    if bullets is None:
        bullets = list(k[5])
        for old, new in ALT_OPC.items():
            bullets = [x.replace(old, new) for x in bullets]
    return dict(code=code, title=title or k[1], qty=k[2] if qty is None else qty, unit=unit or k[3],
                detail=detail or k[4], bullets=bullets)


def carp(code, qty=1, unit='und', title=None):
    return dict(code=code, title=title or C.CARP[code][0], qty=qty, unit=unit, carp=True)


PRE = [
    it('PRE-01', 'Levantamiento y plano de obra', 1, 'gl', 'Global', [
        'Medición con láser de todo el apartamento: muros, alturas, diagonales, vanos, ductos y niveles de piso.',
        'Ubicar y fotografiar lo existente: agua, desagües, gas, tablero, tomas y puntos de TV.',
        'Entregar un plano con las medidas reales antes de comprar materiales. El carpintero hace su despiece sobre este plano.']),
    it('PRE-02', 'Protección de zonas comunes y de lo entregado', 1, 'gl', 'Global', [
        'Proteger ascensor, zonas comunes, ventanería, puerta principal y el baño auxiliar durante toda la obra.',
        'Tramitar con la administración el permiso de obra y cumplir sus horarios y rutas de escombros.']),
    it('DEM-01'),
    it('PIS-03', 'Nivelación de pisos', bullets=[
        'Revisar niveles de la placa en todo el apartamento y nivelar donde haga falta con mortero o autonivelante, antes del SPC.',
        'Tolerancia según el fabricante del SPC (en general, máximo 3 mm en 2 m).']),
]
RED = [
    it('HID-01'), it('HID-02'), it('HID-03'),
    it('HID-04', 'Redes del baño principal', 1, 'gl', 'Global', [
        'Revisar los puntos de sanitario, lavamanos y ducha que entrega Inacar y adecuarlos a los aparatos elegidos, sin moverlos.',
        'Si no hay agua caliente, indique cómo se resuelve (ducha eléctrica o calentador) y su valor por aparte, en observaciones.',
        'Prueba de presión y de desagües antes de cerrar; fotos de la tubería.']),
    it('GAS-01'),
]
ELE = [
    it('ELE-01', 'Circuitos dedicados de cocina y ropas'),
    it('ELE-02', 'Tomas de cocina y ropas'),
    it('ELE-03', 'Iluminación de cocina'),
    it('ELE-04', 'Revisión general y certificación', 1, 'gl', 'Global', [
        'Revisar tablero, acometida y circuitos existentes; marcar cada circuito en el tablero.',
        'Cumplir el RETIE en todo lo intervenido y entregar la declaración de cumplimiento.']),
    it('ELE-05', 'Luminarias del resto del apartamento', 7, 'und', '7 luminarias', [
        'Plafón LED 3.000–4.000 K en sala, hall, tres alcobas y baño principal (6), en lugar de los plafones entregados.',
        'Aplique para exterior en el balcón (1).',
        'En la sala, dos circuitos o un regulador para tener luz de ambiente.']),
    it('ELE-06', 'Tomas adicionales en alcobas', 6, 'und', '6 tomas dobles', [
        'Una toma doble a cada lado de la cama en las tres alcobas, donde no haya. En la visita, confirme cuántas faltan y ajuste la cantidad.']),
    it('ELE-07', 'Cableado de los puntos de TV', 2, 'und', '2 puntos', [
        'Inacar entrega 2 puntos de TV solo con tubería: cablearlos con coaxial y datos UTP categoría 6 hasta la caja de comunicaciones, con sus placas y una toma doble al lado.']),
    it('ELE-08', 'Placas de tomas y apagadores', '', 'und', 'Por contar', [
        'Tomas y apagadores de todo el apartamento en una misma línea de placas. Cotice el valor unitario; la cantidad se cuenta en la visita.']),
]
IMP = [
    it('IMP-01'),
    it('IMP-02', 'Impermeabilización del baño principal', 8.5, 'm²', '≈ 8,5 m²', [
        'Sistema cementicio o equivalente en todo el piso y en los muros de la ducha hasta 1,80 m, con media caña en los encuentros y subida de 30 cm en el resto del perímetro.',
        'Prueba de estanqueidad de 24 a 48 horas antes de enchapar, con acta y fotos.']),
    it('IMP-03', 'Impermeabilización del balcón', 2.0, 'm²', '≈ 2,0 m²', [
        'Piso del balcón con subida de 15 cm y sello en el encuentro con la puerta-ventana; revisar la pendiente hacia el desagüe.',
        'Prueba de estanqueidad con acta antes del enchape.']),
]
ACA = [
    it('ENC-01'), it('ENC-02'),
    it('ENC-03', 'Enchape de muros del baño principal', 14, 'm²', '≈ 14 m²', [
        'Cerámica clara 30 × 60 del piso al techo (2,40 m) en los cuatro muros.',
        'Boquilla antihongos y remates con perfil de aluminio.']),
    it('PIS-01', 'Piso SPC', 37, 'm²', '≈ 37 m²', [
        'SPC roble natural en sala-comedor, cocina, hall y las tres alcobas, con ficha técnica: marca, espesor, capa de uso de 0,5 mm o más, base acústica IXPE y garantía.',
        'No debe quedar debajo de muebles fijos: se deja libre la huella de la cocina, la península y los closets, según el despiece del carpintero. El zócalo del mueble tapa la dilatación.',
        'Cantidad medida sin desperdicio; inclúyalo en su valor unitario.']),
    it('PIS-02'),
    it('PIS-04', 'Piso cerámico del baño principal', 2.5, 'm²', '≈ 2,5 m²', [
        'Cerámica antideslizante 30 × 30 gris piedra sobre la impermeabilización, con pendiente hacia el sifón de la ducha.']),
    it('PIS-05', 'Piso cerámico del balcón', 1.5, 'm²', '≈ 1,5 m²', [
        'Cerámica antideslizante 30 × 30 para exterior sobre la impermeabilización, con guardaescoba cerámico.']),
    it('PIS-06', 'Zócalos y perfiles de transición', 40, 'ml', '≈ 40 ml', [
        'Zócalo del sistema del SPC o en MDF RH blanco en todo el perímetro con SPC.',
        'Perfiles de transición de aluminio en las puertas de baño, ropas y balcón.']),
]
PIN = [
    it('PIN-03', 'Pañete o resane de muros', '', 'm²', 'Por medir', [
        'Los muros de bloque se entregan sin pañete. Cotice por m² el pañete o el resane que haga falta antes del estuco; la cantidad se define en la visita.']),
    it('PIN-01', 'Estuco y pintura de muros', 100, 'm²', '≈ 100 m²', [
        'Estuco y pintura lavable de buena gama, color blanco cálido, en todos los muros sin enchape: alcobas, sala, hall, cocina y ropas.',
        'Detrás de muebles fijos y enchapes basta una mano de sellador. La mano final va después de la carpintería.']),
    it('PIN-02', 'Estuco y pintura de techos', 42, 'm²', '≈ 42 m²', [
        'Estuco y pintura blanca mate en todos los techos; en el baño principal, pintura antihongos.']),
    it('PIN-04', 'Balcón', 1, 'gl', 'Global', [
        'Resanes y pintura para exterior de los muros del balcón, en el color de fachada que exija la administración.',
        'Sellos de la puerta-ventana y de la baranda. No se cambia la fachada ni se cierra el balcón.']),
]
SAN = [
    it('SAN-01', 'Sanitario', 1, 'und', '1 und', [
        'Sanitario ahorrador de marca (4,8 litros o menos por descarga) con asiento de cierre lento, instalado y sellado.']),
    it('SAN-02', 'Lavamanos y grifería', 1, 'und', '1 und', [
        'Lavamanos de sobreponer o cubierta con lavamanos para el mueble flotante de 60 × 45 cm (BAN-01).',
        'Grifería monomando de marca con repuestos, sifón y acoples.']),
    it('SAN-03', 'Grifería de ducha', 1, 'und', '1 und', [
        'Mezcladora o grifería de ducha de marca con regadera; sifón de piso con rejilla inoxidable. Si no hay agua caliente, ver HID-04.']),
    it('SAN-04', 'División de ducha', 1, 'und', '1 und', [
        'Corrediza en vidrio templado de 8 mm, 2,00 m de alto, con herrajes inoxidables, a lo ancho del baño (≈ 1,08 m).']),
    it('SAN-05', 'Espejo con luz', 1, 'und', '1 und', [
        'Espejo de unos 50 × 70 cm con luz LED frontal sobre el mueble, conectado.']),
    it('SAN-06', 'Accesorios', 1, 'jgo', '1 juego', [
        'Toallero, portarrollos, gancho doble y repisa de ducha en acero inoxidable, anclados sin romper la impermeabilización.']),
]
COC = [it('EXT-01'), it('APA-01'), it('APA-02'), it('MES-01'), it('MES-02')]
CAR = [carp('COC-01', 1, 'gl'), carp('COC-02', 1, 'gl'), carp('COC-03', 1, 'gl'), carp('COC-04', 1, 'gl'),
       carp('CLO-01'), carp('CLO-02'), carp('CLO-03'), carp('BAN-01'), carp('SAL-01', 1, 'gl'),
       dict(code='PUE-01 a 04', title='Puertas interiores con marco y chapa', qty=4, unit='und', carp=True)]
ASE = [
    it('ASE-01', 'Escombros y aseo final', 1, 'gl', 'Global', [
        'Retiro periódico de escombros por las rutas y horarios de la administración.',
        'Aseo final: vidrios, pisos, enchapes y muebles por dentro.']),
    it('ENT-01', 'Pruebas, actas y garantías', 1, 'gl', 'Global', [
        'Pruebas de agua, desagües, gas y electricidad con acta; lista de pendientes corregida.',
        'Entregar fotos de redes antes de cerrar, fichas técnicas, manuales, garantías y la declaración RETIE.']),
]

# ---------------------------------------------------------------- capítulos
FIG_COC = f'''
<div class="shots2">
{shot(img64('cocina-b.jpg'), 'Render de la cocina desde la sala con la península y el mueble sobre el muro sur.', '<b>Desde la sala.</b> Península hacia la sala y mueble sobre el muro sur.')}
{shot(img64('ropas-b.jpg'), 'Render de la cocina desde la entrada con mesón, península, nevera y ropas.', '<b>Desde la entrada.</b> Mesón, península y ropas bajo su ventana.')}
</div>
<div class="figs">{fig(K.PTS_PLAN, '<b>Plano de puntos.</b> Los puntos del muro sur se dibujan sobre el muro aunque van a distintas alturas: la elevación de abajo las muestra. Agua, desagüe y gas quedan donde están hoy.', 'panel')}</div>
{K.LEG_PTS}
<div class="figs">{fig(B.KE, '<b>Muro sur visto desde la cocina.</b> Mesón a 90 cm, salpicadero hasta los altos (1,47 m) y tomas a 1,10 m. El enchape de ropas sube a 1,20 m.', 'panel')}</div>
'''
FIG_BAN = f'''
{shot(img64('bano-b.jpg'), 'Render del baño principal con mueble flotante, espejo con luz, sanitario y ducha con división de vidrio.', '<b>Baño principal.</b> Enchape claro a techo, piso antideslizante, mueble flotante con espejo y luz, y división corrediza.')}
<div class="figs">{fig(B.PLAN_BP, '<b>Planta.</b> Mueble, sanitario y ducha sobre el muro oriental; la puerta entra por el norte.', 'panel')}
{fig(B.BE, '<b>Muro oriental.</b> Mueble de 60 cm junto a la puerta, sanitario y ducha al fondo con ventana.', 'panel')}</div>
'''
CARP_INTRO = f'''
<p class="lead2">Es el mismo alcance del pliego de carpintería. Si no hace carpintería, puede subcontratarla (diga con quién) o dejar estos ítems en blanco.</p>
<div class="figs">{fig(C.TAG_PLAN, '<b>Dónde va cada mueble.</b> Norte arriba, con el balcón; la entrada es por el sur. BAN-02 es del baño auxiliar y va en las opciones.', 'panel')}</div>
{C.MAT_CARDS}
'''


def carp_body():
    it_ = lambda c: C.item(c, *C.CARP[c]).replace('COC-05', 'MES-02')  # noqa: E731
    return f'''
<h3 class="h3s">Cocina y península</h3>
<div class="figs">{fig(B.PLAN_COCINA, '<b>Planta de la cocina.</b> Mesón de 60 cm sobre el muro sur, pasillo de 1,10 m y península hacia la sala.', 'panel')}</div>
<div class="figs">{fig(B.PE, '<b>Península.</b> Hacia la sala, frente en WPC; en corte, cuerpo de 60 cm y voladizo de 30 cm; hacia la cocina, puerta, cajonero y puerta.', 'panel')}</div>
{it_('COC-01')}{it_('COC-02')}{it_('COC-03')}{it_('COC-04')}
<h3 class="h3s">Closets</h3>
{shot(img64('alcoba-b.jpg'), 'Render de la alcoba principal con el closet en roble natural junto a la ventana.', '<b>Closet de la alcoba principal (CLO-01)</b>, junto a la ventana.')}
<div class="figs panel">
  {fig(B.PLAN_AP, '<b>Alcoba principal.</b> Closet de 1,50 m.')}
  {fig(B.PLAN_A2, '<b>Alcoba 2.</b> Closet de 1,45 m.')}
  {fig(B.PLAN_A3, '<b>Alcoba 3.</b> Closet corredizo de 1,20 m.')}
</div>
<div class="figs">{fig(B.CE, '<b>Interior de CLO-01</b>, sin puertas: doble colgado, cajones, zapatero con colgado medio y maletero.', 'panel')}</div>
{C.CLO_CARD}
{it_('CLO-01')}{it_('CLO-02')}{it_('CLO-03')}
<h3 class="h3s">Baño y sala</h3>
{it_('BAN-01')}{it_('SAL-01')}
<h3 class="h3s">Puertas interiores (PUE-01 a 04)</h3>
<p class="sub">Inacar no entrega las puertas de las tres alcobas ni la del baño principal.</p>
{C.PUE}
'''


CHAPTERS = [  # (id, título, qué incluye, intro, ítems)
    ('preliminares', 'Preliminares y retiros', 'Plano de obra, protección, retiro de la cocina básica y nivelación', '', PRE),
    ('redes', 'Agua, desagüe y gas', 'Cocina, ropas y baño principal, sin mover puntos', note('', '!', '<b>No se mueven redes.</b> Lavaplatos, estufa, lavadero y aparatos del baño quedan donde Inacar deja el agua, el desagüe y el gas.'), RED),
    ('electrico', 'Electricidad e iluminación', 'Circuitos, tomas, luminarias, TV y certificación RETIE', '<p class="sub">Los puntos de la cocina están en el plano de puntos del capítulo 11.</p>', ELE),
    ('impermeabilizacion', 'Impermeabilización', 'Ropas, baño principal y balcón, con prueba de estanqueidad', '<p class="sub">Ropas, baño principal y balcón. No se enchapa sin prueba de estanqueidad y acta.</p>', IMP),
    ('pisos', 'Enchapes y pisos', 'SPC, cerámicas, enchapes y zócalos', '', ACA),
    ('pintura', 'Pañete, estuco y pintura', 'Pañete donde falte, estuco, pintura y balcón', '', PIN),
    ('bano', 'Baño principal', 'Aparatos, griferías, división, espejo y accesorios', FIG_BAN, SAN),
    ('cocina', 'Cocina y ropas', 'Campana, lavaplatos, electrodomésticos y mesones', '<p class="sub">Todo lo de la cocina menos la carpintería: los muebles van en el capítulo 12.</p>' + FIG_COC, COC),
    ('carpinteria', 'Carpintería', 'Cocina, península, closets, mueble de baño, panel de TV y puertas', CARP_INTRO, CAR),
    ('entrega', 'Aseo y entrega', 'Escombros, aseo, pruebas y garantías', '', ASE),
]


S = []
ch_rows = ''.join(f'<tr><td class="z"><a href="#{cid}">{n:02d}</a></td><td><b>{t}</b></td><td>{d}</td><td class="num">{len(its)}</td></tr>'
                  for n, (cid, t, d, _, its) in enumerate(CHAPTERS, 4))
ENTREGA = [
    ('Muros', 'En bloque y concreto a la vista, sin pañete ni pintura.'),
    ('Pisos', 'Placa de concreto, salvo el baño auxiliar.'),
    ('Ventanería', 'Ventanas corredizas en aluminio con vidrio de 5 mm; puerta-ventana del balcón en vidrio templado.'),
    ('Puertas', 'Puerta principal y puerta del baño auxiliar. Las 3 alcobas y el baño principal no traen puerta.'),
    ('Baño auxiliar', 'Terminado: piso cerámico, muros en estuco y vinilo, ducha enchapada, sanitario y griferías.'),
    ('Baño principal', 'En obra gris, con puntos de agua y desagüe.'),
    ('Cocina', 'Básica: mueble inferior, mesón de acero inoxidable de 1,82 m con lavaplatos, cubierta a gas de 4 puestos y grifería.'),
    ('Ropas', 'Lavadero de fibra de vidrio con grifería y punto de lavadora sin llave.'),
    ('Balcón', 'Baranda metálica, techo en graniplax y piso en concreto.'),
    ('Eléctrico', 'Plafones en techo y 2 puntos de TV solo con tubería.'),
]
ent_rows = ''.join(f'<tr><td class="z">{a}</td><td>{b}</td></tr>' for a, b in ENTREGA)
S.append(sec('alcance', '01 · Alcance', 'Qué se va a cotizar', f'''
<p class="lead2">Obra blanca completa del apartamento 901, Torre 1, Alto Tramonti VIS (Girón): 44,30 m² que Inacar entrega en obra gris, con 2,40 m de altura libre. Incluye pisos, pintura, electricidad, baño principal completo, cocina con península, closets, puertas y balcón. Cada trabajo tiene un código; cotice por código en el cuadro del final. Puede cotizar todo o solo algunos capítulos.</p>
<div class="tbl"><table><thead><tr><th>Cap.</th><th>Capítulo</th><th>Qué incluye</th><th class="num">Ítems</th></tr></thead><tbody>{ch_rows}</tbody></table></div>
{note('blue', 'i', '<b>Las cantidades son aproximadas</b>, tomadas del plano comercial. Confírmelas en la visita y, si cambian, corríjalas en el cuadro de cotización. Los códigos son los mismos de los pliegos de cocina y de carpintería.')}
{note('', '!', '<b>El baño auxiliar ya viene terminado</b> y no está en el total: su remodelación va en las opciones, para decidir después.')}
<h3 class="h3s">Lo que entrega Inacar</h3>
<div class="tbl"><table><thead><tr><th>Zona</th><th>Estado de entrega</th></tr></thead><tbody>{ent_rows}</tbody></table></div>
'''))

ROOMS = [
    ('Alcoba principal', '2,50 × 3,38', '8,45 m²', 'SPC', 'Closet de 1,50 m junto a la ventana; puerta'),
    ('Alcoba 2', '2,30 × 2,80', '6,44 m²', 'SPC', 'Closet de 1,45 m; puerta'),
    ('Alcoba 3', '2,00 × 2,55', '5,10 m²', 'SPC', 'Closet corredizo de 1,20 m; puerta'),
    ('Baño principal', '1,10 × 2,10', '2,31 m²', 'Cerámica', 'Baño completo; puerta'),
    ('Baño auxiliar', '1,10 × 2,10', '2,31 m²', 'Entregado', 'Solo en opciones'),
    ('Cocina y ropas', '4,05 × 2,30', '9,32 m²', 'SPC y cerámica', 'Cocina nueva con península; ropas enchapada'),
    ('Sala-comedor', '2,65 × 3,40', '9,01 m²', 'SPC', 'Panel de TV, luz de ambiente'),
    ('Balcón', '2,00 × 0,72', '1,44 m²', 'Cerámica', 'Impermeabilización, piso, sellos, luz y pintura'),
]
room_rows = ''.join(f'<tr><td class="z">{a}</td><td class="num">{b}</td><td class="num">{c}</td><td>{d}</td><td>{e}</td></tr>' for a, b, c, d, e in ROOMS)
S.append(sec('planos', '02 · Planos', 'El apartamento', f'''
{shot(img64('sala-b.jpg'), 'Render de la sala-comedor desde la cocina hacia el balcón, con la península en primer plano.', '<b>Sala-comedor</b> desde la cocina, hacia el balcón.')}
<div class="figs">{fig(B.PLAN_FULL, '<b>Planta del Apto 901.</b> Norte arriba, con el balcón. La entrada es por el sur, junto al baño auxiliar.', 'panel')}</div>
{B.LEG_PLAN}
<div class="tbl"><table><thead><tr><th>Espacio</th><th class="num">Medidas (m)</th><th class="num">Área</th><th>Piso</th><th>Qué se hace</th></tr></thead><tbody>{room_rows}</tbody></table></div>
<p class="disc">Las vistas y renders son conceptuales. La ubicación de ventanas es aproximada y los muebles sueltos son solo referencia.</p>
'''))

S.append(sec('materiales', '03 · Materiales', 'Paleta y acabados', f'''
<p class="sub">Roble natural, blanco cálido y gris piedra suave. Traiga muestras físicas y fichas técnicas de lo que ofrece.</p>
<div class="mgrid2">{''.join(sample(sid, el, name) for el, _, sid, name, _ in B.MATROWS)}</div>
<p class="disc">Muestras generadas por computador: los colores son aproximados.</p>
'''))

for n, (cid, title, desc, intro, its) in enumerate(CHAPTERS, 4):
    body = intro
    if cid == 'carpinteria':
        body += carp_body()
    else:
        body += ''.join(block(i['code'], i['title'], i['detail'], i['bullets']) for i in its)
    S.append(sec(cid, f'{n:02d} · Capítulo · {len(its)} ítems', title, body))

N = 4 + len(CHAPTERS)
S.append(sec('orden', f'{N:02d} · Orden de obra', 'De la visita a la entrega', '''
<ol class="steps2">
  <li><b>Levantamiento y plano de obra</b> (PRE-01); aprobación de la distribución final.</li>
  <li><b>Protección y retiros:</b> zonas comunes y cocina básica.</li>
  <li><b>Redes:</b> agua, desagües, gas y electricidad; fotos de todo antes de cerrar.</li>
  <li><b>Impermeabilización</b> de ropas, baño principal y balcón, con prueba de estanqueidad y acta.</li>
  <li><b>Pañete, estuco, nivelación y enchapes</b> de baño, ropas y balcón.</li>
  <li><b>Primera mano de pintura.</b></li>
  <li><b>SPC y zócalos,</b> dejando libre la huella de los muebles fijos según el despiece.</li>
  <li><b>Carpintería:</b> cocina, península, closets, mueble de baño, panel de TV y puertas.</li>
  <li><b>Mesones y salpicadero</b>, con plantilla tomada sobre los muebles instalados.</li>
  <li><b>Aparatos, luminarias y pintura final.</b></li>
  <li><b>Pruebas y entrega</b> (ENT-01) con lista de pendientes.</li>
</ol>
'''))

OPC = [
    ('OPC-01', 'Baño auxiliar completo igual al principal, retirando lo entregado', 'Baño auxiliar'),
    ('OPC-02', 'Baño auxiliar solo con mueble flotante (BAN-02), espejo con luz y división en vidrio', 'Baño auxiliar'),
    ('OPC-03', 'Salida de la campana al exterior con ducto, si la administración la autoriza', 'EXT-01'),
    ('OPC-04', 'Mesones en superficie compacta (cuarzo o sinterizado) en lugar de granito', 'MES-01 y MES-02'),
    ('OPC-05', 'Muebles altos y torre hasta el techo (90 cm en vez de 75)', 'COC-02 y COC-03'),
    ('OPC-06', 'Suministro de cubierta a gas, horno empotrado y campana de gama media, con marca y referencia', 'APA-02'),
    ('OPC-07', 'Lavadero compacto nuevo en lugar de reinstalar el entregado', 'HID-03'),
    ('OPC-08', 'Autonivelante en todo el apartamento en lugar de nivelación localizada', 'PIS-03'),
    ('OPC-09', 'Cajillo en drywall con luz indirecta en la sala, solo si la altura lo permite', 'Sala'),
    ('OPC-10', 'Tira LED con sensor de movimiento dentro de los tres closets', 'CLO-01 a 03'),
    ('OPC-11', 'Puertas interiores en roble natural, para que combinen con los closets', 'PUE-01 a 04'),
]
opc_rows = ''.join(f'<tr><td class="z">{c}</td><td>{t}</td><td>{w}</td></tr>' for c, t, w in OPC)
S.append(sec('opciones', f'{N + 1:02d} · Opciones', 'Cotizar por separado', f'''
<p class="sub">No van en el total. Dé un valor para cada una, para decidir después.</p>
<div class="tbl"><table><thead><tr><th>Código</th><th>Opción</th><th>Afecta a</th></tr></thead><tbody>{opc_rows}</tbody></table></div>
'''))

S.append(sec('condiciones', f'{N + 2:02d} · Condiciones', 'Cómo presentar la cotización', '''
<div class="grid2">
  <div class="card"><h3>La cotización debe traer</h3><ul>
    <li>Valor unitario por código y total por capítulo. AIU e IVA por aparte, si los cobra.</li>
    <li>Marca y referencia de SPC, cerámicas, impermeabilizante, pinturas, aparatos sanitarios, griferías, luminarias, tableros y herrajes.</li>
    <li>Qué capítulos no cotiza y qué subcontrata (carpintería, mesones, vidrio), con quién.</li>
    <li>Cronograma por fases, tiempo total y fecha posible de inicio.</li>
    <li>Garantía por capítulo, en años; en impermeabilización, aparte.</li>
    <li>Fotos de tres obras terminadas y validez de la oferta.</li>
  </ul></div>
  <div class="card"><h3>Reglas de la obra</h3><ul>
    <li>Visita y medición antes de la cotización definitiva.</li>
    <li>Electricidad según el RETIE, con declaración de cumplimiento; gas por instalador certificado.</li>
    <li>No enchapar sin prueba de estanqueidad; no cerrar redes sin fotos y pruebas; no fabricar carpintería sin despiece aprobado.</li>
    <li>Personal con seguridad social y ARL al día, y un maestro o residente responsable con teléfono.</li>
    <li>Pagos contra avance verificable: anticipo moderado, pagos por hitos y 10% retenido hasta las pruebas y la corrección de pendientes.</li>
    <li>Cualquier adicional se aprueba por escrito antes de hacerlo.</li>
  </ul></div>
</div>
<div class="grid2">
  <div class="card"><h3>No incluye</h3><ul>
    <li>Mobiliario suelto, bancos, cortinas y persianas.</li>
    <li>Nevera, lavadora, cubierta, horno, campana y lámparas colgantes: los compra el propietario y aquí solo se instalan (salvo OPC-06).</li>
    <li>Aire acondicionado, domótica y cerraduras inteligentes.</li>
    <li>Cambios de fachada, cierre del balcón y cambios estructurales.</li>
    <li>Baño auxiliar, salvo que se elija una opción.</li>
  </ul></div>
  <div class="card"><h3>Se coordina con</h3><ul>
    <li><b>Administración:</b> permiso de obra, horarios, ascensor, escombros y salida de la campana si se pide.</li>
    <li><b>Propietario:</b> elección de electrodomésticos antes del despiece de cocina (horno y campana definen medidas y voltaje).</li>
  </ul></div>
</div>
'''))

# ---------------------------------------------------------------- cuadro de cotización
ALL = []
qrows = ''
for n, (cid, title, _, _, its) in enumerate(CHAPTERS, 4):
    qrows += f'<tr class="ch"><td colspan="6">{n:02d} · {title}</td></tr>'
    for i in its:
        k = len(ALL)
        ALL.append(i)
        q = i['qty']
        qv = f' value="{K.qn(q)}"' if q != '' else ' placeholder="medir"'
        qrows += (f'<tr data-ch="{n}" data-i="{k}"><td class="z">{i["code"]}</td><td>{i["title"]}</td>'
                  f'<td class="num"><input class="qty" id="q-{k}"{qv} inputmode="decimal" aria-label="Cantidad {i["code"]}"></td><td>{i["unit"]}</td>'
                  f'<td class="num"><input class="money" id="u-{k}" inputmode="numeric" aria-label="Valor unitario {i["code"]}" placeholder="$"></td>'
                  f'<td class="num tot" id="t-{k}">—</td></tr>')
    qrows += f'<tr class="chs"><td colspan="5">Subtotal {n:02d}</td><td class="num" data-chs="{n}">—</td></tr>'
orows = ''.join(
    f'<tr><td class="z">{c}</td><td>{t}</td><td class="num"><input class="money alt" id="o-{i}" inputmode="numeric" aria-label="Valor {c}" placeholder="$"></td></tr>'
    for i, (c, t, w) in enumerate(OPC))
FIELDS = [('Proponente o empresa', 'f-nom'), ('NIT o cédula', 'f-nit'), ('Teléfono', 'f-tel'), ('Correo', 'f-mail'),
          ('Capítulos que cotiza', 'f-cap'), ('Maestro o residente', 'f-res'), ('Tiempo total de obra', 'f-tie'), ('Fecha posible de inicio', 'f-ini'),
          ('Garantía de obra', 'f-gar'), ('Garantía de impermeabilización', 'f-gim'), ('Forma de pago', 'f-pago'), ('Validez de la oferta', 'f-val')]
ftags = ''.join(f'<label class="fld" for="{i}"><span>{n}</span><input id="{i}" type="text"></label>' for n, i in FIELDS)
S.append(sec('cotizacion', f'{N + 3:02d} · Cuadro de cotización', 'Para llenar y devolver', f'''
<p class="sub">Escriba los valores en pesos. Si no cotiza un ítem o un capítulo, déjelo en blanco. Los totales se calculan solos. Al terminar, use el botón para imprimir o guardar como PDF y envíe ese PDF.</p>
<div class="fields">{ftags}</div>
<div class="tbl qform"><table><thead><tr><th>Código</th><th>Trabajo</th><th class="num">Cant.</th><th>Und.</th><th class="num">Valor unitario</th><th class="num">Total</th></tr></thead>
<tbody>{qrows}</tbody>
<tfoot>
<tr><td colspan="5">Costo directo</td><td class="num" id="dir">—</td></tr>
<tr><td colspan="4">AIU (si lo cobra por aparte)</td><td class="num"><input class="money" id="aiu" inputmode="numeric" aria-label="Valor del AIU" placeholder="$"></td><td class="num" id="aiut">—</td></tr>
<tr><td colspan="4">IVA</td><td class="num"><input class="money" id="iva" inputmode="numeric" aria-label="Valor del IVA" placeholder="$"></td><td class="num" id="ivat">—</td></tr>
<tr class="big"><td colspan="5">Total</td><td class="num" id="tot">—</td></tr>
</tfoot></table></div>
<h3 class="h3s">Opciones (no suman al total)</h3>
<div class="tbl qform"><table><thead><tr><th>Código</th><th>Opción</th><th class="num">Valor</th></tr></thead><tbody>{orows}</tbody></table></div>
<label class="fld wide" for="f-obs"><span>Observaciones</span><textarea id="f-obs" rows="4"></textarea></label>
<div class="actions noprint"><button type="button" id="print">Imprimir o guardar como PDF</button></div>
'''))

toc = ''.join(f'<a href="#{i}">{t}</a>' for i, t in
              [('alcance', 'Alcance'), ('planos', 'Planos'), ('materiales', 'Materiales')]
              + [(c[0], c[1]) for c in CHAPTERS]
              + [('orden', 'Orden'), ('opciones', 'Opciones'), ('condiciones', 'Condiciones'), ('cotizacion', 'Cotización')])

EXTRA = K.EXTRA + r'''
.qform tr.ch td{background:var(--accent-soft);font-weight:700;font-size:.86rem}
.qform tr.chs td{font-weight:600;color:var(--muted);font-size:.84rem}
.qform tr.chs td.num{color:var(--ink)}
.qform input.qty::placeholder{font-size:.78rem}
'''

JS = r'''
(function(){
  function num(v){var d=(v||'').replace(/\D/g,'');return d?parseInt(d,10):0}
  function dec(v){var s=(v||'').replace(/\./g,'').replace(',','.').replace(/[^0-9.]/g,'');var n=parseFloat(s);return isNaN(n)?0:n}
  function fmt(n){n=Math.round(n);return n?'$'+n.toString().replace(/\B(?=(\d{3})+(?!\d))/g,'.'):'—'}
  function val(id){return num(document.getElementById(id).value)}
  function calc(){
    var chs={},dir=0;
    document.querySelectorAll('tr[data-ch]').forEach(function(tr){
      var i=tr.dataset.i,t=val('u-'+i)*dec(document.getElementById('q-'+i).value);
      document.getElementById('t-'+i).textContent=fmt(t);
      chs[tr.dataset.ch]=(chs[tr.dataset.ch]||0)+t;dir+=t;
    });
    document.querySelectorAll('[data-chs]').forEach(function(td){td.textContent=fmt(chs[td.dataset.chs]||0)});
    var aiu=val('aiu'),iva=val('iva');
    document.getElementById('dir').textContent=fmt(dir);
    document.getElementById('aiut').textContent=fmt(aiu);
    document.getElementById('ivat').textContent=fmt(iva);
    document.getElementById('tot').textContent=fmt(dir+aiu+iva);
  }
  document.querySelectorAll('input.money').forEach(function(inp){
    inp.addEventListener('input',function(){var n=num(inp.value);inp.value=n?n.toString().replace(/\B(?=(\d{3})+(?!\d))/g,'.'):'';calc();});
  });
  document.querySelectorAll('input.qty').forEach(function(inp){inp.addEventListener('input',calc)});
  var b=document.getElementById('print');if(b)b.addEventListener('click',function(){window.print()});
  calc();
})();
'''

page = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Obra completa Apto 901</title>
<meta name="description" content="Pliego de toda la obra blanca del Apto 901, Torre 1, Alto Tramonti (Girón), para solicitar cotizaciones: preliminares, redes, electricidad, impermeabilización, pisos, pintura, baño, cocina, carpintería y entrega.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap">
<style>:root{{color-scheme:light}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}
{C.PAGE_CSS}
{EXTRA}</style>
</head>
<body>
<header><div class="wrap top">
  <div class="eyebrow">Solicitud de cotización · Obra completa</div>
  <h1>Obra completa Apto 901</h1>
  <p class="lede">Torre 1, Alto Tramonti VIS, Girón (Santander). Pliego con todo lo que hay que hacer para pasar de obra gris a obra blanca, para cotizar por ítem.</p>
  <dl class="ficha">
    <div><dt>Área</dt><dd>44,30 m²<small>Obra gris, 2,40 m libres</small></dd></div>
    <div><dt>Pisos</dt><dd>37 + 6,5 m²<small>SPC y cerámica</small></dd></div>
    <div><dt>Baño</dt><dd>1 completo<small>El auxiliar va en opciones</small></dd></div>
    <div><dt>Cocina</dt><dd>2,03 m<small>Con península hacia la sala</small></dd></div>
    <div><dt>Closets</dt><dd>4,15 m<small>Lineales, en tres alcobas</small></dd></div>
    <div><dt>Puertas</dt><dd>4<small>Tres alcobas y baño principal</small></dd></div>
  </dl>
  <nav class="toc noprint" aria-label="Contenido">{toc}</nav>
</div></header>
<main>{''.join(S)}</main>
<footer><div class="wrap">
  <p class="disc">Pliego elaborado a partir del plano comercial del Apto 901 y la propuesta de acabados (Opción B con península). Las vistas y renders son conceptuales; las medidas y cantidades se confirman en obra.</p>
</div></footer>
<script>{JS}</script>
</body>
</html>
'''
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(page, encoding='utf-8')
print(OUT, f'{OUT.stat().st_size / 1024 / 1024:.2f} MB', len(ALL), 'ítems')
