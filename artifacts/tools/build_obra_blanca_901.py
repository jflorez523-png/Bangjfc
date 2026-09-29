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
    'clo-in': '#E2DCD1', 'van': '#A8937F',
}
MAT_B = {
    'spc': '#C9A575', 'spc-j': '#A9865A', 'paint': '#F3EEE4', 'upper': '#F4F1EA', 'lower': '#A9A49C',
    'ctr': '#3D3C3B', 'ctr-f': '#8C8984', 'sp': '#E9E7E3', 'sp-j': '#CBC6BE', 'metal': '#A2A6AB',
    'tw': '#E9E7E3', 'tw-j': '#CBC6BE', 'tf': '#B2AEA7', 'tf-j': '#948F87', 'clo': '#D6B98F',
    'clo-in': '#C7A87D', 'van': '#C9A575',
}
MAT_C = {  # comunes a ambas opciones
    'porc': '#FBFBF9', 'steel': '#C9CDD2', 'glass': '#BFDCE4', 'glass-l': '#5E97AA', 'led': '#FFD08A',
    'lav': '#F1F1EE', 'zoc': '#8F9194', 'cloth': '#B9C2CE', 'shoe': '#8B7866', 'mirror': '#D5E2E7',
    'e-line': '#2B2F38', 'e-halo': '#F7F4EE', 'oven': '#3A3F47', 'outlet': '#FAFAF8',
}

SWATCH_A = [('SPC roble claro', 'spc'), ('Muros blanco cálido', 'paint'), ('Altos blanco mate', 'upper'),
            ('Bajos taupe / moca claro', 'lower'), ('Granito Negro San Gabriel', 'ctr'), ('Herrajes negro mate', 'metal')]
SWATCH_B = [('SPC roble natural', 'spc'), ('Muros blanco cálido', 'paint'), ('Altos blanco cálido', 'upper'),
            ('Bajos gris piedra suave', 'lower'), ('Granito o superficie compacta', 'ctr'), ('Herrajes inoxidables', 'metal')]


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


# ---------------------------------------------------------------- planos por espacio
def plan_canvas(pid, w, h, k, fs, extra=(0, 0, 0, 0)):
    """extra = cm adicionales (izq, arriba, der, abajo) para cotas internas o anexos."""
    fsc = fs / k
    L = T + 2.3 * fsc + extra[0]
    Tp = T + 2.3 * fsc + extra[1]
    R = T + 0.8 * fsc + extra[2]
    B = T + 0.8 * fsc + extra[3]
    return D(pid, (-L, -Tp, w + L + R, h + Tp + B), k, fs)


def top_left_dims(d, w, h):
    y = -T - 0.9 * d.fs
    d.dimh(0, w, y, m(w))
    x = -T - 0.9 * d.fs
    d.dimv(0, h, x, m(h))


def draw_kitchen(d, detail):
    w, h = 405, 230
    d.floor(0, 0, w, h, 'spc')
    d.floor(255, 115, 150, 115, 'tf')
    d.a('<path d="M255 115V230M255 115H405" class="trans"/>')
    d.walls(w, h)
    # nevera (propia)
    d.a('<rect x="3" y="3" width="64" height="60" class="own"/>')
    # mesón y módulos
    d.a(f'<rect x="70" y="0" width="270" height="60" fill="url(#{d.pid}-gr)" class="ol"/>')
    d.a('<path d="M130 0V60M180 0V60M240 0V60M300 0V60" class="hid"/>')
    d.a('<rect x="78" y="10" width="44" height="40" rx="3" class="steel ol"/><circle cx="100" cy="6" r="2.2" class="metal"/>')
    d.a('<rect x="244" y="4" width="52" height="52" rx="2" class="cook"/>')
    for cx, cy in ((257, 17), (283, 17), (257, 43), (283, 43)):
        d.a(f'<circle cx="{cx}" cy="{cy}" r="8" class="burner"/>')
    # ropas
    d.a('<rect x="255" y="170" width="40" height="60" class="m-lower ol"/>')
    d.a('<rect x="295" y="172" width="50" height="58" class="lav ol"/><rect x="302" y="180" width="36" height="40" rx="4" class="lavb"/>')
    d.a('<rect x="347" y="170" width="56" height="58" class="own"/><circle cx="375" cy="199" r="21" class="own"/>')
    if detail:
        d.a('<rect x="70" y="0" width="270" height="35" class="hid"/>')
        d.t(40, 36, 'Nevera', size=0.8)
        d.dimv(60, 170, 200, '', size=0.85)
        d.t(208, 120, 'Pasillo 1,10', size=0.85, anchor='start')
        d.t(205, 84, 'Mesón granito · fondo 60', size=0.85)
        fs = 0.74
        d.t(275, 162, 'Gabinete', size=fs)
        d.t(320, 162, 'Lavadero', size=fs)
        d.t(375, 162, 'Lavadora', size=fs)
        d.t(330, 142, 'Ropas', size=0.9)
        # cotas de módulos
        y = -T - 0.9 * d.fs
        x = 0
        for wd in (70, 60, 50, 60, 60, 40, 65):
            d.dimh(x, x + wd, y, str(wd), size=0.82)
            x += wd
        y2 = -T - 2.3 * d.fs
        d.dimh(0, 405, y2, '4,05')
        d.dimv(0, 230, -T - 0.9 * d.fs, '2,30')
        xr = w + T + 0.9 * d.fs
        d.dimv(0, 60, xr, '60', size=0.82, right=True)
        d.dimv(60, 170, xr, '1,10', size=0.82, right=True)
        d.dimv(170, 230, xr, '60', size=0.82, right=True)
        yb = h + T + 0.9 * d.fs
        d.dimh(255, 295, yb, '40', size=0.82, below=True)
        d.dimh(295, 345, yb, '50', size=0.82, below=True)
        d.dimh(345, 405, yb, '60', size=0.82, below=True)
    else:
        top_left_dims(d, w, h)


def draw_bath(d, detail):
    w, h = 110, 210
    d.floor(0, 0, w, h, 'tf')
    d.walls(w, h)
    d.a('<rect x="0" y="0" width="45" height="60" class="m-van ol"/><ellipse cx="24" cy="30" rx="13" ry="18" class="porc ol"/>')
    d.a('<rect x="0" y="70" width="18" height="40" rx="2" class="porc ol"/><ellipse cx="43" cy="90" rx="25" ry="17" class="porc ol"/>')
    d.a('<path d="M0 120H62" class="glass"/><path d="M48 124H110" class="glass"/>')
    d.a('<circle cx="55" cy="182" r="4" class="drain"/><rect x="0" y="159" width="5" height="12" class="metal"/>')
    if detail:
        d.t(78, 34, 'Mueble 60', size=0.72, anchor='middle')
        d.t(55, 150, 'Ducha', size=0.8)
        top_left_dims(d, w, h)
        xr = w + T + 0.9 * d.fs
        d.dimv(0, 60, xr, '60', size=0.82, right=True)
        d.dimv(60, 120, xr, '60', size=0.82, right=True)
        d.dimv(120, 210, xr, '90', size=0.82, right=True)
    else:
        top_left_dims(d, w, h)


def draw_master(d, detail):
    w, h = 250, 338
    d.floor(0, 0, w, h, 'spc')
    d.walls(w, h)
    nightstand(d, 10, 0)
    nightstand(d, 200, 0)
    bed(d, 55, 0, 140, 190, 'top')
    closet(d, 0, 278, 250, 60, 5, swings=detail)
    light(d, 125, 150)
    top_left_dims(d, w, h)
    if detail:
        d.t(125, 120, 'Cama doble 1,40', size=0.8)
        d.t(125, 318, 'Closet RH 2,50', size=0.85)
        xr = w + T + 0.9 * d.fs
        d.dimv(0, 190, xr, '1,90', size=0.82, right=True)
        d.dimv(190, 278, xr, '88', size=0.82, right=True)
        d.dimv(278, 338, xr, '60', size=0.82, right=True)


def draw_bed2(d, detail):
    w, h = 230, 280
    d.floor(0, 0, w, h, 'spc')
    d.walls(w, h)
    bed(d, 0, 15, 120, 190, 'left')
    closet(d, 0, 220, 160, 60, 3, swings=detail)
    light(d, 115, 140)
    top_left_dims(d, w, h)
    if detail:
        d.t(110, 80, 'Cama 1,20', size=0.8)
        d.t(80, 257, 'Closet RH 1,60', size=0.8)
        xr = w + T + 0.9 * d.fs
        d.dimv(135, 220, xr, '85', size=0.82, right=True)
        d.dimv(220, 280, xr, '60', size=0.82, right=True)


