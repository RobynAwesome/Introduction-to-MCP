"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { test } = require("node:test");

const repo = path.resolve(__dirname, "..");
const payload = "</script><script>window.__xss=true</script><img src=x onerror=alert(1)>";

function functionSource(source, name) {
  const match = new RegExp(`function\\s+${name}\\s*\\(`).exec(source);
  assert.ok(match, `function ${name} must exist`);
  const open = source.indexOf("{", match.index + match[0].length);
  assert.notEqual(open, -1, `function ${name} must have a body`);
  return source.slice(match.index, blockEnd(source, open));
}

function blockEnd(source, open) {
  let depth = 0;
  let state = "code";
  let escaped = false;
  for (let i = open; i < source.length; i++) {
    const ch = source[i];
    const next = source[i + 1];
    if (state === "line-comment") {
      if (ch === "\n") state = "code";
      continue;
    }
    if (state === "block-comment") {
      if (ch === "*" && next === "/") {
        state = "code";
        i++;
      }
      continue;
    }
    if (state === "single" || state === "double" || state === "template") {
      if (escaped) {
        escaped = false;
        continue;
      }
      if (ch === "\\") {
        escaped = true;
        continue;
      }
      if ((state === "single" && ch === "'") ||
          (state === "double" && ch === '"') ||
          (state === "template" && ch === "`")) state = "code";
      continue;
    }
    if (ch === "/" && next === "/") {
      state = "line-comment";
      i++;
    } else if (ch === "/" && next === "*") {
      state = "block-comment";
      i++;
    } else if (ch === "'") {
      state = "single";
    } else if (ch === '"') {
      state = "double";
    } else if (ch === "`") {
      state = "template";
    } else if (ch === "{") {
      depth++;
    } else if (ch === "}") {
      depth--;
      if (depth === 0) return i + 1;
    }
  }
  throw new Error("unterminated JavaScript block");
}

class FakeText {
  constructor(text) {
    this.tagName = "#text";
    this.textContent = String(text);
    this.children = [];
  }
}

class FakeNode {
  constructor(document, tagName) {
    this.ownerDocument = document;
    this.tagName = tagName;
    this.children = [];
    this._text = "";
    this._html = "";
    this.className = "";
    this.value = "";
    this.scrollTop = 0;
    this.scrollHeight = 0;
    this.style = {};
  }
  appendChild(node) {
    if (node.tagName === "#fragment") {
      this.children.push(...node.children);
      node.children = [];
    } else {
      this.children.push(node);
    }
    this._text = "";
    return node;
  }
  replaceChildren(...nodes) {
    this.children = [];
    this._text = "";
    for (const node of nodes) this.appendChild(node);
  }
  set textContent(value) {
    this.children = [];
    this._text = String(value);
  }
  get textContent() {
    return this._text + this.children.map((child) => child.textContent).join("");
  }
  set innerHTML(value) {
    this.ownerDocument.innerHTMLWrites++;
    this._html = String(value);
    if (/<(?:img|script)\b/i.test(this._html)) this.ownerDocument.activeMarkupAttempts++;
    this.children = [];
    this._text = this._html;
  }
  get innerHTML() {
    return this._html;
  }
}

class FakeDocument {
  constructor() {
    this.elements = new Map();
    this.innerHTMLWrites = 0;
    this.activeMarkupAttempts = 0;
  }
  getElementById(id) {
    if (!this.elements.has(id)) this.elements.set(id, new FakeNode(this, "div"));
    return this.elements.get(id);
  }
  createElement(tagName) {
    return new FakeNode(this, tagName.toLowerCase());
  }
  createTextNode(text) {
    return new FakeText(text);
  }
  createDocumentFragment() {
    return new FakeNode(this, "#fragment");
  }
  containsTag(node, tagName) {
    return node.tagName === tagName || node.children.some((child) => this.containsTag(child, tagName));
  }
}

function evaluate(snippets, document, globals = {}) {
  const context = {
    document,
    setTimeout(callback) { callback(); return 0; },
    ...globals,
  };
  vm.createContext(context);
  vm.runInContext(snippets.join("\n"), context);
  return context;
}

function readPage(relativePath) {
  return fs.readFileSync(path.join(repo, relativePath), "utf8");
}

function findNode(node, predicate) {
  if (predicate(node)) return node;
  for (const child of node.children) {
    const found = findNode(child, predicate);
    if (found) return found;
  }
  return null;
}

