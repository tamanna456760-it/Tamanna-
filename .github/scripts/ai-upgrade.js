const fs = require('fs');
const path = require('path');
const axios = require('axios');

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
if (!OPENAI_API_KEY) {
  console.error("OPENAI_API_KEY সিক্রেটে নেই");
  process.exit(1);
}

const EXTENSIONS = ['.js', '.ts', '.py', '.java', '.go', '.rb', '.php', '.html', '.css', '.json'];

function shouldProcess(filePath) {
  return EXTENSIONS.includes(path.extname(filePath)) &&
         !filePath.includes('node_modules') &&
         !filePath.includes('.git') &&
         !filePath.includes('.github/scripts');
}

async function upgradeCode(code, filename) {
  const prompt = `You are an expert. Improve this ${filename} code for performance, security, modern best practices. Return only code, no explanation. If no change needed, return same code.\n\n${code}`;
  try {
    const res = await axios.post('https://api.openai.com/v1/chat/completions', {
      model: 'gpt-3.5-turbo', // সস্তা, চাইলে gpt-4 দিতে পারেন
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.2,
      max_tokens: 4000
    }, {
      headers: { 'Authorization': `Bearer ${OPENAI_API_KEY}` }
    });
    let newCode = res.data.choices[0].message.content;
    if (newCode.startsWith('```') && newCode.includes('\n')) {
      newCode = newCode.replace(/```\w*\n?/g, '').replace(/```$/, '');
    }
    return newCode;
  } catch (err) {
    console.error(`Error upgrading ${filename}:`, err.message);
    return code;
  }
}

async function walk(dir) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const full = path.join(dir, file);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      await walk(full);
    } else if (shouldProcess(full)) {
      console.log(`Processing ${full}...`);
      const original = fs.readFileSync(full, 'utf8');
      const upgraded = await upgradeCode(original, full);
      if (upgraded !== original) {
        fs.writeFileSync(full, upgraded, 'utf8');
        console.log(`✅ Updated ${full}`);
      } else {
        console.log(`⏩ No change ${full}`);
      }
    }
  }
}

walk('.').then(() => console.log("Upgrade complete!"));