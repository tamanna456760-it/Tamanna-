// server.js – Tamanna Server with WebSocket & AI Bot
const express = require('express');
const WebSocket = require('ws');
const cors = require('cors');
const http = require('http');
const url = require('url');
const Groq = require('groq-sdk');

// ---------- Configuration ----------
const PORT = process.env.PORT || 3000;
const GROQ_API_KEY = process.env.GROQ_API_KEY;

// ---------- AI Setup ----------
let groq = null;
if (GROQ_API_KEY) {
    groq = new Groq({ apiKey: GROQ_API_KEY });
    console.log('[AI] Groq client initialized');
} else {
    console.log('[AI] No API key – running in echo mode');
}

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
    if (groq && userMessage.toLowerCase().startsWith('/ai ')) {
        const query = userMessage.slice(4);
        try {
            const completion = await groq.chat.completions.create({
                messages: [
                    { role: 'system', content: 'You are Tamanna, a helpful AI assistant. Keep answers short and friendly.' },
                    { role: 'user', content: query }
                ],
                model: 'llama3-70b-8192',
                temperature: 0.7,
                max_tokens: 150
            });
            return completion.choices[0]?.message?.content || 'Sorry, no reply.';
        } catch (err) {
            console.error('Groq API error:', err);
            return 'AI service temporarily unavailable.';
        }
    }

    const cmd = userMessage.toLowerCase().trim();
    if (cmd === '/help') {
        return `Available commands:\n/help – Show help\n/ai <question> – Ask AI\n/echo <text> – Echo\n/server – Server info`;
    }
    if (cmd === '/server') {
        return `Tamanna Server v1.0\nActive clients: ${clients.size}\nAI mode: ${groq ? 'enabled' : 'disabled'}`;
    }
    if (cmd.startsWith('/echo ')) {
        return `Echo: ${userMessage.slice(6)}`;
    }
    return `🤖 Tamanna: You said “${userMessage}” – try /ai your question!`;
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
        aiEnabled: !!groq,
        timestamp: new Date().toISOString()
    });
});

server.listen(PORT, () => {
    console.log(`
╔══════════════════════════════════════╗
║      🚀 Tamanna Server Started       ║
║   HTTP  : http://localhost:${PORT}     ║
║   WS    : ws://localhost:${PORT}/ws    ║
║   AI    : ${groq ? '✅ enabled' : '❌ disabled'}
╚══════════════════════════════════════╝
    `);
});