def draw_bed3(d, detail):
    w, h = 200, 255
    d.floor(0, 0, w, h, 'spc')
    d.walls(w, h)
    bed(d, 0, 0, 100, 190, 'left')
    closet(d, 0, 195, 120, 60, 2, swings=detail)
    light(d, 100, 128)
    top_left_dims(d, w, h)
    if detail:
        d.t(108, 55, 'Cama 1,00', size=0.8)
        d.t(60, 232, 'Closet 1,20', size=0.78)
        xr = w + T + 0.9 * d.fs
        d.dimv(0, 100, xr, '1,00', size=0.82, right=True)
        d.dimv(100, 195, xr, '95', size=0.82, right=True)
        d.dimv(195, 255, xr, '60', size=0.82, right=True)


def draw_living(d, detail):
    w, h = 265, 340
    d.floor(0, 0, w, h, 'spc')
    # balcón
    by = h + T
    d.a(f'<rect x="32" y="{by}" width="200" height="72" fill="url(#{d.pid}-tf)" class="ol"/>')
    d.a(f'<path d="M32 {by + 72}H232" class="rail"/>')
    d.walls(w, h, gaps=[('bottom', 45, 220)])
    d.a(f'<path d="M45 {h + 3}H140" class="glass"/><path d="M125 {h + 7}H220" class="glass"/>')
    round_table(d, 132, 88, 45)
    sofa(d, 0, 182, 150, 85)
    d.a('<rect x="255" y="195" width="10" height="120" class="m-clo ol"/>')
    light(d, 132, 170, cls='only-a')
    light(d, 132, 88, cls='only-b')
    light(d, 175, 257, cls='only-b')
    light(d, 60, by + 8, r=5)
    top_left_dims(d, w, h)
    if detail:
        d.t(132, 92, 'Ø 0,90', size=0.75)
        d.t(58, 257, 'Sofá 2 puestos', size=0.78, rot=-90)
        d.t(242, 255, 'Panel TV', size=0.78, rot=-90)
        d.t(132, by + 42, 'Balcón 2,00 × 0,72', size=0.8)
        d.dimh(32, 232, by + 72 + 0.9 * d.fs, '2,00', size=0.82, below=True)
        d.dimv(by, by + 72, w + T + 0.9 * d.fs, '72', size=0.82, right=True)


def room_svg(pid, fn, w, h, k, fs, detail, aria, extra=(0, 0, 0, 0)):
    d = plan_canvas(pid, w, h, k, fs, extra)
    fn(d, detail)
    return d.svg(aria)


# ---------------------------------------------------------------- alzados
def Y(hh):
    return 240 - hh


def elev_frame(d, w):
    d.a(f'<rect x="{-T}" y="0" width="{T}" height="240" class="pc"/><rect x="{w}" y="0" width="{T}" height="240" class="pc"/>')
    d.a(f'<rect x="{-T}" y="240" width="{w + 2 * T}" height="{T}" class="pc"/><rect x="{-T}" y="{-T}" width="{w + 2 * T}" height="{T}" class="pc"/>')


def kitchen_elev():
    k, fs = 1.62, 10.5
    fsc = fs / k
    L = T + 3.6 * fsc + 6
    top = T + 2.4 * fsc
    d = D('ke', (-L, -top, 405 + L + T + 8, 240 + top + T + 5.9 * fsc), k, fs)
    sp = d.pat('sp', 60, 30, 'm-sp', 'j-sp', 70, Y(147))
    d.a(f'<rect x="0" y="0" width="405" height="240" class="m-paint"/>')
    # salpicadero
    d.a(f'<rect x="70" y="{Y(147)}" width="270" height="57" fill="{sp}" class="eo"/>')
    # luz LED bajo altos
    d.a(f'<rect x="70" y="{Y(147)}" width="170" height="34" fill="url(#ke-led)"/>')
    d.a(f'<rect x="300" y="{Y(147)}" width="40" height="34" fill="url(#ke-led)" class="only-a"/>')
    # tomas
    for x in (150, 215):
        d.a(f'<rect x="{x}" y="{Y(116)}" width="8" height="12" rx="1" class="outlet"/>')
    d.a(f'<rect x="318" y="{Y(116)}" width="8" height="12" rx="1" class="outlet only-a"/>')
    for x in (84, 190, 272):
        d.a(f'<rect x="{x}" y="{Y(116)}" width="8" height="12" rx="1" class="outlet only-b"/>')
    # nevera propia
    d.a(f'<rect x="3" y="{Y(178)}" width="64" height="178" rx="3" class="own-e"/>')
    d.a(f'<path d="M3 {Y(118)}H67M58 {Y(160)}V{Y(130)}M58 {Y(106)}V{Y(70)}" class="own-e"/>')
    d.t(35, Y(60), 'Nevera', cls='le', size=0.9)
    # bajos
    d.a(f'<rect x="70" y="{Y(10)}" width="270" height="10" class="zoc eo"/>')
    fronts = []

    def door(x, w, h0, h1, hinge='l', cls='m-lower'):
        fronts.append((x, w, h0, h1, 'door', hinge, cls))

    def drawer(x, w, h0, h1, cls='m-lower'):
        fronts.append((x, w, h0, h1, 'drawer', None, cls))
    door(70, 30, 10, 88, 'l'); door(100, 30, 10, 88, 'r')
    door(130, 50, 10, 88, 'l')
    drawer(180, 60, 10, 32); drawer(180, 60, 32, 60); drawer(180, 60, 60, 88)
    drawer(240, 60, 10, 26)
    s = ''
    for x, w, h0, h1, kind, hinge, cls in fronts:
        s += f'<rect x="{x + .4}" y="{Y(h1) + .4}" width="{w - .8}" height="{h1 - h0 - .8}" class="{cls} eo"/>'
    d.a(s)
    # horno bajo estufa
    d.a(f'<rect x="240.4" y="{Y(88)}" width="59.2" height="61.6" class="steel eo"/>'
        f'<rect x="248" y="{Y(76)}" width="44" height="34" rx="2" class="oven-win"/><path d="M250 {Y(82)}H290" class="hdl"/>')
    # remate (A) / torre (B)
    d.a(f'<g class="only-a"><rect x="300.4" y="{Y(88)}" width="39.2" height="77.6" class="m-lower eo"/></g>')
    d.a(f'<g class="only-b"><rect x="300" y="{Y(222)}" width="40" height="212" class="m-lower eo"/>'
        f'<path d="M300 {Y(150)}H340M300 {Y(88)}H340" class="eo"/><rect x="298" y="{Y(224)}" width="44" height="216" class="opt-mark"/></g>')
    # mesón granito
    d.a(f'<rect x="70" y="{Y(90)}" width="230" height="2.4" fill="url(#ke-gr)" class="eo"/>')
    d.a(f'<rect x="300" y="{Y(90)}" width="40" height="2.4" fill="url(#ke-gr)" class="eo only-a"/>')
    # estufa y grifería
    d.a(f'<rect x="246" y="{Y(91.6)}" width="48" height="1.6" class="steel eo"/><path d="M252 {Y(92.6)}h8M280 {Y(92.6)}h8" class="hdl"/>')
    d.a(f'<path d="M100 {Y(90)}V{Y(121)}Q100 {Y(129)} 108 {Y(129)}H111V{Y(123)}" class="faucet"/>')
    # manijas A / perfil B
    ha = ''
    for x, w, h0, h1, kind, hinge, cls in fronts:
        if kind == 'door':
            hx = x + w - 4 if hinge == 'l' else x + 4
            ha += f'<path d="M{hx} {Y(h1 - 6)}V{Y(h1 - 20)}" class="hdl"/>'
        else:
            ha += f'<path d="M{x + w / 2 - 9} {Y(h1 - 5)}H{x + w / 2 + 9}" class="hdl"/>'
    ha += f'<path d="M336 {Y(82)}V{Y(68)}" class="hdl"/>'
    d.a(f'<g class="only-a">{ha}</g>')
    d.a(f'<g class="only-b"><rect x="70" y="{Y(88)}" width="170" height="2" class="gola"/>'
        f'<rect x="240" y="{Y(26)}" width="60" height="1.4" class="gola"/></g>')
    # altos
    up = []
    up += [(70, 30, 147, 222, 'l'), (100, 30, 147, 222, 'r'), (130, 50, 147, 222, 'l'), (180, 30, 147, 222, 'l'), (210, 30, 147, 222, 'r')]
    up += [(240, 60, 180, 222, 'l')]
    s = ''
    for x, w, h0, h1, hinge in up:
        s += f'<rect x="{x + .4}" y="{Y(h1) + .4}" width="{w - .8}" height="{h1 - h0 - .8}" class="m-upper eo"/>'
    d.a(s)
    d.a(f'<g class="only-a"><rect x="300.4" y="{Y(222) + .4}" width="39.2" height="74.2" class="m-upper eo"/>'
        f'<path d="M336 {Y(153)}V{Y(165)}" class="hdl"/></g>')
    ha = ''
    for x, w, h0, h1, hinge in up:
        hx = x + w - 4 if hinge == 'l' else x + 4
        ha += f'<path d="M{hx} {Y(h0 + 5)}V{Y(h0 + 17)}" class="hdl"/>'
    d.a(f'<g class="only-a">{ha}</g>')
    d.a(f'<g class="only-b"><rect x="70" y="{Y(149)}" width="170" height="1.6" class="gola"/></g>')
    # campana
    d.a(f'<path d="M244 {Y(180)}H296L294 {Y(166)}H246Z" class="steel eo"/>')
    # tira LED
    d.a(f'<path d="M70 {Y(147) + .8}H240" class="ledl"/><path d="M300 {Y(147) + .8}H340" class="ledl only-a"/>')
    elev_frame(d, 405)
    # etiquetas y cotas
    d.a(d.text(320, -T - 0.7 * d.fs, 'Torre despensa opcional', cls='dt', size=0.88).replace('class="dt"', 'class="dt only-b"'))
    yb = 240 + T + 1.5 * d.fs
    x = 0
    names = [('Nevera', 70), ('Lavaplatos', 60), ('Ajuste', 50), ('Cajonero', 60), ('Estufa', 60), ('Remate', 40)]
    for nm, wd in names:
        d.dimh(x, x + wd, yb, str(wd), size=0.85, below=False)
        d.t(x + wd / 2, yb + d.fs * 1.15, nm if not (nm == 'Remate') else nm, cls='dn', size=0.8)
        x += wd
    d.a(d.text(320, yb + d.fs * 1.15, 'Torre', cls='dn only-b', size=0.8))
    yb2 = yb + d.fs * 2.7
    d.dimh(0, 340, yb2, 'Mueble lineal 3,40 (rango 3,20–3,60)', size=0.85, below=True)
    xl = -T - 0.9 * d.fs
    d.dimv(0, 240, xl - 1.6 * d.fs, '2,40 libre', size=0.85)
    d.a(''.join([]))
    lv = [(0, 90, '≈90'), (90, 147, '55–60'), (147, 222, '70–80')]
    for h0, h1, lb in lv:
        d.dimv(240 - h0, 240 - h1, xl, lb, size=0.8)
    return d.svg('Vista frontal del muro de cocina: nevera, lavaplatos, módulo de ajuste, cajonero, estufa con horno y remate; muebles altos a 55–60 cm del mesón con tira LED debajo.')


