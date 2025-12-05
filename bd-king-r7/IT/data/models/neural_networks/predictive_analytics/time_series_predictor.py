"""
Time Series Predictor for TI-PULS
Advanced neural networks for time series forecasting and prediction
"""

import tensorflow as tf
from tensorflow.keras import layers, models, Model
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import logging
from ..common.base_neural_network import BaseNeuralNetwork

class TimeSeriesPredictor(BaseNeuralNetwork):
    """
    Advanced Time Series Predictor using multiple neural network architectures
    Supports LSTM, CNN, Transformer, and hybrid models
    """
    
    def __init__(self, config: Dict = None):
        if config is None:
            config = self._load_default_config()
        
        super().__init__(config, "TimeSeriesPredictor")
        
        # Time series specific attributes
        self.sequence_length = self.config['architecture']['sequence_length']
        self.n_features = self.config['architecture']['n_features']
        self.prediction_horizon = self.config['architecture']['prediction_horizon']
        self.model_type = self.config['architecture']['model_type']
        
        # Statistical properties
        self.data_mean = None
        self.data_std = None
        self.feature_importance = None
        
        self.logger.info(f"🔄 Time Series Predictor initialized with {self.model_type} architecture")

    def _load_default_config(self) -> Dict:
        """Load default Time Series configuration"""
        return {
            "architecture": {
                "model_type": "lstm",  # lstm, cnn, transformer, hybrid
                "sequence_length": 60,
                "n_features": 10,
                "prediction_horizon": 1,
                "lstm_layers": [128, 64],
                "cnn_filters": [64, 128],
                "transformer_heads": 8,
                "transformer_layers": 4,
                "dense_layers": [64, 32],
                "dropout_rate": 0.2,
                "recurrent_dropout": 0.2,
                "bidirectional": True,
                "attention_mechanism": True
            },
            "training": {
                "batch_size": 32,
                "epochs": 100,
                "learning_rate": 0.001,
                "optimizer": "adam",
                "loss": "mse",
                "metrics": ["mae", "mse"],
                "validation_split": 0.2,
                "early_stopping": True,
                "shuffle_sequences": False
            },
            "prediction": {
                "confidence_interval": 0.95,
                "monte_carlo_dropout": True,
                "num_mc_samples": 100,
                "use_quantile_regression": False,
                "multiple_horizons": True
            },
            "feature_engineering": {
                "temporal_features": True,
                "seasonal_features": True,
                "trend_features": True,
                "external_features": True,
                "lag_features": True
            }
        }

    def build_model(self) -> tf.keras.Model:
        """Build time series prediction model based on architecture type"""
        try:
            if self.model_type == "lstm":
                model = self._build_lstm_model()
            elif self.model_type == "cnn":
                model = self._build_cnn_model()
            elif self.model_type == "transformer":
                model = self._build_transformer_model()
            elif self.model_type == "hybrid":
                model = self._build_hybrid_model()
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
            
            self.logger.info(f"✅ {self.model_type.upper()} Time Series model built successfully")
            return model
            
        except Exception as e:
            self.logger.error(f"❌ Time Series model build failed: {e}")
            raise

    def _build_lstm_model(self) -> Model:
        """Build LSTM-based time series model"""
        inputs = layers.Input(shape=(self.sequence_length, self.n_features))
        
        x = inputs
        for i, units in enumerate(self.config['architecture']['lstm_layers']):
            return_sequences = i < len(self.config['architecture']['lstm_layers']) - 1
            
            lstm_layer = layers.LSTM(
                units=units,
                return_sequences=return_sequences,
                dropout=self.config['architecture'].get('dropout_rate', 0),
                recurrent_dropout=self.config['architecture'].get('recurrent_dropout', 0),
                name=f'lstm_{i}'
            )
            
            if self.config['architecture'].get('bidirectional', False):
                lstm_layer = layers.Bidirectional(lstm_layer)
            
            x = lstm_layer(x)
            
            # Add attention mechanism if enabled
            if self.config['architecture'].get('attention_mechanism', False) and return_sequences:
                x = layers.Attention()([x, x])
        
        # Dense layers
        for i, units in enumerate(self.config['architecture']['dense_layers']):
            x = layers.Dense(units, activation='relu', name=f'dense_{i}')(x)
            x = layers.Dropout(self.config['architecture'].get('dropout_rate', 0))(x)
        
        # Output layer
        outputs = layers.Dense(self.prediction_horizon, name='output')(x)
        
        return Model(inputs, outputs, name='lstm_time_series')

    def _build_cnn_model(self) -> Model:
        """Build CNN-based time series model"""
        inputs = layers.Input(shape=(self.sequence_length, self.n_features))
        
        x = inputs
        for i, filters in enumerate(self.config['architecture']['cnn_filters']):
            x = layers.Conv1D(
                filters=filters,
                kernel_size=3,
                activation='relu',
                padding='same',
                name=f'conv1d_{i}'
            )(x)
            x = layers.MaxPooling1D(pool_size=2, name=f'pool_{i}')(x)
            x = layers.Dropout(self.config['architecture'].get('dropout_rate', 0))(x)
        
        x = layers.Flatten()(x)
        
        # Dense layers
        for i, units in enumerate(self.config['architecture']['dense_layers']):
            x = layers.Dense(units, activation='relu', name=f'dense_{i}')(x)
            x = layers.Dropout(self.config['architecture'].get('dropout_rate', 0))(x)
        
        # Output layer
        outputs = layers.Dense(self.prediction_horizon, name='output')(x)
        
        return Model(inputs, outputs, name='cnn_time_series')

    def _build_transformer_model(self) -> Model:
        """Build Transformer-based time series model"""
        def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0):
            # Normalization and Attention
            x = layers.LayerNormalization(epsilon=1e-6)(inputs)
            x = layers.MultiHeadAttention(
                key_dim=head_size, num_heads=num_heads, dropout=dropout
            )(x, x)
            x = layers.Dropout(dropout)(x)
            res = x + inputs

            # Feed Forward Part
            x = layers.LayerNormalization(epsilon=1e-6)(res)
            x = layers.Conv1D(filters=ff_dim, kernel_size=1, activation="relu")(x)
            x = layers.Dropout(dropout)(x)
            x = layers.Conv1D(filters=inputs.shape[-1], kernel_size=1)(x)
            return x + res
        
        inputs = layers.Input(shape=(self.sequence_length, self.n_features))
        x = inputs
        
        # Positional encoding
        positions = tf.range(start=0, limit=self.sequence_length, delta=1)
        positions = tf.cast(positions, tf.float32)
        position_embedding = layers.Embedding(
            input_dim=self.sequence_length, 
            output_dim=self.n_features
        )(positions)
        x = x + position_embedding
        
        # Transformer blocks
        for i in range(self.config['architecture']['transformer_layers']):
            x = transformer_encoder(
                x,
                head_size=self.config['architecture'].get('head_size', 256),
                num_heads=self.config['architecture']['transformer_heads'],
                ff_dim=self.config['architecture'].get('ff_dim', 512),
                dropout=self.config['architecture'].get('dropout_rate', 0)
            )
        
        x = layers.GlobalAveragePooling1D()(x)
        
        # Dense layers
        for i, units in enumerate(self.config['architecture']['dense_layers']):
            x = layers.Dense(units, activation='relu', name=f'dense_{i}')(x)
            x = layers.Dropout(self.config['architecture'].get('dropout_rate', 0))(x)
        
        # Output layer
        outputs = layers.Dense(self.prediction_horizon, name='output')(x)
        
        return Model(inputs, outputs, name='transformer_time_series')

    def _build_hybrid_model(self) -> Model:
        """Build Hybrid CNN-LSTM time series model"""
        inputs = layers.Input(shape=(self.sequence_length, self.n_features))
        
        # CNN branch for feature extraction
        cnn_branch = inputs
        for i, filters in enumerate(self.config['architecture']['cnn_filters']):
            cnn_branch = layers.Conv1D(
                filters=filters,
                kernel_size=3,
                activation='relu',
                padding='same',
                name=f'conv1d_{i}'
            )(cnn_branch)
            cnn_branch = layers.MaxPooling1D(pool_size=2, name=f'pool_{i}')(cnn_branch)
        
        # LSTM branch for temporal patterns
        lstm_branch = inputs
        for i, units in enumerate(self.config['architecture']['lstm_layers']):
            return_sequences = i < len(self.config['architecture']['lstm_layers']) - 1
            
            lstm_layer = layers.LSTM(
                units=units,
                return_sequences=return_sequences,
                dropout=self.config['architecture'].get('dropout_rate', 0),
                recurrent_dropout=self.config['architecture'].get('recurrent_dropout', 0),
                name=f'lstm_{i}'
            )
            
            if self.config['architecture'].get('bidirectional', False):
                lstm_layer = layers.Bidirectional(lstm_layer)
            
            lstm_branch = lstm_layer(lstm_branch)
        
        # Combine branches
        cnn_flat = layers.Flatten()(cnn_branch)
        combined = layers.concatenate([cnn_flat, lstm_branch])
        
        # Dense layers
        x = combined
        for i, units in enumerate(self.config['architecture']['dense_layers']):
            x = layers.Dense(units, activation='relu', name=f'dense_{i}')(x)
            x = layers.Dropout(self.config['architecture'].get('dropout_rate', 0))(x)
        
        # Output layer
        outputs = layers.Dense(self.prediction_horizon, name='output')(x)
        
        return Model(inputs, outputs, name='hybrid_time_series')

    def compile_model(self, optimizer: str = 'adam', loss: str = None, metrics: List[str] = None):
        """Compile the time series model"""
        try:
            if loss is None:
                loss = self.config['training']['loss']
            
            if metrics is None:
                metrics = self.config['training']['metrics']
            
            learning_rate = self.config['training'].get('learning_rate', 0.001)
            
            if optimizer == 'adam':
                opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)
            elif optimizer == 'rmsprop':
                opt = tf.keras.optimizers.RMSprop(learning_rate=learning_rate)
            else:
                opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)
            
            self.model.compile(
                optimizer=opt,
                loss=loss,
                metrics=metrics
            )
            
            self.logger.info("✅ Time Series model compiled successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Time Series model compilation failed: {e}")
            raise

    async def _execute_training(self, X_train, y_train, X_val=None, y_val=None, config: Dict = None) -> Dict:
        """Execute time series training"""
        try:
            if config is None:
                config = self.config['training']
            
            callbacks = []
            
            if config.get('early_stopping', True):
                callbacks.append(
                    tf.keras.callbacks.EarlyStopping(
                        patience=config.get('patience', 15),
                        restore_best_weights=True,
                        monitor='val_loss' if X_val is not None else 'loss'
                    )
                )
            
            # Learning rate scheduler
            callbacks.append(
                tf.keras.callbacks.ReduceLROnPlateau(
                    factor=0.5,
                    patience=5,
                    min_lr=0.00001
                )
            )
            
            history = self.model.fit(
                X_train, y_train,
                batch_size=config['batch_size'],
                epochs=config['epochs'],
                validation_data=(X_val, y_val) if X_val is not None else None,
                callbacks=callbacks,
                verbose=1,
                shuffle=config.get('shuffle_sequences', False)
            )
            
            # Calculate data statistics for normalization
            self.data_mean = np.mean(X_train, axis=(0, 1))
            self.data_std = np.std(X_train, axis=(0, 1))
            
            training_result = {
                'history': history.history,
                'final_loss': history.history['loss'][-1],
                'final_mae': history.history.get('mae', [0])[-1],
                'training_time': len(history.history['loss']) * config['batch_size'] / len(X_train),
                'data_statistics': {
                    'mean': self.data_mean.tolist(),
                    'std': self.data_std.tolist()
                }
            }
            
            if X_val is not None:
                training_result.update({
                    'val_loss': history.history['val_loss'][-1],
                    'val_mae': history.history.get('val_mae', [0])[-1]
                })
            
            return training_result
            
        except Exception as e:
            self.logger.error(f"❌ Time Series training execution failed: {e}")
            raise

    async def _execute_prediction(self, X) -> np.ndarray:
        """Execute time series prediction"""
        try:
            predictions = self.model.predict(X, verbose=0)
            return predictions
        except Exception as e:
            self.logger.error(f"❌ Time Series prediction failed: {e}")
            raise

    async def _execute_evaluation(self, X_test, y_test) -> Dict:
        """Evaluate time series model performance"""
        try:
            evaluation = self.model.evaluate(X_test, y_test, verbose=0)
            
            metrics_dict = {}
            for i, metric in enumerate(self.model.metrics_names):
                metrics_dict[metric] = float(evaluation[i])
            
            # Additional time series specific metrics
            predictions = await self._execute_prediction(X_test)
            
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            metrics_dict.update({
                'mae': float(mean_absolute_error(y_test, predictions)),
                'mse': float(mean_squared_error(y_test, predictions)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, predictions))),
                'r2_score': float(r2_score(y_test, predictions)),
                'mape': float(self._calculate_mape(y_test, predictions))
            })
            
            return metrics_dict
            
        except Exception as e:
            self.logger.error(f"❌ Time Series evaluation failed: {e}")
            raise

    def _calculate_mape(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Mean Absolute Percentage Error"""
        mask = y_true != 0  # Avoid division by zero
        return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

    async def forecast(self, last_sequence: np.ndarray, steps: int = None, 
                      include_confidence: bool = True) -> Dict:
        """
        Generate multi-step forecasts
        """
        try:
            if steps is None:
                steps = self.prediction_horizon
            
            forecasts = []
            confidence_intervals = []
            current_sequence = last_sequence.copy()
            
            for step in range(steps):
                # Predict next step
                prediction = await self._execute_prediction(current_sequence[np.newaxis, ...])
                next_value = prediction[0]
                
                # Calculate confidence interval if requested
                if include_confidence and self.config['prediction'].get('monte_carlo_dropout', False):
                    ci = await self._calculate_confidence_interval(current_sequence)
                    confidence_intervals.append(ci)
                
                forecasts.append(next_value)
                
                # Update sequence for next prediction
                if len(current_sequence.shape) == 2:  # Multi-feature
                    new_row = np.zeros((1, current_sequence.shape[1]))
                    new_row[0, 0] = next_value[0]  # Update first feature, assume others are external
                    current_sequence = np.vstack([current_sequence[1:], new_row])
                else:  # Single feature
                    current_sequence = np.append(current_sequence[1:], next_value)
            
            forecast_result = {
                'forecasts': np.array(forecasts).tolist(),
                'steps': steps,
                'last_sequence': last_sequence.tolist(),
                'model_type': self.model_type
            }
            
            if confidence_intervals:
                forecast_result['confidence_intervals'] = confidence_intervals
            
            return forecast_result
            
        except Exception as e:
            self.logger.error(f"❌ Time Series forecasting failed: {e}")
            raise

    async def _calculate_confidence_interval(self, sequence: np.ndarray, num_samples: int = None) -> Dict:
        """Calculate confidence interval using Monte Carlo dropout"""
        try:
            if num_samples is None:
                num_samples = self.config['prediction'].get('num_mc_samples', 100)
            
            predictions = []
            for _ in range(num_samples):
                # Enable dropout during inference
                pred = self.model(sequence[np.newaxis, ...], training=True)
                predictions.append(pred.numpy().flatten())
            
            predictions = np.array(predictions)
            
            # Calculate statistics
            mean_pred = np.mean(predictions, axis=0)
            std_pred = np.std(predictions, axis=0)
            
            # Calculate confidence intervals
            confidence_level = self.config['prediction'].get('confidence_interval', 0.95)
            z_score = self._get_z_score(confidence_level)
            
            return {
                'mean': mean_pred.tolist(),
                'std': std_pred.tolist(),
                'lower_bound': (mean_pred - z_score * std_pred).tolist(),
                'upper_bound': (mean_pred + z_score * std_pred).tolist(),
                'confidence_level': confidence_level
            }
            
        except Exception as e:
            self.logger.error(f"❌ Confidence interval calculation failed: {e}")
            return {}

    def _get_z_score(self, confidence_level: float) -> float:
        """Get Z-score for given confidence level"""
        from scipy import stats
        return stats.norm.ppf((1 + confidence_level) / 2)

    async def analyze_trends(self, sequences: np.ndarray, window_size: int = 10) -> Dict:
        """Analyze trends and patterns in time series data"""
        try:
            predictions = await self._execute_prediction(sequences)
            
            trend_analysis = {
                'overall_trend': await self._calculate_overall_trend(predictions),
                'seasonality': await self._detect_seasonality(sequences),
                'volatility': await self._calculate_volatility(predictions),
                'turning_points': await self._detect_turning_points(predictions),
                'pattern_analysis': await self._analyze_patterns(sequences, predictions)
            }
            
            return trend_analysis
            
        except Exception as e:
            self.logger.error(f"❌ Trend analysis failed: {e}")
            return {}

    async def _calculate_overall_trend(self, predictions: np.ndarray) -> Dict:
        """Calculate overall trend direction and strength"""
        try:
            if len(predictions.shape) > 1:
                predictions = predictions.flatten()
            
            # Simple linear trend
            x = np.arange(len(predictions))
            slope, intercept = np.polyfit(x, predictions, 1)
            
            # Trend strength (R-squared)
            y_pred = slope * x + intercept
            ss_res = np.sum((predictions - y_pred) ** 2)
            ss_tot = np.sum((predictions - np.mean(predictions)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            return {
                'slope': float(slope),
                'intercept': float(intercept),
                'direction': 'increasing' if slope > 0 else 'decreasing',
                'strength': float(r_squared),
                'magnitude': float(abs(slope))
            }
        except Exception as e:
            self.logger.error(f"❌ Trend calculation failed: {e}")
            return {}

    async def _detect_seasonality(self, sequences: np.ndarray) -> Dict:
        """Detect seasonal patterns in time series"""
        try:
            # Simple seasonality detection using FFT
            from scipy import fftpack
            
            if len(sequences.shape) > 2:
                sequences = sequences[:, :, 0]  # Use first feature
            
            seasonal_analysis = {}
            
            for i, seq in enumerate(sequences):
                # Perform FFT
                fft = fftpack.fft(seq)
                frequencies = fftpack.fftfreq(len(seq))
                
                # Find dominant frequencies (excluding DC component)
                power = np.abs(fft)
                dominant_freq_idx = np.argmax(power[1:]) + 1
                dominant_freq = frequencies[dominant_freq_idx]
                
                seasonal_analysis[f'sequence_{i}'] = {
                    'dominant_frequency': float(dominant_freq),
                    'period': float(1 / abs(dominant_freq)) if dominant_freq != 0 else 0,
                    'seasonal_strength': float(power[dominant_freq_idx] / np.sum(power))
                }
            
            return seasonal_analysis
            
        except Exception as e:
            self.logger.error(f"❌ Seasonality detection failed: {e}")
            return {}

    async def _calculate_volatility(self, predictions: np.ndarray) -> float:
        """Calculate volatility of predictions"""
        try:
            returns = np.diff(predictions.flatten()) / predictions.flatten()[:-1]
            volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
            return float(volatility)
        except:
            return 0.0

    async def _detect_turning_points(self, predictions: np.ndarray) -> List[int]:
        """Detect turning points in time series"""
        try:
            turning_points = []
            pred_flat = predictions.flatten()
            
            for i in range(1, len(pred_flat) - 1):
                # Check for local maxima/minima
                if (pred_flat[i] > pred_flat[i-1] and pred_flat[i] > pred_flat[i+1]) or \
                   (pred_flat[i] < pred_flat[i-1] and pred_flat[i] < pred_flat[i+1]):
                    turning_points.append(i)
            
            return turning_points
        except:
            return []

    async def _analyze_patterns(self, sequences: np.ndarray, predictions: np.ndarray) -> Dict:
        """Analyze patterns in sequences and predictions"""
        try:
            pattern_analysis = {
                'prediction_accuracy': float(np.mean(np.abs(sequences[:, -1, 0] - predictions.flatten()))),
                'pattern_consistency': await self._calculate_pattern_consistency(sequences),
                'outlier_detection': await self._detect_prediction_outliers(predictions)
            }
            return pattern_analysis
        except Exception as e:
            self.logger.error(f"❌ Pattern analysis failed: {e}")
            return {}

    async def _calculate_pattern_consistency(self, sequences: np.ndarray) -> float:
        """Calculate consistency of patterns across sequences"""
        try:
            # Calculate correlation between sequences
            if sequences.shape[0] > 1:
                correlations = []
                for i in range(sequences.shape[0]):
                    for j in range(i+1, sequences.shape[0]):
                        corr = np.corrcoef(sequences[i, :, 0], sequences[j, :, 0])[0, 1]
                        correlations.append(corr)
                return float(np.mean(correlations)) if correlations else 0.0
            return 0.0
        except:
            return 0.0

    async def _detect_prediction_outliers(self, predictions: np.ndarray) -> List[int]:
        """Detect outlier predictions using IQR method"""
        try:
            pred_flat = predictions.flatten()
            Q1 = np.percentile(pred_flat, 25)
            Q3 = np.percentile(pred_flat, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = np.where((pred_flat < lower_bound) | (pred_flat > upper_bound))[0]
            return outliers.tolist()
        except:
            return []

    async def _save_model_weights(self, save_path: Path):
        """Save time series model weights"""
        try:
            self.model.save(save_path / "time_series_model.h5")
            
            # Save additional data
            model_data = {
                'data_mean': self.data_mean.tolist() if self.data_mean is not None else None,
                'data_std': self.data_std.tolist() if self.data_std is not None else None,
                'feature_importance': self.feature_importance.tolist() if self.feature_importance is not None else None,
                'config': self.config
            }
            
            with open(save_path / "time_series_data.json", 'w') as f:
                import json
                json.dump(model_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ Time Series model save failed: {e}")
            raise

    async def _load_model_weights(self, load_path: Path):
        """Load time series model weights"""
        try:
            self.model = tf.keras.models.load_model(load_path / "time_series_model.h5")
            
            # Load additional data
            data_path = load_path / "time_series_data.json"
            if data_path.exists():
                with open(data_path, 'r') as f:
                    import json
                    model_data = json.load(f)
                    self.data_mean = np.array(model_data.get('data_mean')) if model_data.get('data_mean') else None
                    self.data_std = np.array(model_data.get('data_std')) if model_data.get('data_std') else None
                    self.feature_importance = np.array(model_data.get('feature_importance')) if model_data.get('feature_importance') else None
                    
        except Exception as e:
            self.logger.error(f"❌ Time Series model load failed: {e}")
            raise