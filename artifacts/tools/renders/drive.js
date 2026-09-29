const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
const fs = require('fs');
const jobs = JSON.parse(process.argv[2]);  // [[name,opt,w,h,ss,out], ...]
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage(); const errs = [];
  p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.text()); });
  await p.goto('http://127.0.0.1:8765/render.html');
  await p.waitForFunction(() => window.ready, null, { timeout: 30000 });
  for (const [name, opt, w, h, ss, out] of jobs) {
    const t0 = Date.now();
    const url = await p.evaluate(([n, o, w, h, ss]) => window.R(n, o, w, h, ss), [name, opt, w, h, ss]);
    fs.writeFileSync(out, Buffer.from(url.split(',')[1], 'base64'));
    console.log(out, ((Date.now() - t0) / 1000).toFixed(1) + 's', fs.statSync(out).size);
  }
  if (errs.length) console.log('ERR', [...new Set(errs)].slice(0, 8));
  await b.close();
})();
