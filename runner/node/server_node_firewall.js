const blocked = new Set();

function firewallNode(req, res, next) {
    const ip = req.ip;

    if (blocked.has(ip)) {
        return res.status(403).send("Blocked by Tamanna Global Firewall");
    }

    next();
}

// 🔥 block from master
function block_ip(ip) {
    blocked.add(ip);
    console.log("[NODE FIREWALL] BLOCKED:", ip);
}

// 🔄 update rules
function update_rules(config) {
    console.log("[NODE] Rules updated:", config);
}

module.exports = { firewallNode, block_ip, update_rules };