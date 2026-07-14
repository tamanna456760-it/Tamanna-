"""
Neural Network Utilities for TI-PULS
Common utilities and helper functions for neural networks
"""

from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf


class NeuralNetworkUtils:
    """Utility functions for neural network operations"""

    @staticmethod
    def calculate_model_complexity(model: tf.keras.Model) -> Dict:
        """Calculate model complexity metrics"""
        trainable_params = np.sum(
            [tf.keras.backend.count_params(w) for w in model.trainable_weights]
        )
        non_trainable_params = np.sum(
            [tf.keras.backend.count_params(w) for w in model.non_trainable_weights]
        )
        total_params = trainable_params + non_trainable_params

        return {
            "trainable_parameters": int(trainable_params),
            "non_trainable_parameters": int(non_trainable_params),
            "total_parameters": int(total_params),
            "model_depth": len(model.layers),
            "parameter_efficiency": (
                trainable_params / total_params if total_params > 0 else 0
            ),
        }

    @staticmethod
    def visualize_training_history(history: Dict, save_path: Path = None):
        """Visualize training history"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Accuracy plot
        if "accuracy" in history:
            axes[0, 0].plot(history["accuracy"], label="Training Accuracy")
            if "val_accuracy" in history:
                axes[0, 0].plot(history["val_accuracy"], label="Validation Accuracy")
            axes[0, 0].set_title("Model Accuracy")
            axes[0, 0].set_ylabel("Accuracy")
            axes[0, 0].set_xlabel("Epoch")
            axes[0, 0].legend()

        # Loss plot
        if "loss" in history:
            axes[0, 1].plot(history["loss"], label="Training Loss")
            if "val_loss" in history:
                axes[0, 1].plot(history["val_loss"], label="Validation Loss")
            axes[0, 1].set_title("Model Loss")
            axes[0, 1].set_ylabel("Loss")
            axes[0, 1].set_xlabel("Epoch")
            axes[0, 1].legend()

        # Precision plot
        if "precision" in history:
            axes[1, 0].plot(history["precision"], label="Training Precision")
            if "val_precision" in history:
                axes[1, 0].plot(history["val_precision"], label="Validation Precision")
            axes[1, 0].set_title("Model Precision")
            axes[1, 0].set_ylabel("Precision")
            axes[1, 0].set_xlabel("Epoch")
            axes[1, 0].legend()

        # Recall plot
        if "recall" in history:
            axes[1, 1].plot(history["recall"], label="Training Recall")
            if "val_recall" in history:
                axes[1, 1].plot(history["val_recall"], label="Validation Recall")
            axes[1, 1].set_title("Model Recall")
            axes[1, 1].set_ylabel("Recall")
            axes[1, 1].set_xlabel("Epoch")
            axes[1, 1].legend()

        plt.tight_layout()

        if save_path:
            plt.savefig(
                save_path / "training_history.png", dpi=300, bbox_inches="tight"
            )

        plt.close()

    @staticmethod
    def optimize_model_for_inference(model: tf.keras.Model) -> tf.keras.Model:
        """Optimize model for faster inference"""
        # Convert to TensorFlow Lite compatible format
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        tflite_model = converter.convert()

        return tflite_model

    @staticmethod
    def calculate_inference_latency(
        model: tf.keras.Model, input_shape: Tuple, num_runs: int = 100
    ) -> float:
        """Calculate average inference latency"""
        # Create dummy input
        dummy_input = np.random.random((1, *input_shape)).astype(np.float32)

        # Warm-up run
        model.predict(dummy_input, verbose=0)

        # Measure latency
        latencies = []
        for _ in range(num_runs):
            start_time = tf.timestamp()
            model.predict(dummy_input, verbose=0)
            end_time = tf.timestamp()
            latencies.append((end_time - start_time).numpy())

        return float(np.mean(latencies) * 1000)  # Convert to milliseconds


class PatternRecognitionAnalyzer:
    """Advanced analysis for pattern recognition models"""

    @staticmethod
    def analyze_pattern_confidence(
        predictions: np.ndarray, confidence_threshold: float = 0.8
    ) -> Dict:
        """Analyze prediction confidence patterns"""
        max_confidences = np.max(predictions, axis=1)
        predicted_classes = np.argmax(predictions, axis=1)

        high_confidence_indices = np.where(max_confidences >= confidence_threshold)[0]
        low_confidence_indices = np.where(max_confidences < confidence_threshold)[0]

        return {
            "total_predictions": len(predictions),
            "high_confidence_count": len(high_confidence_indices),
            "low_confidence_count": len(low_confidence_indices),
            "average_confidence": float(np.mean(max_confidences)),
            "confidence_std": float(np.std(max_confidences)),
            "high_confidence_classes": np.bincount(
                predicted_classes[high_confidence_indices]
            ).tolist(),
            "low_confidence_classes": np.bincount(
                predicted_classes[low_confidence_indices]
            ).tolist(),
        }

    @staticmethod
    def detect_emerging_patterns(
        historical_predictions: List[np.ndarray],
        current_predictions: np.ndarray,
        change_threshold: float = 0.1,
    ) -> Dict:
        """Detect emerging patterns in prediction distributions"""
        if not historical_predictions:
            return {"emerging_patterns": [], "change_magnitude": 0.0}

        # Calculate historical average
        historical_avg = np.mean(np.array(historical_predictions), axis=0)
        current_avg = np.mean(current_predictions, axis=0)

        # Calculate change
        change = current_avg - historical_avg
        significant_changes = np.where(np.abs(change) > change_threshold)[0]

        emerging_patterns = []
        for class_idx in significant_changes:
            emerging_patterns.append(
                {
                    "class_index": int(class_idx),
                    "change_magnitude": float(change[class_idx]),
                    "direction": (
                        "increasing" if change[class_idx] > 0 else "decreasing"
                    ),
                }
            )

        return {
            "emerging_patterns": emerging_patterns,
            "total_change_magnitude": float(np.sum(np.abs(change))),
            "most_changed_class": (
                int(np.argmax(np.abs(change))) if len(change) > 0 else -1
            ),
        }
