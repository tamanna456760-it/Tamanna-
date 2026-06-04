function activateFeature(featureId) {
  // যে feature টা on করতে চাই
  const newFeature = features.find(f => f.id === featureId);
  if (!newFeature) return;

  // আগে যার power কম, সেগুলো off করে দাও
  features.forEach(f => {
    if (f.power < newFeature.power && f.active) {
      f.active = false; // auto remove/disable
    }
  });

  // নতুনটাকে on করো
  newFeature.active = true;
}
