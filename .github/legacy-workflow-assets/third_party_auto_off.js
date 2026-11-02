const features = [
  { id: 'thirdParty', type: 'external', power: 1, active: false },
  { id: 'proFilter',  type: 'internal', power: 3, active: false },
];

function activateFeature(featureId) {
  const newFeature = features.find(f => f.id === featureId);
  if (!newFeature) return;

  // যদি নতুন feature বেশি powerful হয়, তাহলে কম power external গুলো off
  features.forEach(f => {
    if (f.type === 'external' && f.power < newFeature.power && f.active) {
      f.active = false; // third party auto remove
    }
  });

  newFeature.active = true;
}
