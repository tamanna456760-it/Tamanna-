class FeatureManager {
  constructor() {
    this.features = new Map(); // id -> feature
  }

  // নতুন feature রেজিস্টার
  registerFeature(id, power, options = {}) {
    if (this.features.has(id)) {
      throw new Error(`Feature "${id}" already registered`);
    }

    this.features.set(id, {
      id,
      power,
      type: options.type || 'default', // internal / external / thirdParty etc.
      active: false,
      meta: options.meta || {}
    });
  }

  // কোন feature info দরকার হলে
  getFeature(id) {
    return this.features.get(id) || null;
  }

  // সব active feature
  getActiveFeatures() {
    return [...this.features.values()].filter(f => f.active);
  }

  // core logic: বেশি power আসলে কম power auto remove
  activate(id) {
    const newFeature = this.features.get(id);
    if (!newFeature) {
      throw new Error(`Feature "${id}" not found`);
    }

    // আগে থেকে active গুলোর মধ্যে যাদের power কম, তাদের off করো
    for (const feature of this.features.values()) {
      if (feature.active && feature.power < newFeature.power) {
        feature.active = false;
        // চাইলে এখানে callback / event trigger করতে পারো
        // this.onDeactivate && this.onDeactivate(feature);
      }
    }

    // নতুনটাকে on করো
    newFeature.active = true;
    // this.onActivate && this.onActivate(newFeature);
  }

  // force off
  deactivate(id) {
    const feature = this.features.get(id);
    if (!feature) return;
    feature.active = false;
  }

  // আরও strict: শুধু একটাই সর্বোচ্চ power feature active থাকবে
  activateStrict(id) {
    const newFeature = this.features.get(id);
    if (!newFeature) {
      throw new Error(`Feature "${id}" not found`);
    }

    // সব off
    for (const feature of this.features.values()) {
      feature.active = false;
    }

    // শুধু নতুনটা on
    newFeature.active = true;
  }
}

// ---------- ব্যবহার উদাহরণ ----------

const fm = new FeatureManager();

// feature রেজিস্টার
fm.registerFeature('basic',   1, { type: 'external' });
fm.registerFeature('medium',  2, { type: 'internal' });
fm.registerFeature('strong',  3, { type: 'internal' });
fm.registerFeature('thirdPartyShield', 1, { type: 'thirdParty' });

// normal priority-based activate
fm.activate('basic');            // basic on
fm.activate('thirdPartyShield'); // basic off হবে না, কারণ power same (1)
fm.activate('medium');           // basic + thirdPartyShield দুটোই off, medium on
fm.activate('strong');           // medium off, strong on

console.log('Active:', fm.getActiveFeatures());

// যদি strict mode চাও (একটাই feature থাকবে)
fm.activateStrict('basic');      // সব off, শুধু basic on
console.log('Strict Active:', fm.getActiveFeatures());