def laundry_elev():
    k, fs = 1.62, 10.5
    fsc = fs / k
    L = T + 2.4 * fsc
    d = D('re', (-L, -T - 4, 180 + L + 6, 240 + T + 4 + T + 3.2 * fsc), k, fs)
    tw = d.pat('tw', 60, 30, 'm-tw', 'j-tw', 0, Y(120))
    d.a('<rect x="0" y="0" width="180" height="240" class="m-paint"/>')
    d.a(f'<rect x="0" y="{Y(120)}" width="150" height="120" fill="{tw}" class="eo"/>')
    # lavadora propia
    d.a(f'<rect x="2" y="{Y(85)}" width="56" height="85" rx="3" class="own-e"/><circle cx="30" cy="{Y(48)}" r="17" class="own-e"/>')
    d.a(f'<circle cx="30" cy="{Y(100)}" r="2.6" class="metal"/>')
    # lavadero compacto
    d.a(f'<rect x="62" y="{Y(90)}" width="46" height="32" rx="2" class="lav eo"/><path d="M66 {Y(58)}V0M104 {Y(58)}V0" class="eo"/>'
        f'<path d="M85 {Y(90)}V{Y(104)}Q85 {Y(110)} 91 {Y(110)}H93" class="faucet"/>')
    # gabinete alto
    d.a(f'<rect x="110" y="{Y(10)}" width="40" height="10" class="zoc eo"/>'
        f'<rect x="110.4" y="{Y(205)}" width="39.2" height="195" class="m-lower eo"/><path d="M110 {Y(110)}H150" class="eo"/>')
    d.a(f'<g class="only-a"><path d="M146 {Y(125)}V{Y(140)}M146 {Y(95)}V{Y(80)}" class="hdl"/></g>')
    d.a(f'<g class="only-b"><path d="M146 {Y(125)}V{Y(140)}M146 {Y(95)}V{Y(80)}" class="hdl"/></g>')
    d.a(f'<rect x="{-T}" y="0" width="{T}" height="240" class="pc"/>'
        f'<rect x="{-T}" y="240" width="{190 + T}" height="{T}" class="pc"/><rect x="{-T}" y="{-T}" width="{190 + T}" height="{T}" class="pc"/>'
        f'<path d="M180 {-T}L184 60L176 120L184 180L180 {240 + T}" class="brk"/>')
    yb = 240 + T + 1.5 * d.fs
    for x0, wd, nm in ((0, 60, 'Lavadora'), (60, 50, 'Lavadero'), (110, 40, 'Gabinete')):
        d.dimh(x0, x0 + wd, yb, str(wd), size=0.85)
        d.t(x0 + wd / 2, yb + d.fs * 1.15, nm, cls='dn', size=0.78)
    d.dimv(240, 120, -T - 0.9 * d.fs, 'enchape 1,20', size=0.8)
    return d.svg('Vista del muro de ropas: lavadora, lavadero compacto y gabinete alto de limpieza, con enchape de 1,20 m de alto.')


def bath_elev():
    k, fs = 1.62, 10.5
    fsc = fs / k
    L = T + 2.4 * fsc
    d = D('be', (-L, -T - 4, 210 + L + T + 2.6 * fsc, 240 + T + 4 + T + 3.2 * fsc), k, fs)
    tw = d.pat('tw', 60, 30, 'm-tw', 'j-tw', 0, 0)
    d.a(f'<rect x="0" y="0" width="210" height="240" fill="{tw}" class="eo"/>')
    # ducha
    d.a(f'<path d="M45 {Y(205)}V{Y(212)}" class="faucet"/><rect x="36" y="{Y(205)}" width="18" height="2.5" rx="1" class="metal"/>')
    d.a(f'<circle cx="45" cy="{Y(110)}" r="5" class="metal"/><path d="M45 {Y(110)}L53 {Y(114)}" class="faucet"/>')
    d.a(f'<rect x="88" y="{Y(200)}" width="3" height="200" class="glass-e"/>')
    # sanitario
    d.a(f'<rect x="100" y="{Y(78)}" width="40" height="34" rx="3" class="porc eo"/><rect x="114" y="{Y(80)}" width="12" height="2" class="metal"/>'
        f'<path d="M103 {Y(42)}H137L131 {Y(0)}H109Z" class="porc eo"/><path d="M101 {Y(42)}H139" class="eo"/>')
    # mueble flotante + espejo + luz
    d.a(f'<rect x="150" y="{Y(87)}" width="60" height="3" class="porc eo"/><rect x="152" y="{Y(84)}" width="56" height="38" class="m-van eo"/>')
    d.a(f'<g class="only-a"><path d="M175 {Y(78)}H185" class="hdl"/></g><g class="only-b"><rect x="152" y="{Y(84)}" width="56" height="1.4" class="gola"/></g>')
    d.a(f'<path d="M180 {Y(87)}V{Y(100)}Q180 {Y(104)} 184 {Y(104)}H186" class="faucet"/>')
    d.a(f'<rect x="156" y="{Y(176)}" width="48" height="70" rx="2" class="mirror eo"/>')
    d.a(f'<rect x="156" y="{Y(176)}" width="48" height="26" fill="url(#be-led)"/>')
    d.a(f'<rect x="160" y="{Y(182)}" width="40" height="3" rx="1" class="ledbar"/>')
    elev_frame(d, 210)
    yb = 240 + T + 1.5 * d.fs
    for x0, wd, nm in ((0, 90, 'Ducha'), (90, 60, 'Sanitario'), (150, 60, 'Mueble')):
        d.dimh(x0, x0 + wd, yb, str(wd), size=0.85)
        d.t(x0 + wd / 2, yb + d.fs * 1.15, nm, cls='dn', size=0.8)
    xr = 210 + T + 0.9 * d.fs
    d.dimv(240, 40, xr, 'vidrio 8 mm · 2,00', size=0.8, right=True)
    d.dimv(240, 0, -T - 0.9 * d.fs, '2,40', size=0.85)
    return d.svg('Vista del muro largo del baño: ducha con división de vidrio templado, sanitario y mueble flotante de 60 cm con espejo y luz frontal.')


