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
                await self._save_sklearn