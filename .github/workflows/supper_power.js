const engine = new FeatureDefenseEngine();

engine.register("basic", 1, "external");
engine.register("shield", 2, "internal");
engine.register("ultraShield", 5, "internal");
engine.register("thirdPartyBoost", 1, "thirdParty");

// Activate basic
engine.activate("basic");

// Activate third‑party
engine.activate("thirdPartyBoost");

// Activate shield → auto removes weaker + blocks third‑party
engine.activate("shield");

// Activate ultraShield → everything weaker removed
engine.activate("ultraShield");

console.log("Active Features:", engine.getActive());
console.log("Action Log:", engine.getLog());