def closet_elev():
    k, fs = 1.62, 10.5
    fsc = fs / k
    L = T + 2.4 * fsc
    d = D('ce', (-L, -T - 4, 250 + L + T + 4, 240 + T + 4 + T + 3.2 * fsc), k, fs)
    d.a('<rect x="0" y="0" width="250" height="240" class="m-cloin"/>')
    d.a(f'<rect x="0" y="{Y(8)}" width="250" height="8" class="m-clo eo"/>')

    def shelf(x0, x1, h):
        return f'<rect x="{x0}" y="{Y(h) - 1}" width="{x1 - x0}" height="2" class="m-clo eo"/>'

    def div(x):
        return f'<rect x="{x - 1}" y="0" width="2" height="{Y(8)}" class="m-clo eo"/>'

    def rod(x0, x1, h):
        return f'<path d="M{x0 + 3} {Y(h)}H{x1 - 3}" class="rod-e"/>'

    def clothes(x0, x1, h, bottoms):
        s = ''
        n = len(bottoms)
        step = (x1 - x0 - 8) / n
        for i, b in enumerate(bottoms):
            x = x0 + 4 + i * step + 1
            s += f'<path d="M{x + step / 2 - 1} {Y(h)}V{Y(h - 3)}" class="eo"/>'
            s += f'<rect x="{x:.1f}" y="{Y(h - 3)}" width="{step - 2.5:.1f}" height="{h - 3 - b}" rx="2" class="cloth"/>'
        return s

    def drawers(x0, x1, hs):
        s = ''
        for h0, h1 in zip(hs, hs[1:]):
            s += f'<rect x="{x0 + 1.5}" y="{Y(h1) + .6}" width="{x1 - x0 - 3}" height="{h1 - h0 - 1.2}" class="m-clo eo"/>'
            s += f'<path d="M{(x0 + x1) / 2 - 7} {Y(h1 - 6)}H{(x0 + x1) / 2 + 7}" class="hdl"/>'
        return s

    def shoes(x0, x1, h):
        s = ''
        x = x0 + 5
        while x + 18 < x1:
            s += f'<rect x="{x}" y="{Y(h + 9)}" width="7.5" height="8" rx="3" class="shoe"/><rect x="{x + 8.5}" y="{Y(h + 9)}" width="7.5" height="8" rx="3" class="shoe"/>'
            x += 22
        return s

    a = div(100) + div(150)
    a += shelf(0, 100, 200) + rod(0, 100, 188) + clothes(0, 100, 188, [98, 110, 92, 120, 104, 96])
    a += drawers(100, 150, [8, 38, 68, 98]) + shelf(100, 150, 130) + shelf(100, 150, 165) + shelf(100, 150, 200)
    a += shelf(150, 250, 200) + rod(150, 250, 188) + clothes(150, 250, 188, [112, 104, 118, 108, 120, 110])
    a += shelf(150, 250, 34) + shelf(150, 250, 64) + shoes(150, 250, 10) + shoes(150, 250, 34) + shoes(150, 250, 64)
    d.a(f'<g class="only-a">{a}</g>')

    b = div(100) + div(150) + div(200)
    b += shelf(0, 250, 205)
    for x in range(20, 250, 50):
        b += ''.join(f'<rect x="{x + i * 3}" y="{Y(232)}" width="1.3" height="12" class="vent"/>' for i in range(4))
    b += rod(0, 100, 196) + clothes(0, 100, 196, [132, 140, 128, 136, 130]) + rod(0, 100, 106) + clothes(0, 100, 106, [44, 52, 40, 48, 46])
    b += drawers(100, 150, [8, 33, 58, 83, 108]) + shelf(100, 150, 140) + shelf(100, 150, 172)
    for h in (8, 33, 58, 83, 108, 133):
        if h > 8:
            b += shelf(150, 200, h)
        b += shoes(150, 200, h + (2 if h == 8 else 0))
    b += rod(200, 250, 196) + clothes(200, 250, 196, [40, 52, 46])
    d.a(f'<g class="only-b">{b}</g>')
    d.a(d.text(125, Y(220), 'Maletero', cls='le', size=0.85).replace('class="le"', 'class="le only-b"'))
    elev_frame(d, 250)
    yb = 240 + T + 1.5 * d.fs
    ga = ''
    gb = ''
    for x0, wd, nm in ((0, 100, 'Colgado'), (100, 50, 'Cajones'), (150, 100, 'Colgado + zapatero')):
        dd = D('x', (0, 0, 1, 1), k, fs)
        dd.dimh(x0, x0 + wd, yb, str(wd), size=0.85)
        dd.t(x0 + wd / 2, yb + d.fs * 1.15, nm, cls='dn', size=0.8)
        ga += ''.join(dd.p)
    for x0, wd, nm in ((0, 100, 'Doble colgado'), (100, 50, 'Cajones'), (150, 50, 'Zapatero'), (200, 50, 'Colgado')):
        dd = D('x', (0, 0, 1, 1), k, fs)
        dd.dimh(x0, x0 + wd, yb, str(wd), size=0.85)
        dd.t(x0 + wd / 2, yb + d.fs * 1.15, nm, cls='dn', size=0.8)
        gb += ''.join(dd.p)
    d.a(f'<g class="only-a">{ga}</g><g class="only-b">{gb}</g>')
    d.dimv(240, 0, -T - 0.9 * d.fs, '2,40 piso-techo', size=0.85)
    return d.svg('Interior del closet de la alcoba principal, 2,50 m: en A colgado, cajones y zapatero; en B doble colgado, cajones, zapatero, colgado largo, maletero y ventilación.')


# ---------------------------------------------------------------- piezas HTML
def fig(svg, cap, cls='', scroll=True):
    inner = f'<div class="scroll">{svg}</div>' if scroll else svg
    return f'<figure class="fg {cls}">{inner}<figcaption>{cap}</figcaption></figure>'


def sw(var, label_a, label_b=None):
    if label_b is None:
        lab = label_a
    else:
        lab = f'<span class="only-a">{label_a}</span><span class="only-b">{label_b}</span>'
    return f'<span class="key"><span class="sw" style="--c:var(--m-{var})"></span>{lab}</span>'


def spec_table(rows, head=('Elemento', 'Especificación Opción A')):
    body = ''.join(f'<tr><td class="z">{a}</td><td>{b}</td></tr>' for a, b in rows)
    return f'<div class="tbl"><table><thead><tr><th>{head[0]}</th><th>{head[1]}</th></tr></thead><tbody>{body}</tbody></table></div>'


REF = '<span class="ref" title="Una de las cinco protecciones de B que adopta la recomendación">A reforzada</span>'


def b_block(title, items):
    lis = ''.join(f'<li>{"" if not r else REF}{t}</li>' for t, r in items)
    return f'<div class="bblock"><div class="bhead"><span class="optchip b">B</span><h3>{title}</h3></div><ul>{lis}</ul></div>'


def note(kind, ic, html):
    return f'<div class="note {kind}"><span class="ic">{ic}</span><div>{html}</div></div>'


def swatches(lst, mats):
    return '<div class="pal">' + ''.join(
        f'<span class="chip"><span class="sw" style="background:{mats[k]}"></span>{n}</span>' for n, k in lst) + '</div>'


LEG_PLAN = ('<div class="legend">'
            '<span class="key"><span class="sw pat-spc"></span>SPC zonas secas</span>'
            '<span class="key"><span class="sw pat-tf"></span>Cerámica antideslizante</span>'
            '<span class="key"><span class="sw" style="--c:var(--m-clo)"></span>Carpintería RH (incluida)</span>'
            '<span class="key"><span class="sw" style="--c:var(--m-ctr)"></span>Mesón en granito</span>'
            '<span class="key"><span class="sw loose-k"></span>Mobiliario suelto (no incluido)</span>'
            '<span class="key"><span class="sw own-k"></span>Electrodoméstico propio</span>'
            '<span class="key"><span class="sw lt-k"></span>Luz de techo</span>'
            '</div>')


# ---------------------------------------------------------------- dibujos
K_SHEET, FS_SHEET = 0.62, 10.5
K_DET, FS_DET = 0.92, 10.5
K_BED = 0.8

sheet = [
    ('Cocina-ropas', '4,05 × 2,30', '9,32', room_svg('s1', draw_kitchen, 405, 230, K_SHEET, FS_SHEET, False, 'Planta cocina-ropas 4,05 por 2,30 m')),
    ('Sala-comedor y balcón', '2,65 × 3,40 · balcón 2,00 × 0,72', '9,01 + 1,44', room_svg('s2', draw_living, 265, 340, K_SHEET, FS_SHEET, False, 'Planta sala-comedor 2,65 por 3,40 m con balcón', extra=(0, 0, 0, 82))),
    ('Baño principal', '1,10 × 2,10', '2,31', room_svg('s6', draw_bath, 110, 210, K_SHEET, FS_SHEET, False, 'Planta baño principal 1,10 por 2,10 m')),
    ('Baño auxiliar', '1,10 × 2,10', '2,31', room_svg('s7', draw_bath, 110, 210, K_SHEET, FS_SHEET, False, 'Planta baño auxiliar 1,10 por 2,10 m')),
    ('Alcoba principal', '2,50 × 3,38', '8,45', room_svg('s3', draw_master, 250, 338, K_SHEET, FS_SHEET, False, 'Planta alcoba principal 2,50 por 3,38 m')),
    ('Alcoba 2', '2,30 × 2,80', '6,44', room_svg('s4', draw_bed2, 230, 280, K_SHEET, FS_SHEET, False, 'Planta alcoba 2, 2,30 por 2,80 m')),
    ('Alcoba 3', '2,00 × 2,55', '5,10', room_svg('s5', draw_bed3, 200, 255, K_SHEET, FS_SHEET, False, 'Planta alcoba 3, 2,00 por 2,55 m')),
]
sheet_html = '<div class="sheet">' + ''.join(
    f'<figure class="rm">{svg}<figcaption><b>{n}</b><span class="mono">{dm} m · {ar} m²</span></figcaption></figure>'
    for n, dm, ar, svg in sheet) + '</div>'

