"""
Autoencoder Anomaly Detector for TI-PULS
Advanced autoencoder models for unsupervised anomaly detection in BD-King-R7 data
"""

import tensorflow as tf
from tensorflow.keras import layers, models, losses
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import logging
from ..common.base_neural_network import BaseNeuralNetwork

class AutoencoderAnomalyDetector(BaseNeuralNetwork):
    """
    Advanced Autoencoder for unsupervised anomaly detection
    Uses reconstruction error to identify anomalies
    """
    
    def __init__(self, config: Dict = None):
        if config is None:
            config = self._load_default_config()
        
        super().__init__(config, "AutoencoderAnomalyDetector")
        
        # Autoencoder specific attributes
        self.input_dim = self.config['architecture']['input_dim']
        self.encoding_dim = self.config['architecture']['encoding_dim']
        self.latent_dim = self.config['architecture']['latent_dim']
        
        # Anomaly detection thresholds
        self.reconstruction_threshold = None
        self.normal_data_mean = None
        self.normal_data_std = None
        
        self.logger.info(f"🔄 Autoencoder Anomaly Detector initialized for {self.input_dim} features")

    def _load_default_config(self) -> Dict:
        """Load default Autoencoder configuration"""
        return {
            "architecture": {
                "input_dim": 100,
                "encoding_dim": 64,
                "latent_dim": 32,
                "encoder_layers": [128, 64],
                "decoder_layers": [64, 128],
                "activation": "relu",
                "output_activation": "sigmoid",
                "dropout_rate": 0.2,
                "batch_normalization": True
            },
            "training": {
                "batch_size": 32,
                "epochs": 100,
                "learning_rate": 0.001,
                "optimizer": "adam",
                "loss": "mse",
                "validation_split": 0.2,
                "early_stopping": True
            },
            "anomaly_detection": {
                "threshold_method": "percentile",  # percentile, std_dev, dynamic
                "threshold_percentile": 95,
                "threshold_std_multiplier": 3.0,
                "min_reconstruction_error": 0.01
            }
        }

    def build_model(self) -> tf.keras.Model:
        """Build Autoencoder architecture"""
        try:
            # Input layer
            input_layer = layers.Input(shape=(self.input_dim,), name='input')
            
            # Encoder
            x = input_layer
            for i, units in enumerate(self.config['architecture']['encoder_layers']):
                x = layers.Dense(units, activation=self.config['architecture']['activation'], 
                               name=f'encoder_dense_{i}')(x)
                
                if self.config['architecture'].get('batch_normalization', False):
                    x = layers.BatchNormalization(name=f'encoder_bn_{i}')(x)
                
                if self.config['architecture'].get('dropout_rate', 0) > 0:
                    x = layers.Dropout(self.config['architecture']['dropout_rate'], 
                                     name=f'encoder_dropout_{i}')(x)
            
            # Latent space
            latent = layers.Dense(self.latent_dim, activation=self.config['architecture']['activation'], 
                                name='latent')(x)
            
            # Decoder
            x = latent
            for i, units in enumerate(self.config['architecture']['decoder_layers']):
                x = layers.Dense(units, activation=self.config['architecture']['activation'], 
                               name=f'decoder_dense_{i}')(x)
                
                if self.config['architecture'].get('batch_normalization', False):
                    x = layers.BatchNormalization(name=f'decoder_bn_{i}')(x)
                
                if self.config['architecture'].get('dropout_rate', 0) > 0:
                    x = layers.Dropout(self.config['architecture']['dropout_rate'], 
                                     name=f'decoder_dropout_{i}')(x)
            
            # Output layer
            output_layer = layers.Dense(self.input_dim, 
                                      activation=self.config['architecture']['output_activation'],
                                      name='output')(x)
            
            # Create models
            autoencoder = models.Model(input_layer, output_layer, name='autoencoder')
            encoder = models.Model(input_layer, latent, name='encoder')
            
            # Decoder model
            latent_input = layers.Input(shape=(self.latent_dim,), name='latent_input')
            decoder_output = autoencoder.layers[-len(self.config['architecture']['decoder_layers'])-1](latent_input)
            for layer in autoencoder.layers[-len(self.config['architecture']['decoder_layers']):]:
                decoder_output = layer(decoder_output)
            decoder = models.Model(latent_input, decoder_output, name='decoder')
            
            self.encoder = encoder
            self.decoder = decoder
            self.logger.info("✅ Autoencoder model built successfully")
            
            return autoencoder
            
        except Exception as e:
            self.logger.error(f"❌ Autoencoder model build failed: {e}")
            raise

    def compile_model(self, optimizer: str = 'adam', loss: str = None, metrics: List[str] = None):
        """Compile the Autoencoder model"""
        try:
            if loss is None:
                loss = self.config['training']['loss']
            
            learning_rate = self.config['training'].get('learning_rate', 0.001)
            
            if optimizer == 'adam':
                opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)
            else:
                opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)
            
            self.model.compile(optimizer=opt, loss=loss)
            
            self.logger.info("✅ Autoencoder model compiled successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Autoencoder model compilation failed: {e}")
            raise

    async def _execute_training(self, X_train, y_train=None, X_val=None, y_val=None, config: Dict = None) -> Dict:
        """Execute Autoencoder training"""
        try:
            if config is None:
                config = self.config['training']
            
            # For autoencoders, input is also the target
            if y_train is None:
                y_train = X_train
            
            if X_val is not None and y_val is None:
                y_val = X_val
            
            callbacks = []
            
            if config.get('early_stopping', True):
                callbacks.append(
                    tf.keras.callbacks.EarlyStopping(
                        patience=config.get('patience', 10),
                        restore_best_weights=True,
                        monitor='val_loss' if X_val is not None else 'loss'
                    )
                )
            
            history = self.model.fit(
                X_train, y_train,
                batch_size=config['batch_size'],
                epochs=config['epochs'],
                validation_data=(X_val, y_val) if X_val is not None else None,
                callbacks=callbacks,
                verbose=1,
                shuffle=True
            )
            
            # Calculate reconstruction threshold on training data
            await self._calculate_reconstruction_threshold(X_train)
            
            training_result = {
                'history': history.history,
                'final_loss': history.history['loss'][-1],
                'reconstruction_threshold': self.reconstruction_threshold,
                'training_time': len(history.history['loss']) * config['batch_size'] / len(X_train)
            }
            
            if X_val is not None:
                training_result['val_loss'] = history.history['val_loss'][-1]
            
            return training_result
            
        except Exception as e:
            self.logger.error(f"❌ Autoencoder training execution failed: {e}")
            raise

    async def _calculate_reconstruction_threshold(self, X_normal: np.ndarray):
        """Calculate reconstruction error threshold from normal data"""
        try:
            # Get reconstructions
            reconstructions = await self._execute_prediction(X_normal)
            
            # Calculate reconstruction errors
            reconstruction_errors = np.mean(np.square(X_normal - reconstructions), axis=1)
            
            # Set threshold based on configuration
            threshold_method = self.config['anomaly_detection']['threshold_method']
            
            if threshold_method == 'percentile':
                percentile = self.config['anomaly_detection']['threshold_percentile']
                self.reconstruction_threshold = np.percentile(reconstruction_errors, percentile)
            
            elif threshold_method == 'std_dev':
                multiplier = self.config['anomaly_detection']['threshold_std_multiplier']
                self.reconstruction_threshold = np.mean(reconstruction_errors) + multiplier * np.std(reconstruction_errors)
            
            else:  # dynamic - will be calculated per batch
                self.reconstruction_threshold = np.mean(reconstruction_errors) + 2 * np.std(reconstruction_errors)
            
            # Store normal data statistics
            self.normal_data_mean = np.mean(reconstruction_errors)
            self.normal_data_std = np.std(reconstruction_errors)
            
            self.logger.info(f"📊 Reconstruction threshold set to: {self.reconstruction_threshold:.6f}")
            
        except Exception as e:
            self.logger.error(f"❌ Reconstruction threshold calculation failed: {e}")
            raise

    async def _execute_prediction(self, X) -> np.ndarray:
        """Execute reconstruction prediction"""
        try:
            reconstructions = self.model.predict(X, verbose=0)
            return reconstructions
        except Exception as e:
            self.logger.error(f"❌ Autoencoder prediction failed: {e}")
            raise

    async def _execute_evaluation(self, X_test, y_test=None) -> Dict:
        """Evaluate Autoencoder performance"""
        try:
            if y_test is None:
                y_test = X_test
            
            loss = self.model.evaluate(X_test, y_test, verbose=0)
            
            # Calculate reconstruction metrics
            reconstructions = await self._execute_prediction(X_test)
            reconstruction_errors = np.mean(np.square(X_test - reconstructions), axis=1)
            
            evaluation_results = {
                'reconstruction_loss': float(loss),
                'mean_reconstruction_error': float(np.mean(reconstruction_errors)),
                'std_reconstruction_error': float(np.std(reconstruction_errors)),
                'max_reconstruction_error': float(np.max(reconstruction_errors)),
                'min_reconstruction_error': float(np.min(reconstruction_errors))
            }
            
            return evaluation_results
            
        except Exception as e:
            self.logger.error(f"❌ Autoencoder evaluation failed: {e}")
            raise

    async def detect_anomalies(self, X: np.ndarray, dynamic_threshold: bool = False) -> Dict:
        """
        Detect anomalies using reconstruction error
        """
        try:
            if self.reconstruction_threshold is None:
                raise ValueError("Model must be trained before anomaly detection")
            
            # Get reconstructions
            reconstructions = await self._execute_prediction(X)
            
            # Calculate reconstruction errors
            reconstruction_errors = np.mean(np.square(X - reconstructions), axis=1)
            
            # Calculate anomaly scores (normalized reconstruction errors)
            anomaly_scores = (reconstruction_errors - self.normal_data_mean) / self.normal_data_std
            
            # Determine threshold
            if dynamic_threshold:
                current_threshold = np.mean(reconstruction_errors) + 2 * np.std(reconstruction_errors)
            else:
                current_threshold = self.reconstruction_threshold
            
            # Identify anomalies
            anomaly_indices = np.where(reconstruction_errors > current_threshold)[0]
            normal_indices = np.where(reconstruction_errors <= current_threshold)[0]
            
            anomaly_analysis = {
                'total_samples': len(X),
                'anomalies_detected': len(anomaly_indices),
                'anomaly_percentage': len(anomaly_indices) / len(X) * 100,
                'threshold_used': current_threshold,
                'reconstruction_errors': reconstruction_errors.tolist(),
                'anomaly_scores': anomaly_scores.tolist(),
                'anomaly_indices': anomaly_indices.tolist(),
                'normal_indices': normal_indices.tolist(),
                'severity_scores': (anomaly_scores / np.max(anomaly_scores)).tolist() if len(anomaly_scores) > 0 else []
            }
            
            self.logger.info(f"🚨 Anomalies detected: {len(anomaly_indices)}/{len(X)} "
                           f"({anomaly_analysis['anomaly_percentage']:.2f}%)")
            
            return anomaly_analysis
            
        except Exception as e:
            self.logger.error(f"❌ Anomaly detection failed: {e}")
            raise

    async def get_latent_representations(self, X: np.ndarray) -> np.ndarray:
        """Get latent space representations"""
        try:
            latent_representations = self.encoder.predict(X, verbose=0)
            return latent_representations
        except Exception as e:
            self.logger.error(f"❌ Latent representation extraction failed: {e}")
            raise

    async def reconstruct_from_latent(self, latent_vectors: np.ndarray) -> np.ndarray:
        """Reconstruct data from latent space"""
        try:
            reconstructions = self.decoder.predict(latent_vectors, verbose=0)
            return reconstructions
        except Exception as e:
            self.logger.error(f"❌ Reconstruction from latent failed: {e}")
            raise

    async def analyze_anomaly_clusters(self, X: np.ndarray, n_clusters: int = 5) -> Dict:
        """Analyze anomaly clusters in latent space"""
        try:
            from sklearn.cluster import KMeans
            from sklearn.manifold import TSNE
            
            # Get latent representations
            latent_vectors = await self.get_latent_representations(X)
            
            # Detect anomalies first
            anomaly_results = await self.detect_anomalies(X)
            anomaly_indices = anomaly_results['anomaly_indices']
            
            if len(anomaly_indices) == 0:
                return {'clusters_found': 0, 'cluster_analysis': []}
            
            # Get latent vectors of anomalies only
            anomaly_latent = latent_vectors[anomaly_indices]
            
            # Perform clustering on anomalies
            kmeans = KMeans(n_clusters=min(n_clusters, len(anomaly_indices)), random_state=42)
            cluster_labels = kmeans.fit_predict(anomaly_latent)
            
            # Dimensionality reduction for visualization
            tsne = TSNE(n_components=2, random_state=42)
            latent_2d = tsne.fit_transform(anomaly_latent)
            
            cluster_analysis = []
            for cluster_id in range(kmeans.n_clusters):
                cluster_indices = np.where(cluster_labels == cluster_id)[0]
                cluster_anomaly_indices = anomaly_indices[cluster_indices]
                
                cluster_analysis.append({
                    'cluster_id': cluster_id,
                    'cluster_size': len(cluster_indices),
                    'anomaly_indices': cluster_anomaly_indices.tolist(),
                    'centroid': kmeans.cluster_centers_[cluster_id].tolist(),
                    'latent_2d_coordinates': latent_2d[cluster_indices].tolist(),
                    'average_anomaly_score': np.mean([anomaly_results['anomaly_scores'][i] for i in cluster_anomaly_indices])
                })
            
            return {
                'clusters_found': kmeans.n_clusters,
                'cluster_analysis': cluster_analysis,
                'total_anomalies': len(anomaly_indices),
                'silhouette_score': float(self._calculate_silhouette_score(anomaly_latent, cluster_labels))
            }
            
        except Exception as e:
            self.logger.error(f"❌ Anomaly cluster analysis failed: {e}")
            return {'clusters_found': 0, 'cluster_analysis': []}

    def _calculate_silhouette_score(self, X: np.ndarray, labels: np.ndarray) -> float:
        """Calculate silhouette score for clustering"""
        try:
            from sklearn.metrics import silhouette_score
            if len(np.unique(labels)) > 1:
                return silhouette_score(X, labels)
            return 0.0
        except:
            return 0.0

    async def _save_model_weights(self, save_path: Path):
        """Save Autoencoder model weights"""
        try:
            self.model.save(save_path / "autoencoder.h5")
            self.encoder.save(save_path / "encoder.h5")
            self.decoder.save(save_path / "decoder.h5")
            
            # Save threshold and statistics
            model_data = {
                'reconstruction_threshold': float(self.reconstruction_threshold) if self.reconstruction_threshold else None,
                'normal_data_mean': float(self.normal_data_mean) if self.normal_data_mean else None,
                'normal_data_std': float(self.normal_data_std) if self.normal_data_std else None,
                'config': self.config
            }
            
            with open(save_path / "anomaly_detector_data.json", 'w') as f:
                import json
                json.dump(model_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ Autoencoder model save failed: {e}")
            raise

    async def _load_model_weights(self, load_path: Path):
        """Load Autoencoder model weights"""
        try:
            self.model = tf.keras.models.load_model(load_path / "autoencoder.h5")
            self.encoder = tf.keras.models.load_model(load_path / "encoder.h5")
            self.decoder = tf.keras.models.load_model(load_path / "decoder.h5")
            
            # Load threshold and statistics
            data_path = load_path / "anomaly_detector_data.json"
            if data_path.exists():
                with open(data_path, 'r') as f:
                    import json
                    model_data = json.load(f)
                    self.reconstruction_threshold = model_data.get('reconstruction_threshold')
                    self.normal_data_mean = model_data.get('normal_data_mean')
                    self.normal_data_std = model_data.get('normal_data_std')
                    
        except Exception as e:
            self.logger.error(f"❌ Autoencoder model load failed: {e}")
            raise