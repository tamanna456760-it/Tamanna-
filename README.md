{
  "name": "tamanna-ai",
  "version": "1.0.0",
  "scripts": {
    "build": "npm run build:frontend && npm run build:backend",
    "build:frontend": "cd frontend && npm run build",
    "build:backend": "cd backend && npm run build",
    "test": "npm run test:frontend && npm run test:backend",
    "test:frontend": "cd frontend && npm test",
    "test:backend": "cd backend && npm test",
    "dev": "concurrently \"npm run dev:frontend\" \"npm run dev:backend\"",
    "dev:frontend": "cd frontend && npm run dev",
    "dev:backend": "cd backend && npm run dev",
    "sync": "python scripts/auto_sync.py",
    "deploy": "npm run build && npm test && npm run deploy:prod",
    "deploy:prod": "your-deployment-command-here"
  },
  "devDependencies": {
    "concurrently": "^7.6.0"
  }
}