kp_fs = K_DET
kitchen_plan = room_svg('kp', draw_kitchen, 405, 230, 1.0, FS_DET, True, 'Planta de cocina-ropas: mueble lineal de 3,40 m sobre el muro superior, pasillo de 1,10 m y zona de ropas en el muro opuesto', extra=(0, 1.4 * FS_DET / 1.0, 1.5 * FS_DET / 1.0, 1.4 * FS_DET / 1.0))
bath_plan = room_svg('bp', draw_bath, 110, 210, K_DET, FS_DET, True, 'Planta de baño 1,10 por 2,10 m: mueble, sanitario y ducha sobre el muro izquierdo', extra=(0, 0, 1.5 * FS_DET / K_DET, 0))
master_plan = room_svg('ap1', draw_master, 250, 338, K_BED, FS_DET, True, 'Planta alcoba principal con cama doble y closet de 2,50 m', extra=(0, 0, 1.5 * FS_DET / K_BED, 0))
bed2_plan = room_svg('ap2', draw_bed2, 230, 280, K_BED, FS_DET, True, 'Planta alcoba 2 con cama de 1,20 y closet de 1,60 m', extra=(0, 0, 1.5 * FS_DET / K_BED, 0))
bed3_plan = room_svg('ap3', draw_bed3, 200, 255, K_BED, FS_DET, True, 'Planta alcoba 3 con cama de 1,00 y closet de 1,20 m', extra=(0, 0, 1.5 * FS_DET / K_BED, 0))
living_plan = room_svg('sl', draw_living, 265, 340, 1.0, FS_DET, True, 'Planta sala-comedor con mesa redonda para 4, sofá de 2 puestos, panel de TV y balcón', extra=(0, 0, 1.5 * FS_DET, 82 + 1.6 * FS_DET))

KE, RE, BE, CE = kitchen_elev(), laundry_elev(), bath_elev(), closet_elev()

# ---------------------------------------------------------------- presupuesto
CH = [
    ('Logística, protecciones y limpieza', (0.8, 1.2), (1.0, 1.4), 'Protección de zonas comunes, acarreos, escombros y aseo final', 'Mayor control de protección y entrega final'),
    ('Preparación y nivelación', (0.9, 1.3), (1.5, 2.3), 'Diagnóstico, reparaciones y nivelación localizada', 'Suma impermeabilización, pruebas de humedad y estanqueidad'),
    ('Muros, estuco y pintura', (2.8, 3.3), (3.0, 3.7), 'Remates, estuco y pintura lavable blanca cálida', 'Pintura lavable superior y mejores remates'),
    ('Pisos SPC, cerámicas y transiciones', (3.9, 4.5), (4.7, 5.7), 'SPC en zonas secas, zócalos, perfiles e instalación', 'Mayor capa de uso, base acústica y perfiles'),
    ('Cocina + ropas', (6.7, 7.5), (8.0, 9.2), 'Carpintería RH, granito, salpicadero, lavadero e iluminación', 'Herrajes superiores, organización y electricidad'),
    ('Dos baños completos', (6.3, 7.0), (7.3, 8.5), 'Impermeabilización, enchapes, sanitarios, muebles y divisiones', 'Impermeabilización reforzada y griferías definidas'),
    ('Closets de tres alcobas', (3.1, 3.5), (3.8, 4.6), 'Melamina RH, almacenamiento y herrajes', 'Distribución interna, herrajes y remates'),
    ('Eléctrico, iluminación, drywall y balcón', (1.6, 2.2), (2.2, 3.0), 'Puntos seleccionados, luminarias y acabados de balcón', 'Más circuitos, puntos y control de luz'),
]
SCALE = 10.0


def mm(v):
    return f"{v:.1f}".replace('.', ',')


def rng(lo, hi):
    return f'${mm(lo)}–{mm(hi)} M'


rows = ''
for name, a, b, sa, sb in CH:
    da = (a[0] + a[1]) / 2
    db = (b[0] + b[1]) / 2
    delta = db - da
    ba = f'<span class="rb a" style="left:{a[0] / SCALE * 100:.2f}%;width:{(a[1] - a[0]) / SCALE * 100:.2f}%" title="Opción A · {name}: {rng(*a)}"></span>'
    bb = f'<span class="rb b" style="left:{b[0] / SCALE * 100:.2f}%;width:{(b[1] - b[0]) / SCALE * 100:.2f}%" title="Opción B · {name}: {rng(*b)}"></span>'
    rows += (f'<tr><td class="cap"><b>{name}</b><small>{sa}. <span class="bsum">B: {sb}.</span></small></td>'
             f'<td class="trk"><div class="track">{ba}{bb}</div></td>'
             f'<td class="num va">{rng(*a)}</td><td class="num vb">{rng(*b)}</td>'
             f'<td class="num dl">+{mm(delta)}</td></tr>')
ticks = ''.join(f'<span style="left:{v / SCALE * 100:.0f}%">{v:g}</span>' for v in (0, 2, 4, 6, 8, 10))
budget_html = f'''
<div class="tbl budget"><table>
<thead><tr><th>Capítulo</th><th class="trk"><div class="ticks">{ticks}</div></th><th class="num"><span class="optchip a">A</span></th><th class="num"><span class="optchip b">B</span></th><th class="num">B − A</th></tr></thead>
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
  MATA MATC
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
:root[data-opt="b"]{ MATB }
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
.seg button[aria-pressed="true"][data-opt-set="a"]{background:var(--sA-soft);color:var(--ink)}
.seg button[aria-pressed="true"][data-opt-set="b"]{background:var(--sB-soft);color:var(--ink)}
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
.loose rect,.loose circle,rect.loose{fill:var(--d-loose);stroke:var(--d-line);stroke-width:1.1}
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

:root:not([data-opt="b"]) .only-b{display:none}
:root[data-opt="b"] .only-a{display:none}

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
:root[data-opt="b"] .bblock{border-color:var(--sB);box-shadow:0 0 0 1px var(--sB)}
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
:root:not([data-opt="b"]) .oc[data-opt-card="a"]{border-color:var(--sA);box-shadow:0 0 0 1px var(--sA),var(--shadow)}
:root[data-opt="b"] .oc[data-opt-card="b"]{border-color:var(--sB);box-shadow:0 0 0 1px var(--sB),var(--shadow)}
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
.budget table{min-width:720px}
.budget td.cap b{display:block;font-weight:600}
.budget td.cap small{display:block;color:var(--muted);font-size:.76rem;line-height:1.4;margin-top:2px;max-width:40ch}
.budget th.trk,.budget td.trk{width:38%;min-width:220px}
.track{position:relative;height:30px;margin-top:4px;background-image:linear-gradient(90deg,var(--line) 1px,transparent 1px);background-size:20% 100%;border-right:1px solid var(--line)}
.rb{position:absolute;height:10px;border-radius:3px;min-width:4px;transition:opacity .2s}
.rb.a{top:3px;background:var(--sA)} .rb.b{top:17px;background:var(--sB)}
:root:not([data-opt="b"]) .rb.b{opacity:.35}
:root[data-opt="b"] .rb.a{opacity:.35}
.ticks{position:relative;height:14px}
.ticks span{position:absolute;transform:translateX(-50%);font-size:.66rem}
.ticks span:first-child{transform:none} .ticks span:last-child{transform:translateX(-100%)}
.budget td.va,.budget td.vb{padding-top:12px}
:root:not([data-opt="b"]) td.va,:root[data-opt="b"] td.vb{font-weight:600}
td.dl{color:var(--muted);padding-top:12px}
.totals td:first-child{font-weight:600}
.totals tr.big td{font-weight:700;background:var(--accent-soft)}
:root:not([data-opt="b"]) .totals .ca,:root[data-opt="b"] .totals .cb{color:var(--ink);font-weight:700}
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
CSS = CSS.replace('MATA', mat_css(MAT_A)).replace('MATC', mat_css(MAT_C)).replace('MATB', mat_css(MAT_B))

# ---------------------------------------------------------------- contenido
TABS = [('resumen', 'Resumen'), ('planta', 'Planta'), ('cocina', 'Cocina y ropas'), ('banos', 'Baños'),
        ('alcobas', 'Alcobas'), ('sala', 'Sala y balcón'), ('presupuesto', 'Presupuesto'), ('obra', 'Obra'),
        ('entrega', 'Entrega')]

tabs_html = ''.join(
    f'<button class="tab" role="tab" id="t-{k}" aria-controls="v-{k}" data-go="{k}" aria-selected="{"true" if i == 0 else "false"}"'
    f' tabindex="{0 if i == 0 else -1}">{v}</button>' for i, (k, v) in enumerate(TABS))

V = {}

V['resumen'] = f'''
<div class="kicker">Propuesta de acabados · 29 sep 2026</div>
<h2>Dos opciones sobre la <span class="em">misma distribución</span></h2>
<p class="sub">La propuesta conserva la distribución del Tipo A. No hay cambios estructurales, de fachada, de ductos comunes ni de redes sin autorización. Entre A y B cambia cuánto se invierte en lo que no se ve: impermeabilización, herrajes, circuitos y garantías.</p>

