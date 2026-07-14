#!/usr/bin/env node

const http = require("http");

const PORT = process.env.PORT || 3000;

const systemInfo = {
    name: "Tamanna System",
    version: "1.0.0",
    status: "online",
    started: new Date().toISOString()
};

const server = http.createServer((req, res) => {

    res.setHeader("Content-Type", "application/json");

    if (req.url === "/") {
        res.writeHead(200);
        return res.end(JSON.stringify({
            message: "Welcome to Tamanna System",
            ...systemInfo
        }, null, 2));
    }

    if (req.url === "/health") {
        res.writeHead(200);
        return res.end(JSON.stringify({
            status: "healthy",
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            node: process.version
        }, null, 2));
    }

    if (req.url === "/version") {
        res.writeHead(200);
        return res.end(JSON.stringify({
            name: systemInfo.name,
            version: systemInfo.version
        }, null, 2));
    }

    res.writeHead(404);
    res.end(JSON.stringify({
        error: "Route not found"
    }));
});

server.listen(PORT, () => {
    console.log("====================================");
    console.log("🚀 Tamanna System Started");
    console.log(`Listening on http://localhost:${PORT}`);
    console.log("====================================");
});
