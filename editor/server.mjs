import { createReadStream, existsSync, statSync } from 'node:fs';
import { createServer } from 'node:http';
import { extname, join, normalize, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

const root = resolve(fileURLToPath(new URL('../', import.meta.url)));
const editorRoot = join(root, 'editor');
const port = Number(process.env.PORT || 4173);
const git = process.env.BLOG_GIT_EXE || 'git';
const python = process.env.BLOG_PYTHON_EXE || 'python';
const mime = {
  '.css': 'text/css; charset=utf-8', '.gif': 'image/gif', '.html': 'text/html; charset=utf-8',
  '.ico': 'image/x-icon', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8', '.png': 'image/png',
  '.svg': 'image/svg+xml', '.webp': 'image/webp'
};

function run(command, args, input = '') {
  return new Promise((resolveRun) => {
    const child = spawn(command, args, { cwd: root, env: { ...process.env, GIT_TERMINAL_PROMPT: '0' }, windowsHide: true });
    let stdout = '', stderr = '';
    child.stdout.on('data', data => { stdout += data; });
    child.stderr.on('data', data => { stderr += data; });
    child.on('error', error => resolveRun({ code: -1, stdout, stderr: `${stderr}${error.message}` }));
    child.on('close', code => resolveRun({ code, stdout, stderr }));
    if (input) child.stdin.write(input);
    child.stdin.end();
  });
}
function runGit(args, input = '') {
  return run(git, ['-c', `safe.directory=${root}`, '-C', root, ...args], input);
}
function json(res, status, value) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(JSON.stringify(value));
}
async function body(req) {
  let raw = '';
  for await (const chunk of req) {
    raw += chunk;
    if (raw.length > 20_000) throw new Error('Request is too large.');
  }
  return raw ? JSON.parse(raw) : {};
}
async function audit() {
  const result = await run(python, ['-B', 'tools/blog_audit.py']);
  const output = `${result.stdout}${result.stderr}`.trim();
  const blockers = output.split(/\r?\n/).filter(line => /^ERROR\b/.test(line) || /image (uses a local filesystem path|points to a missing file|path does not match)/.test(line));
  return { output, blockers, code: result.code };
}
async function publish(message) {
  const checked = await audit();
  if (checked.code !== 0 || checked.blockers.length) return { ok: false, stage: 'audit', ...checked };
  const changed = await runGit(['status', '--porcelain']);
  if (changed.code !== 0) return { ok: false, stage: 'status', output: changed.stderr };
  if (!changed.stdout.trim()) return { ok: true, stage: 'complete', output: `${checked.output}\n\nNo changes to publish.` };
  const add = await runGit(['add', '--all']);
  if (add.code !== 0) return { ok: false, stage: 'add', output: add.stderr };
  const commit = await runGit(['commit', '-m', message || 'Publish blog update']);
  if (commit.code !== 0) return { ok: false, stage: 'commit', output: `${commit.stdout}${commit.stderr}` };
  const push = await runGit(['push', 'origin', 'gh-pages']);
  return { ok: push.code === 0, stage: push.code === 0 ? 'complete' : 'push', output: `${checked.output}\n\n${commit.stdout}${commit.stderr}${push.stdout}${push.stderr}` };
}

createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://${req.headers.host}`);
    if (req.method === 'POST' && url.pathname === '/api/token') {
      const { token } = await body(req);
      if (typeof token !== 'string' || token.length < 20) return json(res, 400, { ok: false, message: 'GitHub personal access token is required.' });
      const approved = await runGit(['credential', 'approve'], `protocol=https\nhost=github.com\nusername=dhkim900331\npassword=${token}\n\n`);
      return json(res, approved.code === 0 ? 200 : 500, { ok: approved.code === 0, message: approved.code === 0 ? 'Token saved in Windows Git Credential Manager.' : approved.stderr });
    }
    if (req.method === 'POST' && url.pathname === '/api/publish') {
      const { message } = await body(req);
      const result = await publish(typeof message === 'string' ? message.slice(0, 200) : 'Publish blog update');
      return json(res, result.ok ? 200 : 409, result);
    }
    const requested = decodeURIComponent(url.pathname);
    const relative = requested === '/' || requested === '/editor/' ? '/editor/index.html' : requested;
    const target = normalize(join(root, relative));
    if (!target.startsWith(editorRoot) || !existsSync(target) || statSync(target).isDirectory()) { res.writeHead(404); res.end('Not found'); return; }
    res.writeHead(200, { 'Content-Type': mime[extname(target).toLowerCase()] || 'application/octet-stream', 'Cache-Control': 'no-store' });
    createReadStream(target).pipe(res);
  } catch (error) {
    json(res, 500, { ok: false, message: error.message });
  }
}).listen(port, () => console.log(`Blog editor: http://localhost:${port}/editor/`));
