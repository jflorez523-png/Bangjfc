// Escenas 3D del Apto 901 (unidades: metros, y hacia arriba). Se renderizan fuera de línea a JPEG.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';
import { Reflector } from 'three/addons/objects/Reflector.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

RectAreaLightUniformsLib.init();
const H = 2.40;

// ------------------------------------------------------------------ paletas
export const OPT = {
  a: {
    spc: '#D9BF98', spcJ: '#B39670', upper: '#F7F5F0', lower: '#A8937F', ctr: '#232326',
    ctrF: ['#7A7672', '#9C9892', '#5E625C', '#C4C0BA', '#3E4240'], sp: '#F1EEE9', spJ: '#D6CFC5', spVeins: false,
    metal: { color: '#1F1F21', roughness: 0.55, metalness: 0.35 }, tw: '#EDE9E2', twJ: '#D2CBC0',
    tf: '#C2BAAE', tfJ: '#9F9588', clo: '#EEE9E0', cloWood: false, van: '#A8937F', vanWood: false,
    gola: false, tower: false, lights2: false,
  },
  b: {
    spc: '#C9A575', spcJ: '#9E7C52', upper: '#F4F1EA', lower: '#A9A49C', ctr: '#3D3C3B',
    ctrF: ['#8C8984', '#A7A39D', '#5A5856', '#C9C5BF', '#2E2D2C'], sp: '#ECEAE6', spJ: '#CFCAC2', spVeins: true,
    metal: { color: '#B4B8BD', roughness: 0.28, metalness: 1.0 }, tw: '#E9E7E3', twJ: '#CBC6BE',
    tf: '#B2AEA7', tfJ: '#8F8A82', clo: '#D2B28A', cloWood: true, van: '#C9A575', vanWood: true,
    gola: true, tower: true, lights2: true,
  },
};

// ------------------------------------------------------------------ utilidades
function rng(seed) {
  return function () {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
const hex = c => '#' + c.getHexString();
function jitter(base, dl, ds, r) {
  const c = new THREE.Color(base);
  c.offsetHSL(0, (r() - 0.5) * ds, (r() - 0.5) * dl);
  return hex(c);
}

function canvasTex(w, h, draw, srgb = true) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// Tablas de madera: vetas a lo largo del eje v del lienzo
function woodSpec(base, joint, { cols = 8, rows = 2, pw = 0.18, pl = 1.22, px = 1024, joints = true, vary = 0.07, seed = 1 } = {}) {
  const W = px, Hh = Math.round(px * (rows * pl) / (cols * pw));
  const tex = canvasTex(W, Hh, (g) => {
    const cw = W / cols, ch = Hh / rows;
    for (let i = 0; i < cols; i++) {
      const off = ((i * 0.37 + 0.11) % 1) * ch;
      for (let j = -1; j <= rows; j++) {
        const jm = ((j % rows) + rows) % rows;
        const r = rng(seed * 1000 + i * 37 + jm * 7);
        const y0 = j * ch + off;
        g.fillStyle = jitter(base, vary, 0.04, r);
        g.fillRect(i * cw, y0, cw, ch);
        for (let k = 0; k < 70; k++) {
          const x = i * cw + r() * cw, a = 0.03 + r() * 0.11, lw = 0.4 + r() * 1.5;
          const ph = r() * 6.28, f = 0.003 + r() * 0.012, amp = 0.8 + r() * 3.2;
          g.strokeStyle = `rgba(84,56,28,${a})`; g.lineWidth = lw; g.beginPath();
          for (let y = y0; y <= y0 + ch + 1; y += 8) {
            const xx = Math.min(i * cw + cw - 1, Math.max(i * cw + 1, x + Math.sin(y * f + ph) * amp));
            if (y === y0) g.moveTo(xx, y); else g.lineTo(xx, y);
          }
          g.stroke();
        }
        for (let k = 0; k < 18; k++) {
          g.strokeStyle = `rgba(255,248,235,${0.03 + r() * 0.05})`; g.lineWidth = 1 + r() * 2;
          const x = i * cw + r() * cw; g.beginPath(); g.moveTo(x, y0); g.lineTo(x + (r() - 0.5) * 3, y0 + ch); g.stroke();
        }
        if (joints) { g.fillStyle = joint; g.fillRect(i * cw, y0, cw, Math.max(1.5, px / 600)); }
      }
      if (joints) { g.fillStyle = joint; g.fillRect(i * cw, 0, Math.max(1.5, px / 600), Hh); }
    }
  });
  return { tex, sx: cols * pw, sy: rows * pl };
}

function graniteSpec(base, flecks, seed = 3, px = 1024, size = 0.6) {
  const tex = canvasTex(px, px, (g, w, h) => {
    const r = rng(seed);
    g.fillStyle = base; g.fillRect(0, 0, w, h);
    for (let k = 0; k < 420; k++) {
      const dark = r() < 0.55;
      g.fillStyle = dark ? `rgba(0,0,0,${0.05 + r() * 0.08})` : `rgba(140,140,135,${0.03 + r() * 0.05})`;
      const s = 6 + r() * 26; g.beginPath(); g.arc(r() * w, r() * h, s, 0, 7); g.fill();
    }
    for (let k = 0; k < 26000; k++) {
      g.fillStyle = flecks[Math.floor(r() * flecks.length)];
      g.globalAlpha = 0.25 + r() * 0.7;
      const s = 0.5 + r() * 2.2; g.fillRect(r() * w, r() * h, s, s * (0.5 + r() * 0.9));
    }
    g.globalAlpha = 1;
  });
  return { tex, sx: size, sy: size };
}

function tileSpec({ tw, th, cols, rows, base, grout, px = 1024, vary = 0.025, veins = false, speckle = false, seed = 5 }) {
  const W = px, Hh = Math.round(px * rows * th / (cols * tw));
  const tex = canvasTex(W, Hh, (g) => {
    const r = rng(seed);
    g.fillStyle = grout; g.fillRect(0, 0, W, Hh);
    const cw = W / cols, ch = Hh / rows, gp = Math.max(2, px / 260);
    for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
      const x = i * cw + gp / 2, y = j * ch + gp / 2, w = cw - gp, h = ch - gp;
      g.fillStyle = jitter(base, vary, 0.02, r); g.fillRect(x, y, w, h);
      g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip();
      if (speckle) {
        for (let k = 0; k < w * h / 18; k++) {
          g.fillStyle = r() < 0.5 ? `rgba(60,55,48,${0.08 + r() * 0.16})` : `rgba(255,255,250,${0.08 + r() * 0.14})`;
          const s = 0.6 + r() * 1.6; g.fillRect(x + r() * w, y + r() * h, s, s);
        }
      }
      if (veins) {
        for (let k = 0; k < 4; k++) {
          g.strokeStyle = `rgba(128,126,120,${0.06 + r() * 0.08})`; g.lineWidth = 0.5 + r() * 1.1;
          g.beginPath(); const sx = x + r() * w * 0.3, sy = y + r() * h;
          g.moveTo(sx, sy);
          g.bezierCurveTo(x + r() * w, y + r() * h, x + r() * w, y + r() * h, x + w * (0.7 + r() * 0.3), y + r() * h);
          g.stroke();
        }
      }
      const gr = g.createLinearGradient(x, y, x + w, y + h);
      gr.addColorStop(0, 'rgba(255,255,255,0.05)'); gr.addColorStop(1, 'rgba(0,0,0,0.04)');
      g.fillStyle = gr; g.fillRect(x, y, w, h);
      g.restore();
    }
  });
  return { tex, sx: cols * tw, sy: rows * th };
}

function noiseSpec(base, amt = 0.03, seed = 9, px = 256, size = 0.5) {
  const tex = canvasTex(px, px, (g, w, h) => {
    const r = rng(seed); g.fillStyle = base; g.fillRect(0, 0, w, h);
    for (let k = 0; k < 9000; k++) {
      g.fillStyle = r() < 0.5 ? `rgba(0,0,0,${amt * r()})` : `rgba(255,255,255,${amt * r()})`;
      g.fillRect(r() * w, r() * h, 1.5, 1.5);
    }
  });
  return { tex, sx: size, sy: size };
}

function texFor(spec, w, h, rot = false) {
  const t = spec.tex.clone(); t.needsUpdate = true;
  t.repeat.set(w / spec.sx, h / spec.sy);
  if (rot) { t.center.set(0.5, 0.5); t.rotation = Math.PI / 2; t.repeat.set(h / spec.sx, w / spec.sy); }
  return t;
}

const std = (o) => new THREE.MeshStandardMaterial(o);

// ------------------------------------------------------------------ geometría
function mesh(parent, geo, mat, x, y, z, cast = true, receive = true) {
  const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z);
  m.castShadow = cast; m.receiveShadow = receive; parent.add(m); return m;
}
function box(p, x0, y0, z0, x1, y1, z1, mat, o = {}) {
  return mesh(p, new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0), mat, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, o.cast ?? true, o.receive ?? true);
}
function rbox(p, x0, y0, z0, x1, y1, z1, mat, r = 0.02, o = {}) {
  const w = x1 - x0, h = y1 - y0, d = z1 - z0;
  const rr = Math.min(r, w / 2 - 0.001, h / 2 - 0.001, d / 2 - 0.001);
  return mesh(p, new RoundedBoxGeometry(w, h, d, 4, rr), mat, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, o.cast ?? true, o.receive ?? true);
}
function cyl(p, x, y0, z, r, h, mat, seg = 32, rTop = null) {
  return mesh(p, new THREE.CylinderGeometry(rTop ?? r, r, h, seg), mat, x, y0 + h / 2, z);
}
// planos: 'xy' mira a +z (f=1) o -z; 'zy' mira a +x o -x; 'xz' mira arriba o abajo
function plane(p, kind, a0, b0, a1, b1, c, mat, f = 1, o = {}) {
  const w = a1 - a0, h = b1 - b0;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat);
  if (kind === 'xy') { m.position.set((a0 + a1) / 2, (b0 + b1) / 2, c); if (f < 0) m.rotation.y = Math.PI; }
  if (kind === 'zy') { m.position.set(c, (b0 + b1) / 2, (a0 + a1) / 2); m.rotation.y = f > 0 ? Math.PI / 2 : -Math.PI / 2; }
  if (kind === 'xz') { m.position.set((a0 + a1) / 2, c, (b0 + b1) / 2); m.rotation.x = f > 0 ? -Math.PI / 2 : Math.PI / 2; }
  m.receiveShadow = o.receive ?? true; m.castShadow = o.cast ?? false; p.add(m); return m;
}
function texPlane(p, kind, a0, b0, a1, b1, c, spec, props, f = 1, rot = false) {
  const mat = std({ ...props, map: texFor(spec, a1 - a0, b1 - b0, rot) });
  return plane(p, kind, a0, b0, a1, b1, c, mat, f);
}

