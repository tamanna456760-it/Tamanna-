// ============================================================
// Tamanna AI - Feature Level Manager
// Owner: HM INSAN ALI
// ============================================================
//
// Levels:
//   basic  -> ON
//   medium -> basic OFF, medium ON
//   strong -> medium OFF, strong ON
//
// Rule:
//   এক সময়ে শুধুমাত্র একটি feature level active থাকবে.
// ============================================================


// ------------------------------------------------------------
// 1. Available Feature Levels
// ------------------------------------------------------------

const FEATURE_LEVELS = Object.freeze([
  'basic',
  'medium',
  'strong'
]);


// ------------------------------------------------------------
// 2. Feature State
// ------------------------------------------------------------

const featureState = {
  basic: false,
  medium: false,
  strong: false
};


// ------------------------------------------------------------
// 3. Current Active Feature
// ------------------------------------------------------------

let activeFeature = null;


// ------------------------------------------------------------
// 4. Validate Feature
// ------------------------------------------------------------

function isValidFeature(level) {
  return FEATURE_LEVELS.includes(level);
}


// ------------------------------------------------------------
// 5. Turn OFF All Features
// ------------------------------------------------------------

function deactivateAllFeatures() {
  FEATURE_LEVELS.forEach(level => {
    featureState[level] = false;
  });

  activeFeature = null;

  console.log('[Tamanna AI] All feature levels OFF');
}


// ------------------------------------------------------------
// 6. Activate Feature
// ------------------------------------------------------------

function activateFeature(level) {

  // Invalid level protection
  if (!isValidFeature(level)) {
    console.warn(
      `[Tamanna AI] Unknown feature level: ${level}`
    );

    return false;
  }


  // Same feature already active
  if (activeFeature === level) {
    console.log(
      `[Tamanna AI] ${level} is already active`
    );

    return true;
  }


  // Turn everything OFF first
  deactivateAllFeatures();


  // Activate requested feature
  featureState[level] = true;
  activeFeature = level;


  console.log(
    `[Tamanna AI] Feature activated: ${level}`
  );


  // Optional event notification
  dispatchFeatureEvent(level);


  return true;
}


// ------------------------------------------------------------
// 7. Deactivate One Feature
// ------------------------------------------------------------

function deactivateFeature(level) {

  if (!isValidFeature(level)) {
    console.warn(
      `[Tamanna AI] Cannot deactivate unknown level: ${level}`
    );

    return false;
  }


  featureState[level] = false;


  if (activeFeature === level) {
    activeFeature = null;
  }


  console.log(
    `[Tamanna AI] Feature deactivated: ${level}`
  );


  dispatchFeatureEvent(null);

  return true;
}


// ------------------------------------------------------------
// 8. Get Current Active Feature
// ------------------------------------------------------------

function getActiveFeature() {
  return activeFeature;
}


// ------------------------------------------------------------
// 9. Get Complete Feature Status
// ------------------------------------------------------------

function getFeatureStatus() {

  return {
    active: activeFeature,

    basic: featureState.basic,
    medium: featureState.medium,
    strong: featureState.strong,

    timestamp: new Date().toISOString()
  };
}


// ------------------------------------------------------------
// 10. Check Whether Feature Is Active
// ------------------------------------------------------------

function isFeatureActive(level) {

  if (!isValidFeature(level)) {
    return false;
  }

  return featureState[level] === true;
}


// ------------------------------------------------------------
// 11. Feature Event System
// ------------------------------------------------------------

function dispatchFeatureEvent(level) {

  if (typeof window === 'undefined') {
    return;
  }


  try {

    window.dispatchEvent(
      new CustomEvent('tamanna-feature-change', {
        detail: {
          active: level,
          status: getFeatureStatus()
        }
      })
    );

  } catch (error) {

    console.warn(
      '[Tamanna AI] Feature event error:',
      error
    );

  }
}


// ------------------------------------------------------------
// 12. Listen For Feature Changes
// ------------------------------------------------------------

if (typeof window !== 'undefined') {

  window.addEventListener(
    'tamanna-feature-change',
    event => {

      console.log(
        '[Tamanna AI] Feature status changed:',
        event.detail
      );

    }
  );

}


// ------------------------------------------------------------
// 13. Convenience Functions
// ------------------------------------------------------------

function activateBasic() {
  return activateFeature('basic');
}


function activateMedium() {
  return activateFeature('medium');
}


function activateStrong() {
  return activateFeature('strong');
}


// ------------------------------------------------------------
// 14. Safe Reset
// ------------------------------------------------------------

function resetFeatures() {
  deactivateAllFeatures();

  console.log(
    '[Tamanna AI] Feature system reset'
  );

  return true;
}


// ------------------------------------------------------------
// 15. Debug Information
// ------------------------------------------------------------

function printFeatureStatus() {

  const status = getFeatureStatus();

  console.log(
    '========================================'
  );

  console.log(
    'Tamanna AI Feature Status'
  );

  console.log(
    '========================================'
  );

  console.log(
    'Active:',
    status.active
  );

  console.log(
    'Basic:',
    status.basic
  );

  console.log(
    'Medium:',
    status.medium
  );

  console.log(
    'Strong:',
    status.strong
  );

  console.log(
    'Time:',
    status.timestamp
  );

  console.log(
    '========================================'
  );

  return status;
}


// ============================================================
// 16. TEST / USAGE
// ============================================================

// Basic ON
activateFeature('basic');


// Medium ON
// Basic automatically OFF
activateFeature('medium');


// Strong ON
// Medium automatically OFF
activateFeature('strong');


// Check current status
printFeatureStatus();


// Direct convenience methods:
//
// activateBasic();
// activateMedium();
// activateStrong();


// Check individual state:
//
// isFeatureActive('basic');
// isFeatureActive('medium');
// isFeatureActive('strong');


// Current active feature:
//
// getActiveFeature();


// Reset everything:
//
// resetFeatures();