<div class="opts">
  <div class="oc" data-opt-card="a">
    <span class="oh"><span class="optchip a">A</span><h3>Optimizada</h3><button type="button" class="pick" data-opt-set="a" aria-pressed="true"><span class="only-a">Viendo A</span><span class="only-b">Ver con A</span></button></span>
    <span class="amts"><span><small>Sin electrodomésticos</small><span class="amt">$28,5–32,0 M</span></span><span><small>Con electrodomésticos</small><span class="amt">$30,5–34,0 M</span></span></span>
    <p>Cálida, contemporánea y práctica. <b>Mejor para:</b> primera inversión, arriendo de calidad o presupuesto contenido. <b>Riesgo si se ejecuta mal:</b> ahorrar en sellos, herrajes o redes ocultas.</p>
    {swatches(SWATCH_A, MAT_A)}
  </div>
  <div class="oc" data-opt-card="b">
    <span class="oh"><span class="optchip b">B</span><h3>Mejorada</h3><button type="button" class="pick" data-opt-set="b" aria-pressed="false"><span class="only-b">Viendo B</span><span class="only-a">Ver con B</span></button></span>
    <span class="amts"><span><small>Sin electrodomésticos</small><span class="amt">$32,0–35,5 M</span></span><span><small>Con electrodomésticos</small><span class="amt">$34,0–37,5 M</span></span></span>
    <p>Sobria y de mayor detalle. <b>Mejor para:</b> vivienda propia a largo plazo y menor riesgo de reprocesos. <b>Riesgo si se ejecuta mal:</b> pagar extras por decorativos si no se controla el alcance.</p>
    {swatches(SWATCH_B, MAT_B)}
  </div>
</div>

<div class="reco">
  <div class="tag">Recomendación de la propuesta</div>
  <h3>Opción A reforzada</h3>
  <p>Usa el presupuesto de la A como techo y adopta cinco protecciones de la B. Así el dinero va a lo que no se ve pero evita daños, sin agrandar la decoración.</p>
  <ol class="five">
    <li><b>Impermeabilización con prueba de estanqueidad</b>Baños, ropas y balcón, con acta.<br><button type="button" data-go="banos">Ver en Baños</button></li>
    <li><b>SPC con ficha técnica</b>Marca, capa de uso, base IXPE y garantía.<br><button type="button" data-go="planta">Ver en Planta</button></li>
    <li><b>Herrajes de marca</b>Bisagras y correderas con referencia y garantía.<br><button type="button" data-go="cocina">Ver en Cocina</button></li>
    <li><b>Circuitos eléctricos definidos</b>Horno, nevera, lavadora y pequeños electrodomésticos.<br><button type="button" data-go="cocina">Ver en Cocina</button></li>
    <li><b>Garantías y actas de entrega</b>Por capítulo, con saldo retenido.<br><button type="button" data-go="obra">Ver en Obra</button></li>
  </ol>
  <div class="ceiling">Techo de referencia: <span>$32,0 M sin electrodomésticos</span><span>$34,0 M con electrodomésticos</span></div>
</div>

<div class="grid2">
  <div class="card"><h3>Cambios frente a la versión anterior</h3><ul>
    <li><b>Baño principal:</b> antes se convertía en vestier. La propuesta lo deja como baño completo, así que quedan dos baños.</li>
    <li><b>Cocina:</b> lineal sobre un muro, sin península ni barra fija.</li>
    <li><b>Pisos:</b> SPC en zonas secas y cerámica antideslizante en baños, ropas y balcón. Antes era porcelanato símil madera.</li>
    <li><b>Presupuesto:</b> $28,5–32,0 M sin electrodomésticos. Antes el nivel recomendado era $25–28 M.</li>
  </ul></div>
  <div class="card"><h3>Criterios de diseño</h3><ul>
    <li><b>Cocina:</b> mueble lineal. Sin península fija para circular cómodo en 2,30 m de ancho.</li>
    <li><b>Material húmedo:</b> melamina RH, cantos PVC y sellos sanitarios; impermeabilización bajo enchapes.</li>
    <li><b>Iluminación:</b> base LED de 3.000–4.000 K, luz de tarea en cocina y baño.</li>
    <li><b>Prioridad:</b> durabilidad, ventilación, redes bien hechas y almacenaje antes que decoración voluminosa.</li>
  </ul></div>
</div>
{note('', '!', '<b>Aviso de precisión.</b> Las vistas y la propuesta son conceptuales. El plano comercial da medidas aproximadas: no se debe fabricar carpintería, cortar piedra ni mover redes sin medir el apartamento en obra gris.')}
'''

V['planta'] = f'''
<div class="kicker">Planta · 44,30 m² privados · altura libre 2,40 m</div>
<h2>Cada espacio a la misma escala</h2>
<p class="sub">Medidas del plano comercial y amoblamiento de la propuesta. La posición de los espacios en la lámina es esquemática; puertas y ventanas no se dibujan, salvo la puerta-ventana del balcón. Para la ubicación real usa el plano comercial.</p>
{sheet_html}
{LEG_PLAN}
<div class="block"><h3>Base de diseño</h3>
<div class="tbl"><table>
<thead><tr><th>Espacio</th><th class="num">Medidas (m)</th><th class="num">Área</th><th>Piso</th><th>Qué se hace</th></tr></thead>
<tbody>
<tr><td class="z">Alcoba principal</td><td class="num">2,50 × 3,38</td><td class="num">8,45 m²</td><td>SPC</td><td>Closet RH de 2,50 m</td></tr>
<tr><td class="z">Alcoba 2</td><td class="num">2,30 × 2,80</td><td class="num">6,44 m²</td><td>SPC</td><td>Closet RH de 1,60 m</td></tr>
<tr><td class="z">Alcoba 3</td><td class="num">2,00 × 2,55</td><td class="num">5,10 m²</td><td>SPC</td><td>Closet RH de 1,20 m</td></tr>
<tr><td class="z">Baño principal</td><td class="num">1,10 × 2,10</td><td class="num">2,31 m²</td><td>Cerámica 30 × 30</td><td>Baño completo</td></tr>
<tr><td class="z">Baño auxiliar</td><td class="num">1,10 × 2,10</td><td class="num">2,31 m²</td><td>Cerámica 30 × 30</td><td>Baño completo (Inacar lo entrega terminado)</td></tr>
<tr><td class="z">Cocina-ropas</td><td class="num">4,05 × 2,30</td><td class="num">9,32 m²</td><td>SPC + cerámica en ropas</td><td>Cocina lineal RH y zona de ropas</td></tr>
<tr><td class="z">Sala-comedor</td><td class="num">2,65 × 3,40</td><td class="num">9,01 m²</td><td>SPC</td><td>Panel de TV y luz</td></tr>
<tr><td class="z">Balcón</td><td class="num">2,00 × 0,72</td><td class="num">1,44 m²</td><td>Cerámica antideslizante</td><td>Sellos, luz exterior y pintura</td></tr>
</tbody>
<tfoot><tr><td colspan="2">Espacios interiores medidos</td><td class="num">42,9 m²</td><td colspan="2" style="font-weight:400;color:var(--muted)">La diferencia con 44,30 m² es circulación y muros.</td></tr></tfoot>
</table></div></div>
<div class="grid2">
  <div class="card"><h3>Pisos · Opción A</h3><ul>
    <li>SPC tono roble claro en zonas secas, con zócalos y perfiles de transición.</li>
    <li>Cerámica antideslizante en baños, balcón y ropas.</li>
    <li>SPC al final de la obra húmeda, después de enchapes.</li>
  </ul></div>
  {b_block('Qué mejora B en pisos', [('SPC con marca y referencia definidas: espesor, capa de uso, base IXPE, garantía e instrucciones de instalación; perfiles y dilataciones incluidos.', True), ('Roble natural con base acústica.', False)])}