// muros con vanos; open[lado] = [[a, b, y0, y1], ...] medidos sobre x (N/S) o z (O/E)
function walls(p, W, D, mat, { open = {}, skip = [], t = 0.12 } = {}) {
  const make = {
    N: (a, b, y0, y1) => box(p, a, y0, -t, b, y1, 0, mat),
    S: (a, b, y0, y1) => box(p, a, y0, D, b, y1, D + t, mat),
    W: (a, b, y0, y1) => box(p, -t, y0, a, 0, y1, b, mat),
    E: (a, b, y0, y1) => box(p, W, y0, a, W + t, y1, b, mat),
  };
  for (const s of ['N', 'S', 'W', 'E']) {
    if (skip.includes(s)) continue;
    const ns = s === 'N' || s === 'S';
    const lo = ns ? -t : 0, hi = ns ? W + t : D;
    let cur = lo;
    for (const [a, b, y0, y1] of (open[s] || []).slice().sort((u, v) => u[0] - v[0])) {
      if (a > cur) make[s](cur, a, 0, H);
      if (y0 > 0) make[s](a, b, 0, y0);
      if (y1 < H) make[s](a, b, y1, H);
      cur = b;
    }
    if (cur < hi) make[s](cur, hi, 0, H);
  }
  box(p, -t, H, -t, W + t, H + 0.18, D + t, mat.userData.ceil || mat);
}

function skirting(p, W, D, mat, sides = ['N', 'S', 'W', 'E'], gaps = {}) {
  const hgt = 0.07, th = 0.012;
  const seg = (s, a, b) => {
    if (s === 'N') box(p, a, 0, 0, b, hgt, th, mat);
    if (s === 'S') box(p, a, 0, D - th, b, hgt, D, mat);
    if (s === 'W') box(p, 0, 0, a, th, hgt, b, mat);
    if (s === 'E') box(p, W - th, 0, a, W, hgt, b, mat);
  };
  for (const s of sides) {
    const len = (s === 'N' || s === 'S') ? W : D;
    let cur = 0;
    for (const [a, b] of (gaps[s] || [])) { if (a > cur) seg(s, cur, a); cur = b; }
    if (cur < len) seg(s, cur, len);
  }
}

// carpintería de aluminio y vidrio en un vano
function glazing(p, side, a, b, y0, y1, W, D, M, { door = false } = {}) {
  const t = 0.12, fd = 0.05, fw = 0.045;
  const g = new THREE.Group();
  // coordenadas locales: u a lo largo del muro, v arriba, z hacia la habitación (vano en z∈[-t,0])
  let u0, u1;
  if (side === 'N') { g.position.set(0, 0, 0); u0 = a; u1 = b; }
  if (side === 'S') { g.position.set(W, 0, D); g.rotation.y = Math.PI; u0 = W - b; u1 = W - a; }
  if (side === 'W') { g.position.set(0, 0, D); g.rotation.y = Math.PI / 2; u0 = D - b; u1 = D - a; }
  if (side === 'E') { g.position.set(W, 0, 0); g.rotation.y = -Math.PI / 2; u0 = a; u1 = b; }
  const zc = -t / 2;
  const al = M.alu;
  box(g, u0, y0, zc - fd / 2, u0 + fw, y1, zc + fd / 2, al);
  box(g, u1 - fw, y0, zc - fd / 2, u1, y1, zc + fd / 2, al);
  box(g, u0, y1 - fw, zc - fd / 2, u1, y1, zc + fd / 2, al);
  box(g, u0, y0, zc - fd / 2, u1, y0 + (door ? 0.02 : fw), zc + fd / 2, al);
  const mid = (u0 + u1) / 2;
  // dos hojas corredizas
  for (const [s0, s1, dz] of [[u0 + fw, mid + 0.03, -0.012], [mid - 0.03, u1 - fw, 0.012]]) {
    box(g, s0, y0 + 0.02, zc + dz - 0.012, s0 + 0.035, y1 - fw, zc + dz + 0.012, al);
    box(g, s1 - 0.035, y0 + 0.02, zc + dz - 0.012, s1, y1 - fw, zc + dz + 0.012, al);
    const gl = new THREE.Mesh(new THREE.PlaneGeometry(s1 - s0 - 0.07, y1 - y0 - fw - 0.04), M.glass);
    gl.position.set((s0 + s1) / 2, (y0 + 0.02 + y1 - fw) / 2, zc + dz); gl.castShadow = false; g.add(gl);
  }
  if (!door) box(g, u0 - 0.03, y0 - 0.025, -0.02, u1 + 0.03, y0, 0.035, M.sill);
  p.add(g);
  // luz de ventana (área) en coordenadas del mundo
  const cu = (u0 + u1) / 2, cv = (y0 + y1) / 2;
  const c = new THREE.Vector3(cu, cv, -0.03).applyMatrix4(g.matrix.compose(g.position, g.quaternion, g.scale));
  const n = new THREE.Vector3(0, 0, 1).applyQuaternion(g.quaternion);
  return { center: c, normal: n, w: u1 - u0, h: y1 - y0 };
}

