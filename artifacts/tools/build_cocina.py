#!/usr/bin/env python3
"""Pliego de cocina del Apto 901 sin carpintería (obra, redes, acabados, aparatos y mesones), para pedir cotizaciones."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_carpinteria as C  # noqa: E402  (regenera la página y el pliego de carpintería)

B = C.B
BASE = HERE.parent
OUT = BASE / 'descarga' / 'cocina-apto-901.html'
esc, fig, note, sec, shot, sample, img64 = B.esc, B.fig, B.note, C.sec, C.shot, C.sample, C.img64


# ---------------------------------------------------------------- plano de puntos
PTS = {  # tipo: (letra, clase)
    'agua': ('A', 'p-agua'), 'desague': ('D', 'p-des'), 'gas': ('G', 'p-gas'),
    'toma': ('T', 'p-toma'), 'luz': ('L', 'p-luz'), 'apag': ('S', 'p-apag'),
}
POINTS = [  # sobre el muro sur (y = 238) los puntos van a distintas alturas; ver la elevación
    ('toma', 100, 238), ('agua', 116, 238), ('desague', 134, 238), ('toma', 165, 238), ('toma', 200, 238),
    ('gas', 228, 238), ('toma', 246, 238), ('toma', 264, 238), ('toma', 285, 238),
    ('agua', 305, 238), ('desague', 321, 238), ('toma', 337, 238), ('agua', 372, 238), ('desague', 390, 238),
    ('toma', 330, -7), ('toma', 245, 60), ('luz', 190, 115), ('luz', 350, 115), ('luz', 140, 18), ('luz', 190, 18),
    ('apag', -8, 122),
]


def points_plan():
    d = B.D('pp', (-45, -110, 495, 400), 1.3, 10.5)
    B.plan_content(d, 'crop')
    d.a('<path d="M92 199H355" class="p-led"/>')
    r = d.fs * 0.62
    for kind, x, y in POINTS:
        letter, cls = PTS[kind]
        d.a(f'<g class="pt {cls}"><circle cx="{x}" cy="{y}" r="{r:.1f}"/>'
            f'<text x="{x}" y="{y + r * 0.42:.1f}" font-size="{r * 1.25:.2f}" text-anchor="middle">{letter}</text></g>')
    return d.svg('Plano de puntos de la cocina: agua, desagües y gas sobre el muro sur, tomas sobre el salpicadero, en la península y la nevera, luces del techo y de la barra, y apagadores junto a la entrada.', cls='dw crop')


PTS_PLAN = points_plan()


def dot(cls, letter):
    return f'<svg class="dotk" viewBox="0 0 20 20" aria-hidden="true"><g class="pt {cls}"><circle cx="10" cy="10" r="9"/><text x="10" y="14" font-size="11" text-anchor="middle">{letter}</text></g></svg>'


LEG_PTS = ('<div class="legend">'
           + f'<span class="key">{dot("p-agua", "A")}Agua</span><span class="key">{dot("p-des", "D")}Desagüe</span>'
           + f'<span class="key">{dot("p-gas", "G")}Gas</span><span class="key">{dot("p-toma", "T")}Toma</span>'
           + f'<span class="key">{dot("p-luz", "L")}Luz de techo</span><span class="key">{dot("p-apag", "S")}Apagadores (3)</span>'
           + '<span class="key"><span class="ledk"></span>Tira LED</span></div>')


# ---------------------------------------------------------------- ítems
def block(code, title, qty, bullets):
    lis = ''.join(f'<li>{b}</li>' for b in bullets)
    return (f'<div class="item" id="{code.lower()}"><div class="ihead"><span class="code">{code}</span><h3>{title}</h3>'
            f'<span class="where">{qty}</span></div><ul class="bul">{lis}</ul></div>')


# (código, título corto, cantidad, unidad, detalle de cantidad, viñetas)
ITEMS = [
    ('DEM-01', 'Retiro de la cocina básica entregada', 1, 'gl', 'Global', [
        'Desmontar el mueble inferior, el mesón de acero inoxidable de 1,82 m, el lavaplatos, la cubierta a gas y la grifería que entrega Inacar.',
        'Entregar las piezas limpias al propietario; no se botan.',
        'Taponar provisionalmente agua, desagüe y gas mientras dura la obra.']),
    ('PIS-03', 'Nivelación del piso', 1, 'gl', 'Global', [
        'Revisar niveles de la placa en cocina y ropas y nivelar donde haga falta con mortero o autonivelante.',
        'Tolerancia para SPC según el fabricante (en general, máximo 3 mm en 2 m).']),
    ('HID-01', 'Punto del lavaplatos', 1, 'und', '1 punto', [
        'Revisar y adecuar agua y desagüe al nuevo mueble, sin mover el punto de lugar.',
        'Llaves de paso bajo el mesón y desagüe con sifón accesible.',
        'Prueba de presión y de desagüe antes de cerrar; fotos de la tubería.']),
    ('HID-02', 'Punto de la lavadora', 1, 'und', '1 punto', [
        'Llave de paso para la lavadora (hoy solo está el punto) y desagüe con sifón a la altura que pida la máquina.']),
    ('HID-03', 'Lavadero compacto', 1, 'und', '1 und', [
        'Instalar el lavadero bajo la ventana de ropas con su grifería y sifón.',
        'Cotizar reinstalando el lavadero de fibra entregado; el cambio por uno nuevo va en la alternativa ALT-04.']),
    ('GAS-01', 'Punto de gas de la cubierta', 1, 'und', '1 punto', [
        'Revisar y adecuar el punto existente para la cubierta de 4 puestos (y el horno, si es a gas).',
        'Conexión con manguera o tubería certificada, llave de corte accesible y prueba de hermeticidad.',
        'Hecho por instalador certificado, con constancia de la prueba.']),
    ('ELE-01', 'Circuitos dedicados', 4, 'und', '4 circuitos', [
        'Horno, nevera, lavadora y pequeños electrodomésticos del mesón, cada uno desde el tablero con su protección.',
        'Revisar el tablero y la acometida; si no hay espacio o capacidad, indicarlo en la cotización.',
        'Cumplir el RETIE y entregar la declaración de cumplimiento.']),
    ('ELE-02', 'Tomas', 9, 'und', '9 tomas dobles', [
        '4 sobre el salpicadero a 1,10 m, 1 en la península hacia la cocina, 1 para la nevera, 1 para la lavadora, 1 para la campana y 1 para el horno (120 o 220 V según el modelo que se compre).',
        'Protección contra falla a tierra (GFCI) en la toma junto al lavaplatos y en la de la lavadora.',
        'Placas del mismo modelo en toda la cocina.']),
    ('ELE-03', 'Iluminación y apagadores', 1, 'gl', 'Global', [
        'Dos plafones LED de techo, 3.000–4.000 K: uno en la cocina y otro en ropas.',
        'Tira LED 3.000 K de 2,63 m bajo los muebles altos, con driver oculto; el carpintero deja el perfil de aluminio.',
        'Instalar dos lámparas colgantes sobre la península en un circuito propio (las compra el propietario).',
        'Tres apagadores junto a la entrada (techo, LED y colgantes); ubicación exacta en la visita. Ropas puede llevar su propio apagador.']),
    ('EXT-01', 'Instalación de la campana', 1, 'gl', 'Global', [
        'Campana de 60 cm sobre la cubierta, a la distancia que pida su fabricante (la suministra el propietario).',
        'Cotizar con recirculación y filtros reemplazables. La salida al exterior va en la alternativa ALT-01, solo si la administración la autoriza.']),
    ('IMP-01', 'Impermeabilización de ropas', 3.0, 'm²', '≈ 3,0 m²', [
        'Sistema cementicio o equivalente en el piso de ropas (≈ 1,10 × 2,30 m), con media caña y subida de 15 cm en los muros.',
        'Prueba de estanqueidad de 24 a 48 horas antes de enchapar, con acta y fotos.']),
    ('ENC-01', 'Enchape de ropas', 2.0, 'm²', '≈ 2,0 m²', [
        'Cerámica clara 30 × 60 a 1,20 m de alto detrás del lavadero y la lavadora, con retorno en el muro oriental.',
        'Boquilla antihongos y remates con perfil de aluminio.']),
    ('ENC-02', 'Salpicadero', 1.2, 'm²', '≈ 1,2 m²', [
        'Porcelanato gran formato 60 × 120 rectificado, blanco con veta muy suave, mate o satinado, en horizontal entre el mesón y los muebles altos (2,03 × 0,57 m).',
        'Pegante flexible para gran formato con doble encolado y junta de 2 mm o menos con boquilla antihongos.',
        'Se coloca después del mesón; cortes limpios para las tomas y perfil de aluminio en los bordes.']),
    ('PIS-01', 'Piso SPC de la cocina', 6.8, 'm²', '≈ 6,8 m²', [
        'SPC roble natural con ficha técnica: marca, espesor, capa de uso de 0,5 mm o más, base acústica IXPE y garantía.',
        'No debe quedar aprisionado bajo muebles fijos: se deja sin SPC la huella del mueble del muro sur, el módulo, la torre y la península, según el plano de despiece del carpintero. El zócalo del mueble tapa la dilatación.',
        'Continúa en la sala: cotice por m² para poder extenderlo sin juntas en el límite.']),
    ('PIS-02', 'Piso cerámico de ropas', 2.5, 'm²', '≈ 2,5 m²', [
        'Cerámica antideslizante 30 × 30 gris piedra sobre la impermeabilización.',
        'Perfil de transición de aluminio con el SPC.']),
    ('PIN-01', 'Estuco y pintura de muros', 10, 'm²', '≈ 10 m²', [
        'Muros visibles de cocina y ropas: remates, estuco y pintura lavable de buena gama, color blanco cálido.',
        'Detrás de muebles y enchapes basta una mano de sellador.']),
    ('PIN-02', 'Estuco y pintura de techo', 9.3, 'm²', '≈ 9,3 m²', [
        'Techo de cocina y ropas: estuco y pintura blanca mate.']),
    ('APA-01', 'Lavaplatos y grifería', 1, 'und', '1 und', [
        'Suministro e instalación de lavaplatos de acero inoxidable de 60 × 40 cm, profundo, para empotrar en el mesón.',
        'Grifería monomando de cuello alto de marca con repuestos, canastilla y sifón.']),
    ('APA-02', 'Instalación de electrodomésticos', 1, 'gl', 'Global', [
        'Conectar y probar la cubierta a gas, el horno empotrado y la campana, que suministra el propietario.']),
    ('MES-01', 'Mesón del muro sur', 1, 'und', '203 × 63,5 cm', [
        'Piedra sinterizada blanca mate, parecida al blanco de los muebles altos, lisa o con veta muy suave. Se aprueba con muestra física.',
        '12 mm con color en masa, para que el canto y un eventual despique no muestren otro color; ficha técnica del fabricante. No requiere sellado.',
        'Recortes para lavaplatos y cubierta con esquinas redondeadas, según el fabricante; canto pulido; silicona neutra antihongos.',
        'Plantilla tomada después de instalar los muebles. Instalador con experiencia en sinterizado: adjunte fotos de trabajos.']),
    ('MES-02', 'Mesón de la península en L', 1, 'und', '100 × 94 + 80 × 64 cm', [
        'Mismo material del MES-01, en L: 100 × 94 cm en el tramo con voladizo de 30 cm y 80 × 64 cm sobre el resto de la península y el módulo. En una pieza o en dos con junta mínima, según el fabricante.',
        'El voladizo de 30 cm va apoyado en platina de acero o escuadras ocultas ancladas al cuerpo de la península, según la ficha del fabricante. Inclúyalas en el valor.',
        'Canto pulido a la vista por los tres lados libres.']),
    ('ASE-01', 'Protección, escombros y aseo', 1, 'gl', 'Global', [
        'Proteger zonas comunes, ascensor y lo ya instalado; retirar escombros; entregar limpio.']),
]

GROUPS = [
    ('prep', 'Retiro y preparación', ['DEM-01', 'PIS-03']),
    ('redes', 'Agua, desagüe y gas', ['HID-01', 'HID-02', 'HID-03', 'GAS-01']),
    ('electrico', 'Electricidad, luz y campana', ['ELE-01', 'ELE-02', 'ELE-03', 'EXT-01']),
    ('acabados', 'Impermeabilización, enchapes, pisos y pintura', ['IMP-01', 'ENC-01', 'ENC-02', 'PIS-01', 'PIS-02', 'PIN-01', 'PIN-02']),
    ('aparatos', 'Aparatos y mesones', ['APA-01', 'APA-02', 'MES-01', 'MES-02', 'ASE-01']),
]
BYCODE = {i[0]: i for i in ITEMS}

ALTS = [
    ('ALT-01', 'Salida de la campana al exterior con ducto, si la administración la autoriza', 'EXT-01'),
    ('ALT-02', 'Mesones en granito gris oscuro de 2 cm en lugar de sinterizado, para comparar', 'MES-01 y MES-02'),
    ('ALT-03', 'Grifería del lavaplatos con ducha extraíble', 'APA-01'),
    ('ALT-04', 'Lavadero compacto nuevo en lugar de reinstalar el entregado', 'HID-03'),
    ('ALT-05', 'Autonivelante en todo el piso de cocina y ropas en lugar de nivelación localizada', 'PIS-03'),
    ('ALT-06', 'Suministro de cubierta a gas de 4 puestos, horno empotrado de 60 cm y campana de 60 cm de gama media, con marca y referencia', 'APA-02'),
    ('ALT-07', 'Salpicadero en la misma piedra sinterizada del mesón, en lugar de porcelanato', 'ENC-02'),
]

# ---------------------------------------------------------------- secciones
S = []
res_rows = ''.join(f'<tr><td class="z"><a href="#{c.lower()}">{c}</a></td><td>{t}</td><td class="num">{d}</td></tr>' for c, t, q, u, d, _ in ITEMS)
S.append(sec('alcance', '01 · Alcance', 'Qué se va a cotizar', f'''
<p class="lead2">Todo lo que hay que hacer en la cocina y la zona de ropas del apartamento 901, Torre 1, Alto Tramonti (Girón), menos la carpintería: retiro de lo entregado, redes, electricidad, campana, impermeabilización, enchapes, pisos, pintura, aparatos y mesones. El apartamento está en obra gris, con 2,40 m de altura libre. Cada trabajo tiene un código; úselo en la cotización.</p>
<div class="tbl"><table><thead><tr><th>Código</th><th>Trabajo</th><th class="num">Cantidad aprox.</th></tr></thead><tbody>{res_rows}</tbody></table></div>
{note('blue', 'i', '<b>La carpintería se cotiza aparte</b>: muebles bajos y altos, torre, península y su frente en WPC. Este pliego es todo lo demás. Las cantidades son aproximadas, tomadas del plano comercial; confírmelas en la visita.')}
{note('', '!', '<b>No se mueven redes.</b> El lavaplatos, la estufa y el lavadero quedan donde Inacar deja el agua, el desagüe y el gas.')}
'''))

S.append(sec('planos', '02 · Planos', 'Cocina, puntos y muro sur', f'''
<div class="shots2">
{shot(img64('cocina-b.jpg'), 'Render de la cocina desde la sala con la península y el mueble sobre el muro sur.', '<b>Así queda.</b> Península hacia la sala y mueble sobre el muro sur.')}
{shot(img64('ropas-b.jpg'), 'Render de la cocina desde la entrada con mesón, península, nevera y ropas.', '<b>Desde la entrada.</b> Mesón, península y ropas bajo su ventana.')}
</div>
<div class="figs">{fig(PTS_PLAN, '<b>Plano de puntos.</b> Los puntos del muro sur se dibujan sobre el muro aunque van a distintas alturas: la elevación de abajo las muestra. Agua, desagüe y gas quedan donde están hoy.', 'panel')}</div>
{LEG_PTS}
<div class="figs">{fig(B.KE, '<b>Muro sur visto desde la cocina.</b> Mesón a 90 cm, salpicadero hasta los altos (1,47 m) y tomas a 1,10 m. El enchape de ropas sube a 1,20 m.', 'panel')}</div>
<div class="figs">{fig(B.PLAN_COCINA, '<b>Planta con medidas.</b> La línea café punteada es el cambio de SPC a cerámica en ropas.', 'panel')}</div>
'''))

S.append(sec('materiales', '03 · Materiales', 'Acabados de la cocina', f'''
<div class="mgrid2">
{sample('spc-b', 'Piso de cocina', 'SPC roble natural')}
{sample('tf-b', 'Piso de ropas', 'Cerámica antideslizante 30 × 30 gris piedra')}
{sample('sp-b', 'Salpicadero', 'Porcelanato gran formato 60 × 120')}
{sample('tw-b', 'Enchape de ropas', 'Cerámica clara 30 × 60')}
{sample('ctr-b', 'Mesones', 'Piedra sinterizada blanca mate')}
{sample('metal-b', 'Grifería', 'Acero inoxidable')}
</div>
<p class="disc">Muestras generadas por computador: los colores son aproximados. Traiga muestras físicas y fichas técnicas de lo que ofrece.</p>
'''))

for n, (gid, gtitle, codes) in enumerate(GROUPS, 4):
    body = ''.join(block(c, BYCODE[c][1], BYCODE[c][4], BYCODE[c][5]) for c in codes)
    rng = ' y '.join(codes) if len(codes) == 2 else f'{codes[0]} a {codes[-1]}'
    S.append(sec(gid, f'{n:02d} · {rng}', gtitle, body))

S.append(sec('orden', '09 · Orden de obra', 'Cómo se coordina con la carpintería', '''
<ol class="steps2">
  <li><b>Retiro y protección.</b> DEM-01 y protección de zonas comunes.</li>
  <li><b>Redes.</b> Agua, desagüe, gas y electricidad; fotos de todo antes de cerrar.</li>
  <li><b>Impermeabilización de ropas</b> con prueba de estanqueidad y acta.</li>
  <li><b>Estuco, nivelación y enchape de ropas</b> (piso y muro).</li>
  <li><b>Primera mano de pintura.</b></li>
  <li><b>SPC,</b> dejando libre la huella de los muebles según el plano de despiece.</li>
  <li><b>Carpintería</b> (otro contratista): muebles, torre y península sobre la placa nivelada.</li>
  <li><b>Mesones:</b> plantilla sobre los muebles instalados, fabricación e instalación.</li>
  <li><b>Salpicadero</b> sobre el mesón.</li>
  <li><b>Aparatos, luminarias y pintura final.</b></li>
  <li><b>Pruebas y entrega:</b> fugas, desagües, gas, electricidad y lista de pendientes.</li>
</ol>
'''))

alt_rows = ''.join(f'<tr><td class="z">{c}</td><td>{t}</td><td>{w}</td></tr>' for c, t, w in ALTS)
S.append(sec('alternativas', '10 · Alternativas', 'Cotizar por separado', f'''
<p class="sub">No van en el total. Dé un valor para cada una, para decidir después.</p>
<div class="tbl"><table><thead><tr><th>Código</th><th>Alternativa</th><th>Afecta a</th></tr></thead><tbody>{alt_rows}</tbody></table></div>
'''))

S.append(sec('condiciones', '11 · Condiciones', 'Cómo presentar la cotización', '''
<div class="grid2">
  <div class="card"><h3>La cotización debe traer</h3><ul>
    <li>Valor por código (HID-01, ELE-02…) y total, con IVA aparte.</li>
    <li>Materiales con marca y referencia: SPC, cerámicas, impermeabilizante, grifería, lavaplatos, luminarias y cables.</li>
    <li>Si ajusta cantidades después de medir, corrija la columna de cantidad.</li>
    <li>Tiempo de ejecución por etapa y fecha posible de inicio.</li>
    <li>Garantía de mano de obra y de materiales, en años.</li>
    <li>Fotos de tres trabajos terminados y validez de la oferta.</li>
  </ul></div>
  <div class="card"><h3>Reglas de la obra</h3><ul>
    <li>Visita y medición antes de la cotización definitiva.</li>
    <li>Electricidad según el RETIE, con declaración de cumplimiento; gas por instalador certificado, con prueba de hermeticidad.</li>
    <li>No enchapar sin prueba de estanqueidad; no cerrar redes sin fotos y pruebas.</li>
    <li>Pagos contra avance verificable: anticipo moderado, pagos por hitos y 10% retenido hasta las pruebas y la corrección de pendientes.</li>
    <li>Cualquier adicional se aprueba por escrito antes de hacerlo.</li>
  </ul></div>
</div>
<div class="grid2">
  <div class="card"><h3>No incluye</h3><ul>
    <li>Carpintería: muebles, torre, península y frente en WPC.</li>
    <li>Nevera, lavadora, cubierta, horno, campana y lámparas colgantes (los compra el propietario; aquí solo se instalan).</li>
    <li>Cambios de fachada o de ductos comunes.</li>
  </ul></div>
  <div class="card"><h3>Se coordina con</h3><ul>
    <li><b>Carpintero:</b> plano de despiece (huella de los muebles para el SPC), perfil para el LED, perforaciones del lavaplatos y de la toma de la península, refuerzo para la platina del voladizo y fechas.</li>
    <li><b>Administración:</b> permisos de obra, horarios y salida de la campana si se pide.</li>
  </ul></div>
</div>
'''))

# ---------------------------------------------------------------- cuadro de cotización
def qn(v):
    return (f'{v:g}').replace('.', ',')


qrows = ''.join(
    f'<tr><td class="z">{c}</td><td>{t}</td>'
    f'<td class="num"><input class="qty" id="q-{i}" value="{qn(q)}" inputmode="decimal" aria-label="Cantidad {c}"></td><td>{u}</td>'
    f'<td class="num"><input class="money" id="u-{i}" inputmode="numeric" aria-label="Valor unitario {c}" placeholder="$"></td>'
    f'<td class="num tot" id="t-{i}">—</td></tr>'
    for i, (c, t, q, u, d, _) in enumerate(ITEMS))
arows = ''.join(
    f'<tr><td class="z">{c}</td><td>{t}</td><td class="num"><input class="money alt" id="a-{i}" inputmode="numeric" aria-label="Valor {c}" placeholder="$"></td></tr>'
    for i, (c, t, w) in enumerate(ALTS))
FIELDS = [('Proponente o empresa', 'f-nom'), ('NIT o cédula', 'f-nit'), ('Teléfono', 'f-tel'), ('Correo', 'f-mail'),
          ('Oficios que cotiza', 'f-of'), ('Tiempo de ejecución', 'f-tie'), ('Garantía de mano de obra', 'f-gm'),
          ('Garantía de materiales', 'f-gma'), ('Forma de pago', 'f-pago'), ('Validez de la oferta', 'f-val')]
ftags = ''.join(f'<label class="fld" for="{i}"><span>{n}</span><input id="{i}" type="text"></label>' for n, i in FIELDS)
S.append(sec('cotizacion', '12 · Cuadro de cotización', 'Para llenar y devolver', f'''
<p class="sub">Escriba los valores en pesos. Si cotiza solo algunos oficios, deje en blanco los demás. Los totales se calculan solos. Al terminar, use el botón para imprimir o guardar como PDF y envíe ese PDF.</p>
<div class="fields">{ftags}</div>
<div class="tbl qform"><table><thead><tr><th>Código</th><th>Trabajo</th><th class="num">Cant.</th><th>Und.</th><th class="num">Valor unitario</th><th class="num">Total</th></tr></thead>
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

toc = ''.join(f'<a href="#{i}">{t}</a>' for i, t in [('alcance', 'Alcance'), ('planos', 'Planos'), ('materiales', 'Materiales'),
                                                     ('prep', 'Retiro'), ('redes', 'Agua y gas'), ('electrico', 'Electricidad'),
                                                     ('acabados', 'Acabados'), ('aparatos', 'Aparatos y mesones'), ('orden', 'Orden'),
                                                     ('alternativas', 'Alternativas'), ('condiciones', 'Condiciones'), ('cotizacion', 'Cotización')])

EXTRA = C.EXTRA + r'''
:root{--pt-agua:#2F7FC1;--pt-des:#1E4F7A;--pt-gas:#C98A12;--pt-luz:#E8B400;--pt-apag:#5E6572;--pt-ink:#FFFFFF;--pt-ink-dark:#1B1B1B}
.pt circle{stroke:var(--card);stroke-width:1.2}
.pt text{font-family:var(--f-mono);font-weight:700;fill:var(--pt-ink)}
.p-agua circle{fill:var(--pt-agua)} .p-des circle{fill:var(--pt-des)} .p-gas circle{fill:var(--pt-gas)}
.p-toma circle{fill:var(--accent)} .p-luz circle{fill:var(--pt-luz)} .p-luz text{fill:var(--pt-ink-dark)} .p-apag circle{fill:var(--pt-apag)}
.p-led{stroke:var(--pt-luz);stroke-width:3;stroke-dasharray:7 4;fill:none}
.dotk{width:18px;height:18px;flex:0 0 auto}
.ledk{width:22px;height:0;border-top:3px dashed var(--pt-luz)}
.qform input.qty{max-width:80px}
.steps2{margin:16px 0 0;padding-left:22px;display:grid;gap:8px;font-size:.93rem;max-width:72ch}
'''

JS = r'''
(function(){
  function num(v){var d=(v||'').replace(/\D/g,'');return d?parseInt(d,10):0}
  function dec(v){var s=(v||'').replace(/\./g,'').replace(',','.').replace(/[^0-9.]/g,'');var n=parseFloat(s);return isNaN(n)?0:n}
  function fmt(n){n=Math.round(n);return n?'$'+n.toString().replace(/\B(?=(\d{3})+(?!\d))/g,'.'):'—'}
  function calc(){
    var sub=0;
    document.querySelectorAll('input.money[id^="u-"]').forEach(function(inp){
      var i=inp.id.slice(2),t=num(inp.value)*dec(document.getElementById('q-'+i).value);
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
<title>Cocina Apto 901</title>
<meta name="description" content="Pliego de la cocina del Apto 901, Torre 1, Alto Tramonti (Girón), sin carpintería, para solicitar cotizaciones: redes, electricidad, campana, impermeabilización, enchapes, pisos, pintura, aparatos y mesones.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap">
<style>:root{{color-scheme:light}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}
{C.PAGE_CSS}
{EXTRA}</style>
</head>
<body>
<header><div class="wrap top">
  <div class="eyebrow">Solicitud de cotización · Cocina sin carpintería</div>
  <h1>Cocina Apto 901</h1>
  <p class="lede">Torre 1, Alto Tramonti VIS, Girón (Santander). Obra, redes, acabados, aparatos y mesones de la cocina y la zona de ropas, para cotizar por trabajo.</p>
  <dl class="ficha">
    <div><dt>Espacio</dt><dd>9,3 m²<small>Cocina y ropas de 4,05 × 2,30 m</small></dd></div>
    <div><dt>Pisos</dt><dd>6,8 + 2,5 m²<small>SPC y cerámica en ropas</small></dd></div>
    <div><dt>Enchapes</dt><dd>≈ 3,2 m²<small>Salpicadero y ropas</small></dd></div>
    <div><dt>Mesones</dt><dd>≈ 2,7 m²<small>Muro sur y península</small></dd></div>
    <div><dt>Puntos</dt><dd>3 + 1 + 9<small>Agua, gas y tomas</small></dd></div>
    <div><dt>Oficios</dt><dd>6<small>Plomería, gas, electricidad, enchape, pintura y marmolería</small></dd></div>
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
print(OUT, f'{OUT.stat().st_size / 1024 / 1024:.2f} MB')
