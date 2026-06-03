const attackLog = new Map();
const blocked = new Set();

function adaptiveDefense(req, res, next) {
    const ip = req.ip;
    const now = Date.now();

    if (blocked.has(ip)) {
        return res.status(403).send("Blocked by Tamanna Defense Core");
    }

    if (!attackLog.has(ip)) attackLog.set(ip, []);

    let logs = attackLog.get(ip);
    logs = logs.filter(t => now - t < 60000);
    logs.push(now);

    attackLog.set(ip, logs);

    // detection
    if (logs.length > 120) {
        blocked.add(ip);
        console.log("[AUTO DEFENSE] BLOCKED:", ip);
        return res.status(429).send("Attack detected");
    }

    next();
}

module.exports = adaptiveDefense;