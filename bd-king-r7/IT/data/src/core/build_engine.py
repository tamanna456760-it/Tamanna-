# src/core/build_engine.py
import os
import asyncio
import logging
import subprocess
from typing import Dict, List
from pathlib import Path

class BuildEngine:
    """Automated build engine with multi-language support"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.build_queue = asyncio.Queue()
        self.active_builds = {}
        self.build_cache = {}
    
    async def start(self):
        """Start the build engine"""
        self.logger.info("Starting Build Engine...")
        
        # Start build processor
        asyncio.create_task(self._process_build_queue())
        
        self.logger.info("Build Engine started successfully")
        return True
    
    async def trigger_build(self, environment: str, language: str = None, 
                          clean: bool = False):
        """Trigger a build for specific environment and language"""
        build_config = {
            'environment': environment,
            'language': language,
            'clean': clean,
            'timestamp': asyncio.get_event_loop().time()
        }
        
        await self.build_queue.put(build_config)
        self.logger.info(f"Build triggered for {environment} ({language})")
    
    async def _process_build_queue(self):
        """Process build queue"""
        while True:
            try:
                build_config = await self.build_queue.get()
                await self._execute_build(build_config)
                self.build_queue.task_done()
            except Exception as e:
                self.logger.error(f"Error processing build queue: {e}")
    
    async def _execute_build(self, build_config: Dict):
        """Execute build process"""
        environment = build_config['environment']
        language = build_config['language']
        
        try:
            self.logger.info(f"Starting build for {environment} ({language})")
            
            # Get build commands for language
            build_commands = self._get_build_commands(language, environment)
            
            # Execute build steps
            for step_name, command in build_commands.items():
                success = await self._execute_build_step(command, environment)
                if not success:
                    raise Exception(f"Build step failed: {step_name}")
            
            # Run tests if configured
            if self.config['build'].get('run_tests', True):
                await self._run_tests(language, environment)
            
            # Handle build artifacts
            await self._handle_artifacts(language, environment)
            
            self.logger.info(f"Build completed successfully for {environment}")
            
            # Trigger deployment if configured
            if self.config['build'].get('auto_deploy', False):
                await self._trigger_deployment(environment)
                
        except Exception as e:
            self.logger.error(f"Build failed for {environment}: {e}")
            await self._handle_build_failure(environment, str(e))
    
    def _get_build_commands(self, language: str, environment: str) -> Dict:
        """Get build commands for specific language and environment"""
        lang_config = self.config['build']['languages'].get(language, {})
        
        commands = {}
        
        # Dependency installation
        if lang_config.get('install_command'):
            commands['install'] = lang_config['install_command']
        elif language == 'python':
            commands['install'] = 'pip install -r requirements.txt'
        elif language == 'javascript':
            commands['install'] = 'npm install'
        
        # Build process
        if lang_config.get('build_command'):
            commands['build'] = lang_config['build_command']
        
        # Environment-specific overrides
        env_commands = lang_config.get('environments', {}).get(environment, {})
        commands.update(env_commands)
        
        return commands
    
    async def _execute_build_step(self, command: str, environment: str) -> bool:
        """Execute individual build step"""
        try:
            # Set environment variables
            env = os.environ.copy()
            env['BUILD_ENV'] = environment
            env['BUILD_TIMESTAMP'] = str(asyncio.get_event_loop().time())
            
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                self.logger.info(f"Build step completed: {command}")
                if stdout:
                    self.logger.debug(f"Build output: {stdout.decode()}")
                return True
            else:
                self.logger.error(f"Build step failed: {command}")
                self.logger.error(f"Error output: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing build step {command}: {e}")
            return False
    
    async def _run_tests(self, language: str, environment: str):
        """Run tests for the built application"""
        try:
            test_command = self.config['build']['languages'][language].get('test_command')
            if test_command:
                self.logger.info(f"Running tests for {language}")
                success = await self._execute_build_step(test_command, environment)
                if not success:
                    raise Exception("Tests failed")
        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
            raise
    
    async def _handle_artifacts(self, language: str, environment: str):
        """Handle build artifacts"""
        try:
            output_dir = self.config['build']['languages'][language].get('output_dir')
            if output_dir and os.path.exists(output_dir):
                # Archive artifacts
                await self._archive_artifacts(output_dir, environment)
                
                # Upload to storage if configured
                if self.config['build'].get('artifact_storage'):
                    await self._upload_artifacts(output_dir, environment)
        except Exception as e:
            self.logger.error(f"Artifact handling failed: {e}")
    
    async def _archive_artifacts(self, output_dir: str, environment: str):
        """Archive build artifacts"""
        import tarfile
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"build_{environment}_{timestamp}.tar.gz"
        
        with tarfile.open(archive_name, "w:gz") as tar:
            tar.add(output_dir, arcname=os.path.basename(output_dir))
        
        self.logger.info(f"Artifacts archived: {archive_name}")
    
    async def _trigger_deployment(self, environment: str):
        """Trigger deployment after successful build"""
        # This would integrate with a deployment system
        self.logger.info(f"Triggering deployment to {environment}")
    
    async def _handle_build_failure(self, environment: str, error: str):
        """Handle build failure"""
        self.logger.error(f"Build failed for {environment}: {error}")
        
        # Send notifications
        await self._send_build_notification(environment, False, error)
    
    async def _send_build_notification(self, environment: str, success: bool, message: str = ""):
        """Send build status notifications"""
        # Implementation for email, Slack, webhook notifications
        pass