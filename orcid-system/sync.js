const fs = require("fs");

const config = require("./config.json");

const profile = {
  name: config.name,
  orcid: config.orcid,
  github: config.github,
  projects: config.projects,
  last_update: new Date().toISOString(),
  status: "Active AI Developer"
};

// Save profile
fs.writeFileSync("profile.json", JSON.stringify(profile, null, 2));

// Auto README generate
const readme = `
# ${config.name}

## 🔗 ORCID
${config.orcid}

## 💻 GitHub
${config.github}

## 🚀 Projects
${config.projects.map(p => "- " + p).join("\n")}

## 📅 Last Update
${new Date().toLocaleString()}
`;

fs.writeFileSync("README.md", readme);

console.log("✅ ORCID System Ready & Synced");