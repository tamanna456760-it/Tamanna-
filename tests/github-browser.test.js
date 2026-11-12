'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const source = fs.readFileSync(
  path.join(__dirname, '..', 'js', 'github-browser.js'),
  'utf8'
);

class FakeElement {
  constructor(id = '') {
    this.id = id;
    this.value = '';
    this.textContent = '';
    this.dataset = {};
    this.children = [];
    this.listeners = {};
    this.hidden = false;
  }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children = [...items]; }
  addEventListener(type, callback) {
    (this.listeners[type] ||= []).push(callback);
  }
  dispatch(type, event = {}) {
    for (const callback of this.listeners[type] || []) callback(event);
  }
}

const ids = [
  'githubRepo', 'githubBranch', 'githubCurrentPath', 'githubFileTree',
  'githubFilePreview', 'githubBrowserStatus', 'githubRecentCommits',
  'githubLoadRepo', 'githubOpenRepo'
];

function response(status, data) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => data
  };
}

function harness(fetchImpl) {
  const elements = Object.fromEntries(ids.map(id => [id, new FakeElement(id)]));
  elements.githubRepo.value = 'tamanna456760-it/Tamanna-';
  const context = {
    document: { getElementById: id => elements[id] || null, createElement: tag => new FakeElement(tag) },
    window: { open() {} },
    fetch: fetchImpl,
    atob: value => Buffer.from(value, 'base64').toString('binary'),
    Uint8Array,
    TextDecoder,
    URL,
    encodeURIComponent,
    console
  };
  vm.runInNewContext(source, context, { filename: 'github-browser.js' });
  return elements;
}

async function settle() {
  for (let i = 0; i < 12; i += 1) {
    await new Promise(resolve => setImmediate(resolve));
  }
}

function apiFixture(file = 'Hello Tamanna') {
  const encoded = Buffer.from(file, 'utf8').toString('base64');
  return async url => {
    if (url.endsWith('/repos/tamanna456760-it/Tamanna-')) {
      return response(200, { private: false, default_branch: 'main' });
    }
    if (url.includes('/branches?')) {
      return response(200, [{ name: 'main' }, { name: 'feature/demo' }]);
    }
    if (url.includes('/commits?')) {
      return response(200, [{
        sha: '1234567890abcdef',
        html_url: 'https://github.com/tamanna456760-it/Tamanna-/commit/1234567',
        commit: { message: 'Test commit', author: { date: '2026-11-12T00:00:00Z' } }
      }]);
    }
    if (url.includes('/branches/main')) {
      return response(200, { commit: { commit: { tree: { sha: 'tree-sha' } } } });
    }
    if (url.includes('/git/trees/')) {
      return response(200, {
        truncated: false,
        tree: [
          { path: 'README.md', type: 'blob' },
          { path: 'src', type: 'tree' },
          { path: 'src/app.js', type: 'blob' }
        ]
      });
    }
    if (url.includes('/contents/README.md?')) {
      return response(200, { type: 'file', size: Buffer.byteLength(file), encoding: 'base64', content: encoded });
    }
    throw new Error('Unexpected GitHub API request: ' + url);
  };
}

test('loads public repository branches, recent commits and file tree', async () => {
  const el = harness(apiFixture());
  await settle();
  assert.equal(el.githubBrowserStatus.dataset.state, 'ok');
  assert.match(el.githubBrowserStatus.textContent, /Loaded 3 paths/);
  assert.deepEqual(el.githubBranch.children.map(option => option.value), ['main', 'feature/demo']);
  assert.equal(el.githubRecentCommits.children.length, 1);
  assert.equal(el.githubFileTree.children.length, 2);
});

test('decodes a text file into a text-only preview', async () => {
  const el = harness(apiFixture('<img src=x onerror=alert(1)>'));
  await settle();
  const readme = el.githubFileTree.children.find(button => button.textContent.includes('README.md'));
  assert.ok(readme);
  readme.dispatch('click');
  await settle();
  assert.equal(el.githubFilePreview.textContent, '<img src=x onerror=alert(1)>');
  assert.equal(el.githubFilePreview.children.length, 0);
  assert.match(el.githubBrowserStatus.textContent, /Read-only preview/);
});

