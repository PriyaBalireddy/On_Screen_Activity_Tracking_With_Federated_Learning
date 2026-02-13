// Client trains LOCAL model, sends weights only
async function trainLocalModel() {
    // 1. Get global model from server
    const globalModel = await fetch('/fl/global_model').then(r => r.json());
    
    // 2. Train on LOCAL activity data
    const localModel = new ActivityClassifier();
    localModel.loadWeights(globalModel.model_state);
    
    // Train on user's activity patterns
    for (let epoch = 0; epoch < 5; epoch++) {
        trainBatch(localModel, userActivities);  // User's private data
    }
    
    // 3. Send ONLY model weights back (NO DATA)
    const localWeights = localModel.getWeights();
    await fetch('/fl/train_local', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            model_state: localWeights,
            local_accuracy: 0.92  // Client's validation accuracy
        })
    });
}