function areaLight(p, win, intensity, color = '#F2F5FA') {
  const l = new THREE.RectAreaLight(color, intensity, win.w, win.h);
  l.position.copy(win.center).addScaledVector(win.normal, 0.02);
  p.add(l);
  l.lookAt(win.center.clone().addScaledVector(win.normal, 2));
  return l;
}

function ceilingLight(p, x, z, M, intensity = 7, shadow = true) {
  cyl(p, x, H - 0.035, z, 0.16, 0.035, M.plafon, 48);
  const disk = new THREE.Mesh(new THREE.CircleGeometry(0.145, 48), M.plafonGlow);
  disk.rotation.x = Math.PI / 2; disk.position.set(x, H - 0.036, z); p.add(disk);
  const l = new THREE.PointLight('#FFE4C8', intensity, 0, 2);
  l.position.set(x, H - 0.12, z);
  if (shadow) { l.castShadow = true; l.shadow.mapSize.set(1024, 1024); l.shadow.bias = -0.002; l.shadow.radius = 4; }
  p.add(l);
  return l;
}

function sun(p, from, target, intensity = 3.2, color = '#FFF7EC') {
  const l = new THREE.DirectionalLight(color, intensity);
  l.position.copy(from); l.target.position.copy(target);
  l.castShadow = true; l.shadow.mapSize.set(2048, 2048);
  const c = l.shadow.camera; c.left = -5; c.right = 5; c.top = 5; c.bottom = -5; c.near = 0.5; c.far = 30;
  l.shadow.bias = -0.0004; l.shadow.normalBias = 0.02;
  p.add(l); p.add(l.target);
  return l;
}

function skyTexture() {
  return canvasTex(512, 512, (g, w, h) => {
    const gr = g.createLinearGradient(0, 0, 0, h);
    gr.addColorStop(0, '#9FC2E3'); gr.addColorStop(0.45, '#D6E6F2'); gr.addColorStop(0.6, '#EEF2F2'); gr.addColorStop(1, '#E8E4DC');
    g.fillStyle = gr; g.fillRect(0, 0, w, h);
    const r = rng(11);
    g.fillStyle = '#A7B6B8'; g.beginPath(); g.moveTo(0, h * 0.62);
    for (let x = 0; x <= w; x += 16) g.lineTo(x, h * (0.56 - 0.05 * Math.sin(x / 70) - 0.03 * Math.sin(x / 23) - r() * 0.01));
    g.lineTo(w, h); g.lineTo(0, h); g.fill();
    g.fillStyle = '#C3C4BD'; g.fillRect(0, h * 0.64, w, h);
    for (let k = 0; k < 90; k++) { g.fillStyle = `rgba(150,145,135,${0.2 + r() * 0.3})`; g.fillRect(r() * w, h * (0.62 + r() * 0.06), 3 + r() * 14, 2 + r() * 10); }
  });
}

// ------------------------------------------------------------------ materiales
function materials(P) {
  const M = {};
  M.paint = std({ color: '#F3EEE4', roughness: 0.93 });
  M.paint.userData.ceil = std({ color: '#F8F6F2', roughness: 0.95 });
  M.skirt = std({ color: '#F4F1EA', roughness: 0.5 });
  M.alu = std({ color: '#B9BCC0', roughness: 0.35, metalness: 0.9 });
  M.glass = new THREE.MeshPhysicalMaterial({ color: '#E4F0EE', roughness: 0.04, metalness: 0, transparent: true, opacity: 0.16, depthWrite: false, side: THREE.DoubleSide, envMapIntensity: 1.2 });
  M.sill = std({ color: '#F2F0EC', roughness: 0.4 });
  M.plafon = std({ color: '#FAFAF8', roughness: 0.4 });
  M.plafonGlow = std({ color: '#FFFFFF', emissive: '#FFEEDC', emissiveIntensity: 2.2 });
  M.upper = std({ color: P.upper, roughness: 0.6 });
  M.lower = std({ color: P.lower, roughness: 0.5 });
  M.carcass = std({ color: '#EDEAE4', roughness: 0.6 });
  M.zoc = std({ color: '#7C7F83', roughness: 0.4, metalness: 0.6 });
  M.metal = std(P.metal);
  M.steel = std({ color: '#C4C8CC', roughness: 0.28, metalness: 1 });
  M.steelDark = std({ color: '#8E9296', roughness: 0.35, metalness: 1 });
  M.black = std({ color: '#141416', roughness: 0.35 });
  M.blackGlass = std({ color: '#0E1013', roughness: 0.08, metalness: 0.2 });
  M.porc = std({ color: '#FBFBF9', roughness: 0.12 });
  M.white = std({ color: '#F6F6F4', roughness: 0.3 });
  M.fabric = std({ color: '#9C978F', roughness: 1 });
  M.fabric2 = std({ color: '#B8A68F', roughness: 1 });
  M.linen = std({ color: '#F1EEE8', roughness: 1 });
  M.rug = std({ color: '#D7D0C4', roughness: 1 });
  M.wood = std({ color: '#B89470', roughness: 0.55 });
  M.leaf = std({ color: '#4E6B45', roughness: 0.8 });
  M.pot = std({ color: '#B06A48', roughness: 0.9 });
  M.rail = std({ color: '#3B3F45', roughness: 0.5, metalness: 0.5 });
  M.gola = std({ color: '#B4B8BD', roughness: 0.3, metalness: 1 });
  M.led = std({ color: '#FFFFFF', emissive: '#FFD9A6', emissiveIntensity: 3 });
  M.screen = std({ color: '#0B0D10', roughness: 0.12, metalness: 0.3 });
  // texturas
  M.spc = woodSpec(P.spc, P.spcJ, { seed: P === OPT.a ? 2 : 4 });
  M.granite = graniteSpec(P.ctr, P.ctrF, 3);
  M.splash = tileSpec({ tw: 0.6, th: 0.3, cols: 2, rows: 4, base: P.sp, grout: P.spJ, veins: P.spVeins, seed: 6 });
  M.wallTile = tileSpec({ tw: 0.6, th: 0.3, cols: 2, rows: 4, base: P.tw, grout: P.twJ, seed: 8 });
  M.floorTile = tileSpec({ tw: 0.3, th: 0.3, cols: 4, rows: 4, base: P.tf, grout: P.tfJ, speckle: true, vary: 0.035, seed: 10 });
  M.balconyTile = M.floorTile;
  const woodVeneer = woodSpec(P.clo, '#000', { cols: 6, rows: 1, pw: 0.12, pl: 1.2, joints: false, vary: 0.035, seed: 21 });
  M.clo = P.cloWood ? std({ color: '#FFFFFF', roughness: 0.55, map: texFor(woodVeneer, 0.6, 2.4) }) : std({ color: P.clo, roughness: 0.55 });
  const vanVeneer = woodSpec(P.van, '#000', { cols: 6, rows: 1, pw: 0.12, pl: 1.2, joints: false, vary: 0.035, seed: 23 });
  M.van = P.vanWood ? std({ color: '#FFFFFF', roughness: 0.5, map: texFor(vanVeneer, 0.6, 0.6) }) : std({ color: P.van, roughness: 0.5 });
  return M;
}