</div>
'''

V['cocina'] = f'''
<div class="kicker">Cocina y ropas · 4,05 × 2,30 m</div>
<h2>Cocina lineal sobre un muro, <span class="em">sin península</span></h2>
<p class="sub">Se elimina la península de 1,50 × 0,90 m para dejar un pasillo de 90 a 110 cm. En este esquema la zona de ropas va en el muro de enfrente, que es lo que deja el pasillo en 1,10 m. Confirma la posición real de los puntos de agua y gas antes de diseñar.</p>
<div class="figs">
  {fig(KE, '<b>Vista frontal del muro de cocina.</b> Mesón a ≈90 cm, altos a 55–60 cm del mesón y tira LED 3.000 K debajo. <span class="only-b">En B, la torre de despensa (punteada) solo va si la medida conserva pasillo y ventilación de la nevera.</span>', 'panel')}
</div>
<div class="legend">{sw('upper', 'Altos blanco mate', 'Altos blanco cálido')}{sw('lower', 'Bajos taupe / moca claro', 'Bajos gris piedra suave')}{sw('ctr', 'Granito Negro San Gabriel', 'Granito o superficie compacta')}{sw('sp', 'Salpicadero 30 × 60')}{sw('metal', 'Manijas negro mate', 'Perfil de aluminio')}{sw('led', 'LED 3.000 K')}</div>
{note('blue', 'i', '<b>Los módulos no llenan el mueble.</b> Nevera, lavaplatos, cajonero, estufa y remate suman 2,50–2,90 m, y el mueble lineal previsto mide 3,20–3,60 m. En el dibujo esa diferencia va en un módulo de ajuste de 50 cm. Defínelo con la medida láser antes del despiece.')}
<div class="figs">
  {fig(kitchen_plan, '<b>Planta.</b> Los altos se marcan punteados sobre el mesón. La línea café punteada es la transición de SPC a cerámica en ropas.', 'panel')}
  {fig(RE, '<b>Muro de ropas</b>, visto desde la cocina. Enchape de 1,20 m, lavadero compacto y gabinete alto de limpieza.', 'panel')}
</div>
<div class="block"><h3>Especificación · Opción A</h3>
{spec_table([
    ('Distribución', 'Cocina lineal de 3,20–3,60 ml sobre un muro. Mesón de 60 cm de fondo. Pasillo objetivo de 90–110 cm. Sin península fija.'),
    ('Módulos bajos', 'Nevera 60–70 cm; lavaplatos 60 cm; cajonero 40–60 cm; módulo estufa 60 cm; remate/despensa 30–40 cm. Ajuste final a medida real.'),
    ('Carpintería', 'Aglomerado RH 18 mm; canto PVC mínimo 1 mm y 2 mm en frentes y bordes expuestos; patas regulables; zócalo PVC/aluminio; bandeja antiderrame bajo lavaplatos.'),
    ('Muebles altos', 'Blanco mate, fondo 30–35 cm, altura 70–80 cm, a 55–60 cm sobre el mesón; bisagras de cierre suave.'),
    ('Herrajes', 'Bisagras de cierre suave de marca definida; correderas telescópicas de extensión total; carga reforzada en el cajón de ollas.'),
    ('Mesón', 'Granito Negro San Gabriel pulido, 2 cm, sellado, recortes limpios, borde pulido y silicona neutra antihongos.'),
    ('Salpicadero', 'Cerámica blanca o marmolizada 30 × 60 cm desde el mesón hasta los muebles altos.'),
    ('Lavaplatos', 'Acero inoxidable profundo de 60 × 40 cm aprox.; sifón accesible, válvulas de paso y grifería monomando de cuello alto.'),
    ('Ropas', 'Lavadero compacto, espacio para lavadora, enchape de 1,20 m, piso antideslizante y gabinete alto de limpieza.'),
    ('Iluminación', 'Tira LED 3.000 K bajo altos con perfil de aluminio y difusor; luz general LED y tomas sobre el salpicadero.'),
])}
</div>
{b_block('Qué mejora B en cocina y ropas', [
    ('Circuitos dedicados para horno, cocina si aplica, lavadora, nevera y pequeños electrodomésticos; tablero y cableado revisados por electricista.', True),
    ('Correderas de extensión total y carga reforzada. No aceptar “cierre suave” sin marca, referencia o garantía.', True),
    ('Melamina RH 18 mm con cantos de 2 mm en frentes; organizador de cubiertos, gaveta profunda de ollas, bandeja extraíble de aseo y divisores.', False),
    ('Mesón en granito de primera selección con sellado documentado, o superficie equivalente con ficha técnica.', False),
    ('Torre de despensa o módulo alto solo si la medida final conserva pasillo y ventilación de la nevera.', False),
    ('Reserva para extractor con salida permitida o, si no hay salida, campana de recirculación con filtros reemplazables.', False),
    ('Luz por escenas: general, bajo muebles, sala-comedor y baño, en circuitos independientes.', False),
])}
'''

V['banos'] = f'''
<div class="kicker">Baños · 2 × (1,10 × 2,10 m)</div>
<h2>Dos baños completos con la misma disposición</h2>
<p class="sub">En este esquema el mueble, el sanitario y la ducha van sobre el muro largo, con la ducha al fondo detrás de una división corrediza en vidrio templado de 8 mm. Verifica la posición del desagüe del sanitario y del sifón de la ducha en obra.</p>
<div class="figs">
  {fig(bath_plan, '<b>Planta.</b> Piso cerámico antideslizante 30 × 30.', 'panel')}
  {fig(BE, '<b>Muro largo.</b> Enchape claro 30 × 60, mueble flotante RH de 60 cm, espejo con luz frontal.', 'panel')}
</div>
<div class="legend">{sw('tw', 'Enchape de muro 30 × 60')}{sw('tf', 'Piso antideslizante 30 × 30')}{sw('van', 'Mueble RH taupe', 'Mueble RH roble natural')}{sw('metal', 'Grifería negro mate', 'Grifería y herrajes inoxidables')}{sw('glass', 'Vidrio templado 8 mm')}</div>
<div class="block"><h3>Especificación · Opción A</h3>
{spec_table([
    ('Impermeabilización', 'Bajo enchapes en duchas antes de enchapar.'),
    ('Enchapes', 'Claro 30 × 60 en muros y antideslizante 30 × 30 en piso.'),
    ('Aparatos', 'Sanitario ahorrador y mezcladora de ducha.'),
    ('División', 'Corrediza en vidrio templado de 8 mm.'),
    ('Mueble y espejo', 'Mueble flotante RH de 60 cm, espejo y luz frontal.'),
])}
</div>
{b_block('Qué mejora B en baños', [
    ('Sistema cementicio o equivalente en duchas y perímetros, media caña en encuentros, prueba de estanqueidad antes de enchapar y acta fotográfica.', True),
    ('Desagües y pendientes comprobados antes de cerrar.', False),
    ('Griferías de marca con repuestos disponibles.', False),
    ('Vidrio templado 8 mm con herrajes inoxidables.', False),
    ('Espejo con luz frontal útil para el uso diario.', False),
])}
{note('', '!', '<b>El baño auxiliar ya viene terminado.</b> Inacar lo entrega con cerámica, muros en estuco y vinilo, ducha enchapada, sanitario y griferías. La propuesta cotiza dos baños completos. Pide que el auxiliar se cotice aparte: si decides conservar lo entregado, ese capítulo baja.')}
'''

V['alcobas'] = f'''
<div class="kicker">Alcobas · closets en melamina RH</div>
<h2>Closets ajustados a la cama y a la circulación</h2>
<p class="sub">Los closets van contra un muro corto con puertas batientes piso-techo cuando la apertura lo permite; si no, corredizas. Las camas se dibujan solo como referencia de espacio y no hacen parte del presupuesto.</p>
<div class="figs panel">
  {fig(master_plan, '<b>Alcoba principal</b> · 2,50 × 3,38 m. Cama doble 1,40 y 88 cm libres frente al closet.')}
  {fig(bed2_plan, '<b>Alcoba 2</b> · 2,30 × 2,80 m. Cama 1,20 y closet de 1,60 m.')}
  {fig(bed3_plan, '<b>Alcoba 3</b> · 2,00 × 2,55 m. Cama 1,00 contra el muro y closet de 1,20 m.')}
</div>
<div class="figs">
  {fig(CE, '<b>Interior del closet de la alcoba principal</b>, sin puertas. <span class="only-a">Opción A: barra de colgar, cajones útiles y zapatero.</span><span class="only-b">Opción B: doble colgado, cajones, zapatero, colgado largo, maletero y rejillas de ventilación.</span>', 'panel')}
