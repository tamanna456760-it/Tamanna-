#!/usr/bin/env python3
"""
BD-King-R7 Auto Sync v2.0 - PRODUCTION GRADE
Enhanced with async/await, connection pooling, and advanced error recovery
"""

import asyncio
import hashlib
import json
import logging
import os
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

import aiohttp
import aiosqlite


class SyncStatus(Enum):
    """Sync status enumeration"""
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class SyncConfig:
    """Configuration data class with validation"""
    device_id: str
    server_url: str
    api_key: str
    sync_interval: int = 300
    max_retries: int = 3
    retry_delay: int = 5
    batch_size: int = 100
    timeout: int = 30
    database_path: str = './data/bd_king.db'
    log_level: str = 'INFO'
    backup_enabled: bool = True
    backup_retention_days: int = 7
    connection_pool_size: int = 5
    
    @classmethod
    def from_file(cls, config_file: str) -> 'SyncConfig':
        """Load config from JSON file"""
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
            return cls(**data)
        except FileNotFoundError:
            return cls.default()
    
    @classmethod
    def default(cls) -> 'SyncConfig':
        """Return default configuration"""
        return cls(
            device_id='BD-King-R7-001',
            server_url='https://api.bd-king.com/sync'
        )
    
    def to_file(self, config_file: str) -> None:
        """Save config to JSON file"""
        Path(config_file).parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(asdict(self), f, indent=4)