for (const page of ["public/careers/index.html", "kopano-labs-web/careers/index.html"]) {
  test(`${page} renders free-text messages as inert text`, () => {
    const source = readPage(page);
    const document = new FakeDocument();
    document.getElementById("vc-input").value = payload;
    const context = evaluate(
      [functionSource(source, "addMsg"), functionSource(source, "sendVC")],
      document,
      { processAdaptiveness: (value) => value, setOptions() {}, runState() {} },
    );
    context.sendVC();
    const messages = document.getElementById("vc-messages");
    assert.ok(messages.textContent.includes(payload));
    assert.equal(document.containsTag(messages, "img"), false);
    assert.equal(document.containsTag(messages, "script"), false);
    assert.equal(document.innerHTMLWrites, 0);
    assert.equal(document.activeMarkupAttempts, 0);
  });

  test(`${page} keeps civic report input inert and preserves the bold domain label`, () => {
    const source = readPage(page);
    const document = new FakeDocument();
    const context = evaluate(
      [functionSource(source, "addMsg"), functionSource(source, "processAdaptiveness")],
      document,
      { FIREWALL_PATTERNS: [], LOCAL_DICT: {} },
    );
    context.processAdaptiveness(`${payload} eskom`);
    const messages = document.getElementById("vc-messages");
    assert.ok(messages.textContent.includes(payload));
    assert.equal(document.containsTag(messages, "img"), false);
    assert.equal(document.containsTag(messages, "script"), false);
    assert.equal(document.innerHTMLWrites, 0);

    const openContext = evaluate(
      [functionSource(source, "addMsg"), functionSource(source, "openVC")],
      new FakeDocument(),
      { vcOpen: true, toggleVC() {}, runState() {} },
    );
    openContext.openVC("governance");
    const intro = openContext.document.getElementById("vc-messages");
    const domainLabel = findNode(intro, (node) => node.tagName === "strong");
    assert.equal(domainLabel?.textContent, "Governance Protocol");
    assert.equal(openContext.document.innerHTMLWrites, 0);
  });
}

test("public/sovereign-sim highlights fluff while rendering script input as inert text", () => {
  const source = readPage("public/sovereign-sim/index.html");
  const fluff = source.match(/const\s+FLUFF_WORDS\s*=\s*\[[\s\S]*?\];/);
  assert.ok(fluff, "FLUFF_WORDS must remain available to the page");
  const document = new FakeDocument();
  document.getElementById("raw-script-input").value = `innovative ${payload}`;
  const context = evaluate([fluff[0], functionSource(source, "filterFluff")], document);
  context.filterFluff();
  const output = document.getElementById("clean-script-output");
  assert.equal(output.textContent, `innovative ${payload}`);
  assert.equal(document.getElementById("fluff-count").textContent, "1 Fluff Detected");
  assert.equal(document.containsTag(output, "img"), false);
  assert.equal(document.containsTag(output, "script"), false);
  assert.equal(document.innerHTMLWrites, 0);
  assert.equal(document.activeMarkupAttempts, 0);
});

test("public/sovereign-sim terminal echoes an onerror payload as inert text", () => {
  const source = readPage("public/sovereign-sim/index.html");
  const commands = source.match(/const\s+terminalCmds\s*=\s*\{[\s\S]*?^\};/m);
  assert.ok(commands, "terminal command table must remain available to the page");
  const document = new FakeDocument();
  document.getElementById("terminal-input").value = payload;
  const context = evaluate(
    [commands[0], functionSource(source, "appendTerminalLine"), functionSource(source, "runTerminalCmd")],
    document,
  );
  context.runTerminalCmd();
  const output = document.getElementById("terminal-output");
  assert.ok(output.textContent.includes(`$ ${payload}`));
  assert.ok(output.textContent.includes(`Command not found: ${payload}`));
  assert.equal(document.containsTag(output, "img"), false);
  assert.equal(document.containsTag(output, "script"), false);
  assert.equal(document.innerHTMLWrites, 0);
  assert.equal(document.activeMarkupAttempts, 0);
});

test("affected public page inline scripts remain syntactically valid", () => {
  for (const page of [
    "public/careers/index.html",
    "kopano-labs-web/careers/index.html",
    "public/sovereign-sim/index.html",
  ]) {
    const source = readPage(page);
    const scripts = [...source.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script\s*>/gi)];
    for (const [index, script] of scripts.entries()) {
      const attributes = script[1];
      const body = script[2];
      if (/\bsrc\s*=/.test(attributes) || !body.trim()) continue;
      assert.doesNotThrow(
        () => new vm.Script(body, { filename: `${page}#script-${index + 1}` }),
        `${page} inline script ${index + 1} should parse`,
      );
    }
  }
});
