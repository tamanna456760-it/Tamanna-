import { Octokit } from "@octokit/rest";

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN
});

async function run() {
  const { data } = await octokit.repos.listForAuthenticatedUser();

  console.log("Repositories:");
  data.forEach(repo => {
    console.log(`- ${repo.full_name}`);
  });
}

run().catch(console.error);