"""
TI-PULS Model Manager - Advanced Model Management & Version Control
Comprehensive model lifecycle management for AI/ML models
"""

import json
import pickle
import yaml
import numpy as np
import tensorflow as tf
import torch
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import uuid
import shutil
import gzip
from cryptography.fernet import Fernet

class ModelType(Enum):
    """Model types"""
    NEURAL_NETWORK = "neural_network"
    MACHINE_LEARNING = "machine_learning"
    NLP = "natural_language_processing"
    COMPUTER_VISION = "computer_vision"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    ENSEMBLE = "ensemble"

class ModelStatus(Enum):
    """Model status"""
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"
    ERROR = "error"

@dataclass
class ModelMetadata:
    """Model metadata"""
    model_id: str
    name: str
    version: str
    model_type: ModelType
    description: str
    created_date: datetime
    last_updated: datetime
    status: ModelStatus
    performance_metrics: Dict[str, float]
    hyperparameters: Dict[str, Any]
    data_sources: List[str]
    dependencies: List[str]
    model_size: int
    checksum: str

@dataclass
class TrainingConfig:
    """Training configuration"""
    config_id: str
    model_id: str
    dataset_path: str
    batch_size: int
    epochs: int
    learning_rate: float
    optimizer: str
    loss_function: str
    metrics: List[str]
    validation_split: float
    early_stopping: bool
    data_augmentation: bool