test('blocks files larger than the 250 KB preview limit', async () => {
  const el = harness(apiFixture('x'.repeat(250001)));
  await settle();
  el.githubFileTree.children.find(button => button.textContent.includes('README.md')).dispatch('click');
  await settle();
  assert.match(el.githubBrowserStatus.textContent, /250 KB preview limit/);
  assert.equal(el.githubFilePreview.textContent, 'Preview unavailable.');
});

test('reports GitHub API rate limiting without requesting credentials', async () => {
  const el = harness(async () => response(403, { message: 'API rate limit exceeded' }));
  await settle();
  assert.equal(el.githubBrowserStatus.dataset.state, 'error');
  assert.match(el.githubBrowserStatus.textContent, /rate limit reached/i);
});


test('ignores a slower response from a previously selected repository', async () => {
  let releaseOldRepo;
  const oldRepoInfo = new Promise(resolve => { releaseOldRepo = resolve; });
  const fetchImpl = async url => {
    if (url === 'https://api.github.com/repos/tamanna456760-it/Tamanna-') {
      return { ok: true, status: 200, json: () => oldRepoInfo };
    }
    if (url === 'https://api.github.com/repos/example/new-project') {
      return response(200, { private: false, default_branch: 'main' });
    }
    if (url.includes('/branches?')) return response(200, [{ name: 'main' }]);
    if (url.includes('/commits?')) return response(200, []);
    if (url.includes('/branches/main')) {
      return response(200, { commit: { commit: { tree: { sha: 'new-tree' } } } });
    }
    if (url.includes('/git/trees/')) {
      return response(200, { truncated: false, tree: [{ path: 'NEW.md', type: 'blob' }] });
    }
    throw new Error('Unexpected GitHub API request: ' + url);
  };

  const el = harness(fetchImpl);
  el.githubRepo.value = 'example/new-project';
  el.githubLoadRepo.dispatch('click');
  await settle();
  releaseOldRepo({ private: false, default_branch: 'main' });
  await settle();

  assert.match(el.githubBrowserStatus.textContent, /Loaded 1 paths from main/);
  assert.equal(el.githubFileTree.children.length, 1);
  assert.match(el.githubFileTree.children[0].textContent, /NEW\.md/);
});


test('ignores a pending file preview after navigating to another folder', async () => {
  let releaseFile;
  const pendingFile = new Promise(resolve => { releaseFile = resolve; });
  const normalFetch = apiFixture();
  const fetchImpl = async url => {
    if (url.includes('/contents/README.md?')) {
      return { ok: true, status: 200, json: () => pendingFile };
    }
    return normalFetch(url);
  };

  const el = harness(fetchImpl);
  await settle();
  const readme = el.githubFileTree.children.find(button => button.textContent.includes('README.md'));
  const folder = el.githubFileTree.children.find(button => button.textContent.includes('src'));
  readme.dispatch('click');
  folder.dispatch('click');
  await settle();

  releaseFile({
    type: 'file',
    size: 11,
    encoding: 'base64',
    content: Buffer.from('Old preview', 'utf8').toString('base64')
  });
  await settle();

  assert.equal(el.githubCurrentPath.textContent, 'src');
  assert.equal(el.githubFilePreview.textContent, 'Choose a file to preview its text.');
});


test('does not turn untrusted commit URLs into clickable links', async () => {
  const fixture = apiFixture();
  const fetchImpl = async url => {
    const result = await fixture(url);
    if (url.includes('/commits?') && result.ok) {
      const items = await result.json();
      items[0].html_url = 'javascript:alert(1)';
      return response(200, items);
    }
    return result;
  };
  const el = harness(fetchImpl);
  await settle();
  const link = el.githubRecentCommits.children[0].children[0];
  assert.equal(link.href, undefined);
  assert.equal(link.target, undefined);
});


test('resets the displayed folder path when switching repositories', async () => {
  const el = harness(apiFixture());
  await settle();
  el.githubCurrentPath.textContent = 'src';
  el.githubRepo.value = 'example/new-project';
  el.githubLoadRepo.dispatch('click');
  assert.equal(el.githubCurrentPath.textContent, '/');
});
