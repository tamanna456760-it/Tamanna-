"""
GAN Anomaly Detector for TI-PULS
Generative Adversarial Networks for advanced anomaly detection
"""

import tensorflow as tf
from tensorflow.keras import layers, models, Model
import numpy as np
from typing import Dict, List, Any, Tuple
import logging
from ..common.base_neural_network import BaseNeuralNetwork

class GANAnomalyDetector(BaseNeuralNetwork):
    """
    GAN-based Anomaly Detector using discriminator confidence scores
    """
    
    def __init__(self, config: Dict = None):
        if config is None:
            config = self._load_default_config()
        
        super().__init__(config, "GANAnomalyDetector")
        
        # GAN components
        self.generator = None
        self.discriminator = None
        self.gan = None
        
        # GAN specific attributes
        self.latent_dim = self.config['architecture']['latent_dim']
        self.input_dim = self.config['architecture']['input_dim']
        
        # Anomaly detection
        self.discriminator_threshold = None
        
        self.logger.info(f"🔄 GAN Anomaly Detector initialized")

    def _load_default_config(self) -> Dict:
        """Load default GAN configuration"""
        return {
            "architecture": {
                "input_dim": 100,
                "latent_dim": 100,
                "generator_layers": [128, 256, 512],
                "discriminator_layers": [512, 256, 128],
                "activation": "leaky_relu",
                "output_activation": "tanh",
                "dropout_rate": 0.3,
                "batch_normalization": True,
                "use_spectral_norm": False
            },
            "training": {
                "batch_size": 32,
                "epochs": 1000,
                "generator_lr": 0.0002,
                "discriminator_lr": 0.0002,
                "discriminator_steps": 1,
                "label_smoothing": True,
                "gradient_penalty": True
            },
            "anomaly_detection": {
                "threshold_percentile": 95,
                "confidence_window": 100,
                "min_confidence": 0.1
            }
        }

    def build_model(self):
        """Build GAN architecture"""
        try:
            # Build generator
            self.generator = self._build_generator()
            
            # Build discriminator
            self.discriminator = self._build_discriminator()
            
            # Build GAN
            self.gan = self._build_gan()
            
            self.logger.info("✅ GAN model built successfully")
            return self.gan
            
        except Exception as e:
            self.logger.error(f"❌ GAN model build failed: {e}")
            raise

    def _build_generator(self) -> Model:
        """Build generator model"""
        noise = layers.Input(shape=(self.latent_dim,))
        
        x = noise
        for i, units in enumerate(self.config['architecture']['generator_layers']):
            x = layers.Dense(units)(x)
            
            if self.config['architecture'].get('batch_normalization', True):
                x = layers.BatchNormalization()(x)
            
            x = layers.LeakyReLU(alpha=0.2)(x)
            
            if self.config['architecture'].get('dropout_rate', 0) > 0:
                x = layers.Dropout(self.config['architecture']['dropout_rate'])(x)
        
        output = layers.Dense(self.input_dim, activation=self.config['architecture']['output_activation'])(x)
        
        return Model(noise, output, name='generator')

    def _build_discriminator(self) -> Model:
        """Build discriminator model"""
        data = layers.Input(shape=(self.input_dim,))
        
        x = data
        for i, units in enumerate(self.config['architecture']['discriminator_layers']):
            x = layers.Dense(units)(x)
            x = layers.LeakyReLU(alpha=0.2)(x)
            
            if self.config['architecture'].get('dropout_rate', 0) > 0:
                x = layers.Dropout(self.config['architecture']['dropout_rate'])(x)
        
        validity = layers.Dense(1, activation='sigmoid')(x)
        
        return Model(data, validity, name='discriminator')

    def _build_gan(self) -> Model:
        """Build combined GAN model"""
        # Make discriminator non-trainable during generator training
        self.discriminator.trainable = False
        
        gan_input = layers.Input(shape=(self.latent_dim,))
        generated_data = self.generator(gan_input)
        gan_output = self.discriminator(generated_data)
        
        return Model(gan_input, gan_output, name='gan')

    def compile_model(self, optimizer: str = 'adam', loss: str = None, metrics: List[str] = None):
        """Compile GAN models"""
        try:
            # Compile discriminator
            self.discriminator.compile(
                optimizer=tf.keras.optimizers.Adam(
                    learning_rate=self.config['training']['discriminator_lr'],
                    beta_1=0.5
                ),
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            # Compile GAN
            self.gan.compile(
                optimizer=tf.keras.optimizers.Adam(
                    learning_rate=self.config['training']['generator_lr'],
                    beta_1=0.5
                ),
                loss='binary_crossentropy'
            )
            
            self.logger.info("✅ GAN models compiled successfully")
            
        except Exception as e:
            self.logger.error(f"❌ GAN model compilation failed: {e}")
            raise

    async def _execute_training(self, X_train, y_train=None, X_val=None, y_val=None, config: Dict = None) -> Dict:
        """Execute GAN training"""
        try:
            if config is None:
                config = self.config['training']
            
            # Adversarial ground truths
            valid = np.ones((config['batch_size'], 1))
            fake = np.zeros((config['batch_size'], 1))
            
            # Label smoothing
            if config.get('label_smoothing', False):
                valid = valid * 0.9 + 0.05
                fake = fake * 0.9 + 0.05
            
            history = {
                'd_loss': [], 'g_loss': [], 'd_acc': [], 'g_acc': []
            }
            
            for epoch in range(config['epochs']):
                # Train discriminator
                d_losses = []
                d_accs = []
                
                for _ in range(config['discriminator_steps']):
                    # Select random real samples
                    idx = np.random.randint(0, X_train.shape[0], config['batch_size'])
                    real_samples = X_train[idx]
                    
                    # Generate fake samples
                    noise = np.random.normal(0, 1, (config['batch_size'], self.latent_dim))
                    fake_samples = self.generator.predict(noise, verbose=0)
                    
                    # Train discriminator
                    d_loss_real = self.discriminator.train_on_batch(real_samples, valid)
                    d_loss_fake = self.discriminator.train_on_batch(fake_samples, fake)
                    d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
                    
                    d_losses.append(d_loss[0])
                    d_accs.append(d_loss[1])
                
                # Train generator
                noise = np.random.normal(0, 1, (config['batch_size'], self.latent_dim))
                g_loss = self.gan.train_on_batch(noise, valid)
                
                # Store history
                history['d_loss'].append(np.mean(d_losses))
                history['g_loss'].append(g_loss)
                history['d_acc'].append(np.mean(d_accs))
                history['g_acc'].append(0.5)  # Placeholder
                
                # Log progress
                if epoch % 100 == 0:
                    self.logger.info(f"🎯 Epoch {epoch}: D Loss: {history['d_loss'][-1]:.4f}, "
                                   f"G Loss: {history['g_loss'][-1]:.4f}, "
                                   f"D Acc: {history['d_acc'][-1]:.4f}")
            
            # Calculate anomaly detection threshold
            await self._calculate_discriminator_threshold(X_train)
            
            return {
                'history': history,
                'final_d_loss': history['d_loss'][-1],
                'final_g_loss': history['g_loss'][-1],
                'final_d_accuracy': history['d_acc'][-1]
            }
            
        except Exception as e:
            self.logger.error(f"❌ GAN training execution failed: {e}")
            raise

    async def _calculate_discriminator_threshold(self, X_normal: np.ndarray):
        """Calculate discriminator confidence threshold"""
        try:
            # Get discriminator predictions on normal data
            normal_predictions = self.discriminator.predict(X_normal, verbose=0)
            normal_confidences = normal_predictions.flatten()
            
            # Set threshold based on percentile
            percentile = self.config['anomaly_detection']['threshold_percentile']
            self.discriminator_threshold = np.percentile(normal_confidences, percentile)
            
            self.logger.info(f"📊 Discriminator threshold set to: {self.discriminator_threshold:.6f}")
            
        except Exception as e:
            self.logger.error(f"❌ Discriminator threshold calculation failed: {e}")
            raise

    async def _execute_prediction(self, X) -> np.ndarray:
        """Execute discriminator prediction"""
        try:
            predictions = self.discriminator.predict(X, verbose=0)
            return predictions
        except Exception as e:
            self.logger.error(f"❌ GAN prediction failed: {e}")
            raise

    async def _execute_evaluation(self, X_test, y_test=None) -> Dict:
        """Evaluate GAN performance"""
        try:
            # Generate samples
            noise = np.random.normal(0, 1, (len(X_test), self.latent_dim))
            generated_samples = self.generator.predict(noise, verbose=0)
            
            # Evaluate discriminator on real and fake data
            real_predictions = await self._execute_prediction(X_test)
            fake_predictions = await self._execute_prediction(generated_samples)
            
            evaluation_results = {
                'real_data_mean_confidence': float(np.mean(real_predictions)),
                'fake_data_mean_confidence': float(np.mean(fake_predictions)),
                'discrimination_accuracy': float(np.mean((real_predictions > 0.5) & (fake_predictions < 0.5))),
                'generator_quality': float(np.mean(fake_predictions)),  # Higher is better generator
                'discriminator_threshold': float(self.discriminator_threshold) if self.discriminator_threshold else None
            }
            
            return evaluation_results
            
        except Exception as e:
            self.logger.error(f"❌ GAN evaluation failed: {e}")
            raise

    async def detect_anomalies(self, X: np.ndarray) -> Dict:
        """
        Detect anomalies using discriminator confidence
        """
        try:
            if self.discriminator_threshold is None:
                raise ValueError("Model must be trained before anomaly detection")
            
            # Get discriminator predictions
            predictions = await self._execute_prediction(X)
            confidences = predictions.flatten()
            
            # Identify anomalies (low discriminator confidence)
            anomaly_indices = np.where(confidences < self.discriminator_threshold)[0]
            normal_indices = np.where(confidences >= self.discriminator_threshold)[0]
            
            # Calculate anomaly scores (inverse of confidence)
            anomaly_scores = 1 - confidences
            
            anomaly_analysis = {
                'total_samples': len(X),
                'anomalies_detected': len(anomaly_indices),
                'anomaly_percentage': len(anomaly_indices) / len(X) * 100,
                'threshold_used': self.discriminator_threshold,
                'discriminator_confidences': confidences.tolist(),
                'anomaly_scores': anomaly_scores.tolist(),
                'anomaly_indices': anomaly_indices.tolist(),
                'normal_indices': normal_indices.tolist(),
                'mean_confidence': float(np.mean(confidences)),
                'confidence_std': float(np.std(confidences))
            }
            
            self.logger.info(f"🚨 GAN Anomalies detected: {len(anomaly_indices)}/{len(X)} "
                           f"({anomaly_analysis['anomaly_percentage']:.2f}%)")
            
            return anomaly_analysis
            
        except Exception as e:
            self.logger.error(f"❌ GAN anomaly detection failed: {e}")
            raise

    async def generate_samples(self, num_samples: int = 100) -> np.ndarray:
        """Generate synthetic samples"""
        try:
            noise = np.random.normal(0, 1, (num_samples, self.latent_dim))
            generated_samples = self.generator.predict(noise, verbose=0)
            return generated_samples
        except Exception as e:
            self.logger.error(f"❌ Sample generation failed: {e}")
            raise

    async def _save_model_weights(self, save_path: Path):
        """Save GAN model weights"""
        try:
            self.generator.save(save_path / "generator.h5")
            self.discriminator.save(save_path / "discriminator.h5")
            self.gan.save(save_path / "gan.h5")
            
            # Save threshold
            model_data = {
                'discriminator_threshold': float(self.discriminator_threshold) if self.discriminator_threshold else None,
                'config': self.config
            }
            
            with open(save_path / "gan_detector_data.json", 'w') as f:
                import json
                json.dump(model_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ GAN model save failed: {e}")
            raise

    async def _load_model_weights(self, load_path: Path):
        """Load GAN model weights"""
        try:
            self.generator = tf.keras.models.load_model(load_path / "generator.h5")
            self.discriminator = tf.keras.models.load_model(load_path / "discriminator.h5")
            self.gan = tf.keras.models.load_model(load_path / "gan.h5")
            
            # Load threshold
            data_path = load_path / "gan_detector_data.json"
            if data_path.exists():
                with open(data_path, 'r') as f:
                    import json
                    model_data = json.load(f)
                    self.discriminator_threshold = model_data.get('discriminator_threshold')
                    
        except Exception as e:
            self.logger.error(f"❌ GAN model load failed: {e}")
            raise