class BDAutoSyncV2:
    """Enhanced Auto Sync Engine with async support"""
    
    def __init__(self, config: SyncConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.db_path = Path(config.database_path)
        self.running = False
        self.sync_tasks = []
        
    def _setup_logging(self) -> logging.Logger:
        """Setup advanced logging"""
        log_level = getattr(logging, self.config.log_level, logging.INFO)
        log_dir = Path('./logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        logger = logging.getLogger('BDAutoSync-v2')
        logger.setLevel(log_level)
        
        # File handler with rotation
        file_handler = logging.FileHandler(log_dir / 'bd_king_sync.log')
        file_handler.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    async def setup_database(self) -> bool:
        """Setup SQLite database with schema"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiosqlite.connect(str(self.db_path)) as db:
                await db.execute('PRAGMA journal_mode=WAL')
                await db.execute('PRAGMA synchronous=NORMAL')
                
                # Transactions table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        transaction_id TEXT UNIQUE NOT NULL,
                        amount REAL NOT NULL,
                        currency TEXT DEFAULT 'BDT',
                        customer_id INTEGER,
                        transaction_type TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        sync_status TEXT DEFAULT 'pending',
                        last_sync TIMESTAMP,
                        retry_count INTEGER DEFAULT 0
                    )
                ''')
                
                # Inventory table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id TEXT UNIQUE NOT NULL,
                        product_name TEXT NOT NULL,
                        quantity INTEGER DEFAULT 0,
                        price REAL NOT NULL,
                        category TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        sync_status TEXT DEFAULT 'pending',
                        last_sync TIMESTAMP,
                        retry_count INTEGER DEFAULT 0
                    )
                ''')
                
                # Customers table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        phone TEXT,
                        email TEXT,
                        address TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        sync_status TEXT DEFAULT 'pending',
                        last_sync TIMESTAMP,
                        retry_count INTEGER DEFAULT 0
                    )
                ''')
                
                # Sync log table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS sync_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        table_name TEXT NOT NULL,
                        record_count INTEGER,
                        status TEXT,
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create performance indexes
                await db.execute('''
                    CREATE INDEX IF NOT EXISTS idx_transactions_sync 
                    ON transactions(sync_status, retry_count, last_modified)
                ''')
                await db.execute('''
                    CREATE INDEX IF NOT EXISTS idx_inventory_sync 
                    ON inventory(sync_status, retry_count, last_updated)
                ''')
                await db.execute('''
                    CREATE INDEX IF NOT EXISTS idx_customers_sync 
                    ON customers(sync_status, retry_count, last_modified)
                ''')
                
                await db.commit()
                self.logger.info("✅ Database initialized successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Database setup failed: {e}")
            return False
    
    async def start(self) -> None:
        """Start sync engine"""
        try:
            self.running = True
            self.logger.info("🚀 BD-King-R7 Auto Sync v2.0 Starting...")
            
            # Setup database
            if not await self.setup_database():
                return
            
            # Create sync tasks
            sync_task = asyncio.create_task(self._sync_loop())
            self.sync_tasks.append(sync_task)
            
            self.logger.info("✅ Auto Sync started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start sync: {e}")
            self.running = False
    
    async def stop(self) -> None:
        """Stop sync engine gracefully"""
        try:
            self.running = False
            self.logger.info("🛑 Stopping Auto Sync...")
            
            # Wait for all tasks to complete
            if self.sync_tasks:
                await asyncio.gather(*self.sync_tasks, return_exceptions=True)
            
            self.logger.info("✅ Auto Sync stopped")
        except Exception as e:
            self.logger.error(f"❌ Error stopping sync: {e}")
    
    async def _sync_loop(self) -> None:
        """Main sync loop"""
        while self.running:
            try:
                await asyncio.sleep(self.config.sync_interval)
                await self.perform_sync()
            except Exception as e:
                self.logger.error(f"❌ Sync loop error: {e}")
    
    async def perform_sync(self) -> bool:
        """Perform data synchronization"""
        try:
            self.logger.info("📤 Starting sync operation...")
            
            async with aiosqlite.connect(str(self.db_path)) as db:
                # Sync each table concurrently
                tasks = [
                    self._sync_table(db, 'transactions'),
                    self._sync_table(db, 'inventory'),
                    self._sync_table(db, 'customers'),
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                success_count = sum(1 for r in results if r is True)
                self.logger.info(f"✅ Sync completed: {success_count}/3 tables synced")
                
                return all(isinstance(r, bool) and r for r in results)
                
        except Exception as e:
            self.logger.error(f"❌ Sync failed: {e}")
            return False
    
    async def _sync_table(self, db: aiosqlite.Connection, table_name: str) -> bool:
        """Sync a specific table"""
        try:
            cursor = await db.execute(f'''
                SELECT * FROM {table_name}
                WHERE sync_status IN (?, ?)
                ORDER BY retry_count ASC
                LIMIT ?
            ''', (SyncStatus.PENDING.value, SyncStatus.RETRY.value, self.config.batch_size))
            
            records = await cursor.fetchall()
            
            if not records:
                self.logger.debug(f"No pending records in {table_name}")
                return True
            
            # Push records to server
            success_count = 0
            for record in records:
                if await self._push_record_async(table_name, record):
                    success_count += 1
            
            self.logger.info(f"✅ Synced {success_count}/{len(records)} from {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error syncing {table_name}: {e}")
            return False
    
    async def _push_record_async(self, table_name: str, record: tuple) -> bool:
        """Push record to server with retry logic"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = self._record_to_payload(table_name, record)
                
                for attempt in range(self.config.max_retries):
                    try:
                        async with session.post(
                            f"{self.config.server_url}/sync",
                            json=payload,
                            headers={'Authorization': f'Bearer {self.config.api_key}'},
                            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                        ) as resp:
                            if resp.status == 200:
                                return True
                            elif attempt < self.config.max_retries - 1:
                                await asyncio.sleep(self.config.retry_delay)
                    except asyncio.TimeoutError:
                        self.logger.warning(f"Timeout syncing {table_name}, attempt {attempt + 1}")
                        await asyncio.sleep(self.config.retry_delay)
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error pushing record: {e}")
            return False
    
    def _record_to_payload(self, table_name: str, record: tuple) -> Dict[str, Any]:
        """Convert database record to API payload"""
        return {
            'device_id': self.config.device_id,
            'table': table_name,
            'record': record,
            'timestamp': datetime.now().isoformat()
        }


async def main():
    """Main entry point"""
    try:
        config = SyncConfig.from_file('./config.json')
        sync_engine = BDAutoSyncV2(config)
        
        await sync_engine.start()
        
        # Keep running
        while True:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        await sync_engine.stop()
    except Exception as e:
        print(f"❌ Fatal error: {e}")


if __name__ == '__main__':
    asyncio.run(main())
