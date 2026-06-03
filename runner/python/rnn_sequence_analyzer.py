"""
RNN Sequence Analyzer for TI-PULS
Advanced recurrent neural networks for sequential pattern recognition
"""

from typing import Dict, List

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

from ..common.base_neural_network import BaseNeuralNetwork


class RNNSequenceAnalyzer(BaseNeuralNetwork):
    """
    Advanced RNN/LSTM for sequential pattern analysis in time-series data
    """

    def __init__(self, config: Dict = None):
        if config is None:
            config = self._load_default_config()

        super().__init__(config, "RNNSequenceAnalyzer")

        # RNN specific attributes
        self.sequence_length = self.config["architecture"]["sequence_length"]
        self.num_features = self.config["architecture"]["num_features"]
        self.num_classes = self.config["architecture"]["num_classes"]

        self.logger.info(
            f"🔄 RNN Sequence Analyzer initialized for {self.num_features} features"
        )

    def _load_default_config(self) -> Dict:
        """Load default RNN configuration"""
        return {
            "architecture": {
                "sequence_length": 50,
                "num_features": 10,
                "num_classes": 5,
                "rnn_type": "lstm",  # lstm, gru, simple_rnn
                "rnn_layers": [
                    {"units": 128, "return_sequences": True},
                    {"units": 64, "return_sequences": False},
                ],
                "dense_layers": [64, 32],
                "dropout_rate": 0.3,
                "recurrent_dropout": 0.2,
                "bidirectional": True,
            },
            "training": {
                "batch_size": 32,
                "epochs": 100,
                "learning_rate": 0.001,
                "optimizer": "adam",
                "loss": "categorical_crossentropy",
                "metrics": ["accuracy"],
            },
        }

    def build_model(self) -> tf.keras.Model:
        """Build RNN architecture"""
        try:
            model = models.Sequential()

            # Input layer
            model.add(
                layers.InputLayer(input_shape=(
                    self.sequence_length, self.num_features))
            )

            # RNN layers
            for i, rnn_config in enumerate(self.config["architecture"]["rnn_layers"]):
                rnn_layer = self._create_rnn_layer(rnn_config, i)

                if self.config["architecture"].get("bidirectional", False):
                    rnn_layer = layers.Bidirectional(rnn_layer)

                model.add(rnn_layer)

                # Add dropout after RNN layer (except last one if return_sequences is False)
                if i < len(
                    self.config["architecture"]["rnn_layers"]
                ) - 1 or rnn_config.get("return_sequences", False):
                    dropout_rate = self.config["architecture"].get(
                        "dropout_rate", 0)
                    if dropout_rate > 0:
                        model.add(layers.Dropout(dropout_rate))

            # Dense layers
            for i, units in enumerate(self.config["architecture"]["dense_layers"]):
                model.add(layers.Dense(
                    units, activation="relu", name=f"dense_{i}"))

                dropout_rate = self.config["architecture"].get(
                    "dropout_rate", 0)
                if dropout_rate > 0:
                    model.add(layers.Dropout(dropout_rate))

            # Output layer
            model.add(
                layers.Dense(self.num_classes,
                             activation="softmax", name="output")
            )

            self.logger.info("✅ RNN model built successfully")
            return model

        except Exception as e:
            self.logger.error(f"❌ RNN model build failed: {e}")
            raise

    def _create_rnn_layer(self, config: Dict, layer_index: int) -> layers.Layer:
        """Create RNN layer based on configuration"""
        rnn_type = self.config["architecture"].get("rnn_type", "lstm")

        if rnn_type == "lstm":
            return layers.LSTM(
                units=config["units"],
                return_sequences=config.get("return_sequences", False),
                dropout=self.config["architecture"].get(
                    "recurrent_dropout", 0),
                recurrent_dropout=self.config["architecture"].get(
                    "recurrent_dropout", 0
                ),
                name=f"lstm_{layer_index}",
            )
        elif rnn_type == "gru":
            return layers.GRU(
                units=config["units"],
                return_sequences=config.get("return_sequences", False),
                dropout=self.config["architecture"].get(
                    "recurrent_dropout", 0),
                recurrent_dropout=self.config["architecture"].get(
                    "recurrent_dropout", 0
                ),
                name=f"gru_{layer_index}",
            )
        else:  # simple_rnn
            return layers.SimpleRNN(
                units=config["units"],
                return_sequences=config.get("return_sequences", False),
                dropout=self.config["architecture"].get(
                    "recurrent_dropout", 0),
                recurrent_dropout=self.config["architecture"].get(
                    "recurrent_dropout", 0
                ),
                name=f"simple_rnn_{layer_index}",
            )

    def compile_model(
        self, optimizer: str = "adam", loss: str = None, metrics: List[str] = None
    ):
        """Compile the RNN model"""
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

            self.logger.info("✅ RNN model compiled successfully")

        except Exception as e:
            self.logger.error(f"❌ RNN model compilation failed: {e}")
            raise

    async def _execute_training(
        self, X_train, y_train, X_val=None, y_val=None, config: Dict = None
    ) -> Dict:
        """Execute RNN training"""
        try:
            if config is None:
                config = self.config["training"]

            callbacks = [
                tf.keras.callbacks.EarlyStopping(
                    patience=config.get("patience", 15), restore_best_weights=True
                ),
                tf.keras.callbacks.ReduceLROnPlateau(
                    factor=0.5, patience=5, min_lr=0.00001
                ),
            ]

            history = self.model.fit(
                X_train,
                y_train,
                batch_size=config["batch_size"],
                epochs=config["epochs"],
                validation_data=(X_val, y_val) if X_val is not None else None,
                callbacks=callbacks,
                verbose=1,
                shuffle=False,  # Important for time series data
            )

            training_result = {
                "history": history.history,
                "final_accuracy": history.history["accuracy"][-1],
                "final_loss": history.history["loss"][-1],
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
            self.logger.error(f"❌ RNN training execution failed: {e}")
            raise

    async def _execute_prediction(self, X) -> np.ndarray:
        """Execute prediction using RNN"""
        try:
            predictions = self.model.predict(X, verbose=0)
            return predictions
        except Exception as e:
            self.logger.error(f"❌ RNN prediction failed: {e}")
            raise

    async def _execute_evaluation(self, X_test, y_test) -> Dict:
        """Evaluate RNN performance"""
        try:
            evaluation = self.model.evaluate(X_test, y_test, verbose=0)

            metrics_dict = {}
            for i, metric in enumerate(self.model.metrics_names):
                metrics_dict[metric] = float(evaluation[i])

            return metrics_dict

        except Exception as e:
            self.logger.error(f"❌ RNN evaluation failed: {e}")
            raise

    async def _save_model_weights(self, save_path: Path):
        """Save RNN model weights"""
        try:
            self.model.save(save_path / "model.h5")
        except Exception as e:
            self.logger.error(f"❌ RNN model save failed: {e}")
            raise

    async def _load_model_weights(self, load_path: Path):
        """Load RNN model weights"""
        try:
            self.model = tf.keras.models.load_model(load_path / "model.h5")
        except Exception as e:
            self.logger.error(f"❌ RNN model load failed: {e}")
            raise

    async def analyze_sequences(
        self, sequences: np.ndarray, window_size: int = None
    ) -> Dict:
        """
        Analyze sequences for patterns and trends
        """
        try:
            if window_size is None:
                window_size = self.sequence_length

            predictions = await self._execute_prediction(sequences)

            analysis_results = {
                "sequence_predictions": predictions.tolist(),
                "trend_analysis": await self._analyze_trends(predictions),
                "pattern_confidence": np.mean(np.max(predictions, axis=1)),
                "anomaly_scores": await self._calculate_anomaly_scores(
                    sequences, predictions
                ),
            }

            return analysis_results

        except Exception as e:
            self.logger.error(f"❌ Sequence analysis failed: {e}")
            raise

    async def _analyze_trends(self, predictions: np.ndarray) -> Dict:
        """Analyze prediction trends"""
        try:
            max_probs = np.max(predictions, axis=1)
            predicted_classes = np.argmax(predictions, axis=1)

            return {
                "average_confidence": float(np.mean(max_probs)),
                "confidence_std": float(np.std(max_probs)),
                "class_distribution": np.bincount(predicted_classes).tolist(),
                "trend_stability": float(
                    1 - np.std(max_probs)
                ),  # Higher is more stable
            }
        except Exception as e:
            self.logger.error(f"❌ Trend analysis failed: {e}")
            return {}

    async def _calculate_anomaly_scores(
        self, sequences: np.ndarray, predictions: np.ndarray
    ) -> np.ndarray:
        """Calculate anomaly scores for sequences"""
        try:
            # Simple anomaly detection based on prediction confidence
            max_confidence = np.max(predictions, axis=1)
            anomaly_scores = (
                1 - max_confidence
            )  # Lower confidence = higher anomaly score

            return anomaly_scores.tolist()
        except Exception as e:
            self.logger.error(f"❌ Anomaly score calculation failed: {e}")
            return []
