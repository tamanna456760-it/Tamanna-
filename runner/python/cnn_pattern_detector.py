"""
CNN Pattern Detector for TI-PULS
Advanced convolutional neural networks for pattern recognition in BD-King-R7 data
"""

from typing import Dict, List

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

from ..common.base_neural_network import BaseNeuralNetwork


class CNNPatternDetector(BaseNeuralNetwork):
    """
    Advanced CNN for pattern recognition in multi-dimensional data
    """

    def __init__(self, config: Dict = None):
        if config is None:
            config = self._load_default_config()

        super().__init__(config, "CNNPatternDetector")

        # CNN specific attributes
        self.input_shape = tuple(self.config["architecture"]["input_shape"])
        self.num_classes = self.config["architecture"]["num_classes"]

        self.logger.info(
            f"🔄 CNN Pattern Detector initialized with input shape {self.input_shape}"
        )

    def _load_default_config(self) -> Dict:
        """Load default CNN configuration"""
        return {
            "architecture": {
                "input_shape": [100, 100, 3],
                "num_classes": 10,
                "conv_layers": [
                    {"filters": 32, "kernel_size": 3, "activation": "relu"},
                    {"filters": 64, "kernel_size": 3, "activation": "relu"},
                    {"filters": 128, "kernel_size": 3, "activation": "relu"},
                ],
                "dense_layers": [512, 256, 128],
                "dropout_rate": 0.5,
                "batch_normalization": True,
            },
            "training": {
                "batch_size": 32,
                "epochs": 50,
                "learning_rate": 0.001,
                "optimizer": "adam",
                "loss": "categorical_crossentropy",
                "metrics": ["accuracy", "precision", "recall"],
            },
        }

    def build_model(self) -> tf.keras.Model:
        """Build CNN architecture"""
        try:
            model = models.Sequential()

            # Input layer
            model.add(layers.InputLayer(input_shape=self.input_shape))

            # Convolutional layers
            for i, conv_config in enumerate(self.config["architecture"]["conv_layers"]):
                model.add(
                    layers.Conv2D(
                        filters=conv_config["filters"],
                        kernel_size=conv_config["kernel_size"],
                        activation=conv_config["activation"],
                        padding="same",
                        name=f"conv_{i}",
                    )
                )

                if self.config["architecture"].get("batch_normalization", False):
                    model.add(layers.BatchNormalization(
                        name=f"batch_norm_{i}"))

                model.add(layers.MaxPooling2D(2, name=f"pool_{i}"))

            # Flatten and dense layers
            model.add(layers.Flatten(name="flatten"))

            for i, units in enumerate(self.config["architecture"]["dense_layers"]):
                model.add(layers.Dense(
                    units, activation="relu", name=f"dense_{i}"))

                if self.config["architecture"].get("dropout_rate", 0) > 0:
                    model.add(
                        layers.Dropout(
                            self.config["architecture"]["dropout_rate"],
                            name=f"dropout_{i}",
                        )
                    )

            # Output layer
            model.add(
                layers.Dense(self.num_classes,
                             activation="softmax", name="output")
            )

            self.logger.info("✅ CNN model built successfully")
            return model

        except Exception as e:
            self.logger.error(f"❌ CNN model build failed: {e}")
            raise

    def compile_model(
        self, optimizer: str = "adam", loss: str = None, metrics: List[str] = None
    ):
        """Compile the CNN model"""
        try:
            if loss is None:
                loss = self.config["training"]["loss"]

            if metrics is None:
                metrics = self.config["training"]["metrics"]

            learning_rate = self.config["training"].get("learning_rate", 0.001)

            if optimizer == "adam":
                opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)
            elif optimizer == "rmsprop":
                opt = tf.keras.optimizers.RMSprop(learning_rate=learning_rate)
            else:
                opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)

            self.model.compile(optimizer=opt, loss=loss, metrics=metrics)

            self.logger.info("✅ CNN model compiled successfully")

        except Exception as e:
            self.logger.error(f"❌ CNN model compilation failed: {e}")
            raise

    async def _execute_training(
        self, X_train, y_train, X_val=None, y_val=None, config: Dict = None
    ) -> Dict:
        """Execute CNN training"""
        try:
            if config is None:
                config = self.config["training"]

            callbacks = []

            # Early stopping
            if config.get("early_stopping", True):
                callbacks.append(
                    tf.keras.callbacks.EarlyStopping(
                        patience=config.get("patience", 10), restore_best_weights=True
                    )
                )

            # Model checkpointing
            if config.get("model_checkpoint", True):
                callbacks.append(
                    tf.keras.callbacks.ModelCheckpoint(
                        str(self.model_path / "best_model.h5"),
                        save_best_only=True,
                        monitor="val_loss",
                    )
                )

            # Learning rate scheduler
            if config.get("lr_scheduler", False):
                callbacks.append(
                    tf.keras.callbacks.ReduceLROnPlateau(
                        factor=0.5, patience=5)
                )

            # Train the model
            history = self.model.fit(
                X_train,
                y_train,
                batch_size=config["batch_size"],
                epochs=config["epochs"],
                validation_data=(X_val, y_val) if X_val is not None else None,
                callbacks=callbacks,
                verbose=1,
            )

            training_result = {
                "history": history.history,
                "final_accuracy": history.history["accuracy"][-1],
                "final_loss": history.history["loss"][-1],
                "training_time": len(history.history["loss"])
                * config["batch_size"]
                / len(X_train),
            }

            if X_val is not None:
                training_result.update(
                    {
                        "val_accuracy": history.history["val_accuracy"][-1],
                        "val_loss": history.history["val_loss"][-1],
                    }
                )

            return training_result

        except Exception as e:
            self.logger.error(f"❌ CNN training execution failed: {e}")
            raise

    async def _execute_prediction(self, X) -> np.ndarray:
        """Execute prediction using CNN"""
        try:
            predictions = self.model.predict(X, verbose=0)
            return predictions
        except Exception as e:
            self.logger.error(f"❌ CNN prediction failed: {e}")
            raise

    async def _execute_evaluation(self, X_test, y_test) -> Dict:
        """Evaluate CNN performance"""
        try:
            evaluation = self.model.evaluate(X_test, y_test, verbose=0)

            # Convert to dictionary
            metrics_dict = {}
            for i, metric in enumerate(self.model.metrics_names):
                metrics_dict[metric] = float(evaluation[i])

            # Additional metrics
            predictions = await self._execute_prediction(X_test)
            predicted_classes = np.argmax(predictions, axis=1)
            true_classes = (
                np.argmax(y_test, axis=1) if len(y_test.shape) > 1 else y_test
            )

            from sklearn.metrics import classification_report, confusion_matrix

            metrics_dict["classification_report"] = classification_report(
                true_classes, predicted_classes, output_dict=True
            )
            metrics_dict["confusion_matrix"] = confusion_matrix(
                true_classes, predicted_classes
            ).tolist()

            return metrics_dict

        except Exception as e:
            self.logger.error(f"❌ CNN evaluation failed: {e}")
            raise

    async def _save_model_weights(self, save_path: Path):
        """Save CNN model weights"""
        try:
            self.model.save(save_path / "model.h5")
        except Exception as e:
            self.logger.error(f"❌ CNN model save failed: {e}")
            raise

    async def _load_model_weights(self, load_path: Path):
        """Load CNN model weights"""
        try:
            self.model = tf.keras.models.load_model(load_path / "model.h5")
        except Exception as e:
            self.logger.error(f"❌ CNN model load failed: {e}")
            raise

    def visualize_feature_maps(self, X_sample, layer_name: str = None):
        """
        Visualize feature maps from convolutional layers
        """
        try:
            if layer_name is None:
                # Use first convolutional layer
                layer_name = "conv_0"

            # Create feature map model
            feature_map_model = tf.keras.models.Model(
                inputs=self.model.input, outputs=self.model.get_layer(
                    layer_name).output
            )

            # Generate feature maps
            feature_maps = feature_map_model.predict(X_sample[np.newaxis, ...])

            return feature_maps

        except Exception as e:
            self.logger.error(f"❌ Feature map visualization failed: {e}")
            return None

    async def detect_patterns(
        self, data: np.ndarray, confidence_threshold: float = 0.8
    ) -> Dict:
        """
        Detect patterns in data with confidence scores
        """
        try:
            predictions = await self._execute_prediction(data)
            results = []

            for i, pred in enumerate(predictions):
                max_confidence = np.max(pred)
                predicted_class = np.argmax(pred)

                if max_confidence >= confidence_threshold:
                    results.append(
                        {
                            "sample_index": i,
                            "predicted_class": int(predicted_class),
                            "confidence": float(max_confidence),
                            "all_probabilities": pred.tolist(),
                        }
                    )

            return {
                "total_samples": len(data),
                "high_confidence_matches": len(results),
                "detections": results,
            }

        except Exception as e:
            self.logger.error(f"❌ Pattern detection failed: {e}")
            raise
