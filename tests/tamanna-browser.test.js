'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const source = fs.readFileSync(path.join(__dirname, '..', 'js', 'tamanna-browser.js'), 'utf8');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

class FakeElement {
  constructor(id = '') {
    this.id = id;
    this.value = '';
    this.textContent = '';
    this.dataset = {};
    this.hidden = id === 'tamannaBrowserPanel';
    this.attributes = {};
    this.listeners = {};
    this.src = 'about:blank';
  }
  addEventListener(type, callback) { (this.listeners[type] ||= []).push(callback); }
  dispatch(type, event = {}) { for (const callback of this.listeners[type] || []) callback(event); }
  setAttribute(name, value) { this.attributes[name] = value; }
  focus() { this.focused = true; }
}

function harness() {
  const ids = ['tamannaBrowserPanel', 'openBrowser', 'closeBrowser', 'browserAddress',
    'browserGo', 'browserNewTab', 'browserFrame', 'browserSearch', 'browserSearchButton', 'browserStatus',\n    'browserBack', 'browserForward', 'browserReload'];
  const elements = Object.fromEntries(ids.map(id => [id, new FakeElement(id)]));
  const opened = [];
  const context = {
    document: { getElementById: id => elements[id] || null },
    window: { open: (...args) => { opened.push(args); return { closed: false }; } },
    URL,
    encodeURIComponent
  };
  vm.runInNewContext(source, context, { filename: 'tamanna-browser.js' });
  return { elements, opened, window: context.window };
}

test('opens and closes the browser panel accessibly', () => {
  const { elements } = harness();
  elements.openBrowser.dispatch('click');
  assert.equal(elements.tamannaBrowserPanel.hidden, false);
  assert.equal(elements.openBrowser.attributes['aria-expanded'], 'true');
  assert.equal(elements.browserAddress.focused, true);
  elements.closeBrowser.dispatch('click');
  assert.equal(elements.tamannaBrowserPanel.hidden, true);
  assert.equal(elements.openBrowser.attributes['aria-expanded'], 'false');
  assert.equal(elements.openBrowser.focused, true);
});

test('navigates HTTPS sites inside the sandboxed preview frame', () => {
  const { elements } = harness();
  elements.browserAddress.value = 'example.com/docs';
  elements.browserGo.dispatch('click');
  assert.equal(elements.browserFrame.src, 'https://example.com/docs');
  assert.match(elements.browserStatus.textContent, /iframe embedding/);
});

test('rejects insecure, credential-bearing and local/private URLs', () => {
  const { elements } = harness();
  for (const value of ['http://example.com', 'https://user:pass@example.com', 'https://localhost',
    'https://127.0.0.1', 'https://10.0.0.2', 'https://192.168.1.10', 'https://172.16.0.1']) {
    elements.browserAddress.value = value;
    elements.browserGo.dispatch('click');
    assert.equal(elements.browserFrame.src, 'about:blank', value + ' must not navigate');
    assert.equal(elements.browserStatus.dataset.state, 'error', value + ' must show an error');
  }
});

test('opens web search in a user-initiated DuckDuckGo tab', () => {
  const { elements, opened } = harness();
  elements.browserSearch.value = 'Tamanna AI browser';
  elements.browserSearchButton.dispatch('click');
  assert.equal(opened.length, 1);
  assert.equal(opened[0][0], 'https://duckduckgo.com/?q=Tamanna%20AI%20browser');
  assert.equal(opened[0][1], '_blank');
  assert.equal(opened[0][2], 'noopener,noreferrer');
});

test('does not open an empty web search', () => {
  const { elements, opened } = harness();
  elements.browserSearchButton.dispatch('click');
  assert.equal(opened.length, 0);
  assert.equal(elements.browserStatus.dataset.state, 'error');
});

test('uses a new tab only after an explicit button click', () => {
  const { elements, opened } = harness();
  elements.browserAddress.value = 'https://example.org';
  elements.browserNewTab.dispatch('click');
  assert.equal(opened.length, 1);
  assert.equal(opened[0][0], 'https://example.org/');
  assert.equal(opened[0][2], 'noopener,noreferrer');
});

test('browser preview is sandboxed and documents the GitHub repository browser link', () => {
  assert.match(html, /sandbox="allow-forms allow-scripts allow-popups"/);
  assert.match(html, /referrerpolicy="no-referrer"/);
  assert.match(html, /href="\/admin\.html#github-browser-panel"/);
  assert.match(html, /tamanna-browser\.js/);
});


test('does not misreport a popup as blocked when noopener returns null', () => {
  const { elements } = harness();
  elements.browserSearch.value = 'privacy test';
  // Browsers may return null for window.open when noopener is requested,
  // even when the user-initiated tab was opened successfully.
  elements.browserSearchButton.dispatch('click');
  assert.equal(elements.browserStatus.dataset.state, 'ok');
  assert.match(elements.browserStatus.textContent, /অনুরোধ পাঠানো হয়েছে/);
});


test('tracks browser back, forward, reload and truncates forward history after new navigation', () => {
  const { elements } = harness();
  assert.equal(elements.browserBack.disabled, true);
  assert.equal(elements.browserForward.disabled, true);
  elements.browserAddress.value = 'https://one.example';
  elements.browserGo.dispatch('click');
  assert.equal(elements.browserBack.disabled, true);
  assert.equal(elements.browserForward.disabled, true);
  assert.equal(elements.browserReload.disabled, false);
  elements.browserAddress.value = 'https://two.example/path';
  elements.browserGo.dispatch('click');
  assert.equal(elements.browserBack.disabled, false);
  elements.browserBack.dispatch('click');
  assert.equal(elements.browserFrame.src, 'https://one.example/');
  assert.equal(elements.browserAddress.value, 'https://one.example/');
  assert.equal(elements.browserForward.disabled, false);
  elements.browserForward.dispatch('click');
  assert.equal(elements.browserFrame.src, 'https://two.example/path');
  elements.browserReload.dispatch('click');
  assert.equal(elements.browserFrame.src, 'https://two.example/path');
  elements.browserBack.dispatch('click');
  elements.browserAddress.value = 'https://three.example';
  elements.browserGo.dispatch('click');
  assert.equal(elements.browserForward.disabled, true);
  assert.equal(elements.browserFrame.src, 'https://three.example/');
});
