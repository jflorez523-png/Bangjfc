#!/usr/bin/env python3
"""Genera la página Obra Blanca Apto 901 con dibujos a escala (unidades SVG = cm)."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'obra-blanca-901.html'
T = 10  # espesor de muro dibujado (cm)


def m(cm):
    return f"{cm / 100:.2f}".replace('.', ',')


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


# ---------------------------------------------------------------- materiales
MAT_A = {
    'spc': '#D9BF98', 'spc-j': '#BFA37C', 'paint': '#F3EEE4', 'upper': '#F7F5F0', 'lower': '#A8937F',
    'ctr': '#26262A', 'ctr-f': '#7A7672', 'sp': '#EFECE7', 'sp-j': '#D3CCC2', 'metal': '#232326',
    'tw': '#EDE9E2', 'tw-j': '#D0C9BE', 'tf': '#C2BAAE', 'tf-j': '#A59B8E', 'clo': '#EEE9E0',
    'clo-in': '#E2DCD1', 'van': '#A8937F', 'wpc': '#B8936A', 'wpc-j': '#8C6A46',
}
MAT_B = {
    'spc': '#C9A575', 'spc-j': '#A9865A', 'paint': '#F3EEE4', 'upper': '#F4F1EA', 'lower': '#A9A49C',
    'ctr': '#EEEBE5', 'ctr-f': '#D8D2C8', 'sp': '#E9E7E3', 'sp-j': '#CBC6BE', 'metal': '#A2A6AB',
    'tw': '#E9E7E3', 'tw-j': '#CBC6BE', 'tf': '#B2AEA7', 'tf-j': '#948F87', 'clo': '#D6B98F',
    'clo-in': '#C7A87D', 'van': '#C9A575', 'wpc': '#B8936A', 'wpc-j': '#8C6A46',
}
MAT_C = {  # comunes a ambas opciones
    'porc': '#FBFBF9', 'steel': '#C9CDD2', 'glass': '#BFDCE4', 'glass-l': '#5E97AA', 'led': '#FFD08A',
    'lav': '#F1F1EE', 'zoc': '#8F9194', 'cloth': '#B9C2CE', 'shoe': '#8B7866', 'mirror': '#D5E2E7',
    'e-line': '#2B2F38', 'e-halo': '#F7F4EE', 'oven': '#3A3F47', 'outlet': '#FAFAF8', 'door': '#D6C3A5',
}

SWATCH_A = [('SPC roble claro', 'spc'), ('Muros blanco cálido', 'paint'), ('Altos blanco mate', 'upper'),
            ('Bajos taupe / moca claro', 'lower'), ('Granito Negro San Gabriel', 'ctr'), ('Herrajes negro mate', 'metal')]
SWATCH_B = [('SPC roble natural', 'spc'), ('Muros blanco cálido', 'paint'), ('Altos blanco cálido', 'upper'),
            ('Bajos gris piedra suave', 'lower'), ('Piedra sinterizada blanca', 'ctr'), ('Herrajes inoxidables', 'metal')]


def mat_css(d):
    return ''.join(f'--m-{k}:{v};' for k, v in d.items())


# ---------------------------------------------------------------- lienzo SVG
class D:
    def __init__(self, pid, vb, k, fs_px=11.0):
        self.pid = pid
        self.x0, self.y0, self.w, self.h = vb
        self.k = k
        self.fs = fs_px / k
        self.tk = 4.5 / k
        self.p = []
        self.extra_defs = []

    def a(self, s):
        self.p.append(s)

    def pat(self, name, w, h, fill_cls, j_cls, ox=0, oy=0):
        self.extra_defs.append(
            f'<pattern id="{self.pid}-{name}" x="{ox}" y="{oy}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">'
            f'<rect width="{w}" height="{h}" class="{fill_cls}"/><path d="M0 0H{w}M0 0V{h}" class="{j_cls}"/></pattern>')
        return f'url(#{self.pid}-{name})'

    def defs(self):
        p = self.pid
        return (f'<defs>'
                f'<pattern id="{p}-spc" width="36" height="122" patternUnits="userSpaceOnUse"><rect width="36" height="122" class="m-spc"/>'
                f'<path d="M0 0V122M18 0V122M0 0H18M18 61H36" class="j-spc"/></pattern>'
                f'<pattern id="{p}-tf" width="30" height="30" patternUnits="userSpaceOnUse"><rect width="30" height="30" class="m-tf"/>'
                f'<path d="M0 0H30M0 0V30" class="j-tf"/></pattern>'
                f'<pattern id="{p}-gr" width="14" height="14" patternUnits="userSpaceOnUse"><rect width="14" height="14" class="m-ctr"/>'
                f'<circle cx="3" cy="4" r=".8" class="m-ctrf"/><circle cx="10" cy="9" r=".6" class="m-ctrf"/><circle cx="7" cy="12.5" r=".5" class="m-ctrf"/></pattern>'
                f'<linearGradient id="{p}-led" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="led0"/><stop offset="1" class="led1"/></linearGradient>'
                + ''.join(self.extra_defs) + '</defs>')

    def svg(self, aria, cls='dw'):
        wpx = round(self.w * self.k)
        hw = 3.2 / self.k
        return (f'<svg class="{cls}" viewBox="{self.x0:g} {self.y0:g} {self.w:g} {self.h:g}" width="{wpx}" '
                f'role="img" aria-label="{esc(aria)}" style="--hw:{hw:.2f}px">'
                + self.defs() + ''.join(self.p) + '</svg>')

    # texto
    def text(self, x, y, s, cls='lb', anchor='middle', size=1.0, rot=None):
        fs = self.fs * size
        tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ''
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs:.2f}" text-anchor="{anchor}" '
                f'class="{cls}"{tr}>{esc(s)}</text>')

    def t(self, *a, **kw):
        self.a(self.text(*a, **kw))

    # cotas
    def dimh(self, x1, x2, y, label, size=0.92, cls='dim', below=False):
        t = self.tk * 0.7
        ty = y + self.fs * 1.05 if below else y - self.fs * 0.4
        self.a(f'<g class="{cls}"><path d="M{x1:.1f} {y:.1f}H{x2:.1f}M{x1 - t:.1f} {y + t:.1f}L{x1 + t:.1f} {y - t:.1f}'
               f'M{x2 - t:.1f} {y + t:.1f}L{x2 + t:.1f} {y - t:.1f}"/>'
               + self.text((x1 + x2) / 2, ty, label, cls='dt', size=size) + '</g>')

    def dimv(self, y1, y2, x, label, size=0.92, cls='dim', right=False):
        t = self.tk * 0.7
        tx = x + self.fs * 1.05 if right else x - self.fs * 0.4
        self.a(f'<g class="{cls}"><path d="M{x:.1f} {y1:.1f}V{y2:.1f}M{x - t:.1f} {y1 + t:.1f}L{x + t:.1f} {y1 - t:.1f}'
               f'M{x - t:.1f} {y2 + t:.1f}L{x + t:.1f} {y2 - t:.1f}"/>'
               + self.text(tx, (y1 + y2) / 2, label, cls='dt', size=size, rot=-90) + '</g>')

    # muros en planta con vanos
    def walls(self, w, h, gaps=()):
        def cut(a, b, side):
            segs = [(a, b)]
            for s, g1, g2 in gaps:
                if s != side:
                    continue
                nxt = []
                for s1, s2 in segs:
                    if g2 <= s1 or g1 >= s2:
                        nxt.append((s1, s2))
                    else:
                        if g1 > s1:
                            nxt.append((s1, g1))
                        if g2 < s2:
                            nxt.append((g2, s2))
                segs = nxt
            return segs
        r = []
        for a, b in cut(-T, w + T, 'top'):
            r.append((a, -T, b - a, T))
        for a, b in cut(-T, w + T, 'bottom'):
            r.append((a, h, b - a, T))
        for a, b in cut(0, h, 'left'):
            r.append((-T, a, T, b - a))
        for a, b in cut(0, h, 'right'):
            r.append((w, a, T, b - a))
        self.a(''.join(f'<rect x="{x:g}" y="{y:g}" width="{ww:g}" height="{hh:g}" class="pc"/>' for x, y, ww, hh in r))

    def floor(self, x, y, w, h, kind='spc'):
        self.a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{self.pid}-{kind})"/>')


# ---------------------------------------------------------------- mobiliario en planta
def bed(d, x, y, bw, bl, head='top'):
    if head == 'top':
        W, H = bw, bl
    else:
        W, H = bl, bw
    s = f'<g class="loose"><rect x="{x}" y="{y}" width="{W}" height="{H}" rx="3"/>'
    n = 2 if bw >= 120 else 1
    pw = (bw - 12 - (n - 1) * 6) / n
    for i in range(n):
        o = 6 + i * (pw + 6)
        if head == 'top':
            s += f'<rect x="{x + o:.1f}" y="{y + 6}" width="{pw:.1f}" height="20" rx="5"/>'
        else:
            s += f'<rect x="{x + 6}" y="{y + o:.1f}" width="20" height="{pw:.1f}" rx="5"/>'
    if head == 'top':
        fy = y + 44
        s += f'<path d="M{x} {fy}H{x + W}M{x + W - 30} {fy}L{x + W} {fy + 26}" class="fold"/>'
    else:
        fx = x + 44
        s += f'<path d="M{fx} {y}V{y + H}M{fx} {y + H - 30}L{fx + 26} {y + H}" class="fold"/>'
    d.a(s + '</g>')


def nightstand(d, x, y, w=40, h=35):
    d.a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" class="loose"/>')


def closet(d, x, y, cw, cd, leaves, swings=False):
    """Closet sobre un muro inferior; frente hacia arriba (y)."""
    s = f'<rect x="{x}" y="{y}" width="{cw}" height="{cd}" class="m-clo ol"/>'
    s += f'<path d="M{x + 4} {y + cd / 2}H{x + cw - 4}" class="rod"/>'
    s += f'<path d="M{x} {y}H{x + cw}" class="front"/>'
    lw = cw / leaves
    for i in range(1, leaves):
        s += f'<path d="M{x + i * lw:.1f} {y}V{y + 5}" class="ol"/>'
    if swings:
        for i in range(leaves):
            left = (i % 2 == 0)
            hx = x + i * lw if left else x + (i + 1) * lw
            fx = hx + lw if left else hx - lw
            sweep = 0 if left else 1
            s += (f'<path d="M{hx:.1f} {y}V{y - lw:.1f}M{fx:.1f} {y}A{lw:.1f} {lw:.1f} 0 0 {sweep} {hx:.1f} {y - lw:.1f}" class="swing"/>')
    d.a(s)


def light(d, cx, cy, r=7, cls=''):
    d.a(f'<g class="lt {cls}"><circle cx="{cx}" cy="{cy}" r="{r}"/><path d="M{cx - r} {cy}H{cx + r}M{cx} {cy - r}V{cy + r}"/></g>')


def sofa(d, x, y, w, dp):
    """Sofá contra el muro izquierdo mirando a la derecha. w = largo (en y), dp = fondo (en x)."""
    d.a(f'<g class="loose"><rect x="{x}" y="{y}" width="{dp}" height="{w}" rx="4"/>'
        f'<rect x="{x}" y="{y}" width="18" height="{w}" rx="3"/>'
        f'<rect x="{x}" y="{y}" width="{dp}" height="15" rx="3"/><rect x="{x}" y="{y + w - 15}" width="{dp}" height="15" rx="3"/>'
        f'<path d="M{x + 18} {y + w / 2}H{x + dp}" class="fold"/></g>')


def round_table(d, cx, cy, r):
    s = '<g class="loose">'
    dd = r + 14
    for dx, dy in ((0, -dd), (0, dd), (-dd, 0), (dd, 0)):
        s += f'<rect x="{cx + dx - 20}" y="{cy + dy - 20}" width="40" height="40" rx="6"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="{r}"/></g>'
    d.a(s)


# ---------------------------------------------------------------- plano real del Apto 901
# Espejo del Tipo A. Coordenadas en cm: X hacia el oriente, Y hacia el sur (norte arriba, balcón al norte).
# Origen: esquina noroccidental interior de la cocina, sobre el límite entre cocina y sala.
WALLS = [
    (-261, -400, -246, -90),   # alcoba 2, muro occidental
    (-246, -400, -115, -385),  # alcoba 2, muro norte
    (-16, -400, 0, -90),       # alcoba 2 / sala
    (199, -366, 281, -339),    # sala, esquina nororiental
    (380, -366, 547, -339),    # alcoba principal, muro norte
    (265, -339, 281, -94),     # sala / alcoba principal
    (529, -339, 547, 246),     # fachada oriental
    (-357, -105, -341, 182),   # alcoba 3, muro occidental
    (-261, -105, -94, -90),    # alcoba 2 / alcoba 3
    (265, -15, 421, 1),        # alcoba principal / ropas
    (490, -15, 529, 1),        # alcoba principal / baño principal
    (-140, -10, -125, 179),    # alcoba 3 / baño auxiliar
    (405, 1, 421, 246),        # ropas / baño principal
    (-56, 5, 0, 15),           # baño auxiliar, norte
    (-16, 15, 0, 246),         # baño auxiliar / entrada
    (-357, 166, -140, 182),    # alcoba 3, sur
    (-140, 230, -16, 246),     # baño auxiliar, sur
    (92, 230, 356, 246),       # cocina, muro sur
    (469, 230, 529, 246),      # baño principal, sur
]
DUCTS = [(-36, 140, -16, 230), (510, 140, 529, 230)]
# vanos de ventana: rect del vano, alféizar y dintel (cm)
WINDOWS = [
    ((-115, -400, -16, -385), 90, 210),   # alcoba 2
    ((281, -366, 380, -339), 90, 210),    # alcoba principal
    ((0, -366, 199, -339), 0, 210),       # puerta-ventana del balcón
    ((-341, -105, -261, -90), 90, 210),   # alcoba 3
    ((-140, 179, -125, 230), 140, 210),   # baño auxiliar
    ((356, 230, 405, 246), 120, 210),     # ropas
    ((421, 230, 469, 246), 140, 210),     # baño principal
]
# puertas: vano, bisagra, extremo cerrado, extremo abierto
DOORS = [
    ((0, 230, 92, 246), (0, 230), (92, 230), (0, 138)),              # entrada
    ((265, -94, 281, -15), (281, -15), (281, -94), (360, -15)),      # alcoba principal
    ((421, -15, 490, 1), (421, 1), (490, 1), (421, 70)),             # baño principal
    ((-94, -105, -16, -90), (-16, -105), (-94, -105), (-16, -183)),  # alcoba 2
    ((-140, -90, -125, -10), (-140, -90), (-140, -10), (-220, -90)), # alcoba 3
    ((-125, 5, -56, 15), (-125, 15), (-56, 15), (-125, 84)),         # baño auxiliar
]
FLOORS = [  # (x0, y0, x1, y1, material)
    (0, -339, 265, 0, 'spc'), (0, 0, 295, 230, 'spc'), (295, 0, 405, 230, 'tf'),
    (-125, -105, 0, 15, 'spc'), (-246, -385, -16, -105, 'spc'), (-341, -90, -140, 166, 'spc'),
    (281, -339, 529, -15, 'spc'), (421, 1, 529, 230, 'tf'), (-125, 15, -16, 230, 'tf'),
    (265, -94, 281, -15, 'spc'), (421, -15, 490, 1, 'tf'), (-140, -90, -125, -10, 'spc'), (0, 230, 92, 246, 'spc'),
]
BALCONY = (0, -438, 200, -366)
ROOM_LABELS = [
    ('SALA-COMEDOR', '2,65 × 3,40', 132, -110), ('COCINA', '4,05 × 2,30', 175, 128), ('ROPAS', '', 352, 128),
    ('ALCOBA PRINCIPAL', '2,50 × 3,38', 405, -150), ('ALCOBA 2', '2,30 × 2,80', -131, -225),
    ('ALCOBA 3', '2,00 × 2,55', -290, 60), ('BAÑO', '1,10 × 2,10', 460, 172), ('BAÑO', '1,10 × 2,10', -86, 172),
    ('BALCÓN', '2,00 × 0,72', 100, -405),
]


def rect(x0, y0, x1, y1, cls, extra=''):
    return f'<rect x="{x0:g}" y="{y0:g}" width="{x1 - x0:g}" height="{y1 - y0:g}" class="{cls}"{extra}/>'


def bed2(d, x0, y0, x1, y1, head):
    """Cama suelta entre (x0,y0)-(x1,y1); head: 'n', 's', 'e' u 'o'."""
    s = '<g class="loose">' + f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="3"/>'
    horiz = head in ('e', 'o')
    across = (y1 - y0) if horiz else (x1 - x0)
    n = 2 if across >= 120 else 1
    pw = (across - 12 - (n - 1) * 6) / n
    for i in range(n):
        o = 6 + i * (pw + 6)
        if head == 'n':
            s += f'<rect x="{x0 + o:.1f}" y="{y0 + 6}" width="{pw:.1f}" height="20" rx="5"/>'
        if head == 's':
            s += f'<rect x="{x0 + o:.1f}" y="{y1 - 26}" width="{pw:.1f}" height="20" rx="5"/>'
        if head == 'o':
            s += f'<rect x="{x0 + 6}" y="{y0 + o:.1f}" width="20" height="{pw:.1f}" rx="5"/>'
        if head == 'e':
            s += f'<rect x="{x1 - 26}" y="{y0 + o:.1f}" width="20" height="{pw:.1f}" rx="5"/>'
    if head == 'n':
        s += f'<path d="M{x0} {y0 + 44}H{x1}" class="fold"/>'
    if head == 's':
        s += f'<path d="M{x0} {y1 - 44}H{x1}" class="fold"/>'
    if head == 'o':
        s += f'<path d="M{x0 + 44} {y0}V{y1}" class="fold"/>'
    if head == 'e':
        s += f'<path d="M{x1 - 44} {y0}V{y1}" class="fold"/>'
    d.a(s + '</g>')


def closet2(d, x0, y0, x1, y1, front, leaves, swings=False, sliding=False):
    s = rect(x0, y0, x1, y1, 'm-clo ol')
    if front in ('n', 's'):
        s += f'<path d="M{x0 + 4} {(y0 + y1) / 2}H{x1 - 4}" class="rod"/>'
        fy = y0 if front == 'n' else y1
        s += f'<path d="M{x0} {fy}H{x1}" class="front"/>'
        lw = (x1 - x0) / leaves
        for i in range(1, leaves):
            s += f'<path d="M{x0 + i * lw:.1f} {fy}V{fy + (4 if front == "n" else -4)}" class="ol"/>'
        if swings:
            sg = -1 if front == 'n' else 1
            for i in range(leaves):
                left = i % 2 == 0
                hx = x0 + i * lw if left else x0 + (i + 1) * lw
                fx = hx + lw if left else hx - lw
                oy = fy + sg * lw
                sweep = (0 if left else 1) if front == 'n' else (1 if left else 0)
                s += f'<path d="M{hx:.1f} {fy}V{oy:.1f}M{fx:.1f} {fy}A{lw:.1f} {lw:.1f} 0 0 {sweep} {hx:.1f} {oy:.1f}" class="swing"/>'
    else:
        s += f'<path d="M{(x0 + x1) / 2} {y0 + 4}V{y1 - 4}" class="rod"/>'
        fx = x0 if front == 'o' else x1
        dx = 4 if front == 'o' else -4
        if sliding:
            my = (y0 + y1) / 2
            s += f'<path d="M{fx} {y0}V{my + 8}" class="front"/><path d="M{fx + dx} {my - 8}V{y1}" class="front"/>'
        else:
            s += f'<path d="M{fx} {y0}V{y1}" class="front"/>'
    d.a(s)


def sofa_e(d, x0, y0, x1, y1):
    """Sofá contra el muro oriental, mirando al occidente."""
    r4, r3 = ' rx="4"', ' rx="3"'
    parts = [rect(x0, y0, x1, y1, '', r4), rect(x1 - 18, y0, x1, y1, '', r3),
             rect(x0, y0, x1, y0 + 15, '', r3), rect(x0, y1 - 15, x1, y1, '', r3)]
    d.a('<g class="loose">' + ''.join(parts) + f'<path d="M{x0} {(y0 + y1) / 2}H{x1 - 18}" class="fold"/></g>')


def door_arc(hinge, closed, opened):
    hx, hy = hinge
    r = ((closed[0] - hx) ** 2 + (closed[1] - hy) ** 2) ** 0.5
    cross = (closed[0] - hx) * (opened[1] - hy) - (closed[1] - hy) * (opened[0] - hx)
    sweep = 1 if cross > 0 else 0
    return (f'<path d="M{hx} {hy}L{opened[0]} {opened[1]}" class="leaf"/>'
            f'<path d="M{closed[0]} {closed[1]}A{r:.1f} {r:.1f} 0 0 {sweep} {opened[0]} {opened[1]}" class="swing"/>')


def plan_content(d, mode):
    """mode: 'full' (planta completa con nombres) o 'crop' (detalle con rótulos de muebles)."""
    det = mode == 'crop'
    for x0, y0, x1, y1, mat in FLOORS:
        d.floor(x0, y0, x1 - x0, y1 - y0, mat)
    bx0, by0, bx1, by1 = BALCONY
    d.a(f'<path d="M{bx0} {by1}V{by0}H{bx1 - 40}A40 40 0 0 1 {bx1} {by0 + 40}V{by1}Z" fill="url(#{d.pid}-tf)" class="ol"/>')
    d.a(f'<path d="M{bx0 - 8} -400V{by0 - 6}H{bx1 - 40}A46 46 0 0 1 {bx1 + 6} {by0 + 40}V{by1}" class="rail"/>')
    d.a('<path d="M295 0V230" class="trans"/>')
    # muros, ductos, ventanas y puertas
    d.a(''.join(rect(*w, 'pc') for w in WALLS))
    for x0, y0, x1, y1 in DUCTS:
        d.a(rect(x0, y0, x1, y1, 'duct') + f'<path d="M{x0} {y0}L{x1} {y1}M{x1} {y0}L{x0} {y1}" class="duct-x"/>')
    for (x0, y0, x1, y1), sill, head in WINDOWS:
        d.a(rect(x0, y0, x1, y1, 'win'))
        if x1 - x0 >= y1 - y0:
            d.a(f'<path d="M{x0} {(y0 + y1) / 2}H{x1}" class="glass"/>')
        else:
            d.a(f'<path d="M{(x0 + x1) / 2} {y0}V{y1}" class="glass"/>')
    for gap, hinge, closed, opened in DOORS:
        d.a(door_arc(hinge, closed, opened))
    # baños: mueble, sanitario y ducha sobre el muro oriental
    for ex, dx0 in ((529, 421), (-16, -125)):
        d.a(rect(ex - 45, 25, ex, 85, 'm-van ol') + f'<ellipse cx="{ex - 22}" cy="55" rx="13" ry="18" class="porc ol"/>')
        d.a(rect(ex - 18, 88, ex, 128, 'porc ol', ' rx="2"') + f'<ellipse cx="{ex - 43}" cy="108" rx="25" ry="17" class="porc ol"/>')
        sx1 = ex - 19
        d.a(f'<path d="M{dx0} 140H{dx0 + 55}" class="glass"/><path d="M{dx0 + 40} 144H{sx1}" class="glass"/>')
        d.a(f'<circle cx="{(dx0 + sx1) / 2}" cy="190" r="4" class="drain"/>')
    # cocina: muro sur (común a A y B)
    d.a(f'<rect x="92" y="170" width="203" height="60" fill="url(#{d.pid}-gr)" class="ol"/>')
    d.a('<path d="M152 170V230M212 170V230M272 170V230" class="hid"/>')
    d.a(rect(100, 180, 144, 220, 'steel ol', ' rx="3"') + '<circle cx="122" cy="226" r="2.2" class="metal"/>')
    d.a(rect(216, 176, 268, 226, 'cook', ' rx="2"'))
    for cx, cy in ((229, 189), (255, 189), (229, 213), (255, 213)):
        d.a(f'<circle cx="{cx}" cy="{cy}" r="8" class="burner"/>')
    d.a(rect(297, 172, 353, 230, 'own') + '<circle cx="325" cy="201" r="21" class="own"/>')
    d.a(rect(357, 174, 405, 230, 'lav ol') + rect(362, 180, 400, 222, 'lavb', ' rx="4"'))
    # cocina: frente norte (nevera y torre en A y B)
    d.a(rect(297, 3, 363, 68, 'own') + rect(365, 1, 405, 61, 'm-lower ol'))
    # B: península + módulo junto a la nevera
    d.a('<g>'
        + rect(265, 1, 295, 61, 'ol', f' fill="url(#{d.pid}-gr)"')
        + f'<path d="M115 -30H215V0H265V60H115Z" fill="url(#{d.pid}-gr)" class="ol"/>'
        + '<path d="M115 0H215" class="hid"/>'
        + '<g class="loose"><circle cx="140" cy="-52" r="17"/><circle cx="190" cy="-52" r="17"/></g></g>')
    light(d, 140, 18, r=5)
    light(d, 190, 18, r=5)
    # sala
    sofa_e(d, 180, -305, 265, -155)
    d.a('<circle cx="118" cy="-230" r="24" class="loose"/>')
    d.a(rect(0, -290, 10, -170, 'm-clo ol'))
    light(d, 132, -215)
    light(d, 60, -392, r=5)
    # alcoba principal: closet al norte junto a la ventana, cama con cabecero al oriente
    closet2(d, 380, -339, 529, -279, 's', 3, swings=det)
    bed2(d, 339, -220, 529, -80, 'e')
    d.a(rect(492, -259, 529, -223, 'loose') + rect(492, -77, 529, -41, 'loose'))
    light(d, 405, -177)
    # alcoba 2: cama contra el muro norte, closet sobre el muro sur
    bed2(d, -246, -385, -56, -265, 'o')
    closet2(d, -246, -165, -100, -105, 'n', 3, swings=det)
    light(d, -131, -245)
    # alcoba 3: cama al occidente, closet corredizo al oriente
    bed2(d, -341, -30, -241, 160, 'n')
    closet2(d, -195, 0, -140, 120, 'o', 2, sliding=True)
    light(d, -240, 38)
    if mode == 'full':
        for name, dims, x, y in ROOM_LABELS:
            d.t(x, y, name, size=0.82)
            if dims:
                d.t(x, y + d.fs * 1.05, dims, cls='dt lbd', size=0.78)
        d.t(46, 246 + d.fs * 2.2, 'ENTRADA', size=0.78)
        d.a(f'<path d="M36 {246 + d.fs * 0.6}H56L46 {246 + d.fs * 0.1}Z" class="arrow"/>')
    else:
        fz = 0.72
        d.t(330, 45, 'Nevera', size=fz)
        d.t(385, 80, 'Torre', size=fz)
        d.t(325, 160, 'Lavadora', size=fz)
        d.t(381, 164, 'Lavadero', size=fz)
        d.t(190, 36, 'Península', size=0.8)
        d.t(222, -273, 'Sofá', size=fz, rot=-90)
        d.t(26, -230, 'TV', size=fz)
        d.t(454, -305, 'Closet', size=fz)
        d.t(-173, -130, 'Closet', size=fz)
        d.t(-168, 60, 'Closet', size=fz, rot=-90)


def plan_svg(pid, crop, k, aria, mode='crop', dims=None, fs=10.5):
    d = D(pid, crop, k, fs)
    plan_content(d, mode)
    if dims:
        dims(d)
    return d.svg(aria, cls='dw crop')


def dims_kitchen(d):
    yb = 246 + 0.9 * d.fs
    x = 0
    for wd in (92, 60, 60, 60, 23, 60, 50):
        d.dimh(x, x + wd, yb, str(wd), size=0.8, below=True)
        x += wd
    d.dimh(0, 405, yb + 2.1 * d.fs, '4,05', below=True)
    d.dimv(0, 230, -16 - 0.9 * d.fs, '2,30')
    d.dimh(115, 265, -96, '1,50')
    d.dimv(60, 170, 172, 'pasillo 1,10', size=0.78, right=True)
    d.dimh(0, 115, 110, '1,15', size=0.78)
    d.dimv(-30, 60, 115 - 0.7 * d.fs, '0,90', size=0.78)


def dims_sala(d):
    d.dimv(-339, 0, -16 - 0.9 * d.fs, '3,40')
    d.dimh(0, 265, -322, '2,65', below=True)
    d.dimh(0, 200, -438 - 0.7 * d.fs, '2,00')
    d.dimv(-438, -366, 219 + 0.9 * d.fs, '0,72', right=True, size=0.8)


def dims_room(x0, y0, x1, y1, lx, ly):
    def f(d):
        d.dimh(x0, x1, y0 - 16 - 0.9 * d.fs, lx)
        d.dimv(y0, y1, x0 - 16 - 0.9 * d.fs, ly)
    return f


# ---------------------------------------------------------------- alzados
def Y(hh):
    return 240 - hh


def elev_frame(d, w):
    d.a(f'<rect x="{-T}" y="0" width="{T}" height="240" class="pc"/><rect x="{w}" y="0" width="{T}" height="240" class="pc"/>')
    d.a(f'<rect x="{-T}" y="240" width="{w + 2 * T}" height="{T}" class="pc"/><rect x="{-T}" y="{-T}" width="{w + 2 * T}" height="{T}" class="pc"/>')


def fronts_svg(fronts, gola_runs=()):
    """fronts: (x, w, h0, h1, tipo, bisagra, clase). Devuelve frentes + manijas A + perfiles B."""
    s = ''.join(f'<rect x="{x + .4}" y="{Y(h1) + .4}" width="{w - .8}" height="{h1 - h0 - .8}" class="{c} eo"/>'
                for x, w, h0, h1, kind, hinge, c in fronts)
    ha = ''
    for x, w, h0, h1, kind, hinge, c in fronts:
        if kind == 'door':
            hx = x + w - 4 if hinge == 'l' else x + 4
            y0, y1 = (h1 - 6, h1 - 20) if hinge != 'up' else (h0 + 5, h0 + 17)
            ha += f'<path d="M{hx} {Y(y0)}V{Y(y1)}" class="hdl"/>'
        elif kind == 'udoor':
            hx = x + w - 4 if hinge == 'l' else x + 4
            ha += f'<path d="M{hx} {Y(h0 + 5)}V{Y(h0 + 17)}" class="hdl"/>'
        else:
            ha += f'<path d="M{x + w / 2 - 9} {Y(h1 - 5)}H{x + w / 2 + 9}" class="hdl"/>'
    gb = ''.join(f'<rect x="{x0}" y="{Y(h)}" width="{x1 - x0}" height="1.6" class="gola"/>' for x0, x1, h in gola_runs)
    return s + gb


def kitchen_elev():
    """Muro sur de cocina y ropas, visto desde la cocina (el oriente queda a la izquierda)."""
    k, fs = 1.55, 10.5
    fsc = fs / k
    L = T + 3.6 * fsc + 6
    top = T + 1.2 * fsc
    d = D('ke', (-L, -top, 405 + L + T + 8, 240 + top + T + 5.9 * fsc), k, fs)
    sp = d.pat('sp', 60, 30, 'm-sp', 'j-sp', 110, Y(147))
    tw = d.pat('tw', 60, 30, 'm-tw', 'j-tw', 0, Y(120))
    d.a('<rect x="0" y="0" width="405" height="240" class="m-paint"/>')
    d.a(f'<rect x="0" y="{Y(120)}" width="110" height="120" fill="{tw}" class="eo"/>')
    d.a(f'<rect x="110" y="{Y(147)}" width="203" height="57" fill="{sp}" class="eo"/>')
    # ventana de ropas
    d.a(f'<rect x="1" y="{Y(210)}" width="48" height="90" class="glass-e"/><path d="M25 {Y(210)}V{Y(120)}" class="eo"/>'
        f'<rect x="-1" y="{Y(121)}" width="52" height="2" class="sill eo"/>')
    # lavadero compacto y lavadora
    d.a(f'<rect x="3" y="{Y(90)}" width="44" height="30" rx="2" class="lav eo"/><path d="M7 {Y(60)}V240M43 {Y(60)}V240" class="eo"/>'
        f'<path d="M25 {Y(90)}V{Y(104)}Q25 {Y(110)} 31 {Y(110)}H33" class="faucet"/>')
    d.a(f'<rect x="52" y="{Y(85)}" width="56" height="85" rx="3" class="own-e"/><circle cx="80" cy="{Y(48)}" r="17" class="own-e"/>'
        f'<circle cx="80" cy="{Y(100)}" r="2.6" class="metal"/>')
    # bajos
    d.a(f'<rect x="110" y="{Y(10)}" width="203" height="10" class="zoc eo"/>')
    fr = [(110, 23, 10, 88, 'door', 'r', 'm-lower'),
          (193, 60, 10, 32, 'drawer', None, 'm-lower'), (193, 60, 32, 60, 'drawer', None, 'm-lower'), (193, 60, 60, 88, 'drawer', None, 'm-lower'),
          (133, 60, 10, 26, 'drawer', None, 'm-lower'),
          (253, 30, 10, 88, 'door', 'l', 'm-lower'), (283, 30, 10, 88, 'door', 'r', 'm-lower')]
    d.a(fronts_svg(fr, [(110, 133, 88), (193, 313, 88), (133, 193, 26)]))
    d.a(f'<rect x="133.4" y="{Y(88)}" width="59.2" height="61.6" class="steel eo"/>'
        f'<rect x="141" y="{Y(76)}" width="44" height="34" rx="2" class="oven-win"/><path d="M143 {Y(82)}H183" class="hdl"/>')
    d.a(f'<rect x="110" y="{Y(90)}" width="203" height="2.4" fill="url(#ke-gr)" class="eo"/>')
    d.a(f'<rect x="139" y="{Y(91.6)}" width="48" height="1.6" class="steel eo"/><path d="M145 {Y(92.6)}h8M173 {Y(92.6)}h8" class="hdl"/>')
    d.a(f'<path d="M283 {Y(90)}V{Y(121)}Q283 {Y(129)} 275 {Y(129)}H272V{Y(123)}" class="faucet"/>')
    for x in (205, 240):
        d.a(f'<rect x="{x}" y="{Y(116)}" width="8" height="12" rx="1" class="outlet"/>')
    for x in (118, 298):
        d.a(f'<rect x="{x}" y="{Y(116)}" width="8" height="12" rx="1" class="outlet"/>')
    # LED y altos
    d.a(f'<rect x="50" y="{Y(147)}" width="83" height="34" fill="url(#ke-led)"/><rect x="193" y="{Y(147)}" width="120" height="34" fill="url(#ke-led)"/>')
    ups = [(50, 42, 147, 222, 'udoor', 'l', 'm-upper'), (92, 41, 147, 222, 'udoor', 'r', 'm-upper'),
           (133, 60, 180, 222, 'udoor', 'l', 'm-upper'),
           (193, 30, 147, 222, 'udoor', 'l', 'm-upper'), (223, 30, 147, 222, 'udoor', 'r', 'm-upper'),
           (253, 30, 147, 222, 'udoor', 'l', 'm-upper'), (283, 30, 147, 222, 'udoor', 'r', 'm-upper')]
    d.a(fronts_svg(ups, [(50, 133, 148.6), (193, 313, 148.6)]))
    d.a(f'<path d="M137 {Y(180)}H189L187 {Y(166)}H139Z" class="steel eo"/>')
    d.a(f'<path d="M50 {Y(147) + .8}H133M193 {Y(147) + .8}H313" class="ledl"/>')
    # puerta de entrada
    d.a(f'<rect x="313" y="{Y(210)}" width="92" height="210" class="m-paint"/>'
        f'<rect x="317" y="{Y(207)}" width="84" height="207" class="door eo"/><path d="M394 {Y(100)}H386" class="hdl-d"/>'
        f'<path d="M313 {Y(210)}V240M405 {Y(210)}V240M313 {Y(210)}H405" class="eo"/>')
    elev_frame(d, 405)
    yb = 240 + T + 1.5 * d.fs
    for x0, wd, nm in ((0, 50, 'Lavadero'), (50, 60, 'Lavadora'), (110, 23, 'Rem.'), (133, 60, 'Estufa'),
                       (193, 60, 'Cajonero'), (253, 60, 'Lavaplatos'), (313, 92, 'Entrada')):
        d.dimh(x0, x0 + wd, yb, str(wd), size=0.8)
        d.t(x0 + wd / 2, yb + d.fs * 1.15, nm, cls='dn', size=0.76)
    d.dimh(110, 313, yb + d.fs * 2.7, 'Mueble 2,03', size=0.85, below=True)
    xl = -T - 0.9 * d.fs
    d.dimv(0, 240, xl - 1.6 * d.fs, '2,40 libre', size=0.85)
    for h0, h1, lb in ((0, 90, '≈90'), (90, 147, '55–60'), (147, 222, '70–80')):
        d.dimv(240 - h0, 240 - h1, xl, lb, size=0.78)
    return d.svg('Muro sur de la cocina visto desde adentro: lavadero bajo la ventana de ropas, lavadora, remate, estufa con horno y campana, cajonero, lavaplatos y la puerta de entrada.')


def peninsula_elev():
    """Península de B: cara hacia la sala, corte y cara hacia la cocina."""
    k, fs = 1.3, 10.5
    fsc = fs / k
    d = D('pe', (-26, -8, 530, 240 + 8 + T + 4.7 * fsc), k, fs)
    wpc = d.pat('wpc', 3, 240, 'm-wpc', 'j-wpc', 0, 0)
    # suelo
    d.a(f'<path d="M-20 240H525" class="eo2"/>')
    # 1. cara hacia la sala (el oriente a la izquierda)
    d.a(f'<rect x="0" y="{Y(88)}" width="150" height="78" fill="{wpc}" class="eo2"/><rect x="0" y="{Y(10)}" width="150" height="10" class="zoc eo2"/>')
    d.a(f'<rect x="0" y="{Y(90)}" width="150" height="2.4" fill="url(#pe-gr)" class="eo2"/>')
    for cx in (75, 125):
        d.a(f'<path d="M{cx} 0V{Y(172)}" class="cable"/><path d="M{cx - 9} {Y(172)}H{cx + 9}L{cx + 13} {Y(158)}H{cx - 13}Z" class="shade"/>'
            f'<ellipse cx="{cx}" cy="{Y(157)}" rx="11" ry="2.4" class="glow"/>')
        d.a(f'<rect x="{cx - 18}" y="{Y(67)}" width="36" height="5" rx="2" class="stool"/>'
            f'<path d="M{cx - 14} {Y(62)}L{cx - 17} 240M{cx + 14} {Y(62)}L{cx + 17} 240M{cx - 15} {Y(25)}H{cx + 15}" class="stool-l"/>')
    d.t(75, 240 + T + 1.5 * d.fs, 'Hacia la sala', cls='dn', size=0.82)
    d.dimh(0, 150, 240 + T + 2.9 * d.fs, '1,50', size=0.8, below=True)
    # 2. corte (cocina a la izquierda, sala a la derecha)
    ox = 205
    d.a(f'<rect x="{ox}" y="{Y(88)}" width="60" height="78" class="m-lower eo2"/><rect x="{ox + 4}" y="{Y(10)}" width="54" height="10" class="zoc eo2"/>'
        f'<path d="M{ox} {Y(60)}H{ox + 60}M{ox} {Y(32)}H{ox + 60}" class="eo2"/>'
        f'<rect x="{ox + 58}" y="{Y(88)}" width="2" height="78" fill="{wpc}" class="eo2"/>'
        f'<rect x="{ox - 1}" y="{Y(90)}" width="92" height="2.6" fill="url(#pe-gr)" class="eo2"/>')
    d.a(f'<rect x="{ox + 84}" y="{Y(67)}" width="36" height="5" rx="2" class="stool"/>'
        f'<path d="M{ox + 88} {Y(62)}L{ox + 85} 240M{ox + 116} {Y(62)}L{ox + 119} 240M{ox + 87} {Y(25)}H{ox + 117}" class="stool-l"/>')
    d.t(ox + 45, 240 + T + 1.5 * d.fs, 'Corte', cls='dn', size=0.82)
    d.dimh(ox, ox + 60, Y(90) - 0.7 * d.fs, '60', size=0.78)
    d.dimh(ox + 60, ox + 90, Y(90) - 0.7 * d.fs, '30', size=0.78)
    d.dimv(240, Y(90), ox - 0.7 * d.fs, '0,90', size=0.78)
    d.t(ox + 30, Y(110), 'cocina', cls='dn', size=0.72)
    d.t(ox + 100, Y(110), 'sala', cls='dn', size=0.72)
    # 3. cara hacia la cocina (el occidente a la izquierda)
    ox = 360
    fr = [(ox, 50, 10, 88, 'door', 'l', 'm-lower'), (ox + 50, 50, 10, 32, 'drawer', None, 'm-lower'),
          (ox + 50, 50, 32, 60, 'drawer', None, 'm-lower'), (ox + 50, 50, 60, 88, 'drawer', None, 'm-lower'),
          (ox + 100, 50, 10, 88, 'door', 'r', 'm-lower')]
    d.a(f'<rect x="{ox}" y="{Y(10)}" width="150" height="10" class="zoc eo2"/>')
    d.a(fronts_svg(fr, [(ox, ox + 150, 88)]).replace(' eo"', ' eo2"'))
    d.a(f'<rect x="{ox}" y="{Y(90)}" width="150" height="2.4" fill="url(#pe-gr)" class="eo2"/>')
    d.t(ox + 75, 240 + T + 1.5 * d.fs, 'Hacia la cocina', cls='dn', size=0.82)
    d.dimh(ox, ox + 150, 240 + T + 2.9 * d.fs, '1,50', size=0.8, below=True)
    return d.svg('Península de 1,50 por 0,90 m: hacia la sala, frente en WPC acanalado con dos bancos y dos lámparas colgantes; en corte, 60 cm de mueble y 30 cm de voladizo a 90 cm de altura; hacia la cocina, puertas y cajones.')


def bath_elev():
    """Muro oriental de cada baño visto desde adentro: el norte (puerta) a la izquierda."""
    k, fs = 1.62, 10.5
    fsc = fs / k
    L = T + 2.4 * fsc
    d = D('be', (-L, -T - 4, 210 + L + T + 2.6 * fsc, 240 + T + 4 + T + 3.2 * fsc), k, fs)
    tw = d.pat('tw', 60, 30, 'm-tw', 'j-tw', 0, 0)
    g = [f'<rect x="0" y="0" width="210" height="240" fill="{tw}" class="eo"/>',
         f'<path d="M45 {Y(205)}V{Y(212)}" class="faucet"/><rect x="36" y="{Y(205)}" width="18" height="2.5" rx="1" class="metal"/>',
         f'<circle cx="45" cy="{Y(110)}" r="5" class="metal"/><path d="M45 {Y(110)}L53 {Y(114)}" class="faucet"/>',
         f'<rect x="88" y="{Y(200)}" width="3" height="200" class="glass-e"/>',
         f'<rect x="100" y="{Y(78)}" width="40" height="34" rx="3" class="porc eo"/><rect x="114" y="{Y(80)}" width="12" height="2" class="metal"/>'
         f'<path d="M103 {Y(42)}H137L131 {Y(0)}H109Z" class="porc eo"/><path d="M101 {Y(42)}H139" class="eo"/>',
         f'<rect x="150" y="{Y(87)}" width="60" height="3" class="porc eo"/><rect x="152" y="{Y(84)}" width="56" height="38" class="m-van eo"/>',
         f'<rect x="152" y="{Y(84)}" width="56" height="1.4" class="gola"/>',
         f'<path d="M180 {Y(87)}V{Y(100)}Q180 {Y(104)} 184 {Y(104)}H186" class="faucet"/>',
         f'<rect x="156" y="{Y(176)}" width="48" height="70" rx="2" class="mirror eo"/>',
         f'<rect x="156" y="{Y(176)}" width="48" height="26" fill="url(#be-led)"/>',
         f'<rect x="160" y="{Y(182)}" width="40" height="3" rx="1" class="ledbar"/>']
    d.a('<g transform="translate(210 0) scale(-1 1)">' + ''.join(g) + '</g>')
    elev_frame(d, 210)
    yb = 240 + T + 1.5 * d.fs
    for x0, wd, nm in ((0, 60, 'Mueble'), (60, 60, 'Sanitario'), (120, 90, 'Ducha')):
        d.dimh(x0, x0 + wd, yb, str(wd), size=0.85)
        d.t(x0 + wd / 2, yb + d.fs * 1.15, nm, cls='dn', size=0.8)
    xr = 210 + T + 0.9 * d.fs
    d.dimv(240, 40, xr, 'vidrio 8 mm · 2,00', size=0.8, right=True)
    d.dimv(240, 0, -T - 0.9 * d.fs, '2,40', size=0.85)
    return d.svg('Muro oriental del baño: mueble flotante de 60 cm con espejo y luz frontal junto a la puerta, sanitario y ducha al fondo con división de vidrio templado.')


def closet_elev():
    """Closet de la alcoba principal, 1,50 m junto a la ventana, sin puertas."""
    k, fs = 1.62, 10.5
    fsc = fs / k
    L = T + 2.4 * fsc
    W = 150
    d = D('ce', (-L, -T - 4, W + L + T + 4, 240 + T + 4 + T + 3.2 * fsc), k, fs)
    d.a(f'<rect x="0" y="0" width="{W}" height="240" class="m-cloin"/>')
    d.a(f'<rect x="0" y="{Y(8)}" width="{W}" height="8" class="m-clo eo"/>')

    def shelf(x0, x1, h):
        return f'<rect x="{x0}" y="{Y(h) - 1}" width="{x1 - x0}" height="2" class="m-clo eo"/>'

    def div(x):
        return f'<rect x="{x - 1}" y="0" width="2" height="{Y(8)}" class="m-clo eo"/>'

    def rod(x0, x1, h):
        return f'<path d="M{x0 + 3} {Y(h)}H{x1 - 3}" class="rod-e"/>'

    def clothes(x0, x1, h, bottoms):
        out = ''
        step = (x1 - x0 - 8) / len(bottoms)
        for i, b in enumerate(bottoms):
            x = x0 + 4 + i * step + 1
            out += f'<path d="M{x + step / 2 - 1} {Y(h)}V{Y(h - 3)}" class="eo"/>'
            out += f'<rect x="{x:.1f}" y="{Y(h - 3)}" width="{step - 2.5:.1f}" height="{h - 3 - b}" rx="2" class="cloth"/>'
        return out

    def drawers(x0, x1, hs):
        out = ''
        for h0, h1 in zip(hs, hs[1:]):
            out += f'<rect x="{x0 + 1.5}" y="{Y(h1) + .6}" width="{x1 - x0 - 3}" height="{h1 - h0 - 1.2}" class="m-clo eo"/>'
            out += f'<path d="M{(x0 + x1) / 2 - 7} {Y(h1 - 6)}H{(x0 + x1) / 2 + 7}" class="hdl"/>'
        return out

    def shoes(x0, x1, h):
        out = ''
        x = x0 + 5
        while x + 18 < x1:
            out += (f'<rect x="{x}" y="{Y(h + 9)}" width="7.5" height="8" rx="3" class="shoe"/>'
                    f'<rect x="{x + 8.5}" y="{Y(h + 9)}" width="7.5" height="8" rx="3" class="shoe"/>')
            x += 22
        return out

    a = div(100)
    a += shelf(0, 100, 200) + rod(0, 100, 188) + clothes(0, 100, 188, [112, 104, 118, 108, 120, 110])
    a += shelf(0, 100, 34) + shelf(0, 100, 64) + shoes(0, 100, 10) + shoes(0, 100, 34) + shoes(0, 100, 64)
    a += drawers(100, 150, [8, 38, 68, 98]) + shelf(100, 150, 130) + shelf(100, 150, 165) + shelf(100, 150, 200)
    b = div(50) + div(100) + shelf(0, W, 205)
    for x in range(12, W, 50):
        b += ''.join(f'<rect x="{x + i * 3}" y="{Y(232)}" width="1.3" height="12" class="vent"/>' for i in range(4))
    b += rod(0, 50, 196) + clothes(0, 50, 196, [132, 140, 128]) + rod(0, 50, 106) + clothes(0, 50, 106, [44, 52, 40])
    b += drawers(50, 100, [8, 33, 58, 83, 108]) + shelf(50, 100, 140) + shelf(50, 100, 172)
    b += shelf(100, 150, 36) + shelf(100, 150, 62) + shoes(100, 150, 10) + shoes(100, 150, 36) + shoes(100, 150, 62)
    b += rod(100, 150, 196) + clothes(100, 150, 196, [80, 88, 76])
    d.a(b)
    d.t(75, Y(220), 'Maletero', cls='le', size=0.85)
    elev_frame(d, W)
    yb = 240 + T + 1.5 * d.fs
    ga = gb = ''
    for x0, wd, nm in ((0, 100, 'Colgado + zapatero'), (100, 50, 'Cajones')):
        dd = D('x', (0, 0, 1, 1), k, fs)
        dd.dimh(x0, x0 + wd, yb, str(wd), size=0.85)
        dd.t(x0 + wd / 2, yb + d.fs * 1.15, nm, cls='dn', size=0.78)
        ga += ''.join(dd.p)
    for x0, wd, nm in ((0, 50, 'Doble'), (50, 50, 'Cajones'), (100, 50, 'Zapatos')):
        dd = D('x', (0, 0, 1, 1), k, fs)
        dd.dimh(x0, x0 + wd, yb, str(wd), size=0.85)
        dd.t(x0 + wd / 2, yb + d.fs * 1.15, nm, cls='dn', size=0.78)
        gb += ''.join(dd.p)
    d.a(gb)
    d.dimv(240, 0, -T - 0.9 * d.fs, '2,40 piso-techo', size=0.85)
    return d.svg('Interior del closet de 1,50 m de la alcoba principal: doble colgado, cajones, zapatero con colgado medio, maletero y ventilación.')


# ---------------------------------------------------------------- piezas HTML
def fig(svg, cap, cls='', scroll=True):
    inner = f'<div class="scroll">{svg}</div>' if scroll else svg
    return f'<figure class="fg {cls}">{inner}<figcaption>{cap}</figcaption></figure>'


def sw(var, label_a, label_b=None):
    lab = label_a if label_b is None else label_b
    return f'<span class="key"><span class="sw" style="--c:var(--m-{var})"></span>{lab}</span>'


def spec_table(rows, head=('Elemento', 'Especificación')):
    body = ''.join(f'<tr><td class="z">{a}</td><td>{b}</td></tr>' for a, b in rows)
    return f'<div class="tbl"><table><thead><tr><th>{head[0]}</th><th>{head[1]}</th></tr></thead><tbody>{body}</tbody></table></div>'


def note(kind, ic, html):
    return f'<div class="note {kind}"><span class="ic">{ic}</span><div>{html}</div></div>'


def swatches(lst, mats):
    return '<div class="pal">' + ''.join(
        f'<span class="chip"><span class="sw" style="background:{mats[k]}"></span>{n}</span>' for n, k in lst) + '</div>'


LEG_PLAN = ('<div class="legend">'
            '<span class="key"><span class="sw pat-spc"></span>SPC zonas secas</span>'
            '<span class="key"><span class="sw pat-tf"></span>Cerámica antideslizante</span>'
            '<span class="key"><span class="sw" style="--c:var(--m-clo)"></span>Carpintería RH (incluida)</span>'
            '<span class="key"><span class="sw" style="--c:var(--m-ctr)"></span>Mesón en piedra sinterizada</span>'
            '<span class="key"><span class="sw loose-k"></span>Mobiliario suelto (no incluido)</span>'
            '<span class="key"><span class="sw own-k"></span>Electrodoméstico propio</span>'
            '<span class="key"><span class="sw lt-k"></span>Luz de techo</span>'
            '</div>')


# ---------------------------------------------------------------- renders y muestras
def img_b(name, alt, w=1600, h=1000, eager=False, prefix=''):
    la = '' if eager else ' loading="lazy"'
    return f'<img src="img/{prefix}{name}-b.jpg" width="{w}" height="{h}" alt="{esc(alt)}"{la} decoding="async">'


def shot(name, alt, cap):
    return (f'<figure class="shot"><div class="shot-img">{img_b(name, alt)}'
            f'<span class="shot-tag">Render ilustrativo</span></div>'
            f'<figcaption>{cap}</figcaption></figure>')


RENDER_NOTE = ('<p class="disc">Renders generados por computador con las medidas y los materiales de la propuesta. '
               'Muebles sueltos, nevera y lavadora son de referencia, la ubicación de ventanas es supuesta y los colores son aproximados.</p>')

ALT = {
    'cocina': 'Render de la cocina vista desde la sala: península con frente en WPC acanalado, dos bancos y colgantes, y el mueble gris piedra sobre el muro sur.',
    'ropas': 'Render de la cocina desde la entrada: mesón a la derecha, península a la izquierda, nevera, torre y ropas al fondo.',
    'sala': 'Render de la sala-comedor desde la cocina: península en primer plano, sofá, TV y puerta-ventana al balcón.',
    'bano': 'Render del baño principal desde la puerta: mueble en roble natural, grifería inoxidable, sanitario y ducha con ventana al fondo.',
    'alcoba': 'Render de la alcoba principal: closet en roble natural de 1,50 m junto a la ventana y cama con cabecero al oriente.',
}

MATROWS = [
    ('Piso de zonas secas', 'Alcobas, sala-comedor y cocina', 'spc-b', 'SPC roble natural', 'Capa de uso y base acústica IXPE, con ficha técnica.'),
    ('Muros y techos', 'Todo el apartamento', 'paint', 'Blanco cálido', 'Estuco y pintura lavable de mejor gama.'),
    ('Muebles altos de cocina', 'Fondo 30–35 cm, alto 70–80 cm', 'upper-b', 'Melamina RH blanco cálido', 'Herrajes de marca con garantía.'),
    ('Muebles bajos y península', 'Cocina, península y torre', 'lower-b', 'Melamina RH gris piedra suave', 'Cantos de 2 mm y perfil tipo gola.'),
    ('Frente de la península', 'Cara hacia la sala', 'wpc-b', 'WPC acanalado roble natural', 'Frente y costado de la península.'),
    ('Mesón', 'Muro sur y península, 12 mm', 'ctr-b', 'Piedra sinterizada blanca mate', 'Color en masa y ficha técnica; no requiere sellado.'),
    ('Salpicadero', 'Del mesón a los muebles altos', 'sp-b', 'Cerámica marmolizada 30 × 60', 'La propuesta admite blanca o marmolizada.'),
    ('Closets y mueble de baño', 'Tres alcobas y dos baños', 'clo-b', 'Melamina RH roble natural', 'Color sugerido dentro de la paleta.'),
    ('Piso de baños, ropas y balcón', 'Cerámica antideslizante', 'tf-b', 'Cerámica 30 × 30 gris piedra', 'Tono sugerido.'),
    ('Muros de baños', 'Y enchape de ropas a 1,20 m', 'tw-b', 'Cerámica clara 30 × 60', 'Impermeabilización con prueba y acta.'),
    ('Herrajes y grifería', 'Manijas, barras y griferías', 'metal-b', 'Inoxidable y perfil de aluminio', 'Cocina con perfil tipo gola, sin manijas.'),
]


def mcard(el, where, sid, name, note_):
    return (f'<figure class="mcard"><img src="img/m-{sid}.jpg" width="640" height="480" alt="Muestra: {esc(name)}" loading="lazy" decoding="async">'
            f'<figcaption><span class="mel">{el}</span><b>{name}</b><small>{note_} {where}.</small></figcaption></figure>')


mat_rows_html = '<div class="mgrid2">' + ''.join(mcard(*r) for r in MATROWS) + '</div>'

GALLERY = f'''
<div class="gal">
  <button type="button" class="gal-main" data-go="sala">{img_b('sala', ALT['sala'], eager=True)}<span class="gal-cap">Sala-comedor hacia el balcón</span></button>
  <div class="gal-grid">
    <button type="button" class="gal-t" data-go="cocina">{img_b('cocina', ALT['cocina'], w=640, h=400, prefix='t-')}<span class="gal-cap">Cocina</span></button>
    <button type="button" class="gal-t" data-go="cocina">{img_b('ropas', ALT['ropas'], w=640, h=400, prefix='t-')}<span class="gal-cap">Desde la entrada</span></button>
    <button type="button" class="gal-t" data-go="banos">{img_b('bano', ALT['bano'], w=640, h=400, prefix='t-')}<span class="gal-cap">Baño</span></button>
    <button type="button" class="gal-t" data-go="alcobas">{img_b('alcoba', ALT['alcoba'], w=640, h=400, prefix='t-')}<span class="gal-cap">Alcoba principal</span></button>
  </div>
</div>'''

# ---------------------------------------------------------------- dibujos
PLAN_FULL = plan_svg('pl', (-385, -470, 960, 790), 0.84, 'Planta completa del Apto 901, espejo del Tipo A: alcobas 2 y 3 y baño auxiliar al occidente, sala-comedor con balcón al norte, cocina abierta a la sala con entrada por el sur, alcoba principal, baño y ropas al oriente.', mode='full')
PLAN_COCINA = plan_svg('pk', (-45, -130, 495, 440), 1.3, 'Planta de la cocina: mueble de 2,03 m sobre el muro sur entre la entrada y ropas, nevera y torre al frente; en B, península de 1,50 por 0,90 m hacia la sala con dos bancos y pasillo de 1,10 m.', dims=dims_kitchen)
PLAN_SALA = plan_svg('ps', (-50, -480, 370, 540), 0.95, 'Planta de la sala-comedor: sofá contra el muro oriental, TV en el muro occidental y balcón al norte.', dims=dims_sala)
PLAN_AP = plan_svg('pa', (232, -395, 343, 428), 0.95, 'Planta de la alcoba principal: closet de 1,50 m junto a la ventana norte y cama con cabecero al oriente.', dims=dims_room(281, -339, 529, -15, '2,50', '3,38'))
PLAN_A2 = plan_svg('p2', (-298, -442, 318, 367), 0.95, 'Planta de la alcoba 2: cama contra el muro norte y closet de 1,45 m sobre el muro sur.', dims=dims_room(-246, -385, -16, -105, '2,30', '2,80'))
PLAN_A3 = plan_svg('p3', (-398, -140, 288, 355), 0.95, 'Planta de la alcoba 3: cama al occidente y closet corredizo de 1,20 m al oriente.', dims=dims_room(-341, -90, -140, 166, '2,00', '2,55'))
PLAN_BP = plan_svg('pb', (368, -52, 205, 330), 1.15, 'Planta del baño principal: mueble, sanitario y ducha sobre el muro oriental, ventana en la ducha.', dims=dims_room(421, 1, 529, 230, '1,10', '2,10'))
PLAN_BA = plan_svg('pu', (-178, -38, 200, 316), 1.15, 'Planta del baño auxiliar: mueble, sanitario y ducha sobre el muro oriental, ventana en la ducha.', dims=dims_room(-125, 15, -16, 230, '1,10', '2,10'))
KE, PE, BE, CE = kitchen_elev(), peninsula_elev(), bath_elev(), closet_elev()

# ---------------------------------------------------------------- presupuesto
CH = [
    ('Logística, protecciones y limpieza', (1.0, 1.4), 'Protección de zonas comunes, acarreos, escombros, aseo y control de entrega'),
    ('Preparación, nivelación e impermeabilización', (1.5, 2.3), 'Diagnóstico, nivelación y pruebas de humedad y estanqueidad'),
    ('Muros, estuco y pintura', (3.0, 3.7), 'Estuco, pintura lavable de mejor gama y remates'),
    ('Pisos SPC, cerámicas y transiciones', (4.7, 5.7), 'SPC con base acústica, cerámicas, zócalos y perfiles'),
    ('Cocina + ropas', (8.0, 9.2), 'Carpintería RH, mesón, salpicadero, herrajes de marca y circuitos'),
    ('Dos baños completos', (7.3, 8.5), 'Impermeabilización reforzada, enchapes, aparatos, griferías y divisiones'),
    ('Closets de tres alcobas', (3.8, 4.6), 'Melamina RH, distribución interna, herrajes y ventilación'),
    ('Eléctrico, iluminación, drywall y balcón', (2.2, 3.0), 'Circuitos, puntos, escenas de luz y acabados de balcón'),
    ('Península 1,50 × 0,90 *', (2.0, 3.5), 'Estimado propio: mueble RH, mesón, frente WPC, toma y colgantes'),
    ('Mesones en piedra sinterizada **', (1.5, 2.5), 'Estimado propio: diferencia frente al granito de la propuesta'),
]
SCALE = 10.0


def mm(v):
    return f"{v:.1f}".replace('.', ',')


def rng(lo, hi):
    return f'${mm(lo)}–{mm(hi)} M'


rows = ''
for name, b, desc in CH:
    bar = f'<span class="rb" style="left:{b[0] / SCALE * 100:.2f}%;width:{(b[1] - b[0]) / SCALE * 100:.2f}%" title="{name}: {rng(*b)}"></span>'
    rows += (f'<tr><td class="cap"><b>{name}</b><small>{desc}.</small></td>'
             f'<td class="trk"><div class="track">{bar}</div></td>'
             f'<td class="num vb">{rng(*b)}</td></tr>')
ticks = ''.join(f'<span style="left:{v / SCALE * 100:.0f}%">{v:g}</span>' for v in (0, 2, 4, 6, 8, 10))
budget_html = f'''
<div class="tbl budget"><table>
<thead><tr><th>Capítulo</th><th class="trk"><div class="ticks">{ticks}</div></th><th class="num">Rango</th></tr></thead>
<tbody>{rows}</tbody>
</table></div>'''

# ---------------------------------------------------------------- CSS
CSS = r'''
/* Layout: encabezado de ficha técnica + barra de vistas fija; cada vista es una lámina con dibujos a escala y su especificación. */
:root{
  --paper:#F4F1EB; --card:#FBFAF7; --ink:#1B2334; --muted:#5C6373;
  --line:#DED8CD; --line-strong:#C8C0B2;
  --accent:#DB6224; --accent-soft:#F3E2D5;
  --ok:#2E7D5B; --ok-soft:#DCEBE2;
  --warn:#B9791E; --warn-soft:#F3E7CE;
  --part:#5B72A8; --part-soft:#E0E5F1;
  --blueprint:#2C3550;
  --sA:#D35F22; --sB:#3E62B5; --sA-soft:#F6E1D3; --sB-soft:#DEE5F5; --on-s:#FFFFFF;
  --d-poche:#343C4E; --d-line:#3C4456; --d-dim:#6A7080; --d-loose:#FFFFFF; --d-trans:#8A6A3E;
  --shadow:0 1px 2px rgba(27,35,52,.06),0 6px 20px rgba(27,35,52,.05);
  --f-display:"Archivo","Arial Narrow",system-ui,sans-serif;
  --f-body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  --f-mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  MATB MATC
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --paper:#151821; --card:#1D212C; --ink:#ECE9E2; --muted:#9AA0AE;
    --line:#2C313E; --line-strong:#3A4150;
    --accent:#F0783C; --accent-soft:#3A2517;
    --ok:#5FB98C; --ok-soft:#1B2E26;
    --warn:#E0A94A; --warn-soft:#332813;
    --part:#94A6D6; --part-soft:#1E2436;
    --blueprint:#AEB7D2;
    --sA:#E06E34; --sB:#6F8FE0; --sA-soft:#3A2517; --sB-soft:#1E2640;
    --d-poche:#8E98B2; --d-line:#C3C8D4; --d-dim:#9AA0AE; --d-loose:#262B37; --d-trans:#E0B77A;
    --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.28);
    color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#151821; --card:#1D212C; --ink:#ECE9E2; --muted:#9AA0AE;
  --line:#2C313E; --line-strong:#3A4150;
  --accent:#F0783C; --accent-soft:#3A2517;
  --ok:#5FB98C; --ok-soft:#1B2E26;
  --warn:#E0A94A; --warn-soft:#332813;
  --part:#94A6D6; --part-soft:#1E2436;
  --blueprint:#AEB7D2;
  --sA:#E06E34; --sB:#6F8FE0; --sA-soft:#3A2517; --sB-soft:#1E2640;
  --d-poche:#8E98B2; --d-line:#C3C8D4; --d-dim:#9AA0AE; --d-loose:#262B37; --d-trans:#E0B77A;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.28);
  color-scheme:dark;
}
*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);font-family:var(--f-body);line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:940px;margin:0 auto;padding-inline:22px}
.bar .wrap{max-width:1120px}
@media(max-width:520px){.wrap{padding-inline:16px}}
h1,h2,h3{font-family:var(--f-display);text-wrap:balance;line-height:1.12;margin:0}
.mono{font-family:var(--f-mono);font-variant-numeric:tabular-nums}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}

header .top{padding-block:34px 26px}
.eyebrow{font-family:var(--f-mono);font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);font-weight:600}
.top h1{font-size:clamp(2rem,5.5vw,3.1rem);font-weight:800;letter-spacing:-.01em;margin:.35em 0 .15em}
.lede{color:var(--muted);font-size:1.02rem;max-width:64ch;margin:.2em 0 0}
.ficha{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:22px 0 0}
.ficha div{background:var(--card);padding:11px 14px;min-width:0}
.ficha dt{font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:600}
.ficha dd{margin:3px 0 0;font-weight:600;font-size:1rem}
.ficha dd small{display:block;font-weight:400;font-size:.76rem;color:var(--muted)}

/* barra de vistas */
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:var(--paper);border-block:1px solid var(--line)}
.bar-in{display:flex;align-items:center;gap:14px;flex-wrap:wrap;padding-block:8px}
.tabs{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none;flex:1 1 420px;min-width:0}
.tabs::-webkit-scrollbar{display:none}
.tab{appearance:none;border:0;background:none;color:var(--muted);font:600 .84rem/1 var(--f-body);padding:9px 10px;border-radius:8px;white-space:nowrap;cursor:pointer}
.tab:hover{color:var(--ink);background:var(--card)}
.tab[aria-selected="true"]{color:var(--ink);background:var(--card);box-shadow:inset 0 -2px 0 var(--accent)}
.opt{display:flex;align-items:center;gap:8px;flex:0 0 auto}
.opt .lbl{font-family:var(--f-mono);font-size:.66rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:600}
.seg{display:inline-flex;border:1px solid var(--line-strong);border-radius:9px;padding:2px;background:var(--card)}
.seg button{appearance:none;border:0;background:none;color:var(--muted);font:600 .8rem/1 var(--f-body);padding:8px 11px;border-radius:7px;cursor:pointer;display:inline-flex;gap:6px;align-items:center}
.optchip{display:inline-grid;place-items:center;width:18px;height:18px;border-radius:5px;font:700 .7rem/1 var(--f-mono);color:var(--on-s)}
.optchip.a{background:var(--sA)} .optchip.b{background:var(--sB)}
@media(max-width:620px){.bar-in{gap:6px}.opt{width:100%}.seg{width:100%}.seg button{flex:1;justify-content:center}}

.view{padding-block:34px 44px}
.kicker{font-family:var(--f-mono);font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);font-weight:600;margin-bottom:8px}
h2{font-size:clamp(1.45rem,3.6vw,2rem);font-weight:700;letter-spacing:-.01em}
h2 .em{color:var(--accent)}
.sub{color:var(--muted);max-width:66ch;margin:10px 0 0}
h3{font-size:1.08rem;font-weight:700;margin:0 0 4px}
.block{margin-top:30px}
.block > h3{margin-bottom:10px}

/* dibujos */
.figs{display:flex;flex-wrap:wrap;gap:22px 28px;align-items:flex-start;margin-top:22px}
.fg{margin:0;min-width:0;max-width:100%;width:min-content}
.fg figcaption{font-size:.8rem;color:var(--muted);margin-top:8px}
.fg figcaption b{color:var(--ink);font-weight:600}
.scroll{overflow-x:auto;max-width:100%}
.panel{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 18px 14px;box-shadow:var(--shadow)}
svg.dw{display:block;height:auto;max-width:none;overflow:visible}
svg.dw *{vector-effect:non-scaling-stroke}
.sheet{display:flex;flex-wrap:wrap;gap:22px 26px;align-items:flex-end;margin-top:20px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:var(--shadow)}
.sheet .rm{margin:0;display:flex;flex-direction:column;gap:6px;width:min-content;max-width:100%}
.rm figcaption{font-size:.78rem;line-height:1.35}
.rm figcaption b{display:block;font-weight:600}
.rm figcaption .mono{color:var(--muted);font-size:.72rem}

.pc{fill:var(--d-poche)}
.ol{stroke:var(--d-line);stroke-width:1}
.m-spc{fill:var(--m-spc)} .j-spc{stroke:var(--m-spc-j);stroke-width:.6;fill:none}
.m-tf{fill:var(--m-tf)} .j-tf{stroke:var(--m-tf-j);stroke-width:.6;fill:none}
.m-tw{fill:var(--m-tw)} .j-tw{stroke:var(--m-tw-j);stroke-width:.6;fill:none}
.m-sp{fill:var(--m-sp)} .j-sp{stroke:var(--m-sp-j);stroke-width:.6;fill:none}
.m-ctr{fill:var(--m-ctr)} .m-ctrf{fill:var(--m-ctr-f)}
.m-paint{fill:var(--m-paint)} .m-upper{fill:var(--m-upper)} .m-lower{fill:var(--m-lower)}
.m-clo{fill:var(--m-clo)} .m-cloin{fill:var(--m-clo-in)} .m-van{fill:var(--m-van)}
.porc{fill:var(--m-porc)} .steel{fill:var(--m-steel)} .lav{fill:var(--m-lav)} .lavb{fill:var(--m-steel);stroke:var(--d-line);stroke-width:.8}
.metal{fill:var(--m-metal)} .zoc{fill:var(--m-zoc)} .mirror{fill:var(--m-mirror)}
.cook{fill:var(--m-ctr);stroke:var(--m-steel);stroke-width:1}
.burner{fill:none;stroke:var(--m-steel);stroke-width:1.4}
.drain{fill:var(--m-steel);stroke:var(--d-line);stroke-width:.8}
.hid{fill:none;stroke:var(--d-line);stroke-width:1;stroke-dasharray:4 3;opacity:.75}
.trans{fill:none;stroke:var(--d-trans);stroke-width:1.6;stroke-dasharray:6 3}
.own{fill:none;stroke:var(--d-line);stroke-width:1.2;stroke-dasharray:5 3}
.loose rect,.loose circle,rect.loose,circle.loose{fill:var(--d-loose);stroke:var(--d-line);stroke-width:1.1}
.loose .fold{fill:none;stroke:var(--d-line);stroke-width:.8}
.rod{fill:none;stroke:var(--d-line);stroke-width:1;stroke-dasharray:2 3}
.front{stroke:var(--d-line);stroke-width:2.2}
.swing{fill:none;stroke:var(--d-line);stroke-width:.8;stroke-dasharray:3 3;opacity:.8}
.glass{stroke:var(--m-glass-l);stroke-width:2.6;fill:none}
.rail{stroke:var(--d-line);stroke-width:3;fill:none;stroke-dasharray:1 3}
.lt circle{fill:var(--m-led);stroke:var(--d-line);stroke-width:1}
.lt path{stroke:var(--d-line);stroke-width:.9;fill:none}
.dim path{stroke:var(--d-dim);stroke-width:1;fill:none}
.dt{font-family:var(--f-mono);fill:var(--d-dim);font-weight:500}
.dn{font-family:var(--f-body);fill:var(--muted)}
.lb{font-family:var(--f-body);font-weight:600;fill:var(--ink);paint-order:stroke;stroke:var(--card);stroke-width:var(--hw);stroke-linejoin:round}
.le{font-family:var(--f-body);font-weight:600;fill:var(--m-e-line);paint-order:stroke;stroke:var(--m-e-halo);stroke-width:var(--hw);stroke-linejoin:round}
/* alzados */
.eo{stroke:var(--m-e-line);stroke-width:1}
.own-e{fill:none;stroke:var(--m-e-line);stroke-width:1.2;stroke-dasharray:5 3}
.hdl{stroke:var(--m-metal);stroke-width:2.6;stroke-linecap:round;fill:none}
.gola{fill:var(--m-metal)}
.faucet{stroke:var(--m-metal);stroke-width:2.6;fill:none;stroke-linecap:round}
.oven-win{fill:var(--m-oven);stroke:var(--m-e-line);stroke-width:1}
.outlet{fill:var(--m-outlet);stroke:var(--m-e-line);stroke-width:.9}
.ledl{stroke:var(--m-led);stroke-width:3;fill:none}
.ledbar{fill:var(--m-led);stroke:var(--m-e-line);stroke-width:.8}
.led0{stop-color:var(--m-led);stop-opacity:.9} .led1{stop-color:var(--m-led);stop-opacity:0}
.glass-e{fill:var(--m-glass);stroke:var(--m-glass-l);stroke-width:1}
.opt-mark{fill:none;stroke:var(--sB);stroke-width:1.6;stroke-dasharray:6 4}
.rod-e{stroke:var(--m-metal);stroke-width:2.4;fill:none;stroke-linecap:round}
.cloth{fill:var(--m-cloth);stroke:var(--m-e-line);stroke-width:.6}
.shoe{fill:var(--m-shoe)}
.vent{fill:var(--m-e-line);opacity:.55}
.brk{fill:none;stroke:var(--d-dim);stroke-width:1}
svg.dw.crop{overflow:hidden}
.only-a{display:none!important}
.win{fill:var(--card);stroke:var(--d-line);stroke-width:.8}
.leaf{stroke:var(--d-line);stroke-width:1.5;fill:none}
.duct{fill:var(--line);stroke:var(--d-line);stroke-width:1}
.duct-x{stroke:var(--d-line);stroke-width:.6;fill:none}
.arrow{fill:var(--d-line)}
.lbd{fill:var(--muted)}
.sill{fill:var(--m-paint)}
.door{fill:var(--m-door)}
.hdl-d{stroke:var(--m-steel);stroke-width:2.6;stroke-linecap:round;fill:none}
.eo2{stroke:var(--d-line);stroke-width:1}
path.eo2:not([class*="m-"]){fill:none}
.m-wpc{fill:var(--m-wpc)} .j-wpc{stroke:var(--m-wpc-j);stroke-width:.7;fill:none}
.cable{stroke:var(--d-line);stroke-width:.8;fill:none}
.shade{fill:var(--m-metal);stroke:var(--d-line);stroke-width:.8}
.glow{fill:var(--m-led)}
.stool{fill:var(--d-loose);stroke:var(--d-line);stroke-width:1.1}
.stool-l{stroke:var(--d-line);stroke-width:1.4;fill:none}


/* leyendas */
.legend{display:flex;flex-wrap:wrap;gap:8px 16px;margin-top:14px;font-size:.8rem;color:var(--muted)}
.key{display:inline-flex;align-items:center;gap:7px}
.sw{width:16px;height:12px;border-radius:3px;background:var(--c,transparent);border:1px solid var(--line-strong);flex:0 0 auto}
.sw.pat-spc{background:repeating-linear-gradient(90deg,var(--m-spc) 0 5px,var(--m-spc-j) 5px 6px)}
.sw.pat-tf{background:var(--m-tf);background-image:linear-gradient(var(--m-tf-j) 1px,transparent 1px),linear-gradient(90deg,var(--m-tf-j) 1px,transparent 1px);background-size:6px 6px}
.sw.loose-k{background:var(--d-loose);border-color:var(--d-line)}
.sw.own-k{background:transparent;border:1.5px dashed var(--d-line)}
.sw.lt-k{background:var(--m-led);border-radius:50%;width:12px;border-color:var(--d-line)}

/* tablas */
.tbl{overflow-x:auto;margin-top:16px;border:1px solid var(--line);border-radius:12px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:.9rem;min-width:520px}
thead th{text-align:left;font-family:var(--f-mono);font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600;padding:11px 14px;border-bottom:1px solid var(--line-strong);vertical-align:bottom}
tbody td{padding:10px 14px;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr:last-child td{border-bottom:none}
td.z{font-weight:600;white-space:nowrap}
.num{text-align:right;font-family:var(--f-mono);font-variant-numeric:tabular-nums;white-space:nowrap}
tfoot td{padding:11px 14px;font-weight:700;border-top:2px solid var(--line-strong)}

/* bloques */
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:18px}
.grid2 > *{min-width:0}
@media(max-width:700px){.grid2{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;box-shadow:var(--shadow)}
.card ul,.bblock ul{margin:8px 0 0;padding-left:0;list-style:none}
.card li,.bblock li{position:relative;padding:6px 0 6px 18px;border-top:1px dashed var(--line);font-size:.9rem}
.card li:first-child,.bblock li:first-child{border-top:none}
.card li::before,.bblock li::before{content:"";position:absolute;left:2px;top:14px;width:6px;height:6px;border-radius:50%;background:var(--accent)}
.bblock{margin-top:16px;border:1px solid var(--line);border-radius:12px;padding:14px 18px;background:var(--card);transition:border-color .2s,box-shadow .2s}
.bblock li::before{background:var(--sB)}
.bhead{display:flex;align-items:center;gap:9px}
.bhead h3{margin:0}
.ref{display:inline-block;font-family:var(--f-mono);font-size:.62rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;padding:2px 6px;border-radius:5px;background:var(--accent-soft);color:var(--accent);margin-right:7px;vertical-align:1px}
.note{display:flex;gap:12px;background:var(--accent-soft);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:10px;padding:13px 16px;margin-top:18px;font-size:.9rem}
.note.blue{background:var(--part-soft);border-left-color:var(--part)}
.note .ic{flex:0 0 auto;font-family:var(--f-display);font-weight:800;color:var(--accent)}
.note.blue .ic{color:var(--part)}
.pill{display:inline-flex;align-items:center;gap:5px;font-family:var(--f-mono);font-size:.68rem;font-weight:600;letter-spacing:.03em;text-transform:uppercase;padding:3px 9px;border-radius:999px;white-space:nowrap}
.pill.ok{background:var(--ok-soft);color:var(--ok)} .pill.part{background:var(--part-soft);color:var(--part)}
.dot{width:7px;height:7px;border-radius:50%;display:inline-block}
.dot.ok{background:var(--ok)} .dot.part{background:var(--part)}

/* resumen: opciones */
.opts{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:22px}
@media(max-width:700px){.opts{grid-template-columns:1fr}}
.oc{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:var(--shadow);cursor:pointer;display:flex;flex-direction:column;gap:10px;min-width:0}
.oc:hover{border-color:var(--line-strong)}
.oc .oh{display:flex;align-items:center;gap:10px}
.oc .oh h3{margin:0;font-size:1.15rem}
.pick{margin-left:auto;appearance:none;border:1px solid var(--line-strong);background:var(--paper);color:var(--ink);font:600 .72rem/1 var(--f-body);padding:7px 10px;border-radius:999px;cursor:pointer}
.pick[aria-pressed="true"]{background:var(--card);color:var(--muted);cursor:default}
.oc .amts{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.oc .amts > span{min-width:0;display:block}
.oc .amts small{display:block;font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-weight:600}
.oc .amt{font-family:var(--f-display);font-weight:800;font-size:1.3rem;letter-spacing:-.01em;white-space:nowrap}
.oc p{margin:0;font-size:.86rem;color:var(--muted)}
.oc p b{color:var(--ink);font-weight:600}
.pal{display:flex;flex-wrap:wrap;gap:6px}
.chip{display:inline-flex;align-items:center;gap:6px;font-size:.74rem;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:3px 9px 3px 4px;background:var(--paper)}
.chip .sw{width:14px;height:14px;border-radius:50%}
.reco{margin-top:22px;border:1px solid var(--accent);border-radius:14px;padding:18px 20px;background:var(--card);box-shadow:0 0 0 1px var(--accent),var(--shadow)}
.reco .tag{font-family:var(--f-mono);font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:600}
.reco h3{font-size:1.3rem;margin:4px 0 6px}
.reco p{margin:0;color:var(--muted);max-width:68ch}
.five{list-style:none;padding:0;margin:14px 0 0;display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px}
.five li{border:1px solid var(--line);border-radius:10px;padding:10px 12px;background:var(--paper);font-size:.86rem;min-width:0}
.five li b{display:block;font-weight:600;line-height:1.3}
.five li button{appearance:none;border:0;background:none;padding:0;margin-top:4px;color:var(--accent);font:600 .76rem/1.3 var(--f-body);cursor:pointer;text-decoration:underline;text-underline-offset:2px}
.ceiling{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:14px;font-size:.88rem}
.ceiling span{font-family:var(--f-mono);font-variant-numeric:tabular-nums;font-weight:600}

/* presupuesto */
.budget table{min-width:600px}
.budget td.cap b{display:block;font-weight:600}
.budget td.cap small{display:block;color:var(--muted);font-size:.76rem;line-height:1.4;margin-top:2px;max-width:40ch}
.budget th.trk,.budget td.trk{width:38%;min-width:220px}
.track{position:relative;height:30px;margin-top:4px;background-image:linear-gradient(90deg,var(--line) 1px,transparent 1px);background-size:20% 100%;border-right:1px solid var(--line)}
.rb{position:absolute;height:10px;border-radius:3px;min-width:4px;transition:opacity .2s}
.rb{top:10px;background:var(--sB)}
.ticks{position:relative;height:14px}
.ticks span{position:absolute;transform:translateX(-50%);font-size:.66rem}
.ticks span:first-child{transform:none} .ticks span:last-child{transform:translateX(-100%)}
.budget td.va,.budget td.vb{padding-top:12px}
td.dl{color:var(--muted);padding-top:12px}
.totals td:first-child{font-weight:600}
.totals tr.big td{font-weight:700;background:var(--accent-soft)}
.totals .ca,.totals .cb{color:var(--muted)}

/* obra */
.steps{margin-top:18px;display:grid;gap:2px}
.step{display:grid;grid-template-columns:38px 1fr;gap:14px;align-items:start;background:var(--card);border:1px solid var(--line);padding:12px 15px}
.step:first-child{border-radius:12px 12px 0 0} .step:last-child{border-radius:0 0 12px 12px}
.step .n{font-family:var(--f-display);font-weight:800;font-size:1.02rem;color:var(--accent);background:var(--accent-soft);border-radius:8px;height:34px;display:flex;align-items:center;justify-content:center}
.step h3{font-size:.97rem;margin:4px 0 2px}
.step p{margin:0;font-size:.86rem;color:var(--muted)}
.checks{list-style:none;margin:10px 0 0;padding:0}
.checks li{border-top:1px dashed var(--line);padding:0}
.checks li::before{display:none}
.checks li:first-child{border-top:none}
.checks label{display:flex;gap:10px;align-items:flex-start;padding:8px 0;font-size:.9rem;cursor:pointer}
.checks input{margin-top:4px;accent-color:var(--accent);width:16px;height:16px;flex:0 0 auto}
.checks input:checked + span{color:var(--muted);text-decoration:line-through;text-decoration-color:var(--line-strong)}
.prog{font-family:var(--f-mono);font-size:.72rem;color:var(--muted);margin-left:auto}
.card h3{display:flex;align-items:center;gap:8px}
footer{padding-block:28px 46px;color:var(--muted);font-size:.84rem;border-top:1px solid var(--line)}
.disc{font-size:.78rem;color:var(--muted);margin-top:12px;padding-top:12px;border-top:1px dashed var(--line)}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
'''
CSS = CSS.replace('MATC', mat_css(MAT_C)).replace('MATB', mat_css(MAT_B))

# ---------------------------------------------------------------- contenido
TABS = [('resumen', 'Resumen'), ('materiales', 'Materiales'), ('planta', 'Planta'), ('cocina', 'Cocina y ropas'), ('banos', 'Baños'),
        ('alcobas', 'Alcobas'), ('sala', 'Sala y balcón'), ('presupuesto', 'Presupuesto'), ('obra', 'Obra'),
        ('entrega', 'Entrega')]

tabs_html = ''.join(
    f'<button class="tab" role="tab" id="t-{k}" aria-controls="v-{k}" data-go="{k}" aria-selected="{"true" if i == 0 else "false"}"'
    f' tabindex="{0 if i == 0 else -1}">{v}</button>' for i, (k, v) in enumerate(TABS))

V = {}

V['resumen'] = f'''
<div class="kicker">Opción B mejorada · con península</div>
<h2>La Mejorada, con <span class="em">península</span> hacia la sala</h2>
<p class="sub">Todo sigue el plano real del Apto 901, espejo del Tipo A. La península de 1,50 × 0,90 m separa la cocina de la sala y sirve de barra para dos personas.</p>
{GALLERY}
<p class="disc">Renders ilustrativos. Toca una imagen para ir a ese espacio.</p>

<div class="reco">
  <div class="tag">Plan de obra blanca</div>
  <h3>B mejorada + península</h3>
  <p>Una península de 1,50 × 0,90 m en el límite entre cocina y sala. Tiene 60 cm de mueble del lado de la cocina y 30 cm de voladizo del lado de la sala, con mesón en piedra sinterizada blanca y frente en WPC acanalado.</p>
  <ol class="five">
    <li><b>Pasillo de 1,10 m</b>Entre la península y el mesón, y 1,15 m libres desde la entrada.<br><button type="button" data-go="planta">Ver en Planta</button></li>
    <li><b>Agua y gas en su sitio</b>Lavaplatos y estufa donde Inacar deja las redes.<br><button type="button" data-go="cocina">Ver en Cocina</button></li>
    <li><b>Nevera y torre al frente</b>Contra el muro de la alcoba principal, junto a ropas.<br><button type="button" data-go="cocina">Ver en Cocina</button></li>
    <li><b>Barra para dos</b>Hace de comedor, con dos lámparas colgantes.<br><button type="button" data-go="sala">Ver en Sala</button></li>
    <li><b>Puerta de la alcoba libre</b>El voladizo va solo donde están los bancos.<br><button type="button" data-go="cocina">Ver en Cocina</button></li>
  </ol>
  <div class="ceiling">Total estimado: <span>$35,5–41,5 M sin electrodomésticos</span><span>$37,5–43,5 M con electrodomésticos</span></div>
  {swatches(SWATCH_B, MAT_B)}
</div>
{note('blue', 'i', '<b>La península no está en la propuesta.</b> El documento no la cotiza por separado. Sumo un estimado propio de $2,0–3,5 M para mueble RH, mesón, frente en WPC, toma y lámparas. Pide que la coticen como capítulo aparte.')}

<div class="grid2">
  <div class="card"><h3>Qué incluye la Opción B</h3><ul>
    <li><b>Impermeabilización con prueba</b> de estanqueidad y acta en duchas, ropas y balcón.</li>
    <li><b>SPC con ficha técnica:</b> marca, capa de uso, base acústica y garantía.</li>
    <li><b>Herrajes de marca</b> con referencia y garantía en cocina y closets.</li>
    <li><b>Circuitos dedicados</b> para horno, nevera, lavadora y pequeños electrodomésticos.</li>
    <li><b>Garantías y actas de entrega</b> por capítulo, con saldo retenido.</li>
  </ul></div>
  <div class="card"><h3>Cambios frente a la versión anterior</h3><ul>
    <li><b>Mesones:</b> piedra sinterizada blanca mate en lugar del granito de la propuesta.</li>
    <li><b>Una sola opción:</b> se quitó la Optimizada; la página muestra solo la B con península.</li>
    <li><b>Plano real:</b> dibujos y renders siguen el plano comercial del 901, con puertas, ventanas y ductos en su sitio.</li>
    <li><b>Cocina:</b> el mueble va sobre el muro sur y mide 2,03 m; la nevera y la torre pasan al frente.</li>
    <li><b>Closets:</b> caben unos 1,50 m en la principal (la propuesta decía 2,50), 1,45 m en la alcoba 2 y 1,20 m en la alcoba 3.</li>
  </ul></div>
</div>
{note('', '!', '<b>Aviso de precisión.</b> Las vistas son conceptuales y el plano comercial da medidas aproximadas. No se debe fabricar carpintería, cortar piedra ni mover redes sin medir el apartamento en obra gris.')}
'''

V['materiales'] = f'''
<div class="kicker">Materiales · muestras generadas por computador</div>
<h2>Los materiales de la Opción B</h2>
<p class="sub">Paleta de roble natural, blanco cálido y gris piedra suave. Los colores en pantalla son aproximados: pide muestras físicas y fichas técnicas antes de comprar.</p>
{mat_rows_html}
{note('blue', 'i', '<b>Qué define la propuesta y qué es sugerencia.</b> La propuesta fija la paleta, el SPC, los formatos cerámicos y los herrajes; pedía granito en el mesón, que se cambió por piedra sinterizada blanca. El tono exacto de las cerámicas de piso y el color de closets, mueble de baño y WPC son sugerencias dentro de esa paleta.')}
'''

V['planta'] = f'''
<div class="kicker">Planta · Apto 901 · espejo del Tipo A · 44,30 m²</div>
<h2>El apartamento completo, a escala</h2>
<p class="sub">Redibujado del plano comercial, con puertas, ventanas y ductos en su sitio. Incluye el amoblamiento de la Opción B, con la península y dos bancos. Las medidas son las del plano comercial hasta hacer el levantamiento con láser.</p>
<div class="figs">{fig(PLAN_FULL, '<b>Planta del Apto 901.</b> Norte arriba, con el balcón. La entrada es por el sur, junto al baño auxiliar.', 'panel')}</div>
{LEG_PLAN}
<div class="block"><h3>Base de diseño</h3>
<div class="tbl"><table>
<thead><tr><th>Espacio</th><th class="num">Medidas (m)</th><th class="num">Área</th><th>Piso</th><th>Qué se hace</th></tr></thead>
<tbody>
<tr><td class="z">Alcoba principal</td><td class="num">2,50 × 3,38</td><td class="num">8,45 m²</td><td>SPC</td><td>Closet RH de 1,50 m junto a la ventana</td></tr>
<tr><td class="z">Alcoba 2</td><td class="num">2,30 × 2,80</td><td class="num">6,44 m²</td><td>SPC</td><td>Closet RH de 1,45 m junto a la puerta</td></tr>
<tr><td class="z">Alcoba 3</td><td class="num">2,00 × 2,55</td><td class="num">5,10 m²</td><td>SPC</td><td>Closet RH corredizo de 1,20 m</td></tr>
<tr><td class="z">Baño principal</td><td class="num">1,10 × 2,10</td><td class="num">2,31 m²</td><td>Cerámica 30 × 30</td><td>Baño completo</td></tr>
<tr><td class="z">Baño auxiliar</td><td class="num">1,10 × 2,10</td><td class="num">2,31 m²</td><td>Cerámica 30 × 30</td><td>Baño completo (Inacar lo entrega terminado)</td></tr>
<tr><td class="z">Cocina-ropas</td><td class="num">4,05 × 2,30</td><td class="num">9,32 m²</td><td>SPC + cerámica en ropas</td><td>Mueble de 2,03 m, nevera y torre al frente, península 1,50 × 0,90</td></tr>
<tr><td class="z">Sala-comedor</td><td class="num">2,65 × 3,40</td><td class="num">9,01 m²</td><td>SPC</td><td>Panel de TV y luz; barra con dos bancos</td></tr>
<tr><td class="z">Balcón</td><td class="num">2,00 × 0,72</td><td class="num">1,44 m²</td><td>Cerámica antideslizante</td><td>Sellos, luz exterior y pintura</td></tr>
</tbody>
<tfoot><tr><td colspan="2">Espacios interiores medidos</td><td class="num">42,9 m²</td><td colspan="2" style="font-weight:400;color:var(--muted)">La diferencia con 44,30 m² es circulación y muros.</td></tr></tfoot>
</table></div></div>
<div class="card" style="margin-top:18px"><h3>Pisos</h3><ul>
  <li>SPC roble natural en zonas secas, con marca y referencia definidas: espesor, capa de uso, base acústica IXPE, garantía e instrucciones de instalación.</li>
  <li>Zócalos, perfiles de transición y dilataciones incluidos.</li>
  <li>Cerámica antideslizante gris piedra en baños, balcón y ropas.</li>
  <li>SPC al final de la obra húmeda, después de enchapes.</li>
</ul></div>
'''

V['cocina'] = f'''
<div class="kicker">Cocina y ropas · 4,05 × 2,30 m</div>
<h2>Mueble sobre el muro sur <span class="em">y península hacia la sala</span></h2>
<p class="sub">La cocina se abre a la sala en 2,65 m. El mueble va entre la puerta de entrada y ropas, donde Inacar deja el agua y el gas. La península de 1,50 × 0,90 m cierra la cocina hacia la sala y deja 1,10 m de pasillo.</p>
<div class="shots2">
{shot('cocina', ALT['cocina'], '<b>Desde la sala.</b> Península con frente en WPC, dos bancos y colgantes; atrás, el mueble sobre el muro sur.')}
{shot('ropas', ALT['ropas'], '<b>Desde la entrada.</b> Mesón a la derecha, península a la izquierda y, al fondo, nevera, torre y ropas bajo su ventana.')}
</div>
{RENDER_NOTE}
<div class="figs">{fig(PLAN_COCINA, '<b>Planta.</b> Península de 1,50 × 0,90 m: 60 cm de mueble y 30 cm de voladizo solo en el tramo de los bancos. La línea café punteada es la transición de SPC a cerámica en ropas.', 'panel')}</div>
<div class="figs">{fig(KE, '<b>Muro sur visto desde la cocina.</b> El mueble mide 2,03 m: lavaplatos, cajonero, estufa con horno y un remate de 23 cm. Ropas queda bajo su ventana y la entrada al otro extremo.', 'panel')}</div>
<div class="figs">{fig(PE, '<b>Península.</b> Hacia la sala, frente en WPC acanalado con dos bancos y dos lámparas colgantes. En corte, 60 cm de mueble y 30 cm de voladizo a 90 cm. Hacia la cocina, puertas y cajones.', 'panel')}</div>
<div class="legend">{sw('upper', 'Altos blanco cálido')}{sw('lower', 'Bajos gris piedra suave')}{sw('ctr', 'Piedra sinterizada blanca')}{sw('sp', 'Salpicadero 30 × 60')}{sw('metal', 'Perfil de aluminio')}{sw('wpc', 'WPC acanalado')}{sw('led', 'LED 3.000 K')}</div>
{note('blue', 'i', '<b>El mueble lineal es más corto de lo que suponía la propuesta.</b> El documento habla de 3,20–3,60 m. En el plano real, entre la entrada y ropas caben 2,03 m, así que la nevera y la torre pasan al frente, contra el muro de la alcoba principal. La península suma 1,50 m de mesón.')}
{note('', '!', '<b>La propuesta pedía no instalar península.</b> Su razón era no bloquear la circulación. En este plano la península queda en el límite con la sala, con 1,10 m de pasillo y 1,15 m libres desde la entrada. El voladizo va solo en el tramo de los bancos para no estorbar la puerta de la alcoba principal.')}
<div class="block"><h3>Especificación</h3>
{spec_table([
    ('Distribución', 'Mueble de 2,03 m sobre el muro sur, entre la entrada y ropas. Al frente, nevera, módulo de 30 cm y torre. Península de 1,50 × 0,90 m hacia la sala. Mesón de 60 cm y pasillo de 1,10 m.'),
    ('Módulos', 'Lavaplatos 60 cm, cajonero 60 cm, estufa 60 cm y remate 23 cm. Al frente, nevera de 70 cm y torre de despensa y limpieza de 40 cm.'),
    ('Península', 'Mueble RH de 60 cm con puertas y cajones hacia la cocina; mesón con voladizo de 30 cm en el tramo de los bancos, apoyado en platina de acero oculta; frente y costado en WPC acanalado; toma doble; dos colgantes en circuito propio; dos bancos de 65 cm.'),
    ('Carpintería', 'Melamina RH 18 mm con cantos de 2 mm en frentes; patas regulables; zócalo PVC/aluminio; bandeja antiderrame; organizador de cubiertos, gaveta profunda de ollas y bandeja extraíble de aseo.'),
    ('Colores', 'Altos en blanco cálido; bajos, península y torre en gris piedra suave, con perfil de aluminio tipo gola en lugar de manijas.'),
    ('Muebles altos', 'Fondo 30–35 cm, altura 70–80 cm, a 55–60 cm sobre el mesón. Siguen sobre la lavadora.'),
    ('Herrajes', 'Bisagras y correderas de extensión total de marca, con referencia y garantía; carga reforzada en el cajón de ollas.'),
    ('Mesón', 'Piedra sinterizada blanca mate, parecida al blanco de los altos, lisa o con veta muy suave; 12 mm con color en masa y ficha técnica; cortes con esquinas redondeadas, canto pulido y silicona neutra antihongos. No requiere sellado.'),
    ('Salpicadero', 'Cerámica 30 × 60 marmolizada o blanca, desde el mesón hasta los muebles altos.'),
    ('Lavaplatos', 'Acero inoxidable de 60 × 40 cm aprox.; sifón accesible, válvulas de paso y grifería monomando de marca con repuestos.'),
    ('Electricidad', 'Circuitos dedicados para horno, lavadora, nevera y pequeños electrodomésticos; tablero y cableado revisados por electricista.'),
    ('Extracción', 'Extractor con salida permitida o, si no hay salida, campana de recirculación con filtros reemplazables.'),
    ('Ropas', 'Lavadero compacto bajo la ventana, lavadora al lado, enchape de 1,20 m y piso antideslizante.'),
    ('Iluminación', 'Tira LED 3.000 K bajo altos con perfil de aluminio y difusor, luz general, colgantes sobre la barra y escenas por circuito.'),
])}
</div>
'''

V['banos'] = f'''
<div class="kicker">Baños · 2 × (1,10 × 2,10 m)</div>
<h2>Dos baños completos con la misma disposición</h2>
<p class="sub">En los dos baños el mueble, el sanitario y la ducha van sobre el muro oriental, con la ducha al fondo junto al ducto y una ventana alta. La puerta entra por el norte. Verifica en obra la posición de los desagües.</p>
{shot('bano', ALT['bano'], '<b>Baño principal</b> desde la puerta. Enchape claro 30 × 60, piso antideslizante, mueble flotante en roble natural con espejo y luz, grifería inoxidable y división corrediza.')}
{RENDER_NOTE}
<div class="figs panel">
  {fig(PLAN_BP, '<b>Baño principal.</b> Entra desde la alcoba principal.')}
  {fig(PLAN_BA, '<b>Baño auxiliar.</b> Entra desde el hall de las alcobas.')}
</div>
<div class="figs">{fig(BE, '<b>Muro oriental.</b> Mueble flotante RH de 60 cm junto a la puerta, sanitario y ducha al fondo.', 'panel')}</div>
<div class="legend">{sw('tw', 'Enchape de muro 30 × 60')}{sw('tf', 'Piso antideslizante 30 × 30')}{sw('van', 'Mueble RH roble natural')}{sw('metal', 'Grifería y herrajes inoxidables')}{sw('glass', 'Vidrio templado 8 mm')}</div>
<div class="block"><h3>Especificación</h3>
{spec_table([
    ('Impermeabilización', 'Sistema cementicio o equivalente en duchas y perímetros, media caña en encuentros, prueba de estanqueidad antes de enchapar y acta fotográfica.'),
    ('Desagües', 'Desagües y pendientes comprobados antes de cerrar.'),
    ('Enchapes', 'Claro 30 × 60 en muros y antideslizante 30 × 30 en piso.'),
    ('Aparatos', 'Sanitario ahorrador, mezcladora de ducha y griferías de marca con repuestos disponibles.'),
    ('División', 'Corrediza en vidrio templado de 8 mm con herrajes inoxidables.'),
    ('Mueble y espejo', 'Mueble flotante RH de 60 cm en roble natural, espejo con luz frontal útil.'),
])}
</div>
{note('', '!', '<b>El baño auxiliar ya viene terminado.</b> Inacar lo entrega con cerámica, muros en estuco y vinilo, ducha enchapada, sanitario y griferías. La propuesta cotiza dos baños completos. Pide que el auxiliar se cotice aparte: si decides conservar lo entregado, ese capítulo baja.')}
'''

V['alcobas'] = f'''
<div class="kicker">Alcobas · closets en melamina RH</div>
<h2>Closets donde caben en el plano real</h2>
<p class="sub">En la principal, 1,50 m junto a la ventana; en la alcoba 2, 1,45 m junto a la puerta; en la alcoba 3, 1,20 m con puertas corredizas, porque la cama queda cerca. Las camas son referencia de espacio y no hacen parte del presupuesto.</p>
{shot('alcoba', ALT['alcoba'], '<b>Alcoba principal.</b> Closet piso-techo de 1,50 m junto a la ventana, en melamina roble natural con perfil de aluminio y rejillas de ventilación; cama con cabecero al oriente.')}
{RENDER_NOTE}
<div class="figs panel">
  {fig(PLAN_AP, '<b>Alcoba principal</b> · 2,50 × 3,38 m.')}
  {fig(PLAN_A2, '<b>Alcoba 2</b> · 2,30 × 2,80 m.')}
  {fig(PLAN_A3, '<b>Alcoba 3</b> · 2,00 × 2,55 m.')}
</div>
<div class="figs">
  {fig(CE, '<b>Interior del closet de la alcoba principal</b>, sin puertas: doble colgado, cajones, zapatero con colgado medio, maletero y rejillas de ventilación.', 'panel')}
</div>
<div class="legend">{sw('clo', 'Melamina RH roble natural (sugerido)')}{sw('metal', 'Barras y herrajes inoxidables')}</div>
{note('blue', 'i', '<b>Los closets son más cortos que en la propuesta.</b> El documento dice 2,50 m en la principal, pero en ese muro está la ventana. En el plano caben unos 4,15 m lineales entre las tres alcobas, contra 5,30 m de la propuesta. Pide que ajusten la cotización a esas medidas.')}
<div class="block"><h3>Especificación</h3>
{spec_table([
    ('Alcoba principal', 'Closet RH piso-techo de unos 1,50 m junto a la ventana, con puertas batientes.'),
    ('Alcobas 2 y 3', 'Closet de 1,45 m con puertas batientes en la alcoba 2 y de 1,20 m con puertas corredizas en la alcoba 3.'),
    ('Interior', 'Diseñado para el uso real: doble colgado donde aplique, cajones, zapatero, maletero y ventilación.'),
    ('Herrajes', 'De marca, con referencia y garantía; perfil de aluminio en lugar de manijas.'),
])}
</div>
'''

V['sala'] = f'''
<div class="kicker">Sala-comedor 2,65 × 3,40 m · balcón 2,00 × 0,72 m</div>
<h2>Sala hacia el balcón, <span class="em">comedor en la barra</span></h2>
<p class="sub">Sofá de 2 puestos contra el muro de la alcoba principal y TV en el muro de la alcoba 2, frente a frente. La puerta-ventana de 2,00 m da al balcón. El comedor pasa a la barra de la península, con dos bancos.</p>
{shot('sala', ALT['sala'], '<b>Sala-comedor</b> desde la cocina, hacia el balcón. En primer plano, la península.')}
{RENDER_NOTE}
<div class="figs">
  {fig(PLAN_SALA, '<b>Planta.</b> El balcón conserva su baranda y fachada; solo se interviene piso, sellos, luz y pintura.', 'panel')}
  <div class="card" style="flex:1 1 280px;min-width:0"><h3>Especificación</h3><ul>
    <li><b>Sala:</b> sofá de 2 puestos, panel de TV liviano y luz propia con control de escena.</li>
    <li><b>Comedor:</b> la barra de la península, con dos bancos y dos colgantes. Si necesitas 4 puestos, suma una mesa plegable.</li>
    <li><b>Piso:</b> SPC roble natural con ficha técnica y base acústica.</li>
    <li><b>Balcón:</b> impermeabilización con prueba antes del enchape, piso antideslizante, sellos, luz exterior y pintura para exterior.</li>
    <li><b>Cielo raso:</b> cajillo simple solo si la altura final lo admite. Con 2,40 m libres, cualquier descuelgue se nota.</li>
  </ul></div>
</div>
{note('', '!', '<b>El balcón no se cierra.</b> Es área de uso exclusivo dentro de la propiedad horizontal: no se puede cerrar ni cambiar la fachada.')}
'''

V['presupuesto'] = f'''
<div class="kicker">Presupuesto objetivo · COP · Bucaramanga / Girón</div>
<h2>Cocina y baños se llevan <span class="em">casi la mitad</span></h2>
<p class="sub">Rangos objetivo de compra e instalación de la Opción B por capítulo, sobre una escala de 0 a 10 millones, más la península y el cambio a piedra sinterizada. Hay que validarlos con visita y cotizaciones comparables.</p>
{budget_html}
<div class="block"><h3>Totales</h3>
<div class="tbl totals"><table>
<thead><tr><th>Concepto</th><th class="num">Valor</th></tr></thead>
<tbody>
<tr><td>Subtotal de capítulos de la propuesta</td><td class="num">$31,5–38,4 M</td></tr>
<tr><td>Ajuste de alcance de la propuesta</td><td class="num">−$0,5–2,9 M</td></tr>
<tr><td>Península 1,50 × 0,90 (estimado propio) *</td><td class="num">+$2,0–3,5 M</td></tr>
<tr><td>Mesones en piedra sinterizada en vez de granito (estimado propio) **</td><td class="num">+$1,5–2,5 M</td></tr>
<tr class="big"><td>Total sin electrodomésticos</td><td class="num">$35,5–41,5 M</td></tr>
<tr><td>Electrodomésticos de gama media (estufa, campana y horno)</td><td class="num">$2,0–2,5 M</td></tr>
<tr class="big"><td>Total con electrodomésticos</td><td class="num">$37,5–43,5 M</td></tr>
</tbody></table></div>
<p class="disc">La propuesta fija la Opción B en $32,0–35,5 M sin electrodomésticos, como objetivo de contratación y no como suma exacta de los rangos; el total de arriba le suma la península y el cambio de mesón. * La propuesta no cotiza la península: el valor es un estimado propio para pedir cotización. ** Diferencia estimada con precios publicados en Colombia en 2025–2026 para unos 2,7 m² de mesón; se confirma con cotización.</p>
<p class="disc">Con el plano real, los closets suman unos 4,15 m lineales contra 5,30 m de la propuesta, y el mueble sobre el muro sur mide 2,03 m. Pide que ajusten esos capítulos a las medidas reales.</p>
</div>
<div class="grid2">
  <div class="card"><h3>No incluido por defecto</h3><ul>
    <li>Mobiliario suelto, cortinas y persianas.</li>
    <li>Aire acondicionado, cerraduras inteligentes, domótica y redes de datos adicionales.</li>
    <li>Cambio de puertas entregadas por la constructora y permisos de administración.</li>
    <li>Reparaciones ocultas de redes existentes y cualquier cambio estructural o de fachada.</li>
  </ul></div>
  <div class="card"><h3>Cómo pedir cotizaciones</h3><ul>
    <li>Entrega este alcance a todos y exige separar materiales, mano de obra, transporte, escombros, administración, impuestos y garantías.</li>
    <li>Mínimo tres cotizaciones comparables para cocina y closets, piedra, vidrio templado, acabados generales y eléctricos.</li>
    <li>No compares totales con materiales distintos: exige marca, modelo, calibre, área, metros lineales, herrajes y accesorios.</li>
    <li>Pide fotos, ficha de materiales, tiempos, fecha de inicio y tres trabajos terminados como referencia.</li>
  </ul></div>
</div>
'''

PHASES = [
    ('Diagnóstico', 'Visita técnica, medidas láser, revisión de redes y aprobación de la distribución final.'),
    ('Protección y obra base', 'Protecciones, retiro de lo que aplique (como la cocina básica), correcciones, nivelación y prueba de humedades.'),
    ('Redes ocultas', 'Hidráulicas, sanitarias, eléctricas, gas y extracción. Fotografiar antes de cerrar.'),
    ('Impermeabilización', 'Baños, duchas, ropas y balcón. Prueba de estanqueidad y acta.'),
    ('Enchapes y pisos', 'Baños, ropas y balcón primero; SPC al final de la obra húmeda.'),
    ('Pintura y cielos', 'Pañete, estuco, pintura y drywall antes de la carpintería.'),
    ('Carpintería y piedra', 'Medida final, fabricación, instalación de muebles, mesón y accesorios.'),
    ('Equipos y luminarias', 'Sanitarios, griferías, divisiones, cocina, campana, horno, lavadora e iluminación.'),
    ('Pruebas y entrega', 'Fugas, desagües, electricidad, apertura de muebles, sellos, limpieza, garantías y lista de pendientes.'),
]
RULES = [
    'Levantamiento con láser: ancho, largo, altura, diagonales, puertas, ventanas, columnas, vigas y ductos.',
    'Ubicar y fotografiar antes de cerrar: agua, desagües, gas, tomas, tablero, salida de campana y punto de lavadora.',
    'No iniciar enchapes sin prueba de estanqueidad en duchas, baños, ropas y balcón.',
    'No iniciar carpintería sin plano de despiece aprobado: módulos, anchos, fondos, apertura de puertas y electrodomésticos definidos.',
    'Contrato por capítulos con cronograma, garantías, materiales y modelos exactos, protección de zonas comunes, retiro de escombros y limpieza final.',
    'Pagos contra avance verificable: anticipo moderado, pagos por hitos y saldo retenido hasta pruebas y entrega.',
]
CONTRACT = [
    'Cualquier adicional se aprueba por escrito antes de ejecutarse.',
    'Definir qué pasa ante medidas distintas, redes defectuosas o daños de obra.',
    'Conservar el 10% del saldo hasta pruebas de funcionamiento y corrección de pendientes.',
    'Pedir actas de prueba, manual de mantenimiento y garantías por capítulo.',
]


def checks(prefix, items):
    return '<ul class="checks">' + ''.join(
        f'<li><label for="{prefix}{i}"><input type="checkbox" id="{prefix}{i}" data-ck><span>{t}</span></label></li>'
        for i, t in enumerate(items)) + '</ul>'


V['obra'] = f'''
<div class="kicker">Obra · de la visita técnica a la entrega</div>
<h2>Nueve fases, cada una con su punto de control</h2>
<p class="sub">El orden evita reprocesos: redes antes de impermeabilizar, obra húmeda antes del SPC y pintura antes de la carpintería.</p>
<div class="steps">{''.join(f'<div class="step"><div class="n">{i + 1}</div><div><h3>{a}</h3><p>{b}</p></div></div>' for i, (a, b) in enumerate(PHASES))}</div>
<div class="grid2">
  <div class="card"><h3>Antes de contratar <span class="prog" data-prog="r"></span></h3>{checks('r', RULES)}</div>
  <div class="card"><h3>En el contrato <span class="prog" data-prog="c"></span></h3>{checks('c', CONTRACT)}</div>
</div>
<p class="disc">Las casillas se guardan solo en este navegador.</p>
'''

V['entrega'] = '''
<div class="kicker">Entrega de Inacar · obra gris</div>
<h2>Lo que ya viene instalado</h2>
<p class="sub">Según el anexo de especificaciones de acabados de tu contrato, el apartamento se entrega en obra gris con dos excepciones: un baño completo y la cocina en su parte básica.</p>
<div class="tbl"><table>
<thead><tr><th>Zona</th><th>Qué incluye la entrega</th><th>Estado</th></tr></thead>
<tbody>
<tr><td class="z">Estructura y muros</td><td>Muros y placas en concreto reforzado; muros interiores en bloque y concreto a la vista, sin pañete ni pintura.</td><td><span class="pill ok"><span class="dot ok"></span>Incluido</span></td></tr>
<tr><td class="z">Ventanería</td><td>Ventanas corredizas en aluminio natural con vidrio de 5 mm. Puerta-ventana corrediza del balcón en vidrio templado.</td><td><span class="pill ok"><span class="dot ok"></span>Incluido</span></td></tr>
<tr><td class="z">Puertas</td><td>Puerta principal entamborada (Duratex Lana) y puerta del baño auxiliar. Las 3 alcobas y el baño principal <b>no</b> traen puerta.</td><td><span class="pill part"><span class="dot part"></span>Parcial</span></td></tr>
<tr><td class="z">Baño auxiliar</td><td>Terminado: piso cerámico, muros en estuco y vinilo, ducha enchapada, combo sanitario y griferías.</td><td><span class="pill ok"><span class="dot ok"></span>Terminado</span></td></tr>
<tr><td class="z">Cocina</td><td>Mueble inferior en melamina, mesón en acero inoxidable de 1,82 m con lavaplatos, cubierta a gas de 4 puestos y grifería. Muros y piso en gris.</td><td><span class="pill part"><span class="dot part"></span>Básica</span></td></tr>
<tr><td class="z">Zona de ropas</td><td>Lavadero en fibra de vidrio, grifería de lavadero y punto hidráulico para lavadora (sin llave).</td><td><span class="pill ok"><span class="dot ok"></span>Incluido</span></td></tr>
<tr><td class="z">Balcón</td><td>Baranda metálica, techo en graniplax y piso en concreto. No se puede cerrar ni modificar.</td><td><span class="pill ok"><span class="dot ok"></span>Incluido</span></td></tr>
<tr><td class="z">Eléctrico</td><td>Plafones en techo y 2 puntos de TV (solo tubería, sin cableado final).</td><td><span class="pill part"><span class="dot part"></span>Punto</span></td></tr>
</tbody></table></div>
<div class="note"><span class="ic">!</span><div><b>Qué pasa con lo entregado.</b> La cocina básica se retira para montar la cocina lineal nueva; ya está pagada en el precio, así que no cuenta como ahorro. Si cabe, el mesón en acero inoxidable puede servir de apoyo en ropas. El baño auxiliar viene terminado: revisa la nota en <button type="button" class="linkbtn" data-go="banos">Baños</button>. Las puertas de las 3 alcobas y del baño principal no vienen y la propuesta no las incluye: cotízalas aparte.</div></div>
<div class="note blue"><span class="ic">i</span><div><b>Proceso y fechas.</b> La entrega se formaliza con la escritura en la Notaría Segunda de Bucaramanga (programada para el 25-jul-2026, reprogramable con 15 días de aviso). El saldo de <span class="mono">$124.400.000</span> se cubre con crédito hipotecario y hay un bono de <span class="mono">$10.000.000</span> condicionado a estar al día. Los gastos de escrituración y registro son por tu cuenta.</div></div>
<div class="grid2">
  <div class="card"><h3>Revisa en el acta de entrega</h3><ul>
    <li>Baño auxiliar y cocina completos y sin daños.</li>
    <li>Ventanas y puerta-ventana: abren, cierran, sellan y sin rayones. En piso alto hay más viento.</li>
    <li>Puntos: 2 de TV, plafones y punto de lavadora.</li>
    <li>Niveles de piso, pendientes de desagües y cero filtraciones en losa y balcón.</li>
    <li>Baranda del balcón firme; medidores y matrículas de servicios.</li>
    <li>Escritura, matrícula inmobiliaria, manual del propietario, reglamento de PH y garantías.</li>
  </ul></div>
  <div class="card"><h3>Ten presente del contrato</h3><ul>
    <li>Es VIS: el precio de $210 M es solo del apartamento. Confirma si el parqueadero está incluido (hay 350 parqueaderos para 576 apartamentos).</li>
    <li>Torre 1, Etapa 1: piscina, gimnasio y cancha llegan con la Etapa 3.</li>
    <li>Zonas comunes de tu etapa: portería, salón de reuniones y administración, edificio de parqueaderos, zonas verdes y cuarto de basuras.</li>
    <li>Las matrículas de servicios las paga el vendedor; los reajustes de instalación, tú.</li>
    <li>No se puede modificar la fachada ni cerrar el balcón.</li>
  </ul></div>
</div>
'''

JS = r'''
(function(){
  var root=document.documentElement;
  var tabs=[].slice.call(document.querySelectorAll('[role="tab"]'));
  var views=[].slice.call(document.querySelectorAll('.view'));
  var names=views.map(function(v){return v.dataset.view});
  var tabsEl=document.querySelector('.tabs');
  function show(name,push){
    if(names.indexOf(name)<0) name='resumen';
    views.forEach(function(v){v.hidden=v.dataset.view!==name});
    tabs.forEach(function(t){
      var on=t.dataset.go===name;
      t.setAttribute('aria-selected',on?'true':'false');
      t.tabIndex=on?0:-1;
      if(on&&tabsEl){var l=t.offsetLeft-tabsEl.offsetLeft;if(l<tabsEl.scrollLeft||l+t.offsetWidth>tabsEl.scrollLeft+tabsEl.clientWidth){tabsEl.scrollLeft=l-16}}
    });
    if(push){try{history.replaceState(null,'','#'+name)}catch(e){}}
  }
  document.addEventListener('click',function(e){
    var g=e.target.closest('[data-go]');
    if(g){
      e.preventDefault();show(g.dataset.go,true);
      if(!g.matches('[role="tab"]')){var bar=document.querySelector('.bar');window.scrollTo({top:bar.offsetTop-0,behavior:'smooth'})}
      return;
    }
  });
  document.querySelector('[role="tablist"]').addEventListener('keydown',function(e){
    var i=tabs.indexOf(document.activeElement);if(i<0)return;
    var j=e.key==='ArrowRight'?i+1:e.key==='ArrowLeft'?i-1:e.key==='Home'?0:e.key==='End'?tabs.length-1:null;
    if(j===null)return;e.preventDefault();j=(j+tabs.length)%tabs.length;tabs[j].focus();show(tabs[j].dataset.go,true);
  });
  window.addEventListener('hashchange',function(){show(location.hash.slice(1),false)});
  show((location.hash||'').slice(1),false);
  // casillas
  var KEY='ob901-checks',state={};
  try{state=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){state={}}
  var boxes=[].slice.call(document.querySelectorAll('[data-ck]'));
  function prog(){
    [].forEach.call(document.querySelectorAll('[data-prog]'),function(p){
      var pre=p.dataset.prog;var bs=boxes.filter(function(b){return b.id.charAt(0)===pre});
      p.textContent=bs.filter(function(b){return b.checked}).length+' / '+bs.length;
    });
  }
  boxes.forEach(function(b){
    b.checked=!!state[b.id];
    b.addEventListener('change',function(){state[b.id]=b.checked;try{localStorage.setItem(KEY,JSON.stringify(state))}catch(e){}prog()});
  });
  prog();
})();
'''

views_html = ''.join(
    f'<section class="view" id="v-{k}" data-view="{k}" role="tabpanel" aria-labelledby="t-{k}"{"" if k == "resumen" else " hidden"}>'
    f'<div class="wrap">{V[k]}</div></section>' for k, _ in TABS)

page = f'''<title>Obra Blanca Apto 901</title>
<meta name="description" content="Apartamento 901, Torre 1 de Alto Tramonti: vistas a escala de cada espacio con la propuesta de acabados A y B, presupuesto, orden de obra y entrega de Inacar.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap">
<style>{CSS}
.shot{{margin:22px 0 0}}
.shot-img{{position:relative;border-radius:14px;overflow:hidden;border:1px solid var(--line);background:var(--card);box-shadow:var(--shadow)}}
.shot-img img{{display:block;width:100%;height:auto}}
.shot-tag{{position:absolute;left:12px;top:12px;display:inline-flex;align-items:center;gap:7px;padding:5px 10px 5px 6px;border-radius:999px;background:var(--card);color:var(--ink);font:600 .72rem/1 var(--f-body);box-shadow:var(--shadow)}}
.shot figcaption{{font-size:.84rem;color:var(--muted);margin-top:9px;max-width:80ch}}
.shot figcaption b{{color:var(--ink);font-weight:600}}
.shots2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.shots2 > *{{min-width:0}}
@media(max-width:760px){{.shots2{{grid-template-columns:1fr}}}}
.gal{{display:grid;gap:10px;margin-top:22px}}
.gal button{{appearance:none;border:0;padding:0;background:var(--card);position:relative;cursor:pointer;border-radius:12px;overflow:hidden;display:block;width:100%;box-shadow:var(--shadow)}}
.gal img{{display:block;width:100%;height:auto;transition:transform .35s ease}}
.gal button:hover img{{transform:scale(1.02)}}
.gal-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}
@media(max-width:700px){{.gal-grid{{grid-template-columns:1fr 1fr}}}}
.gal-cap{{position:absolute;left:10px;bottom:10px;padding:4px 9px;border-radius:999px;background:var(--card);color:var(--ink);font:600 .74rem/1.2 var(--f-body);box-shadow:var(--shadow)}}
.mgrid{{margin-top:20px}}
.mrow{{display:grid;grid-template-columns:minmax(140px,.9fr) 1.2fr 1.2fr;gap:14px;align-items:start;padding-block:16px;border-top:1px solid var(--line)}}
.mrow > *{{min-width:0}}
.mlabels{{border-top:0;padding-block:0 4px;font:600 .8rem/1.2 var(--f-body);color:var(--muted)}}
.mlabels div{{display:flex;align-items:center;gap:7px}}
.mhead h3{{font-size:1rem;margin:2px 0 2px}}
.mhead p{{margin:0;font-size:.82rem;color:var(--muted)}}
.mcard{{margin:0;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--card);transition:opacity .2s,box-shadow .2s,border-color .2s}}
.mcard img{{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;max-width:100%}}
.mgrid2{{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:14px;margin-top:20px}}
.mel{{font-family:var(--f-mono);font-size:.64rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:600}}
.mcard b{{font-weight:600;font-size:.9rem;line-height:1.3}}
.mcard figcaption{{padding:9px 11px 11px;display:grid;gap:3px}}
.mname{{display:flex;align-items:center;gap:7px;font-size:.88rem;line-height:1.25}}
.mname b{{font-weight:600}}
.mcard small{{font-size:.76rem;color:var(--muted);line-height:1.35}}
.mph{{aspect-ratio:4/3;display:grid;place-items:center;color:var(--muted);font:600 .8rem/1 var(--f-body);background:repeating-linear-gradient(135deg,var(--paper) 0 8px,var(--card) 8px 16px)}}
@media(max-width:620px){{.mrow{{grid-template-columns:1fr 1fr;gap:10px}}.mhead{{grid-column:1/-1}}.mlabels div:first-child{{display:none}}}}
@media (prefers-reduced-motion:reduce){{.gal img{{transition:none}}}}
.linkbtn{{appearance:none;border:0;background:none;padding:0;font:inherit;color:var(--accent);text-decoration:underline;text-underline-offset:2px;cursor:pointer}}
</style>
<header><div class="wrap top">
  <div class="eyebrow">Inacar · Alto Tramonti VIS · Girón, Santander</div>
  <h1>De obra gris a obra blanca</h1>
  <p class="lede">Tu apartamento con la Opción B de la propuesta de acabados y una península hacia la sala: plano real, renders, materiales, presupuesto y orden de obra.</p>
  <dl class="ficha">
    <div><dt>Inmueble</dt><dd>Apto 901 · Torre 1<small>Etapa 1 · Piso 9 · Tipo A</small></dd></div>
    <div><dt>Área privada</dt><dd>44,30 m²<small>Altura libre ≈ 2,40 m</small></dd></div>
    <div><dt>Distribución</dt><dd>3 alcobas · 2 baños<small>Cocina-ropas · sala-comedor · balcón</small></dd></div>
    <div><dt>Presupuesto B + península</dt><dd>$35,5–41,5 M<small>Sin electrodomésticos · estimado</small></dd></div>
    <div><dt>Precio</dt><dd>$210.000.000<small>VIS · Notaría 2 Bmga</small></dd></div>
  </dl>
</div></header>
<nav class="bar" aria-label="Vistas"><div class="wrap bar-in">
  <div class="tabs" role="tablist" aria-label="Vistas del apartamento">{tabs_html}</div>
</div></nav>
<main>{views_html}</main>
<footer><div class="wrap">
  <p><b>En resumen:</b> elegiste la Opción B con una península de 1,50 × 0,90 m hacia la sala, sobre el plano real del 901: dos baños completos, cocina sobre el muro sur con nevera y torre al frente, y closets en las tres alcobas. Total estimado de <b>$35,5–41,5 M</b> sin electrodomésticos, con mesones en piedra sinterizada blanca.</p>
  <p class="disc">Hecho a partir de tu contrato de promesa de compraventa, el anexo de especificaciones de Inacar y la Propuesta de acabados Tipo A del 29-sep-2026. Las vistas son conceptuales: no sirven para fabricar carpintería, cortar piedra ni mover redes sin medir en obra.</p>
</div></footer>
<script>{JS}</script>
'''

OUT.write_text(page, encoding='utf-8')
print('ok', OUT, len(page))
