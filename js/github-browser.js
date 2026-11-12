/* Read-only public GitHub browser for the Tamanna admin workspace.
 * Uses GitHub's unauthenticated public REST API. Never asks for or stores tokens.
 * Private repositories and write operations are intentionally unsupported.
 */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const repoInput = $("githubRepo");
  const branchSelect = $("githubBranch");
  const pathLabel = $("githubCurrentPath");
  const tree = $("githubFileTree");
  const preview = $("githubFilePreview");
  const status = $("githubBrowserStatus");
  const commits = $("githubRecentCommits");
  if (!repoInput || !branchSelect || !tree || !preview || !status || !commits) return;

  let currentRepo = "tamanna456760-it/Tamanna-";
  let currentBranch = "main";
  let currentPath = "";
  let treeItems = [];
  let repoRequestId = 0;
  let treeRequestId = 0;
  let fileRequestId = 0;

  function setStatus(message, error = false) {
    status.textContent = message;
    status.dataset.state = error ? "error" : "ok";
  }
  function validRepo(value) {
    return /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(value);
  }
  async function github(path) {
    const response = await fetch("https://api.github.com" + path, {
      headers: { Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" }
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 403 || response.status === 429) {
        throw new Error("GitHub API rate limit reached. Wait and retry; no token is stored by this browser.");
      }
      throw new Error(data.message || ("GitHub API returned HTTP " + response.status));
    }
    return data;
  }
  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  function encodePath(path) {
    return path.split("/").map(encodeURIComponent).join("/");
  }
  async function loadRepo() {
    const requestId = ++repoRequestId;
    ++treeRequestId;
    ++fileRequestId;
    const value = repoInput.value.trim();
    if (!validRepo(value)) { setStatus("Enter a public repository as owner/name.", true); return; }
    currentRepo = value;
    currentPath = "";
    tree.replaceChildren();
    preview.textContent = "Choose a file to preview its text.";
    commits.replaceChildren();
    setStatus("Loading public repository…");
    try {
      const [repoInfo, branchData, commitData] = await Promise.all([
        github("/repos/" + currentRepo),
        github("/repos/" + currentRepo + "/branches?per_page=100"),
        github("/repos/" + currentRepo + "/commits?per_page=6")
      ]);
      if (requestId !== repoRequestId) return;
      if (repoInfo.private) throw new Error("This browser only supports public repositories.");
      branchSelect.replaceChildren();
      branchData.forEach(item => {
        const option = element("option", item.name);
        option.value = item.name;
        branchSelect.append(option);
      });
      currentBranch = repoInfo.default_branch || branchData[0]?.name || "main";
      branchSelect.value = currentBranch;
      commits.replaceChildren();
      commitData.forEach(item => {
        const row = element("li");
        const link = element("a", item.commit.message.split("\n")[0]);
        link.href = item.html_url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        row.append(link, element("small", " · " + item.sha.slice(0, 7) + " · " + (item.commit.author?.date || "")));
        commits.append(row);
      });
      await loadTree();
      if (requestId === repoRequestId) setStatus("Connected to public repository " + currentRepo + ".");
    } catch (error) {
      if (requestId === repoRequestId) setStatus(error.message, true);
    }
  }
  async function loadTree() {
    const requestId = ++treeRequestId;
    const repoSnapshot = currentRepo;
    const branchSnapshot = currentBranch;
    setStatus("Loading repository files…");
    tree.replaceChildren();
    preview.textContent = "Choose a file to preview its text.";
    try {
      const branchInfo = await github("/repos/" + repoSnapshot + "/branches/" + encodeURIComponent(branchSnapshot));
      if (requestId !== treeRequestId || repoSnapshot !== currentRepo || branchSnapshot !== currentBranch) return;
      const treeSha = branchInfo.commit.commit.tree.sha;
      const data = await github("/repos/" + repoSnapshot + "/git/trees/" + encodeURIComponent(treeSha) + "?recursive=1");
      if (requestId !== treeRequestId || repoSnapshot !== currentRepo || branchSnapshot !== currentBranch) return;
      if (data.truncated) setStatus("GitHub returned a truncated file tree; showing available entries.", true);
      treeItems = (data.tree || []).filter(item => item.type === "blob" || item.type === "tree");
      renderTree();
      if (!data.truncated) setStatus("Loaded " + treeItems.length + " paths from " + currentBranch + ".");
    } catch (error) {
      if (requestId === treeRequestId && repoSnapshot === currentRepo && branchSnapshot === currentBranch) setStatus(error.message, true);
    }
  }
  function renderTree() {
    tree.replaceChildren();
    const prefix = currentPath ? currentPath + "/" : "";
    const children = treeItems.filter(item => {
      if (!item.path.startsWith(prefix)) return false;
      return !item.path.slice(prefix.length).includes("/");
    });
    if (currentPath) {
      const up = element("button", "↑ ..", "github-tree-item");
      up.type = "button";
      up.addEventListener("click", () => {
        currentPath = currentPath.split("/").slice(0, -1).join("/");
        pathLabel.textContent = currentPath || "/";
        renderTree();
      });
      tree.append(up);
    }
    children.sort((a,b) => (a.type === b.type ? a.path.localeCompare(b.path) : a.type === "tree" ? -1 : 1));
    children.forEach(item => {
      const name = item.path.slice(prefix.length);
      const button = element("button", (item.type === "tree" ? "📁 " : "📄 ") + name, "github-tree-item");
      button.type = "button";
      button.addEventListener("click", () => {
        if (item.type === "tree") {
          currentPath = item.path;
          pathLabel.textContent = currentPath;
          renderTree();
        } else loadFile(item.path);
      });
      tree.append(button);
    });
    if (!children.length) tree.append(element("p", "No files in this folder."));
  }
  async function loadFile(path) {
    const requestId = ++fileRequestId;
    const repoSnapshot = currentRepo;
    const branchSnapshot = currentBranch;
    setStatus("Fetching " + path + "…");
    preview.textContent = "Loading file…";
    try {
      const data = await github("/repos/" + repoSnapshot + "/contents/" + encodePath(path) + "?ref=" + encodeURIComponent(branchSnapshot));
      if (requestId !== fileRequestId || repoSnapshot !== currentRepo || branchSnapshot !== currentBranch) return;
      if (Array.isArray(data) || data.type !== "file") throw new Error("This item is not a regular file.");
      if (data.size > 250000) throw new Error("File is larger than the 250 KB preview limit.");
      if (data.encoding !== "base64" || !data.content) throw new Error("GitHub did not return a supported text preview.");
      const binary = atob(data.content.replace(/\s/g, ""));
      const bytes = Uint8Array.from(binary, char => char.charCodeAt(0));
      const text = new TextDecoder("utf-8", { fatal: false }).decode(bytes);
      preview.textContent = text;
      setStatus("Read-only preview: " + path + " (" + data.size + " bytes).");
    } catch (error) {
      if (requestId === fileRequestId && repoSnapshot === currentRepo && branchSnapshot === currentBranch) {
        preview.textContent = "Preview unavailable.";
        setStatus(error.message, true);
      }
    }
  }
  $("githubLoadRepo")?.addEventListener("click", loadRepo);
  branchSelect.addEventListener("change", () => {
    currentBranch = branchSelect.value;
    currentPath = "";
    pathLabel.textContent = "/";
    loadTree();
  });
  $("githubOpenRepo")?.addEventListener("click", () => {
    if (!validRepo(currentRepo)) return;
    window.open("https://github.com/" + currentRepo, "_blank", "noopener,noreferrer");
  });
  repoInput.addEventListener("keydown", event => { if (event.key === "Enter") loadRepo(); });
  loadRepo();
})();
