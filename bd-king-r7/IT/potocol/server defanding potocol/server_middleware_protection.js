const rateMap = new Map();

function tamannaDefense(req, res, next) {
    const ip = req.ip;
    const now = Date.now();

    if (!rateMap.has(ip)) {
        rateMap.set(ip, []);
    }

    let logs = rateMap.get(ip);

    logs = logs.filter(t => now - t < 60000);
    logs.push(now);

    rateMap.set(ip, logs);

    if (logs.length > 100) {
        console.log("[DEFENSE] BLOCKED:", ip);
        return res.status(429).send("Blocked by Tamanna Defense Protocol");
    }

    next();
}

module.exports = tamannaDefense;