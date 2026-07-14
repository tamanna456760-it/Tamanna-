"""
Transformer Pattern Engine for TI-PULS
Advanced transformer models for complex pattern recognition
"""

from typing import Dict, List

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

from ..common.base_neural_network import BaseNeuralNetwork


class TransformerPatternEngine(BaseNeuralNetwork):
    """
    Advanced Transformer model for complex pattern recognition with attention mechanisms
    """

    def __init__(self, config: Dict = None):
        if config is None:
            config = self._load_default_config()

        super().__init__(config, "TransformerPatternEngine")

        # Transformer specific attributes
        self.sequence_length = self.config["architecture"]["sequence_length"]
        self.num_features = self.config["architecture"]["num_features"]
        self.num_classes = self.config["architecture"]["num_classes"]
        self.d_model = self.config["architecture"]["d_model"]

        self.logger.info("🔄 Transformer Pattern Engine initialized")

    def _load_default_config(self) -> Dict:
        """Load default Transformer configuration"""
        return {
            "architecture": {
                "sequence_length": 100,
                "num_features": 20,
                "num_classes": 10,
                "d_model": 128,
                "num_heads": 8,
                "num_layers": 6,
                "dff": 512,
                "dropout_rate": 0.1,
                "positional_encoding": True,
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
        """Build Transformer architecture"""
        try:
            # Input layer
            inputs = layers.Input(shape=(self.sequence_length, self.num_features))

            # Positional encoding
            if self.config["architecture"].get("positional_encoding", True):
                x = self._positional_encoding(inputs)
            else:
                x = inputs

            # Transformer blocks
            for i in range(self.config["architecture"]["num_layers"]):
                x = self._transformer_block(x, i)

            # Global average pooling
            x = layers.GlobalAveragePooling1D()(x)

            # Dropout
            x = layers.Dropout(self.config["architecture"]["dropout_rate"])(x)

            # Output layer
            outputs = layers.Dense(self.num_classes, activation="softmax")(x)

            model = models.Model(inputs=inputs, outputs=outputs)

            self.logger.info("✅ Transformer model built successfully")
            return model

        except Exception as e:
            self.logger.error(f"❌ Transformer model build failed: {e}")
            raise

    def _positional_encoding(self, inputs):
        """Add positional encoding to inputs"""
        batch_size = tf.shape(inputs)[0]
        seq_len = self.sequence_length
        d_model = self.d_model

        # Create positional encoding matrix
        position = tf.range(seq_len, dtype=tf.float32)[:, tf.newaxis]
        div_term = tf.exp(
            tf.range(0, d_model, 2, dtype=tf.float32)
            * -(tf.math.log(10000.0) / d_model)
        )

        pos_encoding = tf.zeros((seq_len, d_model))
        pos_encoding = tf.tensor_scatter_nd_update(
            pos_encoding,
            tf.stack(
                [
                    tf.range(seq_len)[:, tf.newaxis],
                    tf.range(0, d_model, 2)[tf.newaxis, :],
                ],
                axis=1,
            ),
            tf.sin(position * div_term),
        )
        pos_encoding = tf.tensor_scatter_nd_update(
            pos_encoding,
            tf.stack(
                [
                    tf.range(seq_len)[:, tf.newaxis],
                    tf.range(1, d_model, 2)[tf.newaxis, :],
                ],
                axis=1,
            ),
            tf.cos(position * div_term),
        )

        pos_encoding = pos_encoding[tf.newaxis, ...]

        # Project inputs to d_model dimensions
        x = layers.Dense(self.d_model)(inputs)
        x = x + pos_encoding

        return x

    def _transformer_block(self, x, block_index):
        """Single transformer block"""
        # Multi-head attention
        attention_output = layers.MultiHeadAttention(
            num_heads=self.config["architecture"]["num_heads"],
            key_dim=self.d_model // self.config["architecture"]["num_heads"],
            dropout=self.config["architecture"]["dropout_rate"],
        )(x, x)

        # Add & Norm
        x = layers.Add()([x, attention_output])
        x = layers.LayerNormalization()(x)

        # Feed forward
        ffn_output = self._feed_forward_network(x)

        # Add & Norm
        x = layers.Add()([x, ffn_output])
        x = layers.LayerNormalization()(x)

        return x

    def _feed_forward_network(self, x):
        """Feed forward network for transformer"""
        dff = self.config["architecture"]["dff"]

        x = layers.Dense(dff, activation="relu")(x)
        x = layers.Dropout(self.config["architecture"]["dropout_rate"])(x)
        x = layers.Dense(self.d_model)(x)

        return x

    def compile_model(
        self, optimizer: str = "adam", loss: str = None, metrics: List[str] = None
    ):
        """Compile the Transformer model"""
        try:
            if loss is None:
                loss = self.config["training"]["loss"]

            if metrics is None:
                metrics = self.config["training"]["metrics"]

            learning_rate = self.config["training"].get("learning_rate", 0.001)

            # Use Adam with custom learning rate
            optimizer = tf.keras.optimizers.Adam(
                learning_rate=learning_rate, beta_1=0.9, beta_2=0.98, epsilon=1e-9
            )

            self.model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

            self.logger.info("✅ Transformer model compiled successfully")

        except Exception as e:
            self.logger.error(f"❌ Transformer model compilation failed: {e}")
            raise

    async def _execute_training(
        self, X_train, y_train, X_val=None, y_val=None, config: Dict = None
    ) -> Dict:
        """Execute Transformer training"""
        try:
            if config is None:
                config = self.config["training"]

            callbacks = [
                tf.keras.callbacks.EarlyStopping(
                    patience=config.get("patience", 10), restore_best_weights=True
                ),
                tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5),
            ]

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
            self.logger.error(f"❌ Transformer training execution failed: {e}")
            raise

    async def _execute_prediction(self, X) -> np.ndarray:
        """Execute prediction using Transformer"""
        try:
            predictions = self.model.predict(X, verbose=0)
            return predictions
        except Exception as e:
            self.logger.error(f"❌ Transformer prediction failed: {e}")
            raise

    async def _execute_evaluation(self, X_test, y_test) -> Dict:
        """Evaluate Transformer performance"""
        try:
            evaluation = self.model.evaluate(X_test, y_test, verbose=0)

            metrics_dict = {}
            for i, metric in enumerate(self.model.metrics_names):
                metrics_dict[metric] = float(evaluation[i])

            return metrics_dict

        except Exception as e:
            self.logger.error(f"❌ Transformer evaluation failed: {e}")
            raise

    async def _save_model_weights(self, save_path: Path):
        """Save Transformer model weights"""
        try:
            self.model.save(save_path / "model.h5")
        except Exception as e:
            self.logger.error(f"❌ Transformer model save failed: {e}")
            raise

    async def _load_model_weights(self, load_path: Path):
        """Load Transformer model weights"""
        try:
            self.model = tf.keras.models.load_model(load_path / "model.h5")
        except Exception as e:
            self.logger.error(f"❌ Transformer model load failed: {e}")
            raise

    async def analyze_attention_patterns(self, X_sample: np.ndarray) -> Dict:
        """
        Analyze attention patterns in the transformer
        """
        try:
            # Create model that outputs attention weights
            attention_model = models.Model(
                inputs=self.model.input,
                outputs=[
                    layer.output
                    for layer in self.model.layers
                    if isinstance(layer, layers.MultiHeadAttention)
                ],
            )

            # Get attention weights
            attention_weights = attention_model.predict(X_sample[np.newaxis, ...])

            attention_analysis = {
                "num_attention_layers": len(attention_weights),
                "attention_patterns": [],
                "average_attention_scores": [],
            }

            for i, weights in enumerate(attention_weights):
                # weights shape: (batch_size, num_heads, seq_len, seq_len)
                avg_attention = np.mean(
                    weights, axis=(0, 1)
                )  # Average over batch and heads

                attention_analysis["attention_patterns"].append(
                    {
                        "layer": i,
                        "shape": weights.shape,
                        "attention_matrix": avg_attention.tolist(),
                    }
                )

                attention_analysis["average_attention_scores"].append(
                    np.mean(avg_attention).tolist()
                )

            return attention_analysis

        except Exception as e:
            self.logger.error(f"❌ Attention pattern analysis failed: {e}")
            return {}
