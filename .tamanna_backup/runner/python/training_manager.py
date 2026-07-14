"""
TI-PULS Training Data Manager - Advanced Dataset Management
Manages training datasets, data preprocessing, and augmentation
"""

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class DatasetInfo:
    """Dataset information"""

    dataset_id: str
    name: str
    description: str
    data_type: str
    size: int
    features: List[str]
    target_column: str
    created_date: datetime
    source: str
    preprocessing_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TrainingDataManager:
    """
    Advanced Training Data Manager for TI-PULS
    """

    def __init__(self, base_path: str = "data/training"):
        self.base_path = Path(base_path)
        self.datasets_path = self.base_path / "datasets"
        self.processed_path = self.datasets_path / "processed"
        self.raw_path = self.datasets_path / "raw"
        self.augmented_path = self.datasets_path / "augmented"

        # Dataset registry
        self.dataset_registry: Dict[str, DatasetInfo] = {}

        # Load existing datasets
        self._load_dataset_registry()

        self.logger = logging.getLogger("TrainingDataManager")

    def _load_dataset_registry(self):
        """Load existing dataset registry"""
        registry_file = self.datasets_path / "dataset_registry.json"
        if registry_file.exists():
            with open(registry_file, "r") as f:
                registry_data = json.load(f)
                for dataset_id, dataset_info in registry_data.items():
                    self.dataset_registry[dataset_id] = DatasetInfo(
                        dataset_id=dataset_info["dataset_id"],
                        name=dataset_info["name"],
                        description=dataset_info["description"],
                        data_type=dataset_info["data_type"],
                        size=dataset_info["size"],
                        features=dataset_info["features"],
                        target_column=dataset_info["target_column"],
                        created_date=datetime.fromisoformat(
                            dataset_info["created_date"]
                        ),
                        source=dataset_info["source"],
                        preprocessing_steps=dataset_info.get("preprocessing_steps", []),
                        metadata=dataset_info.get("metadata", {}),
                    )

    async def register_dataset(self, dataset_config: Dict) -> str:
        """
        Register a new dataset
        """
        try:
            dataset_id = dataset_config.get("dataset_id", f"DS_{uuid.uuid4().hex[:8]}")

            dataset_info = DatasetInfo(
                dataset_id=dataset_id,
                name=dataset_config["name"],
                description=dataset_config.get("description", ""),
                data_type=dataset_config["data_type"],
                size=dataset_config.get("size", 0),
                features=dataset_config.get("features", []),
                target_column=dataset_config.get("target_column", ""),
                created_date=datetime.now(),
                source=dataset_config["source"],
                metadata=dataset_config.get("metadata", {}),
            )

            self.dataset_registry[dataset_id] = dataset_info
            await self._save_dataset_registry()

            self.logger.info(
                f"📁 Dataset Registered: {dataset_info.name} (ID: {dataset_id})"
            )

            return dataset_id

        except Exception as e:
            self.logger.error(f"❌ Dataset registration failed: {e}")
            raise

    async def load_dataset(
        self, dataset_id: str, split: str = "all"
    ) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """
        Load dataset with optional train/test split
        """
        try:
            if dataset_id not in self.dataset_registry:
                raise ValueError(f"Dataset not registered: {dataset_id}")

            dataset_info = self.dataset_registry[dataset_id]

            # Look for processed dataset first
            processed_file = self.processed_path / f"{dataset_id}.parquet"
            if processed_file.exists():
                df = pd.read_parquet(processed_file)
            else:
                # Fall back to raw data
                raw_file = self.raw_path / f"{dataset_id}.csv"
                if raw_file.exists():
                    df = pd.read_csv(raw_file)
                else:
                    raise FileNotFoundError(f"Dataset file not found: {dataset_id}")

            # Split data if requested
            if split != "all" and dataset_info.target_column:
                X = df.drop(columns=[dataset_info.target_column])
                y = df[dataset_info.target_column]

                if split == "train":
                    return X.iloc[: int(0.8 * len(X))], y.iloc[: int(0.8 * len(y))]
                elif split == "test":
                    return X.iloc[int(0.8 * len(X)) :], y.iloc[int(0.8 * len(y)) :]
                else:
                    return X, y
            else:
                return df, None

        except Exception as e:
            self.logger.error(f"❌ Dataset loading failed: {e}")
            raise

    async def preprocess_dataset(
        self, dataset_id: str, preprocessing_steps: List[Dict]
    ) -> str:
        """
        Preprocess dataset with specified steps
        """
        try:
            # Load raw data
            df, _ = await self.load_dataset(dataset_id)

            # Apply preprocessing steps
            for step in preprocessing_steps:
                df = await self._apply_preprocessing_step(df, step)

            # Save processed data
            processed_file = self.processed_path / f"{dataset_id}.parquet"
            df.to_parquet(processed_file)

            # Update dataset info
            dataset_info = self.dataset_registry[dataset_id]
            dataset_info.preprocessing_steps.extend(
                [step["name"] for step in preprocessing_steps]
            )
            dataset_info.size = len(df)

            await self._save_dataset_registry()

            self.logger.info(
                f"🔧 Dataset Preprocessed: {dataset_id} | Steps: {len(preprocessing_steps)}"
            )

            return str(processed_file)

        except Exception as e:
            self.logger.error(f"❌ Dataset preprocessing failed: {e}")
            raise

    async def _apply_preprocessing_step(
        self, df: pd.DataFrame, step: Dict
    ) -> pd.DataFrame:
        """Apply a single preprocessing step"""
        step_name = step["name"]

        if step_name == "handle_missing_values":
            return self._handle_missing_values(df, step.get("strategy", "mean"))
        elif step_name == "normalize":
            return self._normalize_data(df, step.get("columns", []))
        elif step_name == "encode_categorical":
            return self._encode_categorical(df, step.get("columns", []))
        else:
            self.logger.warning(f"Unknown preprocessing step: {step_name}")
            return df

    def _handle_missing_values(self, df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """Handle missing values"""
        if strategy == "mean":
            return df.fillna(df.mean())
        elif strategy == "median":
            return df.fillna(df.median())
        elif strategy == "drop":
            return df.dropna()
        else:
            return df.fillna(0)

    def _normalize_data(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Normalize data"""
        if not columns:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        for col in columns:
            if col in df.columns:
                df[col] = (df[col] - df[col].mean()) / df[col].std()

        return df

    def _encode_categorical(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Encode categorical variables"""
        for col in columns:
            if col in df.columns and df[col].dtype == "object":
                df[col] = pd.Categorical(df[col]).codes
        return df

    async def _save_dataset_registry(self):
        """Save dataset registry"""
        registry_data = {}
        for dataset_id, dataset_info in self.dataset_registry.items():
            registry_data[dataset_id] = {
                "dataset_id": dataset_info.dataset_id,
                "name": dataset_info.name,
                "description": dataset_info.description,
                "data_type": dataset_info.data_type,
                "size": dataset_info.size,
                "features": dataset_info.features,
                "target_column": dataset_info.target_column,
                "created_date": dataset_info.created_date.isoformat(),
                "source": dataset_info.source,
                "preprocessing_steps": dataset_info.preprocessing_steps,
                "metadata": dataset_info.metadata,
            }

        registry_file = self.datasets_path / "dataset_registry.json"
        with open(registry_file, "w") as f:
            json.dump(registry_data, f, indent=2)