function faucet(p, x, y, z, dir, M, h = 0.30, reach = 0.16) {
  // dir: vector unitario horizontal hacia donde sale el chorro
  const d = new THREE.Vector3(dir[0], 0, dir[1]);
  const pts = [
    new THREE.Vector3(x, y, z), new THREE.Vector3(x, y + h * 0.8, z),
    new THREE.Vector3(x, y + h, z).addScaledVector(d, reach * 0.3),
    new THREE.Vector3(x, y + h * 0.95, z).addScaledVector(d, reach * 0.85),
    new THREE.Vector3(x, y + h * 0.78, z).addScaledVector(d, reach),
  ];
  const curve = new THREE.CatmullRomCurve3(pts);
  mesh(p, new THREE.TubeGeometry(curve, 40, 0.011, 12), M.metal, 0, 0, 0);
  cyl(p, x, y, z, 0.026, 0.05, M.metal);
  const lever = box(p, x - 0.006, y + 0.06, z - 0.006, x + 0.006, y + 0.075, z + 0.006, M.metal);
  lever.position.addScaledVector(d, -0.04);
}

// ------------------------------------------------------------------ escenas
function cocina(P, view = 1) {
  const S = new THREE.Scene(); const M = materials(P);
  const W = 4.05, D = 2.30;
  walls(S, W, D, M.paint, { open: { E: [[0.75, 1.55, 1.05, 2.10]] } });
  box(S, -0.12, -0.2, -0.12, W + 0.12, 0, D + 0.12, M.paint);
  texPlane(S, 'xz', 0, 0, W, D, 0.001, M.spc, { color: '#FFFFFF', roughness: 0.55 }, 1, true);
  // cerámica en ropas + perfil de transición
  texPlane(S, 'xz', 2.55, 1.15, W, D, 0.002, M.floorTile, { color: '#FFFFFF', roughness: 0.8 });
  box(S, 2.54, 0, 1.15, 2.56, 0.004, D, M.alu); box(S, 2.55, 0, 1.14, W, 0.004, 1.16, M.alu);
  skirting(S, W, D, M.skirt, ['W', 'S'], { S: [[2.55, W]] });
  const win = glazing(S, 'E', 0.75, 1.55, 1.05, 2.10, W, D, M);
  // nevera (ilustrativa)
  rbox(S, 0.03, 0, 0.02, 0.67, 1.78, 0.66, M.steel, 0.02);
  box(S, 0.03, 1.12, 0.655, 0.67, 1.126, 0.665, M.steelDark);
  box(S, 0.60, 1.22, 0.665, 0.615, 1.62, 0.685, M.steelDark); box(S, 0.60, 0.55, 0.665, 0.615, 1.02, 0.685, M.steelDark);
  // bajos
  const x0 = 0.70, x1 = P.tower ? 3.00 : 3.40;
  box(S, x0, 0, 0.04, x1, 0.10, 0.52, M.zoc);
  box(S, x0, 0.10, 0, x1, 0.88, 0.56, M.carcass);
  const fz = 0.56, ft = 0.018, gap = 0.003;
  const fronts = [
    [0.70, 1.00, 0.10, 0.88, 'dR'], [1.00, 1.30, 0.10, 0.88, 'dL'], [1.30, 1.80, 0.10, 0.88, 'dR'],
    [1.80, 2.40, 0.10, 0.32, 'w'], [1.80, 2.40, 0.32, 0.60, 'w'], [1.80, 2.40, 0.60, 0.88, 'w'],
    [2.40, 3.00, 0.10, 0.26, 'w'],
  ];
  if (!P.tower) fronts.push([3.00, 3.40, 0.10, 0.88, 'dL']);
  const topY = P.gola ? 0.855 : 0.88;
  for (const [a, b, y0, y1, k] of fronts) {
    const yy1 = y1 === 0.88 ? topY : y1;
    box(S, a + gap, y0 + gap, fz, b - gap, yy1 - gap, fz + ft, M.lower);
    if (!P.gola) {
      if (k === 'w') box(S, (a + b) / 2 - 0.09, yy1 - 0.05, fz + ft, (a + b) / 2 + 0.09, yy1 - 0.038, fz + ft + 0.022, M.metal);
      if (k === 'dR') box(S, b - 0.04, yy1 - 0.19, fz + ft, b - 0.028, yy1 - 0.05, fz + ft + 0.022, M.metal);
      if (k === 'dL') box(S, a + 0.028, yy1 - 0.19, fz + ft, a + 0.04, yy1 - 0.05, fz + ft + 0.022, M.metal);
    }
  }
  if (P.gola) box(S, x0, 0.86, fz - 0.02, 3.00, 0.875, fz + 0.005, M.gola);
  // horno
  box(S, 2.402, 0.265, fz, 2.998, 0.878, fz + 0.02, M.steel);
  box(S, 2.45, 0.35, fz + 0.02, 2.95, 0.72, fz + 0.024, M.blackGlass);
  box(S, 2.47, 0.77, fz + 0.02, 2.93, 0.785, fz + 0.05, M.steelDark);
  // mesón granito
  const ctrEnd = P.tower ? 3.00 : 3.40;
  const gmat = std({ color: '#FFFFFF', roughness: 0.16, metalness: 0.05, map: texFor(M.granite, ctrEnd - 0.70, 0.61) });
  box(S, 0.70, 0.88, 0, ctrEnd, 0.90, 0.61, gmat);
  // lavaplatos
  box(S, 0.78, 0.9005, 0.10, 1.22, 0.9015, 0.50, M.steel, { cast: false });
  box(S, 0.80, 0.9016, 0.12, 1.20, 0.9022, 0.48, std({ color: '#7F8387', roughness: 0.3, metalness: 1 }), { cast: false });
  faucet(S, 1.00, 0.90, 0.06, [0, 1], M, 0.34, 0.2);
  // estufa
  box(S, 2.44, 0.9, 0.06, 2.96, 0.905, 0.56, std({ color: '#2A2B2D', roughness: 0.25, metalness: 0.4 }));
  for (const [cx, cz] of [[2.57, 0.19], [2.83, 0.19], [2.57, 0.43], [2.83, 0.43]]) {
    cyl(S, cx, 0.905, cz, 0.05, 0.02, M.black);
    box(S, cx - 0.07, 0.925, cz - 0.006, cx + 0.07, 0.935, cz + 0.006, M.black);
    box(S, cx - 0.006, 0.925, cz - 0.07, cx + 0.006, 0.935, cz + 0.07, M.black);
  }
  // salpicadero
  texPlane(S, 'xy', 0.70, 0.90, ctrEnd, 1.47, 0.002, M.splash, { color: '#FFFFFF', roughness: 0.18 });
  for (const x of P.tower ? [1.5, 2.15, 1.05, 2.75] : [1.5, 2.15, 3.2]) box(S, x, 1.10, 0.002, x + 0.08, 1.22, 0.012, M.white);
  // altos
  const ups = [[0.70, 1.00, 'R'], [1.00, 1.30, 'L'], [1.30, 1.80, 'R'], [1.80, 2.10, 'R'], [2.10, 2.40, 'L']];
  if (!P.tower) ups.push([3.00, 3.40, 'L']);
  box(S, 0.70, 1.47, 0, 2.40, 2.22, 0.33, M.carcass);
  if (!P.tower) box(S, 3.00, 1.47, 0, 3.40, 2.22, 0.33, M.carcass);
  box(S, 2.40, 1.80, 0, 3.00, 2.22, 0.33, M.carcass);
  for (const [a, b, k] of ups) {
    box(S, a + gap, 1.47 + gap, 0.33, b - gap, 2.22 - gap, 0.348, M.upper);
    if (!P.gola) {
      const hx = k === 'R' ? b - 0.04 : a + 0.028;
      box(S, hx, 1.50, 0.348, hx + 0.012, 1.64, 0.37, M.metal);
    }
  }
  box(S, 2.40 + gap, 1.80 + gap, 0.33, 3.00 - gap, 2.22 - gap, 0.348, M.upper);
  if (P.gola) box(S, 0.70, 1.465, 0.30, 2.40, 1.472, 0.345, M.gola);
  // campana
  box(S, 2.44, 1.64, 0.02, 2.96, 1.80, 0.36, M.steel);
  box(S, 2.46, 1.638, 0.05, 2.94, 1.642, 0.34, M.steelDark);
  // torre B
  if (P.tower) {
    box(S, 3.00, 0, 0.04, 3.40, 0.10, 0.52, M.zoc);
    box(S, 3.00, 0.10, 0, 3.40, 2.22, 0.56, M.carcass);
    for (const [y0, y1] of [[0.10, 0.88], [0.88, 1.60], [1.60, 2.22]]) box(S, 3.00 + gap, y0 + gap, fz, 3.40 - gap, y1 - gap, fz + ft, M.lower);
    box(S, 3.00, 0.86, fz - 0.005, 3.40, 0.872, fz + 0.002, M.gola);
  }
  // LED bajo altos
  box(S, 0.72, 1.462, 0.24, 2.40, 1.468, 0.27, M.led, { cast: false });
  const led = new THREE.RectAreaLight('#FFD29C', 9, 1.68, 0.05);
  led.position.set(1.55, 1.46, 0.2); S.add(led); led.lookAt(1.55, 0, 0.3);
  // ropas
  const zr = 1.72;
  texPlane(S, 'xy', 2.55, 0, W, 1.20, D - 0.002, M.wallTile, { color: '#FFFFFF', roughness: 0.25 }, -1);
  // gabinete alto junto a la ventana (x 3.65–4.05)
  box(S, 3.65, 0, zr + 0.04, 4.05, 0.10, D, M.zoc);
  box(S, 3.655, 0.10, zr, 4.045, 2.05, D, M.lower);
  if (!P.gola) box(S, 3.668, 0.95, zr - 0.022, 3.68, 1.15, zr, M.metal);
  else box(S, 3.655, 2.03, zr - 0.012, 4.045, 2.045, zr, M.gola);
  // lavadero compacto (x 3.15–3.65)
  rbox(S, 3.17, 0.62, zr + 0.03, 3.63, 0.90, D - 0.01, M.white, 0.02);
  box(S, 3.21, 0.899, zr + 0.08, 3.59, 0.902, D - 0.05, std({ color: '#D8DAD9', roughness: 0.3 }), { cast: false });
  for (const x of [3.19, 3.585]) box(S, x, 0, D - 0.06, x + 0.025, 0.62, D - 0.035, M.white);
  faucet(S, 3.40, 1.02, D - 0.01, [0, -1], M, 0.06, 0.14);
  // lavadora (x 2.55–3.15, ilustrativa)
  rbox(S, 2.57, 0, zr, 3.14, 0.85, D - 0.02, M.white, 0.025);
  mesh(S, new THREE.TorusGeometry(0.17, 0.025, 16, 48), std({ color: '#9FA4A8', roughness: 0.3, metalness: 0.8 }), 2.855, 0.47, zr - 0.005);
  mesh(S, new THREE.CircleGeometry(0.16, 40), std({ color: '#3C4852', roughness: 0.1, transparent: true, opacity: 0.8 }), 2.855, 0.47, zr - 0.004).rotation.y = Math.PI;
  box(S, 2.59, 0.76, zr - 0.01, 3.12, 0.84, zr - 0.002, std({ color: '#E8E8E6', roughness: 0.4 }));
  // luz
  ceilingLight(S, 2.0, 1.15, M, 6.5);
  areaLight(S, win, 5.5);
  sun(S, new THREE.Vector3(W + 5, 4.2, 1.9), new THREE.Vector3(1.8, 0, 0.9), 2.6);
  S.background = skyTexture();
  const cam = new THREE.PerspectiveCamera(60, 1.6, 0.05, 60);
  if (view === 1) { cam.position.set(0.24, 1.50, 2.14); cam.lookAt(2.45, 1.0, 0.02); }
  else { cam.fov = 62; cam.position.set(0.70, 1.50, 0.98); cam.lookAt(3.75, 0.92, 1.85); }
  return { S, cam, exposure: 0.95, envI: 0.34 };
}

