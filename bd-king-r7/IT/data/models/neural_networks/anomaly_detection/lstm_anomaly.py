"""
LSTM Anomaly Detector for TI-PULS
LSTM-based anomaly detection for time series and sequential data
"""

from typing import Dict, List

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

from ..common.base_neural_network import BaseNeuralNetwork


class LSTMAnomalyDetector(BaseNeuralNetwork):
    """
    LSTM-based Anomaly Detector for sequential data
    Uses prediction error for anomaly detection
    """

    def __init__(self, config: Dict = None):
        if config is None:
            config = self._load_default_config()

        super().__init__(config, "LSTMAnomalyDetector")

        # LSTM specific attributes
        self.sequence_length = self.config["architecture"]["sequence_length"]
        self.n_features = self.config["architecture"]["n_features"]
        self.prediction_horizon = self.config["architecture"]["prediction_horizon"]

        # Anomaly detection
        self.prediction_threshold = None
        self.normal_prediction_errors = None

        self.logger.info(
            f"🔄 LSTM Anomaly Detector initialized for {self.n_features} features"
        )

    def _load_default_config(self) -> Dict:
        """Load default LSTM configuration"""
        return {
            "architecture": {
                "sequence_length": 50,
                "n_features": 10,
                "prediction_horizon": 1,
                "lstm_layers": [64, 32],
                "dense_layers": [32, 16],
                "dropout_rate": 0.2,
                "recurrent_dropout": 0.2,
                "bidirectional": True,
                "return_sequences": False,
            },
            "training": {
                "batch_size": 32,
                "epochs": 100,
                "learning_rate": 0.001,
                "optimizer": "adam",
                "loss": "mse",
                "validation_split": 0.2,
                "early_stopping": True,
            },
            "anomaly_detection": {
                "threshold_method": "percentile",
                "threshold_percentile": 95,
                "threshold_std_multiplier": 3.0,
                "min_prediction_error": 0.01,
                "use_rolling_window": True,
                "window_size": 10,
            },
        }

    def build_model(self) -> tf.keras.Model:
        """Build LSTM architecture"""
        try:
            model = models.Sequential()

            # Input layer
            model.add(layers.Input(
                shape=(self.sequence_length, self.n_features)))

            # LSTM layers
            for i, units in enumerate(self.config["architecture"]["lstm_layers"]):
                return_sequences = i < len(
                    self.config["architecture"]["lstm_layers"]
                ) - 1 or self.config["architecture"].get("return_sequences", False)

                lstm_layer = layers.LSTM(
                    units=units,
                    return_sequences=return_sequences,
                    dropout=self.config["architecture"].get("dropout_rate", 0),
                    recurrent_dropout=self.config["architecture"].get(
                        "recurrent_dropout", 0
                    ),
                    name=f"lstm_{i}",
                )

                if self.config["architecture"].get("bidirectional", False):
                    lstm_layer = layers.Bidirectional(lstm_layer)

                model.add(lstm_layer)

            # Dense layers
            for i, units in enumerate(self.config["architecture"]["dense_layers"]):
                model.add(layers.Dense(
                    units, activation="relu", name=f"dense_{i}"))

                if self.config["architecture"].get("dropout_rate", 0) > 0:
                    model.add(
                        layers.Dropout(
                            self.config["architecture"]["dropout_rate"])
                    )

            # Output layer
            model.add(
                layers.Dense(self.n_features *
                             self.prediction_horizon, name="output")
            )

            self.logger.info("✅ LSTM model built successfully")
            return model

        except Exception as e:
            self.logger.error(f"❌ LSTM model build failed: {e}")
            raise

    def compile_model(
        self, optimizer: str = "adam", loss: str = None, metrics: List[str] = None
    ):
        """Compile the LSTM model"""
        try:
            if loss is None:
                loss = self.config["training"]["loss"]

            learning_rate = self.config["training"].get("learning_rate", 0.001)

            if optimizer == "adam":
                opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)
            else:
                opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)

            self.model.compile(optimizer=opt, loss=loss)

            self.logger.info("✅ LSTM model compiled successfully")

        except Exception as e:
            self.logger.error(f"❌ LSTM model compilation failed: {e}")
            raise

    async def _execute_training(
        self, X_train, y_train=None, X_val=None, y_val=None, config: Dict = None
    ) -> Dict:
        """Execute LSTM training"""
        try:
            if config is None:
                config = self.config["training"]

            # For sequence prediction, y_train should be the next step(s)
            if y_train is None:
                y_train = self._create_target_sequences(X_train)

            if X_val is not None and y_val is None:
                y_val = self._create_target_sequences(X_val)

            callbacks = []

            if config.get("early_stopping", True):
                callbacks.append(
                    tf.keras.callbacks.EarlyStopping(
                        patience=config.get("patience", 10),
                        restore_best_weights=True,
                        monitor="val_loss" if X_val is not None else "loss",
                    )
                )

            history = self.model.fit(
                X_train,
                y_train,
                batch_size=config["batch_size"],
                epochs=config["epochs"],
                validation_data=(X_val, y_val) if X_val is not None else None,
                callbacks=callbacks,
                verbose=1,
                shuffle=False,  # Important for time series
            )

            # Calculate prediction threshold on training data
            await self._calculate_prediction_threshold(X_train)

            training_result = {
                "history": history.history,
                "final_loss": history.history["loss"][-1],
                "prediction_threshold": self.prediction_threshold,
                "training_time": len(history.history["loss"])
                * config["batch_size"]
                / len(X_train),
            }

            if X_val is not None:
                training_result["val_loss"] = history.history["val_loss"][-1]

            return training_result

        except Exception as e:
            self.logger.error(f"❌ LSTM training execution failed: {e}")
            raise

    def _create_target_sequences(self, X: np.ndarray) -> np.ndarray:
        """Create target sequences for training"""
        if self.prediction_horizon == 1:
            # Predict next single step
            return X[:, -1, :]  # Last step of each sequence
        else:
            # Predict multiple future steps
            targets = []
            for i in range(len(X)):
                if i + self.prediction_horizon < len(X):
                    target = X[i + 1: i +
                               self.prediction_horizon + 1].flatten()
                    targets.append(target)
            return np.array(targets)

    async def _calculate_prediction_threshold(self, X_normal: np.ndarray):
        """Calculate prediction error threshold"""
        try:
            # Get predictions
            predictions = await self._execute_prediction(X_normal)

            # Calculate prediction errors
            if self.prediction_horizon == 1:
                actual = X_normal[:, -1, :]  # Last step
                prediction_errors = np.mean(
                    np.square(actual - predictions), axis=1)
            else:
                # For multi-step prediction, calculate error for each sequence
                prediction_errors = []
                for i in range(len(X_normal)):
                    if i + self.prediction_horizon < len(X_normal):
                        actual = X_normal[
                            i + 1: i + self.prediction_horizon + 1
                        ].flatten()
                        error = np.mean(np.square(actual - predictions[i]))
                        prediction_errors.append(error)
                prediction_errors = np.array(prediction_errors)

            # Set threshold
            threshold_method = self.config["anomaly_detection"]["threshold_method"]

            if threshold_method == "percentile":
                percentile = self.config["anomaly_detection"]["threshold_percentile"]
                self.prediction_threshold = np.percentile(
                    prediction_errors, percentile)

            elif threshold_method == "std_dev":
                multiplier = self.config["anomaly_detection"][
                    "threshold_std_multiplier"
                ]
                self.prediction_threshold = np.mean(
                    prediction_errors
                ) + multiplier * np.std(prediction_errors)

            # Store normal prediction errors
            self.normal_prediction_errors = prediction_errors

            self.logger.info(
                f"📊 Prediction threshold set to: {self.prediction_threshold:.6f}"
            )

        except Exception as e:
            self.logger.error(
                f"❌ Prediction threshold calculation failed: {e}")
            raise

    async def _execute_prediction(self, X) -> np.ndarray:
        """Execute sequence prediction"""
        try:
            predictions = self.model.predict(X, verbose=0)
            return predictions
        except Exception as e:
            self.logger.error(f"❌ LSTM prediction failed: {e}")
            raise

    async def _execute_evaluation(self, X_test, y_test=None) -> Dict:
        """Evaluate LSTM performance"""
        try:
            if y_test is None:
                y_test = self._create_target_sequences(X_test)

            loss = self.model.evaluate(X_test, y_test, verbose=0)

            # Calculate prediction metrics
            predictions = await self._execute_prediction(X_test)

            if self.prediction_horizon == 1:
                prediction_errors = np.mean(
                    np.square(y_test - predictions), axis=1)
            else:
                prediction_errors = []
                for i in range(len(X_test)):
                    if i + self.prediction_horizon < len(X_test):
                        actual = X_test[
                            i + 1: i + self.prediction_horizon + 1
                        ].flatten()
                        error = np.mean(np.square(actual - predictions[i]))
                        prediction_errors.append(error)
                prediction_errors = np.array(prediction_errors)

            evaluation_results = {
                "prediction_loss": float(loss),
                "mean_prediction_error": float(np.mean(prediction_errors)),
                "std_prediction_error": float(np.std(prediction_errors)),
                "max_prediction_error": float(np.max(prediction_errors)),
                "prediction_threshold": (
                    float(self.prediction_threshold)
                    if self.prediction_threshold
                    else None
                ),
            }

            return evaluation_results

        except Exception as e:
            self.logger.error(f"❌ LSTM evaluation failed: {e}")
            raise

    async def detect_anomalies(
        self, sequences: np.ndarray, use_rolling_window: bool = None
    ) -> Dict:
        """
        Detect anomalies in sequences using prediction error
        """
        try:
            if self.prediction_threshold is None:
                raise ValueError(
                    "Model must be trained before anomaly detection")

            if use_rolling_window is None:
                use_rolling_window = self.config["anomaly_detection"].get(
                    "use_rolling_window", True
                )

            # Get predictions
            predictions = await self._execute_prediction(sequences)

            # Calculate prediction errors
            if self.prediction_horizon == 1:
                actual = sequences[:, -1, :]  # Last step
                prediction_errors = np.mean(
                    np.square(actual - predictions), axis=1)
            else:
                prediction_errors = []
                for i in range(len(sequences)):
                    if i + self.prediction_horizon < len(sequences):
                        actual = sequences[
                            i + 1: i + self.prediction_horizon + 1
                        ].flatten()
                        error = np.mean(np.square(actual - predictions[i]))
                        prediction_errors.append(error)
                prediction_errors = np.array(prediction_errors)

            # Apply rolling window if requested
            if use_rolling_window and len(prediction_errors) > 1:
                window_size = self.config["anomaly_detection"].get(
                    "window_size", 10)
                smoothed_errors = self._apply_rolling_window(
                    prediction_errors, window_size
                )
                errors_to_use = smoothed_errors
            else:
                errors_to_use = prediction_errors

            # Calculate anomaly scores
            if self.normal_prediction_errors is not None:
                anomaly_scores = (
                    errors_to_use - np.mean(self.normal_prediction_errors)
                ) / np.std(self.normal_prediction_errors)
            else:
                anomaly_scores = (
                    errors_to_use / np.max(errors_to_use)
                    if np.max(errors_to_use) > 0
                    else errors_to_use
                )

            # Identify anomalies
            anomaly_indices = np.where(
                errors_to_use > self.prediction_threshold)[0]
            normal_indices = np.where(
                errors_to_use <= self.prediction_threshold)[0]

            anomaly_analysis = {
                "total_sequences": len(sequences),
                "anomalies_detected": len(anomaly_indices),
                "anomaly_percentage": len(anomaly_indices) / len(sequences) * 100,
                "threshold_used": self.prediction_threshold,
                "prediction_errors": prediction_errors.tolist(),
                "anomaly_scores": anomaly_scores.tolist(),
                "anomaly_indices": anomaly_indices.tolist(),
                "normal_indices": normal_indices.tolist(),
                "mean_prediction_error": float(np.mean(prediction_errors)),
                "max_prediction_error": float(np.max(prediction_errors)),
            }

            if use_rolling_window:
                anomaly_analysis["smoothed_errors"] = errors_to_use.tolist()
                anomaly_analysis["window_size"] = window_size

            self.logger.info(
                f"🚨 LSTM Anomalies detected: {len(anomaly_indices)}/{len(sequences)} "
                f"({anomaly_analysis['anomaly_percentage']:.2f}%)"
            )

            return anomaly_analysis

        except Exception as e:
            self.logger.error(f"❌ LSTM anomaly detection failed: {e}")
            raise

    def _apply_rolling_window(self, values: np.ndarray, window_size: int) -> np.ndarray:
        """Apply rolling window smoothing"""
        if len(values) < window_size:
            return values

        smoothed = np.convolve(values, np.ones(
            window_size) / window_size, mode="valid")
        # Pad to maintain original length
        pad_size = len(values) - len(smoothed)
        padded = np.pad(smoothed, (pad_size, 0), mode="edge")

        return padded

    async def forecast_sequences(
        self, initial_sequence: np.ndarray, steps: int = 10
    ) -> np.ndarray:
        """Forecast future sequences"""
        try:
            forecasts = []
            current_sequence = initial_sequence.copy()

            for _ in range(steps):
                # Predict next step
                prediction = await self._execute_prediction(
                    current_sequence[np.newaxis, ...]
                )
                next_step = prediction[0]

                # Reshape if needed
                if len(next_step.shape) == 1:
                    next_step = next_step.reshape(1, -1)

                # Update sequence (remove first, add prediction)
                current_sequence = np.vstack([current_sequence[1:], next_step])
                forecasts.append(next_step.flatten())

            return np.array(forecasts)

        except Exception as e:
            self.logger.error(f"❌ Sequence forecasting failed: {e}")
            raise

    async def _save_model_weights(self, save_path: Path):
        """Save LSTM model weights"""
        try:
            self.model.save(save_path / "lstm_model.h5")

            # Save threshold and statistics
            model_data = {
                "prediction_threshold": (
                    float(self.prediction_threshold)
                    if self.prediction_threshold
                    else None
                ),
                "normal_prediction_errors": (
                    self.normal_prediction_errors.tolist()
                    if self.normal_prediction_errors is not None
                    else None
                ),
                "config": self.config,
            }

            with open(save_path / "lstm_detector_data.json", "w") as f:
                import json

                json.dump(model_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"❌ LSTM model save failed: {e}")
            raise

    async def _load_model_weights(self, load_path: Path):
        """Load LSTM model weights"""
        try:
            self.model = tf.keras.models.load_model(
                load_path / "lstm_model.h5")

            # Load threshold and statistics
            data_path = load_path / "lstm_detector_data.json"
            if data_path.exists():
                with open(data_path, "r") as f:
                    import json

                    model_data = json.load(f)
                    self.prediction_threshold = model_data.get(
                        "prediction_threshold")
                    normal_errors = model_data.get("normal_prediction_errors")
                    if normal_errors:
                        self.normal_prediction_errors = np.array(normal_errors)

        except Exception as e:
            self.logger.error(f"❌ LSTM model load failed: {e}")
            raise
