#!/usr/bin/env python3
"""
Tamanna AI Auto Sync Script
Synchronizes data, models, and configurations automatically
"""

import os
import json
import requests
import schedule
import time
import logging
from datetime import datetime
from pathlib import Path
import hashlib
import hmac
import base64

class TamannaAIAutoSync:
    def __init__(self):
        self.config = {
            'api_key': os.getenv('TAMANNA_API_KEY'),
            'server_url': os.getenv('SERVER_URL', 'https://api.tamanna-ai.com'),
            'device_id': os.getenv('DEVICE_ID', 'tamanna-ai-001'),
            'sync_interval': 360,  # 6 hours
            'data_paths': [
                'models/',
                'config/',
                'data/training/',
                'data/conversations/'
            ]
        }
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('tamanna_sync.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('TamannaAISync')
    
    def generate_signature(self, data: dict) -> str:
        """Generate HMAC signature for secure API communication"""
        message = json.dumps(data, sort_keys=True).encode()
        signature = hmac.new(
            self.config['api_key'].encode(),
            message,
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()
    
    def sync_models(self):
        """Synchronize AI models with central server"""
        try:
            self.logger.info("Starting model synchronization")
            
            # Check for model updates
            models_path = Path('models')
            local_models = {}
            
            if models_path.exists():
                for model_file in models_path.glob('*.h5'):
                    with open(model_file, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    local_models[model_file.name] = {
                        'hash': file_hash,
                        'size': model_file.stat().st_size,
                        'modified': model_file.stat().st_mtime
                    }
            
            # Send model status to server
            payload = {
                'device_id': self.config['device_id'],
                'local_models': local_models,
                'timestamp': datetime.now().isoformat()
            }
            
            signature = self.generate_signature(payload)
            headers = {
                'Authorization': f'Bearer {self.config["api_key"]}',
                'Content-Type': 'application/json',
                'X-Signature': signature
            }
            
            response = requests.post(
                f"{self.config['server_url']}/api/v1/models/sync",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('updates_available'):
                    self.download_model_updates(result['updates'])
                self.logger.info("Model synchronization completed")
            else:
                self.logger.error(f"Model sync failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Model sync error: {e}")
    
    def download_model_updates(self, updates: list):
        """Download model updates from server"""
        for update in updates:
            try:
                model_name = update['name']
                download_url = update['download_url']
                
                self.logger.info(f"Downloading model update: {model_name}")
                
                response = requests.get(download_url, stream=True, timeout=120)
                response.raise_for_status()
                
                models_path = Path('models')
                models_path.mkdir(exist_ok=True)
                
                with open(models_path / model_name, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.logger.info(f"Model {model_name} updated successfully")
                
            except Exception as e:
                self.logger.error(f"Failed to download model {update['name']}: {e}")
    
    def sync_conversation_data(self):
        """Sync conversation data and training examples"""
        try:
            self.logger.info("Syncing conversation data")
            
            # Collect local conversation data
            conversations_path = Path('data/conversations')
            conversation_files = []
            
            if conversations_path.exists():
                for file_path in conversations_path.glob('*.json'):
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    conversation_files.append({
                        'filename': file_path.name,
                        'data': data,
                        'hash': hashlib.md5(json.dumps(data).encode()).hexdigest()
                    })
            
            # Send to server
            payload = {
                'device_id': self.config['device_id'],
                'conversations': conversation_files,
                'timestamp': datetime.now().isoformat()
            }
            
            signature = self.generate_signature(payload)
            headers = {
                'Authorization': f'Bearer {self.config["api_key"]}',
                'Content-Type': 'application/json',
                'X-Signature': signature
            }
            
            response = requests.post(
                f"{self.config['server_url']}/api/v1/conversations/sync",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Download new training data if available
                if result.get('training_data'):
                    self.update_training_data(result['training_data'])
                self.logger.info("Conversation data sync completed")
            else:
                self.logger.error(f"Conversation sync failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Conversation sync error: {e}")
    
    def update_training_data(self, training_data: dict):
        """Update local training data"""
        try:
            training_path = Path('data/training')
            training_path.mkdir(parents=True, exist_ok=True)
            
            for filename, data in training_data.items():
                file_path = training_path / filename
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
            
            self.logger.info("Training data updated successfully")
            
        except Exception as e:
            self.logger.error(f"Training data update error: {e}")
    
    def sync_configurations(self):
        """Sync configuration files"""
        try:
            self.logger.info("Syncing configurations")
            
            config_path = Path('config')
            config_files = {}
            
            if config_path.exists():
                for file_path in config_path.glob('*.json'):
                    with open(file_path, 'r') as f:
                        config_files[file_path.name] = json.load(f)
            
            payload = {
                'device_id': self.config['device_id'],
                'configurations': config_files,
                'timestamp': datetime.now().isoformat()
            }
            
            signature = self.generate_signature(payload)
            headers = {
                'Authorization': f'Bearer {self.config["api_key"]}',
                'Content-Type': 'application/json',
                'X-Signature': signature
            }
            
            response = requests.post(
                f"{self.config['server_url']}/api/v1/config/sync",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('config_updates'):
                    self.apply_config_updates(result['config_updates'])
                self.logger.info("Configuration sync completed")
            else:
                self.logger.error(f"Configuration sync failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Configuration sync error: {e}")
    
    def apply_config_updates(self, config_updates: dict):
        """Apply configuration updates from server"""
        try:
            config_path = Path('config')
            config_path.mkdir(exist_ok=True)
            
            for filename, config_data in config_updates.items():
                file_path = config_path / filename
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
            
            self.logger.info("Configuration updates applied")
            
        except Exception as e:
            self.logger.error(f"Config update error: {e}")
    
    def perform_full_sync(self):
        """Perform full synchronization"""
        self.logger.info("Starting full synchronization")
        
        sync_tasks = [
            self.sync_models,
            self.sync_conversation_data,
            self.sync_configurations
        ]
        
        for task in sync_tasks:
            try:
                task()
            except Exception as e:
                self.logger.error(f"Sync task failed: {e}")
        
        self.logger.info("Full synchronization completed")
    
    def start_auto_sync(self):
        """Start automatic synchronization"""
        self.logger.info("Starting Tamanna AI Auto Sync")
        
        # Schedule sync tasks
        schedule.every(6).hours.do(self.perform_full_sync)
        schedule.every(1).hours.do(self.sync_conversation_data)
        schedule.every(12).hours.do(self.sync_models)
        schedule.every(24).hours.do(self.sync_configurations)
        
        # Run immediately
        self.perform_full_sync()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    """Main function"""
    sync_manager = TamannaAIAutoSync()
    
    try:
        sync_manager.start_auto_sync()
    except KeyboardInterrupt:
        sync_manager.logger.info("Auto sync stopped by user")
    except Exception as e:
        sync_manager.logger.error(f"Auto sync error: {e}")

if __name__ == "__main__":
    main()