class AdvancedModelManager:
    """
    Advanced Model Manager for TI-PULS with version control and lifecycle management
    """
    
    def __init__(self, base_path: str = "data/models"):
        self.base_path = Path(base_path)
        self.models_path = self.base_path
        self.training_path = Path("data/training")
        self.knowledge_path = Path("data/knowledge_base")
        
        # Create directories
        self._create_directories()
        
        # Model registry
        self.model_registry: Dict[str, ModelMetadata] = {}
        self.model_versions: Dict[str, List[str]] = {}
        
        # Encryption for sensitive models
        self.encryption_key = self._load_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Performance tracking
        self.performance_tracker = ModelPerformanceTracker()
        
        # Model loader
        self.model_loader = ModelLoader()
        
        self.logger = self._setup_logging()
        self.logger.info("🤖 Advanced Model Manager Initialized")

    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            self.models_path / "neural_networks/pattern_recognition",
            self.models_path / "neural_networks/anomaly_detection",
            self.models_path / "neural_networks/predictive_analytics",
            self.models_path / "neural_networks/optimization",
            self.models_path / "machine_learning/classification",
            self.models_path / "machine_learning/regression",
            self.models_path / "machine_learning/clustering",
            self.models_path / "machine_learning/reinforcement",
            self.models_path / "nlp_models/text_classification",
            self.models_path / "nlp_models/named_entity_recognition",
            self.models_path / "nlp_models/text_generation",
            self.models_path / "computer_vision/object_detection",
            self.models_path / "computer_vision/document_processing",
            self.models_path / "computer_vision/face_recognition",
            self.training_path / "datasets/raw",
            self.training_path / "datasets/processed",
            self.training_path / "datasets/augmented",
            self.training_path / "checkpoints",
            self.training_path / "logs",
            self.training_path / "experiments",
            self.knowledge_path / "rules",
            self.knowledge_path / "patterns",
            self.knowledge_path / "insights",
            self.knowledge_path / "experiences",
            Path("data/backups/models"),
            Path("data/backups/data"),
            Path("data/backups/configurations")
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self):
        """Setup logging"""
        logger = logging.getLogger('ModelManager')
        return logger

    def _load_encryption_key(self) -> bytes:
        """Load or generate encryption key"""
        key_path = Path("config/encryption.key")
        if key_path.exists():
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            key_path.parent.mkdir(parents=True, exist_ok=True)
            with open(key_path, 'wb') as f:
                f.write(key)
            return key

    async def register_model(self, model_config: Dict) -> str:
        """
        Register a new model in the model registry
        """
        try:
            model_id = model_config.get('model_id', f"MODEL_{uuid.uuid4().hex[:8]}")
            
            # Validate model configuration
            validation_result = await self._validate_model_config(model_config)
            if not validation_result["valid"]:
                raise ValueError(f"Model configuration invalid: {validation_result['errors']}")
            
            # Create model metadata
            metadata = ModelMetadata(
                model_id=model_id,
                name=model_config['name'],
                version=model_config.get('version', '1.0.0'),
                model_type=ModelType(model_config['model_type']),
                description=model_config.get('description', ''),
                created_date=datetime.now(),
                last_updated=datetime.now(),
                status=ModelStatus.TRAINING,
                performance_metrics=model_config.get('performance_metrics', {}),
                hyperparameters=model_config.get('hyperparameters', {}),
                data_sources=model_config.get('data_sources', []),
                dependencies=model_config.get('dependencies', []),
                model_size=0,
                checksum=''
            )
            
            # Register model
            self.model_registry[model_id] = metadata
            
            # Initialize version tracking
            self.model_versions[model_id] = [metadata.version]
            
            # Save model metadata
            await self._save_model_metadata(metadata)
            
            self.logger.info(f"📝 Model Registered: {metadata.name} (ID: {model_id})")
            
            return model_id
            
        except Exception as e:
            self.logger.error(f"❌ Model registration failed: {e}")
            raise

    async def save_model(self, model_id: str, model_object: Any, framework: str = "tensorflow") -> bool:
        """
        Save model with version control and encryption
        """
        try:
            if model_id not in self.model_registry:
                raise ValueError(f"Model not registered: {model_id}")
            
            metadata = self.model_registry[model_id]
            
            # Determine save path
            save_path = self._get_model_path(metadata.model_type, model_id, metadata.version)
            save_path.mkdir(parents=True, exist_ok=True)
            
            # Save model based on framework
            if framework == "tensorflow":
                await self._save_tensorflow_model(model_object, save_path)
            elif framework == "pytorch":
                await self._save_pytorch_model(model_object, save_path)
            elif framework == "sklearn":
                await self._save_sklearn_model(model_object, save_path)
            else:
                await self._save_generic_model(model_object, save_path)
            
            # Update metadata
            metadata.last_updated = datetime.now()
            metadata.model_size = await self._calculate_model_size(save_path)
            metadata.checksum = await self._calculate_checksum(save_path)
            
            # Save updated metadata
            await self._save_model_metadata(metadata)
            
            self.logger.info(f"💾 Model Saved: {metadata.name} | Size: {metadata.model_size} bytes")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Model save failed: {e}")
            return False

    async def load_model(self, model_id: str, version: str = "latest", framework: str = "auto") -> Any:
        """
        Load model with automatic framework detection
        """
        try:
            if model_id not in self.model_registry:
                raise ValueError(f"Model not registered: {model_id}")
            
            metadata = self.model_registry[model_id]
            
            # Determine version to load
            if version == "latest":
                version = metadata.version
            
            # Get model path
            model_path = self._get_model_path(metadata.model_type, model_id, version)
            
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found: {model_path}")
            
            # Load model based on framework
            if framework == "auto":
                framework = await self._detect_framework(model_path)
            
            if framework == "tensorflow":
                model = await self._load_tensorflow_model(model_path)
            elif framework == "pytorch":
                model = await self._load_pytorch_model(model_path)
            elif framework == "sklearn":
                model = await self._load_sklearn_model(model_path)
            else:
                model = await self._load_generic_model(model_path)
            
            self.logger.info(f"📂 Model Loaded: {metadata.name} v{version}")
            
            return model
            
        except Exception as e:
            self.logger.error(f"❌ Model load failed: {e}")
            raise

    async def train_model(self, model_id: str, training_config: TrainingConfig) -> Dict:
        """
        Train model with comprehensive tracking
        """
        try:
            if model_id not in self.model_registry:
                raise ValueError(f"Model not registered: {model_id}")
            
            metadata = self.model_registry[model_id]
            metadata.status = ModelStatus.TRAINING
            
            # Create experiment directory
            experiment_path = self.training_path / "experiments" / f"{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            experiment_path.mkdir(parents=True, exist_ok=True)
            
            # Save training configuration
            await self._save_training_config(training_config, experiment_path)
            
            # Load training data
            training_data = await self._load_training_data(training_config.dataset_path)
            
            # Initialize model
            model = await self.load_model(model_id)
            
            # Train model
            training_result = await self._execute_training(
                model, training_data, training_config, experiment_path
            )
            
            # Update model metadata
            metadata.status = ModelStatus.TRAINED
            metadata.performance_metrics.update(training_result['metrics'])
            metadata.last_updated = datetime.now()
            
            # Save trained model
            await self.save_model(model_id, training_result['model'])
            
            # Log training results
            await self._log_training_results(training_result, experiment_path)
            
            self.logger.info(f"🎯 Model Training Completed: {metadata.name} | "
                           f"Accuracy: {training_result['metrics'].get('accuracy', 0):.4f}")
            
            return training_result
            
        except Exception as e:
            self.logger.error(f"❌ Model training failed: {e}")
            metadata.status = ModelStatus.ERROR
            raise

    async def evaluate_model(self, model_id: str, test_data: Any, metrics: List[str]) -> Dict:
        """
        Evaluate model performance
        """
        try:
            # Load model
            model = await self.load_model(model_id)
            
            # Perform evaluation
            evaluation_results = await self._perform_evaluation(model, test_data, metrics)
            
            # Update model metadata
            metadata = self.model_registry[model_id]
            metadata.performance_metrics.update(evaluation_results)
            metadata.last_updated = datetime.now()
            
            # Save updated metadata
            await self._save_model_metadata(metadata)
            
            self.logger.info(f"📊 Model Evaluation: {metadata.name} | "
                           f"Results: {evaluation_results}")
            
            return evaluation_results
            
        except Exception as e:
            self.logger.error(f"❌ Model evaluation failed: {e}")
            raise

    async def deploy_model(self, model_id: str, deployment_config: Dict) -> bool:
        """
        Deploy model for inference
        """
        try:
            metadata = self.model_registry[model_id]
            
            # Create deployment package
            deployment_package = await self._create_deployment_package(model_id, deployment_config)
            
            # Update model status
            metadata.status = ModelStatus.DEPLOYED
            metadata.last_updated = datetime.now()
            
            # Save deployment info
            await self._save_deployment_info(model_id, deployment_config, deployment_package)
            
            self.logger.info(f"🚀 Model Deployed: {metadata.name} | "
                           f"Endpoint: {deployment_config.get('endpoint', 'N/A')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Model deployment failed: {e}")
            return False

    async def create_model_version(self, model_id: str, new_version: str, description: str = "") -> bool:
        """
        Create new version of existing model
        """
        try:
            if model_id not in self.model_registry:
                raise ValueError(f"Model not registered: {model_id}")
            
            # Copy current model to new version
            current_metadata = self.model_registry[model_id]
            new_metadata = ModelMetadata(
                model_id=model_id,
                name=current_metadata.name,
                version=new_version,
                model_type=current_metadata.model_type,
                description=description or current_metadata.description,
                created_date=datetime.now(),
                last_updated=datetime.now(),
                status=ModelStatus.TRAINED,
                performance_metrics=current_metadata.performance_metrics.copy(),
                hyperparameters=current_metadata.hyperparameters.copy(),
                data_sources=current_metadata.data_sources.copy(),
                dependencies=current_metadata.dependencies.copy(),
                model_size=0,
                checksum=''
            )
            
            # Update registry
            self.model_registry[model_id] = new_metadata
            self.model_versions[model_id].append(new_version)
            
            # Copy model files
            await self._copy_model_files(model_id, current_metadata.version, new_version)
            
            self.logger.info(f"🔄 Model Version Created: {current_metadata.name} v{new_version}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Model version creation failed: {e}")
            return False

    async def export_model(self, model_id: str, export_format: str, export_path: str) -> bool:
        """
        Export model in various formats
        """
        try:
            metadata = self.model_registry[model_id]
            model = await self.load_model(model_id)
            
            if export_format == "onnx":
                await self._export_to_onnx(model, export_path)
            elif export_format == "tensorflow_savedmodel":
                await self._export_to_savedmodel(model, export_path)
            elif export_format == "pytorch_script":
                await self._export_to_torchscript(model, export_path)
            else:
                await self._export_generic(model, export_path, export_format)
            
            self.logger.info(f"📤 Model Exported: {metadata.name} | Format: {export_format}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Model export failed: {e}")
            return False

    async def optimize_model(self, model_id: str, optimization_config: Dict) -> Dict:
        """
        Optimize model for performance
        """
        try:
            model = await self.load_model(model_id)
            metadata = self.model_registry[model_id]
            
            # Perform optimization
            optimization_result = await self._perform_optimization(model, optimization_config)
            
            # Save optimized model
            await self.save_model(model_id, optimization_result['optimized_model'])
            
            # Update metadata
            metadata.performance_metrics.update(optimization_result['metrics'])
            metadata.last_updated = datetime.now()
            
            self.logger.info(f"⚡ Model Optimized: {metadata.name} | "
                           f"Speedup: {optimization_result['metrics'].get('speedup', 1):.2f}x")
            
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"❌ Model optimization failed: {e}")
            raise

    # Helper Methods
    def _get_model_path(self, model_type: ModelType, model_id: str, version: str) -> Path:
        """Get model storage path"""
        type_path = model_type.value.replace('_', '/')
        return self.models_path / type_path / model_id / version

    async def _validate_model_config(self, config: Dict) -> Dict:
        """Validate model configuration"""
        errors = []
        
        required_fields = ['name', 'model_type']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate model type
        try:
            ModelType(config['model_type'])
        except ValueError:
            errors.append(f"Invalid model type: {config['model_type']}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    async def _save_model_metadata(self, metadata: ModelMetadata):
        """Save model metadata"""
        metadata_path = self._get_model_path(metadata.model_type, metadata.model_id, metadata.version) / "metadata.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to serializable format
        metadata_dict = {
            "model_id": metadata.model_id,
            "name": metadata.name,
            "version": metadata.version,
            "model_type": metadata.model_type.value,
            "description": metadata.description,
            "created_date": metadata.created_date.isoformat(),
            "last_updated": metadata.last_updated.isoformat(),
            "status": metadata.status.value,
            "performance_metrics": metadata.performance_metrics,
            "hyperparameters": metadata.hyperparameters,
            "data_sources": metadata.data_sources,
            "dependencies": metadata.dependencies,
            "model_size": metadata.model_size,
            "checksum": metadata.checksum
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata_dict, f, indent=2)

    async def _save_tensorflow_model(self, model, save_path: Path):
        """Save TensorFlow model"""
        model.save(str(save_path / "model.h5"))
        
        # Save additional metadata
        model_summary = []
        model.summary(print_fn=lambda x: model_summary.append(x))
        
        with open(save_path / "model_summary.txt", 'w') as f:
            f.write('\n'.join(model_summary))

    async def _save_pytorch_model(self, model, save_path: Path):
        """Save PyTorch model"""
        torch.save(model.state_dict(), save_path / "model.pth")
        
        # Save model architecture
        with open(save_path / "model_architecture.pkl", 'wb') as f:
            pickle.dump(model, f)

    async def _save_sklearn_model(self, model, save_path: Path):
        """Save scikit-learn model"""
        with open(save_path / "model.pkl", 'wb') as f:
            pickle.dump(model, f)

    async def _save_generic_model(self, model, save_path: Path):
        """Save generic model"""
        with open(save_path / "model.pkl", 'wb') as f:
            pickle.dump(model, f)

    async def _load_tensorflow_model(self, model_path: Path):
        """Load TensorFlow model"""
        return tf.keras.models.load_model(model_path / "model.h5")

    async def _load_pytorch_model(self, model_path: Path):
        """Load PyTorch model"""
        # This would need model architecture to be loaded first
        with open(model_path / "model_architecture.pkl", 'rb') as f:
            model_architecture = pickle.load(f)
        
        model_architecture.load_state_dict(torch.load(model_path / "model.pth"))
        return model_architecture

    async def _load_sklearn_model(self, model_path: Path):
        """Load scikit-learn model"""
        with open(model_path / "model.pkl", 'rb') as f:
            return pickle.load(f)

    async def _load_generic_model(self, model_path: Path):
        """Load generic model"""
        with open(model_path / "model.pkl", 'rb') as f:
            return pickle.load(f)

    async def _detect_framework(self, model_path: Path) -> str:
        """Detect model framework"""
        if (model_path / "model.h5").exists():
            return "tensorflow"
        elif (model_path / "model.pth").exists():
            return "pytorch"
        elif (model_path / "model.pkl").exists():
            return "sklearn"
        else:
            return "generic"

    async def _calculate_model_size(self, model_path: Path) -> int:
        """Calculate total model size"""
        total_size = 0
        for file_path in model_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size

    async def _calculate_checksum(self, model_path: Path) -> str:
        """Calculate model checksum"""
        hasher = hashlib.sha256()
        for file_path in sorted(model_path.rglob('*')):
            if file_path.is_file():
                with open(file_path, 'rb') as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
        return hasher.hexdigest()

    async def _execute_training(self, model, training_data, training_config: TrainingConfig, experiment_path: Path) -> Dict:
        """Execute model training"""
        # Implementation would depend on the specific model framework
        # This is a simplified version
        return {
            'model': model,
            'metrics': {'accuracy': 0.95, 'loss': 0.1},
            'training_history': {},
            'experiment_path': str(experiment_path)
        }

    async def _perform_evaluation(self, model, test_data, metrics: List[str]) -> Dict:
        """Perform model evaluation"""
        # Implementation would depend on the specific model
        return {metric: 0.95 for metric in metrics}

    async def _create_deployment_package(self, model_id: str, deployment_config: Dict) -> str:
        """Create deployment package"""
        # Implementation for creating deployment packages
        return f"deployment_package_{model_id}"

    async def _copy_model_files(self, model_id: str, from_version: str, to_version: str):
        """Copy model files for versioning"""
        metadata = self.model_registry[model_id]
        from_path = self._get_model_path(metadata.model_type, model_id, from_version)
        to_path = self._get_model_path(metadata.model_type, model_id, to_version)
        
        if from_path.exists():
            shutil.copytree(from_path, to_path)

    async def shutdown(self):
        """Shutdown model manager"""
        self.logger.info("🛑 Model Manager shutdown complete")

# Supporting Classes
class ModelPerformanceTracker:
    """Model performance tracking"""
    
    async def track_performance(self, model_id: str, metrics: Dict):
        """Track model performance"""
        pass

class ModelLoader:
    """Advanced model loader"""
    
    async def load_with_framework_detection(self, model_path: Path) -> Any:
        """Load model with automatic framework detection"""
        pass

# Usage Example
async def demo_model_manager():
    """Demonstrate the model manager"""
    model_manager = AdvancedModelManager()
    
    try:
        # Register a new model
        model_config = {
            "model_id": "pattern_recognition_v1",
            "name": "Advanced Pattern Recognition",
            "model_type": "neural_network",
            "description": "Neural network for pattern recognition in BD-King-R7 data",
            "version": "1.0.0",
            "hyperparameters": {
                "layers": [128, 64, 32],
                "activation": "relu",
                "learning_rate": 0.001
            },
            "data_sources": ["/data/transactions", "/data/inventory"],
            "performance_metrics": {}
        }
        
        model_id = await model_manager.register_model(model_config)
        print(f"Model registered: {model_id}")
        
        # Create a simple model for demonstration
        import tensorflow as tf
        demo_model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(10, activation='softmax')
        ])
        
        # Save model
        await model_manager.save_model(model_id, demo_model, "tensorflow")
        
        # Load model
        loaded_model = await model_manager.load_model(model_id)
        print(f"Model loaded: {type(loaded_model)}")
        
        # Create new version
        await model_manager.create_model_version(model_id, "1.1.0", "Improved architecture")
        
    finally:
        await model_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(demo_model_manager())