function chair(S, cx, cz, ang, M) {
  const g = new THREE.Group(); g.position.set(cx, 0, cz); g.rotation.y = ang;
  box(g, -0.21, 0.44, -0.2, 0.21, 0.47, 0.2, M.wood);
  for (const [x, z] of [[-0.18, -0.17], [0.18, -0.17], [-0.18, 0.17], [0.18, 0.17]]) box(g, x - 0.015, 0, z - 0.015, x + 0.015, 0.44, z + 0.015, M.wood);
  box(g, -0.2, 0.47, 0.17, 0.2, 0.86, 0.2, M.wood);
  rbox(g, -0.2, 0.47, -0.19, 0.2, 0.52, 0.16, M.fabric2, 0.02);
  S.add(g); g.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
}

function plant(S, x, z, M, h = 0.9) {
  cyl(S, x, 0, z, 0.15, 0.32, M.pot, 32, 0.18);
  const r = rng(7);
  for (let k = 0; k < 22; k++) {
    const a = r() * 6.28, rr = r() * 0.18, y = 0.35 + r() * (h - 0.35);
    const s = mesh(S, new THREE.SphereGeometry(0.09 + r() * 0.06, 12, 10), M.leaf, x + Math.cos(a) * rr, y, z + Math.sin(a) * rr);
    s.scale.set(1, 0.7 + r() * 0.5, 1);
  }
}

