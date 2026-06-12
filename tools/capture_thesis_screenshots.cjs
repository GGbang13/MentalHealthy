const fs = require('fs');
const path = require('path');
const http = require('http');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..', 'frontend', 'dist');
const outDir = path.resolve(__dirname, '..', 'docs', 'thesis-assets');
const port = 4181;

const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

fs.mkdirSync(outDir, { recursive: true });

const server = http.createServer((req, res) => {
  let pathname = decodeURIComponent(new URL(req.url || '/', `http://127.0.0.1:${port}`).pathname);
  let filePath = path.join(root, pathname);
  if (!filePath.startsWith(root)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }
  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    filePath = path.join(root, 'index.html');
  }
  res.writeHead(200, { 'Content-Type': mimeTypes[path.extname(filePath).toLowerCase()] || 'application/octet-stream' });
  fs.createReadStream(filePath).pipe(res);
});

function listen() {
  return new Promise((resolve) => server.listen(port, '127.0.0.1', resolve));
}

async function main() {
  await listen();
  const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
  const launchOptions = fs.existsSync(edgePath) ? { headless: true, executablePath: edgePath } : { headless: true };
  const browser = await chromium.launch(launchOptions);
  const page = await browser.newPage({ viewport: { width: 1440, height: 960 }, deviceScaleFactor: 1 });
  const baseUrl = `http://127.0.0.1:${port}`;

  async function setUser(role) {
    await page.goto(`${baseUrl}/login`, { waitUntil: 'networkidle' });
    await page.evaluate((roleName) => {
      const nickname = roleName === 'ADMIN' ? '系统管理员' : roleName === 'COUNSELOR' ? '李老师' : '学生用户';
      localStorage.setItem('token', 'thesis-demo-token');
      localStorage.setItem('user', JSON.stringify({
        id: roleName === 'ADMIN' ? 1 : roleName === 'COUNSELOR' ? 2 : 3,
        username: roleName.toLowerCase(),
        nickname,
        role: roleName,
        email: 'demo@example.com',
        phone: '13800000000',
      }));
    }, role);
  }

  async function screenshot(fileName, role, route) {
    if (role) {
      await setUser(role);
    } else {
      await page.goto(`${baseUrl}/login`, { waitUntil: 'networkidle' });
      await page.evaluate(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      });
    }
    await page.goto(`${baseUrl}${route}`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1200);
    await page.screenshot({ path: path.join(outDir, fileName), fullPage: true });
  }

  await screenshot('screenshot-login.png', null, '/login');
  await screenshot('screenshot-user-portal.png', 'USER', '/user');
  await screenshot('screenshot-assessment.png', 'USER', '/assessments');
  await screenshot('screenshot-chat.png', 'USER', '/chat');
  await screenshot('screenshot-admin-dashboard.png', 'ADMIN', '/dashboard');

  await browser.close();
  server.close();
  console.log(fs.readdirSync(outDir).filter((name) => name.startsWith('screenshot-')).join('\n'));
}

main().catch((error) => {
  server.close();
  console.error(error);
  process.exit(1);
});