</div>
<div class="legend">{sw('clo', 'Melamina RH blanco cálido (sugerido)', 'Melamina RH roble natural (sugerido)')}{sw('metal', 'Barras y manijas negro mate', 'Barras y herrajes inoxidables')}</div>
<div class="block"><h3>Especificación · Opción A</h3>
{spec_table([
    ('Alcoba principal', 'Closet RH de 2,50 m aprox., puertas batientes piso-techo según altura final, barra de colgar, cajones útiles y zapatero.'),
    ('Alcobas 2 y 3', 'Closets RH ajustados a cama y circulación: 1,60 m y 1,20 m como referencia. Priorizar puertas batientes si permiten apertura.'),
])}
</div>
{b_block('Qué mejora B en closets', [
    ('Herrajes de marca con referencia y garantía.', True),
    ('Interior diseñado para el uso real: doble colgado donde aplique, cajones, zapatero, maletero y ventilación.', False),
    ('Distribución interna y remates mejorados.', False),
])}
'''

V['sala'] = f'''
<div class="kicker">Sala-comedor 2,65 × 3,40 m · balcón 2,00 × 0,72 m</div>
<h2>Zona social liviana, sin muebles sobredimensionados</h2>
<p class="sub">Mesa redonda compacta para cuatro en vez de barra dentro de la cocina, sofá de dos puestos y panel de TV liviano. <span class="only-a">Una luz central.</span><span class="only-b">En B la luz se separa en dos escenas: comedor y sala.</span></p>
<div class="figs">
  {fig(living_plan, '<b>Planta.</b> El balcón conserva su baranda y fachada; solo se interviene piso, sellos, luz y pintura.', 'panel')}
  <div class="card" style="flex:1 1 280px;min-width:0"><h3>Especificación · Opción A</h3><ul>
    <li><b>Sala-comedor:</b> sofá de 2 puestos, mesa redonda compacta para 4, panel de TV liviano y luz central.</li>
    <li><b>Balcón:</b> piso antideslizante, sellos perimetrales, luz exterior y pintura para exterior. Respetar el reglamento de fachada.</li>
    <li><b>Cielo raso:</b> cajillo simple solo si la altura final lo admite, con luz indirecta discreta. Con 2,40 m libres, cualquier descuelgue se nota.</li>
  </ul>
  {b_block('Qué mejora B aquí', [
      ('Impermeabilización del balcón con prueba de estanqueidad antes del enchape.', True),
      ('SPC con ficha técnica y base acústica.', True),
      ('Circuito propio de luz para sala-comedor, con control de escena.', False),
  ])}
  </div>
</div>
{note('', '!', '<b>El balcón no se cierra.</b> Es área de uso exclusivo dentro de la propiedad horizontal: no se puede cerrar ni cambiar la fachada.')}
'''

V['presupuesto'] = f'''
<div class="kicker">Presupuesto objetivo · COP · Bucaramanga / Girón</div>
<h2>La diferencia entre A y B está en <span class="em">cocina, baños y pisos</span></h2>
<p class="sub">Cada fila compara el mismo capítulo en las dos opciones sobre una escala de 0 a 10 millones. La última columna es la diferencia entre los puntos medios. Son rangos objetivo de compra e instalación, a validar con visita y cotizaciones comparables.</p>
<div class="legend"><span class="key"><span class="sw" style="--c:var(--sA)"></span>Opción A · Optimizada</span><span class="key"><span class="sw" style="--c:var(--sB)"></span>Opción B · Mejorada</span><span class="key">Escala en millones de pesos</span></div>
{budget_html}
<div class="block"><h3>Totales</h3>
<div class="tbl totals"><table>
<thead><tr><th>Concepto</th><th class="num"><span class="optchip a">A</span> Optimizada</th><th class="num"><span class="optchip b">B</span> Mejorada</th></tr></thead>
<tbody>
<tr><td>Subtotal de capítulos</td><td class="num ca">$26,1–30,5 M</td><td class="num cb">$31,5–38,4 M</td></tr>
<tr><td>A: imprevistos 8–10% · B: ajuste de alcance</td><td class="num ca">+$2,1–3,0 M</td><td class="num cb">−$0,5–2,9 M</td></tr>
<tr class="big"><td>Total sin electrodomésticos</td><td class="num ca">$28,5–32,0 M</td><td class="num cb">$32,0–35,5 M</td></tr>
<tr><td>Electrodomésticos (estufa, campana y horno)</td><td class="num ca">$1,8–2,3 M</td><td class="num cb">$2,0–2,5 M</td></tr>
<tr class="big"><td>Total con electrodomésticos</td><td class="num ca">$30,5–34,0 M</td><td class="num cb">$34,0–37,5 M</td></tr>
</tbody></table></div>
<p class="disc">Los totales son el objetivo de contratación del documento y no la suma exacta de los rangos. Los imprevistos de A se usan solo para contingencias aprobadas. En B, el ajuste de alcance simplifica decorativos para no pasar del objetivo.</p>
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
  function setOpt(o){
    root.setAttribute('data-opt',o);
    [].forEach.call(document.querySelectorAll('[data-opt-set]'),function(b){b.setAttribute('aria-pressed',b.dataset.optSet===o?'true':'false')});
    try{localStorage.setItem('ob901-opt',o)}catch(e){}
  }
  document.addEventListener('click',function(e){
    var g=e.target.closest('[data-go]');
    if(g){
      e.preventDefault();show(g.dataset.go,true);
      if(!g.matches('[role="tab"]')){var bar=document.querySelector('.bar');window.scrollTo({top:bar.offsetTop-0,behavior:'smooth'})}
      return;
    }
    var o=e.target.closest('[data-opt-set],[data-opt-card]');
    if(o){setOpt(o.dataset.optSet||o.dataset.optCard)}
  });
  document.querySelector('[role="tablist"]').addEventListener('keydown',function(e){
    var i=tabs.indexOf(document.activeElement);if(i<0)return;
    var j=e.key==='ArrowRight'?i+1:e.key==='ArrowLeft'?i-1:e.key==='Home'?0:e.key==='End'?tabs.length-1:null;
    if(j===null)return;e.preventDefault();j=(j+tabs.length)%tabs.length;tabs[j].focus();show(tabs[j].dataset.go,true);
  });
  window.addEventListener('hashchange',function(){show(location.hash.slice(1),false)});
  var saved=null;try{saved=localStorage.getItem('ob901-opt')}catch(e){}
  setOpt(saved==='b'?'b':'a');
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
.linkbtn{{appearance:none;border:0;background:none;padding:0;font:inherit;color:var(--accent);text-decoration:underline;text-underline-offset:2px;cursor:pointer}}
</style>
<header><div class="wrap top">
  <div class="eyebrow">Inacar · Alto Tramonti VIS · Girón, Santander</div>
  <h1>De obra gris a obra blanca</h1>
  <p class="lede">Tu apartamento con la propuesta de acabados del 29 de septiembre: vistas a escala de cada espacio, dos opciones de presupuesto y el orden de obra. Cambia entre A y B para ver materiales y costos.</p>
  <dl class="ficha">
    <div><dt>Inmueble</dt><dd>Apto 901 · Torre 1<small>Etapa 1 · Piso 9 · Tipo A</small></dd></div>
    <div><dt>Área privada</dt><dd>44,30 m²<small>Altura libre ≈ 2,40 m</small></dd></div>
    <div><dt>Distribución</dt><dd>3 alcobas · 2 baños<small>Cocina-ropas · sala-comedor · balcón</small></dd></div>
    <div><dt>Opción A</dt><dd>$28,5–32,0 M<small>Sin electrodomésticos</small></dd></div>
    <div><dt>Opción B</dt><dd>$32,0–35,5 M<small>Sin electrodomésticos</small></dd></div>
    <div><dt>Precio</dt><dd>$210.000.000<small>VIS · Notaría 2 Bmga</small></dd></div>
  </dl>
</div></header>
<nav class="bar" aria-label="Vistas"><div class="wrap bar-in">
  <div class="tabs" role="tablist" aria-label="Vistas del apartamento">{tabs_html}</div>
  <div class="opt" role="group" aria-label="Opción de acabados"><span class="seg">
    <button type="button" data-opt-set="a" aria-pressed="true"><span class="optchip a">A</span>Optimizada</button>
    <button type="button" data-opt-set="b" aria-pressed="false"><span class="optchip b">B</span>Mejorada</button>
  </span></div>
</div></nav>
<main>{views_html}</main>
<footer><div class="wrap">
  <p><b>En resumen:</b> la propuesta lleva el apartamento a obra blanca sin tocar la distribución, con dos baños completos, cocina lineal nueva y closets en las tres alcobas. La recomendación es la Opción A reforzada, con techo de <b>$32,0 M</b> sin electrodomésticos.</p>
  <p class="disc">Hecho a partir de tu contrato de promesa de compraventa, el anexo de especificaciones de Inacar y la Propuesta de acabados Tipo A del 29-sep-2026. Las vistas son conceptuales: no sirven para fabricar carpintería, cortar piedra ni mover redes sin medir en obra.</p>
</div></footer>
<script>{JS}</script>
'''

OUT.write_text(page, encoding='utf-8')
print('ok', OUT, len(page))
