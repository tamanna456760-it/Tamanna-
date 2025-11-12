const STMLApplication = require('../src/main');

async function runDemo() {
    const app = new STMLApplication();
    
    console.log('🎪 Tamanna AI Apps STML Demo\n');
    
    // Create a simple app programmatically
    const demoSTML = `
@name: Demo AI Assistant
@version: 1.0.0
@type: demo
@author: tamanna456760-it

component demo_processor {
    type: demo_component
    version: 1.0.0
    description: Demo processing component
    inputs: [input_text]
    outputs: [processed_output]
}

workflow demo_flow {
    trigger: user_input
    steps: [preprocess, analyze, respond]
    output: ai_response
}
`;

    console.log('1. Creating demo app from STML...');
    const appId = app.tamannaAI.createApp(demoSTML);
    
    console.log('2. Listing all apps...');
    app.displayApps();
    
    console.log('3. Generating STML from app config...');
    const appConfig = app.tamannaAI.apps.get(appId).config;
    const generatedSTML = app.tamannaAI.generateAppSTML(appConfig);
    console.log(generatedSTML);
    
    console.log('4. Demo completed! 🎉');
}

runDemo().catch(console.error);