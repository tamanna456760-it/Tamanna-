/* Tamanna AI account UI. Session token stays in HttpOnly cookie. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const panel = $("authPanel"), backdrop = $("authBackdrop"), status = $("authStatus");
  const opener = $("openAuth");
  let currentUser = null;
  const api = async (path, options = {}) => {
    const response = await fetch("/api/auth" + path, {
      credentials: "same-origin",
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) }
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.detail || body.message || ("HTTP " + response.status));
    return body;
  };
  const showStatus = (message, error = false) => {
    status.textContent = message;
    status.classList.toggle("tamanna-error", error);
  };
  const open = () => { panel.hidden = false; backdrop.hidden = false; $("closeAuth").focus(); };
  const close = () => { panel.hidden = true; backdrop.hidden = true; opener.focus(); };
  const showForm = (mode) => {
    $("loginForm").hidden = mode !== "login";
    $("signupForm").hidden = mode !== "signup";
    $("accountDetails").hidden = true;
    showStatus(mode === "login" ? "আপনার অ্যাকাউন্টে লগইন করুন।" : "নতুন Tamanna AI অ্যাকাউন্ট তৈরি করুন।");
  };
  const renderUser = (user) => {
    currentUser = user || null;
    opener.textContent = currentUser ? "অ্যাকাউন্ট" : "লগইন";
    if (currentUser) {
      $("loginForm").hidden = true; $("signupForm").hidden = true;
      $("accountDetails").hidden = false;
      $("accountIdentity").textContent = currentUser.name + " — " + currentUser.email;
      $("profileName").value = currentUser.name;
      showStatus("আপনি লগইন করেছেন।");
    } else {
      $("accountDetails").hidden = true;
      showForm("login");
    }
  };
  $("openAuth").addEventListener("click", open);
  $("closeAuth").addEventListener("click", close);
  backdrop.addEventListener("click", close);
  document.addEventListener("keydown", e => { if (e.key === "Escape" && !panel.hidden) close(); });
  $("showLogin").addEventListener("click", () => showForm("login"));
  $("showSignup").addEventListener("click", () => showForm("signup"));
  $("loginForm").addEventListener("submit", async e => {
    e.preventDefault();
    try {
      const result = await api("/login", { method:"POST", body:JSON.stringify({
        email:$("loginEmail").value, password:$("loginPassword").value
      })});
      renderUser(result.user);
      window.dispatchEvent(new CustomEvent("tamanna:authenticated", {detail:result.user}));
    } catch (error) { showStatus(error.message, true); }
  });
  $("signupForm").addEventListener("submit", async e => {
    e.preventDefault();
    try {
      const result = await api("/signup", { method:"POST", body:JSON.stringify({
        name:$("signupName").value, email:$("signupEmail").value, password:$("signupPassword").value
      })});
      renderUser(result.user);
      window.dispatchEvent(new CustomEvent("tamanna:authenticated", {detail:result.user}));
    } catch (error) { showStatus(error.message, true); }
  });
  $("profileForm").addEventListener("submit", async e => {
    e.preventDefault();
    try {
      await api("/profile", {method:"PATCH",body:JSON.stringify({name:$("profileName").value})});
      currentUser.name = $("profileName").value.trim();
      renderUser(currentUser);
      showStatus("প্রোফাইল আপডেট হয়েছে।");
    } catch (error) { showStatus(error.message, true); }
  });
  $("changePasswordForm")?.addEventListener("submit", async e => {
    e.preventDefault();
    const currentPassword = $("currentPassword").value;
    const newPassword = $("newPassword").value;
    if (newPassword.length < 12) {
      showStatus("নতুন পাসওয়ার্ড কমপক্ষে ১২ অক্ষরের হতে হবে।", true);
      return;
    }
    try {
      await api("/change-password", {
        method: "POST",
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
      });
      $("changePasswordForm").reset();
      renderUser(null);
      window.dispatchEvent(new Event("tamanna:loggedout"));
      showStatus("পাসওয়ার্ড পরিবর্তন হয়েছে। নিরাপত্তার জন্য সব সেশন বন্ধ করা হয়েছে—নতুন পাসওয়ার্ড দিয়ে আবার লগইন করুন।");
    } catch (error) {
      showStatus(error.message, true);
    }
  });
  $("logoutButton").addEventListener("click", async () => {
    try {
      await api("/logout", {method:"POST",body:"{}"});
      renderUser(null);
      window.dispatchEvent(new Event("tamanna:loggedout"));
      showStatus("আপনি লগআউট করেছেন।");
    } catch (error) { showStatus(error.message, true); }
  });
  const isGitHubPagesPreview = location.hostname.endsWith(".github.io");
  if (isGitHubPagesPreview) {
    renderUser(null);
    showStatus("GitHub Pages Preview Mode: the static website is online, but sign-in needs the private Tamanna backend.");
    const loginSubmit = $("loginForm")?.querySelector('button[type="submit"]');
    const signupSubmit = $("signupForm")?.querySelector('button[type="submit"]');
    if (loginSubmit) loginSubmit.disabled = true;
    if (signupSubmit) signupSubmit.disabled = true;
  } else {
    api("/me").then(result => renderUser(result.user)).catch(() => renderUser(null));
  }
  window.TamannaAuth = { api, getUser: () => currentUser };
})();