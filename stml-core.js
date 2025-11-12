class STMLParser {
    constructor() {
        this.version = "1.0.0";
        this.appName = "Tamanna AI Apps";
    }

    parse(stmlContent) {
        try {
            const lines = stmlContent.split('\n').filter(line => line.trim());
            const result = {
                metadata: {},
                components: [],
                workflows: [],
                ai_models: [],
                interfaces: []
            };

            let currentSection = null;
            let currentObject = null;

            for (const line of lines) {
                const trimmedLine = line.trim();
                
                if (trimmedLine.startsWith('@')) {
                    // Metadata line
                    const [key, ...valueParts] = trimmedLine.slice(1).split(':');
                    if (key && valueParts.length) {
                        result.metadata[key.trim()] = valueParts.join(':').trim();
                    }
                } else if (trimmedLine.endsWith('{')) {
                    // Start of section
                    currentSection = trimmedLine.slice(0, -1).trim();
                    currentObject = { type: currentSection, properties: {} };
                } else if (trimmedLine === '}') {
                    // End of section
                    if (currentObject) {
                        this.addToSection(result, currentSection, currentObject);
                    }
                    currentSection = null;
                    currentObject = null;
                } else if (trimmedLine.includes(':') && currentObject) {
                    // Property line
                    const [key, ...valueParts] = trimmedLine.split(':');
                    const value = valueParts.join(':').trim();
                    currentObject.properties[key.trim()] = this.parseValue(value);
                }
            }

            return result;
        } catch (error) {
            throw new Error(`STML Parse Error: ${error.message}`);
        }
    }

    parseValue(value) {
        // Try to parse as different types
        if (value === 'true') return true;
        if (value === 'false') return false;
        if (value === 'null') return null;
        if (!isNaN(value) && value.trim() !== '') return Number(value);
        
        // Array detection
        if (value.startsWith('[') && value.endsWith(']')) {
            return value.slice(1, -1).split(',').map(item => this.parseValue(item.trim()));
        }
        
        // Object detection
        if (value.startsWith('{') && value.endsWith('}')) {
            return this.parse(value);
        }
        
        return value;
    }

    addToSection(result, section, object) {
        const sectionMap = {
            'component': 'components',
            'workflow': 'workflows',
            'ai_model': 'ai_models',
            'interface': 'interfaces'
        };

        const targetSection = sectionMap[section];
        if (targetSection) {
            result[targetSection].push(object);
        }
    }

    generate(config) {
        let stml = `@generator: ${this.appName}\n@version: ${this.version}\n@timestamp: ${new Date().toISOString()}\n\n`;

        // Add metadata
        if (config.metadata) {
            for (const [key, value] of Object.entries(config.metadata)) {
                stml += `@${key}: ${value}\n`;
            }
            stml += '\n';
        }

        // Generate components
        if (config.components) {
            for (const component of config.components) {
                stml += this.generateComponent(component);
            }
        }

        // Generate AI models
        if (config.ai_models) {
            for (const model of config.ai_models) {
                stml += this.generateAIModel(model);
            }
        }

        // Generate workflows
        if (config.workflows) {
            for (const workflow of config.workflows) {
                stml += this.generateWorkflow(workflow);
            }
        }

        return stml;
    }

    generateComponent(component) {
        return `component ${component.name} {
    type: ${component.type}
    version: ${component.version}
    description: ${component.description}
    inputs: [${component.inputs?.join(', ') || ''}]
    outputs: [${component.outputs?.join(', ') || ''}]
    ai_capabilities: ${component.ai_capabilities || 'basic'}
}\n\n`;
    }

    generateAIModel(model) {
        return `ai_model ${model.name} {
    framework: ${model.framework}
    task: ${model.task}
    accuracy: ${model.accuracy}
    training_data: ${model.training_data}
    endpoints: [${model.endpoints?.join(', ') || ''}]
    latency: ${model.latency}
}\n\n`;
    }

    generateWorkflow(workflow) {
        return `workflow ${workflow.name} {
    trigger: ${workflow.trigger}
    steps: [${workflow.steps?.join(', ') || ''}]
    ai_models: [${workflow.ai_models?.join(', ') || ''}]
    output: ${workflow.output}
    error_handling: ${workflow.error_handling}
}\n\n`;
    }
}

module.exports = STMLParser;