function sala(P) {
  const S = new THREE.Scene(); const M = materials(P);
  const W = 2.65, D = 3.40;
  walls(S, W, D, M.paint, { open: { S: [[0.45, 2.20, 0, 2.10]] } });
  box(S, -0.12, -0.2, -0.12, W + 0.12, 0, D + 0.12, M.paint);
  texPlane(S, 'xz', 0, 0, W, D, 0.001, M.spc, { color: '#FFFFFF', roughness: 0.55 });
  skirting(S, W, D, M.skirt, ['N', 'W', 'E', 'S'], { S: [[0.45, 2.20]] });
  const win = glazing(S, 'S', 0.45, 2.20, 0, 2.10, W, D, M, { door: true });
  // balcón
  const bz0 = D + 0.12, bz1 = D + 0.84;
  box(S, 0.20, -0.2, bz0, 2.44, 0, bz1, M.paint);
  texPlane(S, 'xz', 0.32, bz0, 2.32, bz1, 0.001, M.floorTile, { color: '#FFFFFF', roughness: 0.8 });
  box(S, 0.20, 0, bz0, 0.32, H, bz1, M.paint); box(S, 2.32, 0, bz0, 2.44, H, bz1, M.paint);
  box(S, 0.20, H, bz0, 2.44, H + 0.18, bz1, std({ color: '#E9E6E0', roughness: 0.9 }));
  box(S, 0.32, 0.98, bz1 - 0.04, 2.32, 1.02, bz1, M.rail);
  box(S, 0.32, 0.08, bz1 - 0.035, 2.32, 0.11, bz1 - 0.005, M.rail);
  for (let x = 0.36; x < 2.30; x += 0.11) box(S, x, 0.08, bz1 - 0.028, x + 0.016, 0.98, bz1 - 0.012, M.rail);
  plant(S, 2.08, bz0 + 0.3, M);
  // comedor
  cyl(S, 1.32, 0, 0.88, 0.22, 0.02, M.black, 40);
  cyl(S, 1.32, 0.02, 0.88, 0.035, 0.70, M.black, 20);
  const top = cyl(S, 1.32, 0.72, 0.88, 0.45, 0.03, std({ color: '#EDE9E2', roughness: 0.35 }), 64);
  chair(S, 1.32, 0.88 - 0.56, 0, M); chair(S, 1.32, 0.88 + 0.56, Math.PI, M);
  chair(S, 1.32 - 0.56, 0.88, Math.PI / 2, M); chair(S, 1.32 + 0.56, 0.88, -Math.PI / 2, M);
  // tapete y sofá 2 puestos contra el muro oeste
  box(S, 0.95, 0.001, 1.95, 2.25, 0.012, 3.15, M.rug, { cast: false });
  const z0 = 1.84, z1 = 3.32;
  for (const z of [z0 + 0.05, z1 - 0.05]) for (const x of [0.08, 0.80]) cyl(S, x, 0, z, 0.018, 0.1, M.black, 12);
  rbox(S, 0.03, 0.10, z0, 0.88, 0.40, z1, M.fabric, 0.04);
  rbox(S, 0.03, 0.40, z0, 0.24, 0.82, z1, M.fabric, 0.05);
  rbox(S, 0.03, 0.40, z0, 0.88, 0.62, z0 + 0.15, M.fabric, 0.05);
  rbox(S, 0.03, 0.40, z1 - 0.15, 0.88, 0.62, z1, M.fabric, 0.05);
  const zm = (z0 + z1) / 2;
  rbox(S, 0.22, 0.40, z0 + 0.15, 0.86, 0.52, zm - 0.005, M.fabric, 0.05);
  rbox(S, 0.22, 0.40, zm + 0.005, 0.86, 0.52, z1 - 0.15, M.fabric, 0.05);
  rbox(S, 0.20, 0.52, z0 + 0.2, 0.36, 0.78, zm - 0.02, M.fabric, 0.07);
  rbox(S, 0.20, 0.52, zm + 0.02, 0.36, 0.78, z1 - 0.2, M.fabric, 0.07);
  rbox(S, 0.30, 0.52, z0 + 0.22, 0.42, 0.70, z0 + 0.52, std({ color: '#C9B89E', roughness: 1 }), 0.06);
  cyl(S, 1.25, 0, 2.55, 0.28, 0.40, std({ color: '#E7E2DA', roughness: 0.4 }), 48);
  // panel de TV
  box(S, 2.62, 0.95, 1.95, 2.65, 1.95, 3.15, M.clo);
  box(S, 2.33, 0.36, 2.0, 2.65, 0.54, 3.10, M.clo);
  box(S, 2.58, 1.07, 2.03, 2.62, 1.71, 3.07, M.screen);
  // luces
  if (P.lights2) { ceilingLight(S, 1.32, 0.88, M, 4.2); ceilingLight(S, 1.70, 2.55, M, 4.2, false); }
  else ceilingLight(S, 1.32, 1.70, M, 6.5);
  areaLight(S, win, 7.5);
  sun(S, new THREE.Vector3(-2.5, 4.4, D + 6.5), new THREE.Vector3(1.6, 0, 1.9), 3.0);
  S.background = skyTexture();
  const cam = new THREE.PerspectiveCamera(60, 1.6, 0.05, 80);
  cam.position.set(2.45, 1.46, 0.22); cam.lookAt(1.02, 0.98, 3.35);
  return { S, cam, exposure: 0.95, envI: 0.3 };
}

function toilet(S, x0, zc, M) {
  const g = new THREE.Group(); g.position.set(x0, 0, zc);
  rbox(g, 0.0, 0.40, -0.19, 0.17, 0.80, 0.19, M.porc, 0.03);
  rbox(g, 0.0, 0.79, -0.20, 0.19, 0.82, 0.20, M.porc, 0.012);
  box(g, 0.08, 0.82, -0.03, 0.12, 0.826, 0.03, M.metal);
  const prof = [[0.0, 0.0], [0.13, 0.0], [0.12, 0.12], [0.15, 0.30], [0.19, 0.38], [0.19, 0.40], [0.0, 0.40]].map(([r, y]) => new THREE.Vector2(r, y));
  const bowl = new THREE.Mesh(new THREE.LatheGeometry(prof, 48), M.porc);
  bowl.scale.set(1.45, 1, 1); bowl.position.set(0.40, 0, 0); bowl.castShadow = bowl.receiveShadow = true; g.add(bowl);
  const seat = new THREE.Mesh(new THREE.TorusGeometry(0.15, 0.022, 12, 48), M.porc);
  seat.rotation.x = Math.PI / 2; seat.scale.set(1.45, 1, 1); seat.position.set(0.41, 0.415, 0); g.add(seat);
  const lid = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.02, 48), M.porc);
  lid.scale.set(1.35, 1, 1); lid.position.set(0.40, 0.44, 0); g.add(lid);
  box(g, 0.17, 0.40, -0.1, 0.24, 0.44, 0.1, M.porc);
  S.add(g); g.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
}

