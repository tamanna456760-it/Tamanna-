class FeatureDefenseEngine {
  constructor() {
    this.features = new Map();
    this.log = [];
  }

  register(id, power, type = "default", meta = {}) {
    if (this.features.has(id)) {
      throw new Error(`Feature "${id}" already exists`);
    }

    this.features.set(id, {
      id,
      power,
      type,
      active: false,
      meta
    });
  }

  // Internal logger
  _log(action, feature) {
    this.log.push({
      time: Date.now(),
      action,
      feature: feature.id,
      power: feature.power,
      type: feature.type
    });
  }

  // Auto remove weaker features
  _autoRemoveWeaker(newFeature) {
    for (const f of this.features.values()) {
      if (f.active && f.power < newFeature.power) {
        f.active = false;
        this._log("AUTO_REMOVE", f);
      }
    }
  }

  // Auto block third‑party if internal is stronger
  _blockThirdParty(newFeature) {
    if (newFeature.type === "internal") {
      for (const f of this.features.values()) {
        if (f.active && f.type === "thirdParty" && f.power <= newFeature.power) {
          f.active = false;
          this._log("BLOCK_THIRD_PARTY", f);
        }
      }
    }
  }

  // Main activation logic
  activate(id) {
    const feature = this.features.get(id);
    if (!feature) throw new Error(`Feature "${id}" not found`);

    // Remove weaker features
    this._autoRemoveWeaker(feature);

    // Block third‑party if needed
    this._blockThirdParty(feature);

    // Activate new feature
    feature.active = true;
    this._log("ACTIVATE", feature);
  }

  // Strict mode: only one feature allowed
  activateStrict(id) {
    const feature = this.features.get(id);
    if (!feature) throw new Error(`Feature "${id}" not found`);

    for (const f of this.features.values()) {
      f.active = false;
      this._log("FORCE_OFF", f);
    }

    feature.active = true;
    this._log("STRICT_ACTIVATE", feature);
  }

  deactivate(id) {
    const feature = this.features.get(id);
    if (!feature) return;

    feature.active = false;
    this._log("DEACTIVATE", feature);
  }

  getActive() {
    return [...this.features.values()].filter(f => f.active);
  }

  getLog() {
    return this.log;
  }
}
