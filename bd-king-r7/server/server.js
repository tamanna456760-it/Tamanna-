{
  "name": "bd-king-r7-powerhub",
  "version": "9.0.0",
  "description": "BD-KING-R7 Tamanna PowerHub Quantum Server — Cluster‑Optimized Edition",
  "main": "server.js",
  "type": "commonjs",

  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "cluster": "pm2 start server.js -i max --name powerhub",
    "cluster:stop": "pm2 delete powerhub",
    "build": "tsc",
    "lint": "eslint .",
    "test": "node tests/run-tests.js",
    "diagnostics": "node tools/diagnostics.js",
    "prepare": "husky install",
    "release": "standard-version",
    "clean": "rm -rf node_modules dist && npm install"
  },

  "dependencies": {
    "express": "^4.19.2",
    "cors": "^2.8.5",
    "helmet": "^7.0.0",
    "compression": "^1.7.4",
    "dotenv": "^16.4.5",
    "morgan": "^1.10.0",
    "uuid": "^9.0.1"
  },

  "devDependencies": {
    "nodemon": "^3.1.0",
    "pm2": "^5.3.0",
    "typescript": "^5.6.3",
    "eslint": "^9.0.0",
    "husky": "^9.0.10",
    "standard-version": "^9.5.0"
  },

  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  },

  "keywords": [
    "powerhub",
    "reactor",
    "quantum-engine",
    "bd-king-r7",
    "tamanna",
    "api",
    "express",
    "cluster",
    "pm2",
    "nodejs"
  ],

  "author": "System AI",
  "license": "MIT",

  "repository": {
    "type": "git",
    "url": "https://github.com/tamanna456760-it/tamanna-"
  }
}
{
  "name": "bd-king-r7-powerhub",
  "version": "1.0.0",
  "description": "BD-KING-R7 Tamanna PowerHub Server",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.19.2",
    "cors": "^2.8.5"
  }
}