function bano(P) {
  const S = new THREE.Scene(); const M = materials(P);
  const W = 1.10, D = 2.10;
  const tileMat = M.paint.clone(); tileMat.userData.ceil = M.paint.userData.ceil;
  walls(S, W, D, tileMat, { skip: ['N'] });
  box(S, -0.12, -0.2, -0.6, W + 0.12, 0, D + 0.12, M.paint);
  texPlane(S, 'xz', 0, 0, W, D, 0.001, M.floorTile, { color: '#FFFFFF', roughness: 0.75 });
  const tp = { color: '#FFFFFF', roughness: 0.22 };
  texPlane(S, 'zy', 0, 0, D, H, 0.002, M.wallTile, tp, 1);
  texPlane(S, 'zy', 0, 0, D, H, W - 0.002, M.wallTile, tp, -1);
  texPlane(S, 'xy', 0, 0, W, H, D - 0.002, M.wallTile, tp, -1);
  // mueble flotante + lavamanos
  box(S, 0, 0.47, 0.03, 0.44, 0.83, 0.59, M.van);
  if (!P.gola) box(S, 0.44, 0.76, 0.24, 0.462, 0.772, 0.38, M.metal);
  else box(S, 0.43, 0.815, 0.03, 0.445, 0.83, 0.59, M.gola);
  rbox(S, 0, 0.83, 0.02, 0.47, 0.86, 0.60, M.porc, 0.01);
  const basin = new THREE.Mesh(new THREE.CircleGeometry(0.15, 40), std({ color: '#E9ECEC', roughness: 0.15 }));
  basin.rotation.x = -Math.PI / 2; basin.scale.set(1, 1.35, 1); basin.position.set(0.25, 0.8605, 0.31); S.add(basin);
  faucet(S, 0.06, 0.86, 0.31, [1, 0], M, 0.2, 0.13);
  // espejo con luz frontal
  const mirror = new Reflector(new THREE.PlaneGeometry(0.46, 0.68), { textureWidth: 1024, textureHeight: 1536, color: 0xC9CFD2 });
  mirror.position.set(0.012, 1.42, 0.31); mirror.rotation.y = Math.PI / 2; S.add(mirror);
  box(S, 0.0, 1.07, 0.07, 0.01, 1.77, 0.55, M.alu);
  box(S, 0.0, 1.80, 0.11, 0.05, 1.84, 0.51, M.led, { cast: false });
  const ml = new THREE.RectAreaLight('#FFE0B8', 10, 0.4, 0.04);
  ml.position.set(0.06, 1.80, 0.31); S.add(ml); ml.lookAt(0.9, 1.3, 0.31);
  // sanitario
  toilet(S, 0, 0.90, M);
  // ducha: división corrediza en vidrio templado 8 mm
  const gz = 1.20;
  const glass = new THREE.MeshPhysicalMaterial({ color: '#E6F2EF', roughness: 0.03, transparent: true, opacity: 0.1, depthWrite: false, side: THREE.DoubleSide, envMapIntensity: 1.5 });
  for (const [a, b, dz] of [[0.02, 0.62, -0.015], [0.48, 1.08, 0.015]]) {
    const gl = mesh(S, new THREE.BoxGeometry(b - a, 1.96, 0.008), glass, (a + b) / 2, 1.0, gz + dz, false, false);
  }
  box(S, 0, 1.98, gz - 0.03, W, 2.01, gz + 0.03, M.metal);
  box(S, 0.60, 1.0, gz - 0.028, 0.615, 1.30, gz - 0.02, M.metal);
  box(S, 0.485, 1.0, gz + 0.02, 0.50, 1.30, gz + 0.028, M.metal);
  // grifería de ducha
  cyl(S, 0.0, 1.05, 1.65, 0.05, 0.02, M.metal).rotation.z = Math.PI / 2;
  const mix = mesh(S, new THREE.CylinderGeometry(0.05, 0.05, 0.02, 32), M.metal, 0.012, 1.10, 1.65); mix.rotation.z = Math.PI / 2;
  box(S, 0.02, 1.095, 1.62, 0.09, 1.105, 1.64, M.metal);
  box(S, 0, 2.06, 1.64, 0.26, 2.075, 1.66, M.metal);
  const head = mesh(S, new THREE.CylinderGeometry(0.11, 0.11, 0.012, 40), M.metal, 0.26, 2.05, 1.65);
  box(S, 0.51, 0.002, 1.78, 0.61, 0.004, 1.86, M.steel, { cast: false });
  // toalla
  ceilingLight(S, 0.55, 0.95, M, 3.2);
  const cam = new THREE.PerspectiveCamera(66, 1.6, 0.03, 40);
  cam.position.set(0.98, 1.55, -0.12); cam.lookAt(0.22, 1.0, 1.25);
  return { S, cam, exposure: 0.9, envI: 0.3 };
}

function alcoba(P) {
  const S = new THREE.Scene(); const M = materials(P);
  const W = 2.50, D = 3.38;
  walls(S, W, D, M.paint, { open: { W: [[0.70, 1.85, 0.95, 2.10]] } });
  box(S, -0.12, -0.2, -0.12, W + 0.12, 0, D + 0.12, M.paint);
  texPlane(S, 'xz', 0, 0, W, D, 0.001, M.spc, { color: '#FFFFFF', roughness: 0.55 });
  skirting(S, W, D, M.skirt, ['N', 'W', 'E']);
  const win = glazing(S, 'W', 0.70, 1.85, 0.95, 2.10, W, D, M);
  // cortina liviana (ilustrativa)
  box(S, 0.02, 2.14, 0.55, 0.05, 2.16, 2.0, M.alu);
  for (let k = 0; k < 7; k++) rbox(S, 0.03, 0.2, 1.87 + k * 0.022, 0.09, 2.12, 1.89 + k * 0.022, std({ color: '#EFEAE0', roughness: 1 }), 0.01);
  // cabecero, cama y mesas de noche
  rbox(S, 0.50, 0.25, 0, 2.00, 1.20, 0.07, std({ color: '#CFC6B8', roughness: 1 }), 0.03);
  box(S, 0.55, 0.12, 0.07, 1.95, 0.32, 1.95, std({ color: '#D9D2C6', roughness: 0.9 }));
  rbox(S, 0.56, 0.32, 0.08, 1.94, 0.54, 1.94, M.linen, 0.06);
  rbox(S, 0.53, 0.46, 0.55, 1.97, 0.58, 1.98, std({ color: '#ECE7DE', roughness: 1 }), 0.05);
  rbox(S, 0.53, 0.50, 1.45, 1.97, 0.60, 1.85, M.fabric2, 0.04);
  rbox(S, 0.62, 0.54, 0.12, 1.22, 0.70, 0.42, M.linen, 0.07);
  rbox(S, 1.28, 0.54, 0.12, 1.88, 0.70, 0.42, M.linen, 0.07);
  for (const x0 of [0.08, 2.02]) {
    box(S, x0, 0.42, 0.01, x0 + 0.40, 0.58, 0.37, M.clo);
    cyl(S, x0 + 0.2, 0.58, 0.19, 0.06, 0.04, std({ color: '#D8D3CB', roughness: 0.6 }));
    cyl(S, x0 + 0.2, 0.62, 0.19, 0.012, 0.24, M.metal, 12);
    mesh(S, new THREE.CylinderGeometry(0.09, 0.13, 0.17, 32, 1, true), std({ color: '#F3EADB', emissive: '#FFD9A8', emissiveIntensity: 0.35, roughness: 1, side: THREE.DoubleSide }), x0 + 0.2, 0.92, 0.19);
    const ll = new THREE.PointLight('#FFC98E', 0.9, 0, 2); ll.position.set(x0 + 0.2, 0.9, 0.19); S.add(ll);
  }
  box(S, 0.35, 0.001, 1.25, 2.20, 0.012, 2.55, M.rug, { cast: false });
  // closet piso-techo, 5 puertas batientes
  const cz = D - 0.60;
  box(S, 0, 0, cz + 0.05, W, 0.08, D, M.zoc);
  box(S, 0, 0.08, cz, W, H, D, M.carcass);
  for (let i = 0; i < 5; i++) {
    const a = i * 0.5, b = a + 0.5;
    box(S, a + 0.002, 0.082, cz - 0.019, b - 0.002, H - 0.004, cz, M.clo);
    const hingeLeft = i % 2 === 0;
    const hx = hingeLeft ? b - 0.05 : a + 0.038;
    if (!P.gola) box(S, hx, 0.95, cz - 0.04, hx + 0.012, 1.45, cz - 0.019, M.metal);
    else box(S, hingeLeft ? b - 0.012 : a, 0.9, cz - 0.022, hingeLeft ? b : a + 0.012, 1.5, cz - 0.019, M.gola);
    if (P.gola && i < 5) box(S, a + 0.1, 2.26, cz - 0.0195, b - 0.1, 2.3, cz - 0.0185, std({ color: '#2B2D30', roughness: 0.6 }));
  }
  ceilingLight(S, 1.25, 1.55, M, 5.5);
  areaLight(S, win, 6.5);
  sun(S, new THREE.Vector3(-5.5, 3.6, 0.2), new THREE.Vector3(1.2, 0, 1.5), 2.6, '#FFE6C8');
  S.background = skyTexture();
  const cam = new THREE.PerspectiveCamera(60, 1.6, 0.05, 60);
  cam.fov = 64; cam.position.set(2.32, 1.62, 0.40); cam.lookAt(0.95, 0.82, 3.0);
  return { S, cam, exposure: 1.0, envI: 0.32 };
}

