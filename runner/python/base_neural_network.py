"""
Base Neural Network Class for TI-PULS
Foundation for all neural network implementations
"""

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List


class BaseNeuralNetwork(ABC):
    """
    Abstract base class for all TI-PULS neural networks
    """

    def __init__(self, config: Dict, model_name: str):
        self.config = config
        self.model_name = model_name
        self.logger = logging.getLogger(f"NeuralNetwork.{model_name}")

        # Model components
        self.model = None
        self.optimizer = None
        self.loss_function = None
        self.metrics = {}

        # Training state
        self.is_trained = False
        self.training_history = {}
        self.model_path = Path(f"data/models/neural_networks/{model_name}")

        self.logger.info(f"🧠 Initializing {model_name}")

    @abstractmethod
    def build_model(self) -> Any:
        """Build the neural network architecture"""
        pass

    @abstractmethod
    def compile_model(
        self, optimizer: str = "adam", loss: str = None, metrics: List[str] = None
    ):
        """Compile the model with optimizer and loss"""
        pass

    async def train(self, X_train, y_train, X_val=None, y_val=None, **kwargs) -> Dict:
        """
        Train the neural network
        """
        try:
            self.logger.info(f"🎯 Starting training for {self.model_name}")

            # Build model if not already built
            if self.model is None:
                self.model = self.build_model()
                self.compile_model()

            # Training configuration
            training_config = {**self.config.get("training", {}), **kwargs}

            # Execute training
            training_result = await self._execute_training(
                X_train, y_train, X_val, y_val, training_config
            )

            self.is_trained = True
            self.training_history = training_result

            self.logger.info(f"✅ Training completed for {self.model_name}")

            return training_result

        except Exception as e:
            self.logger.error(f"❌ Training failed for {self.model_name}: {e}")
            raise

    async def predict(self, X) -> Any:
        """
        Make predictions using the trained model
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        try:
            return await self._execute_prediction(X)
        except Exception as e:
            self.logger.error(f"❌ Prediction failed: {e}")
            raise

    async def evaluate(self, X_test, y_test) -> Dict:
        """
        Evaluate model performance
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")

        try:
            evaluation_results = await self._execute_evaluation(X_test, y_test)
            self.logger.info(f"📊 Evaluation results: {evaluation_results}")
            return evaluation_results
        except Exception as e:
            self.logger.error(f"❌ Evaluation failed: {e}")
            raise

    async def save_model(self, version: str = "1.0.0") -> str:
        """
        Save model with versioning
        """
        try:
            save_path = self.model_path / version
            save_path.mkdir(parents=True, exist_ok=True)

            # Save model weights
            await self._save_model_weights(save_path)

            # Save model configuration
            config_path = save_path / "model_config.json"
            with open(config_path, "w") as f:
                json.dump(self.config, f, indent=2)

            # Save training history
            history_path = save_path / "training_history.json"
            with open(history_path, "w") as f:
                json.dump(self.training_history, f, indent=2, default=str)

            self.logger.info(f"💾 Model saved to {save_path}")
            return str(save_path)

        except Exception as e:
            self.logger.error(f"❌ Model save failed: {e}")
            raise

    async def load_model(self, version: str = "1.0.0"):
        """
        Load pre-trained model
        """
        try:
            load_path = self.model_path / version

            if not load_path.exists():
                raise FileNotFoundError(f"Model version {version} not found")

            # Load model configuration
            config_path = load_path / "model_config.json"
            with open(config_path, "r") as f:
                self.config = json.load(f)

            # Build and load model
            self.model = self.build_model()
            await self._load_model_weights(load_path)

            self.is_trained = True
            self.logger.info(f"📂 Model loaded from {load_path}")

        except Exception as e:
            self.logger.error(f"❌ Model load failed: {e}")
            raise

    @abstractmethod
    async def _execute_training(
        self, X_train, y_train, X_val, y_val, config: Dict
    ) -> Dict:
        """Execute the training process"""
        pass

    @abstractmethod
    async def _execute_prediction(self, X) -> Any:
        """Execute prediction"""
        pass

    @abstractmethod
    async def _execute_evaluation(self, X_test, y_test) -> Dict:
        """Execute evaluation"""
        pass

    @abstractmethod
    async def _save_model_weights(self, save_path: Path):
        """Save model weights"""
        pass

    @abstractmethod
    async def _load_model_weights(self, load_path: Path):
        """Load model weights"""
        pass

    def get_model_summary(self) -> str:
        """Get model architecture summary"""
        if self.model is None:
            return "Model not built"

        # Implementation depends on framework
        if hasattr(self.model, "summary"):
            return str(self.model.summary())
        else:
            return str(self.model)

    async def fine_tune(self, X_new, y_new, **kwargs):
        """
        Fine-tune pre-trained model on new data
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before fine-tuning")

        self.logger.info("🔄 Fine-tuning model on new data")

        fine_tune_config = {
            "learning_rate": 0.0001,  # Lower learning rate for fine-tuning
            "epochs": 10,
            **kwargs,
        }

        return await self.train(X_new, y_new, **fine_tune_config)
