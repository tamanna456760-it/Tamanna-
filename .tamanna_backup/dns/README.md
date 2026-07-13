Tamanna DNS Worker Project

Structure

Dns/
├── README.md
├── dns/
│   └── dns-records.txt
├── workers/
│   └── worker.js
└── .github/
└── workflows/
└── deploy.yml

Deploy

1. Create Cloudflare API Token
2. Add GitHub Secrets:
   - CLOUDFLARE_API_TOKEN
   - CLOUDFLARE_ACCOUNT_ID
3. Push to GitHub
4. GitHub Actions will deploy automatically