// ------------------------------------------------------------------ muestras de material
export const SAMPLES = {
  'spc-a': { kind: 'wood', opt: 'a' }, 'spc-b': { kind: 'wood', opt: 'b' },
  'paint': { kind: 'paint' },
  'upper-a': { kind: 'mel', key: 'upper', opt: 'a' }, 'upper-b': { kind: 'mel', key: 'upper', opt: 'b' },
  'lower-a': { kind: 'mel', key: 'lower', opt: 'a' }, 'lower-b': { kind: 'mel', key: 'lower', opt: 'b' },
  'clo-b': { kind: 'veneer', opt: 'b' },
  'ctr-a': { kind: 'granite', opt: 'a' }, 'ctr-b': { kind: 'granite', opt: 'b' },
  'sp-a': { kind: 'splash', opt: 'a' }, 'sp-b': { kind: 'splash', opt: 'b' },
  'tf-a': { kind: 'ftile', opt: 'a' }, 'tf-b': { kind: 'ftile', opt: 'b' },
  'tw-a': { kind: 'wtile', opt: 'a' }, 'tw-b': { kind: 'wtile', opt: 'b' },
  'metal-a': { kind: 'metal', opt: 'a' }, 'metal-b': { kind: 'metal', opt: 'b' },
};

function sample(id) {
  const s = SAMPLES[id]; const P = OPT[s.opt || 'a']; const M = materials(P);
  const S = new THREE.Scene();
  S.background = new THREE.Color('#E7E3DC');
  plane(S, 'xz', -3, -3, 3, 3, 0, std({ color: '#E7E3DC', roughness: 0.95 }));
  const w = 0.36, d = 0.26, t = 0.018;
  let top, side = std({ color: '#F1EEE8', roughness: 0.6 });
  if (s.kind === 'wood') { top = std({ color: '#FFFFFF', roughness: 0.5, map: texFor(woodSpec(P.spc, P.spcJ, { seed: 5, px: 1024 }), w * 2.2, d * 2.2) }); side = std({ color: P.spc, roughness: 0.6 }); }
  if (s.kind === 'paint') { top = std({ color: '#FFFFFF', roughness: 0.9, map: texFor(noiseSpec('#F3EEE4', 0.05), w, d) }); }
  if (s.kind === 'mel') { top = std({ color: P[s.key], roughness: 0.55 }); side = std({ color: P[s.key], roughness: 0.45 }); }
  if (s.kind === 'veneer') { top = std({ color: '#FFFFFF', roughness: 0.55, map: texFor(woodSpec(P.clo, '#000', { cols: 6, rows: 1, pw: 0.12, pl: 1.2, joints: false, vary: 0.035, seed: 21 }), w * 2.5, d * 2.5) }); side = std({ color: P.clo, roughness: 0.5 }); }
  if (s.kind === 'granite') { top = std({ color: '#FFFFFF', roughness: 0.14, metalness: 0.05, map: texFor(M.granite, w, d) }); side = top; }
  if (s.kind === 'splash') { top = std({ color: '#FFFFFF', roughness: 0.15, map: texFor(M.splash, 0.9, 0.65) }); }
  if (s.kind === 'ftile') { top = std({ color: '#FFFFFF', roughness: 0.8, map: texFor(M.floorTile, 0.45, 0.33) }); side = std({ color: P.tf, roughness: 0.8 }); }
  if (s.kind === 'wtile') { top = std({ color: '#FFFFFF', roughness: 0.22, map: texFor(M.wallTile, 0.9, 0.65) }); side = std({ color: P.tw, roughness: 0.4 }); }
  if (s.kind === 'metal') { top = std({ color: P.lower, roughness: 0.5 }); side = top; }
  const chip = mesh(S, new THREE.BoxGeometry(w, t, d), [side, side, top, side, side, side], 0, t / 2, 0);
  chip.rotation.y = -0.18;
  if (s.kind === 'metal') {
    const g = new THREE.Group(); g.rotation.y = -0.18; S.add(g);
    if (s.opt === 'a') {
      box(g, -0.12, t, -0.012, 0.12, t + 0.012, 0.012, M.metal);
      for (const x of [-0.1, 0.1]) box(g, x - 0.006, t, -0.006, x + 0.006, t + 0.03, 0.006, M.metal);
      box(g, -0.12, t + 0.03, -0.012, 0.12, t + 0.042, 0.012, M.metal);
    } else {
      box(g, -0.18, t, 0.10, 0.18, t + 0.02, 0.13, M.metal);
      box(g, -0.12, t, -0.06, 0.12, t + 0.012, -0.036, M.metal);
      for (const x of [-0.1, 0.1]) box(g, x - 0.006, t, -0.054, x + 0.006, t + 0.03, -0.042, M.metal);
      box(g, -0.12, t + 0.03, -0.06, 0.12, t + 0.042, -0.036, M.metal);
    }
    g.traverse(o => { if (o.isMesh) o.castShadow = true; });
  }
  const key = new THREE.DirectionalLight('#FFF4E6', 2.6); key.position.set(-1.2, 2.2, 0.9); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); const c = key.shadow.camera; c.left = -0.5; c.right = 0.5; c.top = 0.5; c.bottom = -0.5; key.shadow.bias = -0.0005; key.shadow.radius = 6;
  S.add(key);
  const cam = new THREE.PerspectiveCamera(30, 4 / 3, 0.05, 10);
  cam.position.set(0.0, 0.50, 0.55); cam.lookAt(0, 0.0, 0.01);
  return { S, cam, exposure: 0.78, envI: 0.38, ao: false };
}

// ------------------------------------------------------------------ render
const SCENES = { cocina: (P) => cocina(P, 1), ropas: (P) => cocina(P, 2), sala, bano, alcoba };
let renderer, envTex;
function ensure() {
  if (renderer) return;
  renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.NeutralToneMapping; renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setPixelRatio(1);
  const pm = new THREE.PMREMGenerator(renderer);
  envTex = pm.fromScene(new RoomEnvironment(), 0.04).texture;
}

export function render(name, opt, w, h, ss = 1.5, quality = 0.87) {
  ensure();
  const r = name in SCENES ? SCENES[name](OPT[opt]) : sample(name);
  r.S.environment = envTex; r.S.environmentIntensity = r.envI;
  r.cam.aspect = w / h; r.cam.updateProjectionMatrix();
  renderer.toneMappingExposure = r.exposure;
  const W = Math.round(w * ss), Hh = Math.round(h * ss);
  renderer.setSize(W, Hh, false);
  if (r.ao === false) {
    renderer.render(r.S, r.cam);
  } else {
    const comp = new EffectComposer(renderer);
    comp.setSize(W, Hh);
    comp.addPass(new RenderPass(r.S, r.cam));
    const ao = new GTAOPass(r.S, r.cam, W, Hh);
    ao.updateGtaoMaterial({ radius: 0.35, distanceExponent: 1.2, thickness: 1.0, scale: 1.0, samples: 16 });
    ao.blendIntensity = 0.85;
    comp.addPass(ao);
    comp.addPass(new OutputPass());
    comp.render();
  }
  const out = document.createElement('canvas'); out.width = w; out.height = h;
  const g = out.getContext('2d'); g.imageSmoothingQuality = 'high';
  g.drawImage(renderer.domElement, 0, 0, w, h);
  r.S.traverse(o => { if (o.geometry) o.geometry.dispose(); });
  return out.toDataURL('image/jpeg', quality);
}
