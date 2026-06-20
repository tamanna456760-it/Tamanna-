import { Octokit } from "@octokit/rest";

const octokit = new Octokit({
  auth: process.env.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
});

async function run() {
  const { data } = await octokit.repos.listForAuthenticatedUser();

  console.log("Repositories:");
  data.forEach(repo => {
    console.log(`- ${repo.tamanna-}`);
  });
}

run().catch(console.error);