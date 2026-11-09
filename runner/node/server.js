// server.js – Tamanna Server with WebSocket & AI Bot
const express = require('express');
const WebSocket = require('ws');
const cors = require('cors');
const http = require('http');
const url = require('url');

// ---------- Configuration ----------
const PORT = process.env.PORT || 3000;
// External model providers are disabled; a tested local runtime is not yet configured.
console.log('[AI] Local-only mode; inference runtime not configured');

// ---------- Express Setup ----------
const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// ---------- WebSocket Server ----------
const wsServer = new WebSocket.Server({ noServer: true });
const clients = new Set();

wsServer.on('connection', (socket, request) => {
    const clientId = Date.now();
    clients.add(socket);
    console.log(`[Tamanna Server] Client ${clientId} connected`);

    socket.send(JSON.stringify({
        type: 'welcome',
        message: 'Connected to Tamanna Server 🤖',
        timestamp: new Date().toISOString()
    }));

    socket.on('message', async (data) => {
        const raw = data.toString();
        console.log(`[${clientId}] Received: ${raw}`);

        let messageText = raw;
        let isJson = false;
        try {
            const parsed = JSON.parse(raw);
            if (parsed.text) {
                messageText = parsed.text;
                isJson = true;
            }
        } catch (e) { }

        const reply = await generateReply(messageText);
        const response = isJson
            ? JSON.stringify({ type: 'reply', text: reply, timestamp: new Date().toISOString() })
            : reply;
        socket.send(response);
    });

    socket.on('close', () => {
        clients.delete(socket);
        console.log(`[Tamanna Server] Client ${clientId} disconnected`);
    });
});

async function generateReply(userMessage) {
    const cmd = userMessage.toLowerCase().trim();
    if (cmd === '/help') {
        return `Available commands:\n/help – Show help\n/ai <question> – Local AI (currently unavailable)\n/echo <text> – Echo\n/server – Server info`;
    }
    if (cmd === '/server') {
        return `Tamanna Server v1.0\nActive clients: ${clients.size}\nAI mode: local runtime not configured; external providers disabled`;
    }
    if (cmd.startsWith('/ai ')) {
        return 'Local AI is not configured yet. External model APIs are disabled; connect and test a local model or knowledge database first.';
    }
    if (cmd.startsWith('/echo ')) {
        return `Echo: ${userMessage.slice(6)}`;
    }
    return `🤖 Tamanna: You said “${userMessage}” – try /help for available commands.`;
}

const server = http.createServer(app);
server.on('upgrade', async (req, socket, head) => {
    const { pathname } = url.parse(req.url);
    if (pathname === '/ws') {
        wsServer.handleUpgrade(req, socket, head, (ws) => {
            wsServer.emit('connection', ws, req);
        });
    } else {
        socket.destroy();
    }
});

app.get('/api/status', (req, res) => {
    res.json({
        server: 'Tamanna Server',
        status: 'running',
        clients: clients.size,
        aiEnabled: false,\n        aiMode: 'local-runtime-not-configured',\n        externalProviders: 'disabled',
        timestamp: new Date().toISOString()
    });
});

server.listen(PORT, () => {
    console.log(`
╔══════════════════════════════════════╗
║      🚀 Tamanna Server Started       ║
║   HTTP  : http://localhost:${PORT}     ║
║   WS    : ws://localhost:${PORT}/ws    ║
║   AI    : ${'local runtime not configured'}
╚══════════════════════════════════════╝
    `);
});