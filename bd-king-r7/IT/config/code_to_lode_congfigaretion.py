import json
from pathlib import Path

class TIPULSModelManager:
    def __init__(self, config_path="config/models.json"):
        self.config_path = Path(config_path)
        self.models_config = self.load_config()
    
    def load_config(self):
        """Load models configuration"""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def get_model_config(self, model_name):
        """Get specific model configuration"""
        return self.models_config.get(model_name, {})
    
    def get_deployment_info(self):
        """Get deployment information"""
        return {
            "hardware": self.models_config["hardware_requirements"],
            "endpoints": self.models_config["integration_endpoints"],
            "performance": self.models_config["performance_metrics"]
        }
    
    def validate_config(self):
        """Validate models configuration"""
        required_sections = [
            "neural_networks", 
            "machine_learning_models",
            "model_management"
        ]
        
        for section in required_sections:
            if section not in self.models_config:
                raise ValueError(f"Missing required section: {section}")
        
        return True

# Usage
model_manager = TIPULSModelManager()
print("TI-PULS Model Configuration Loaded:")
print(f"System: {model_manager.models_config['ti_puls_system']['name']}")
print(f"Version: {model_manager.models_config['ti_puls_system']['version']}")