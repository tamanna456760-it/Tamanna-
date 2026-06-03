const express = require("express");
const app = express();

app.use(express.json());

let blocked = new Set();
let rules = {};

// middleware firewall
app.use((req, res, next) => {
    const ip = req.ip;

    if (blocked.has(ip)) {
        return res.status(403).send("Blocked by Tamanna Firewall");
    }

    next();
});

// test route
app.get("/", (req, res) => {
    res.send("Node server running with firewall");
});

// block ip from python core
app.post("/block", (req, res) => {
    const ip = req.body.ip;
    blocked.add(ip);
    console.log("[NODE] BLOCKED:", ip);
    res.json({ status: "blocked" });
});

// update rules
app.post("/rules", (req, res) => {
    rules = req.body;
    console.log("[NODE] rules updated");
    res.json({ status: "updated" });
});

app.listen(3000, () => {
    console.log("Node Firewall Server running on port 3000");
});