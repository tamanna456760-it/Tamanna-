"""
TI-PULS Knowledge Base - Advanced Knowledge Management
Stores and manages learned patterns, rules, and insights
"""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum
import uuid

class KnowledgeType(Enum):
    """Knowledge types"""
    PATTERN = "pattern"
    RULE = "rule"
    INSIGHT = "insight"
    EXPERIENCE = "experience"
    DECISION = "decision"

@dataclass
class KnowledgeUnit:
    """Knowledge unit"""
    knowledge_id: str
    knowledge_type: KnowledgeType
    content: Dict[str, Any]
    confidence: float
    source: str
    created_date: datetime
    last_used: datetime
    usage_count: int
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class KnowledgeBaseManager:
    """
    Advanced Knowledge Base Manager for TI-PULS
    """
    
    def __init__(self, base_path: str = "data/knowledge_base"):
        self.base_path = Path(base_path)
        self.knowledge_store: Dict[str, KnowledgeUnit] = {}
        
        # Create directories
        self._create_directories()
        
        # Load existing knowledge
        self._load_knowledge_base()
        
        self.logger = logging.getLogger('KnowledgeBase')

    def _create_directories(self):
        """Create knowledge base directories"""
        directories = [
            self.base_path / "rules",
            self.base_path / "patterns", 
            self.base_path / "insights",
            self.base_path / "experiences"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_knowledge_base(self):
        """Load existing knowledge base"""
        try:
            for knowledge_file in self.base_path.rglob("*.json"):
                with open(knowledge_file, 'r') as f:
                    knowledge_data = json.load(f)
                    
                    knowledge_unit = KnowledgeUnit(
                        knowledge_id=knowledge_data['knowledge_id'],
                        knowledge_type=KnowledgeType(knowledge_data['knowledge_type']),
                        content=knowledge_data['content'],
                        confidence=knowledge_data['confidence'],
                        source=knowledge_data['source'],
                        created_date=datetime.fromisoformat(knowledge_data['created_date']),
                        last_used=datetime.fromisoformat(knowledge_data['last_used']),
                        usage_count=knowledge_data['usage_count'],
                        tags=knowledge_data.get('tags', []),
                        metadata=knowledge_data.get('metadata', {})
                    )
                    
                    self.knowledge_store[knowledge_unit.knowledge_id] = knowledge_unit
                    
        except Exception as e:
            self.logger.error(f"Error loading knowledge base: {e}")

    async def store_knowledge(self, knowledge_type: KnowledgeType, content: Dict, 
                            confidence: float, source: str, tags: List[str] = None) -> str:
        """
        Store new knowledge in the knowledge base
        """
        try:
            knowledge_id = f"KNOW_{uuid.uuid4().hex[:8]}"
            current_time = datetime.now()
            
            knowledge_unit = KnowledgeUnit(
                knowledge_id=knowledge_id,
                knowledge_type=knowledge_type,
                content=content,
                confidence=confidence,
                source=source,
                created_date=current_time,
                last_used=current_time,
                usage_count=1,
                tags=tags or [],
                metadata={"storage_version": "1.0"}
            )
            
            # Store in memory
            self.knowledge_store[knowledge_id] = knowledge_unit
            
            # Persist to disk
            await self._persist_knowledge(knowledge_unit)
            
            self.logger.info(f"💡 Knowledge Stored: {knowledge_type.value} | ID: {knowledge_id}")
            
            return knowledge_id
            
        except Exception as e:
            self.logger.error(f"❌ Knowledge storage failed: {e}")
            raise

    async def retrieve_knowledge(self, query: Dict, knowledge_type: KnowledgeType = None, 
                               min_confidence: float = 0.0) -> List[KnowledgeUnit]:
        """
        Retrieve relevant knowledge based on query
        """
        try:
            relevant_knowledge = []
            
            for knowledge_id, knowledge_unit in self.knowledge_store.items():
                # Filter by type if specified
                if knowledge_type and knowledge_unit.knowledge_type != knowledge_type:
                    continue
                
                # Filter by confidence
                if knowledge_unit.confidence < min_confidence:
                    continue
                
                # Check relevance (simplified matching)
                if self._is_relevant(knowledge_unit, query):
                    relevant_knowledge.append(knowledge_unit)
            
            # Sort by confidence and usage
            relevant_knowledge.sort(key=lambda x: (x.confidence, x.usage_count), reverse=True)
            
            # Update last used timestamp
            for knowledge in relevant_knowledge:
                knowledge.last_used = datetime.now()
                knowledge.usage_count += 1
            
            self.logger.debug(f"🔍 Knowledge Retrieved: {len(relevant_knowledge)} units")
            
            return relevant_knowledge
            
        except Exception as e:
            self.logger.error(f"❌ Knowledge retrieval failed: {e}")
            return []

    async def update_knowledge_confidence(self, knowledge_id: str, new_confidence: float):
        """
        Update knowledge confidence based on new evidence
        """
        try:
            if knowledge_id in self.knowledge_store:
                knowledge_unit = self.knowledge_store[knowledge_id]
                knowledge_unit.confidence = new_confidence
                knowledge_unit.last_used = datetime.now()
                
                # Repersist updated knowledge
                await self._persist_knowledge(knowledge_unit)
                
                self.logger.info(f"📊 Knowledge Confidence Updated: {knowledge_id} -> {new_confidence}")
                
        except Exception as e:
            self.logger.error(f"❌ Knowledge update failed: {e}")

    async def export_knowledge(self, export_path: str, format: str = "json"):
        """
        Export knowledge base
        """
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "knowledge_units": len(self.knowledge_store),
                "knowledge": [
                    {
                        "knowledge_id": ku.knowledge_id,
                        "knowledge_type": ku.knowledge_type.value,
                        "content": ku.content,
                        "confidence": ku.confidence,
                        "source": ku.source,
                        "created_date": ku.created_date.isoformat(),
                        "last_used": ku.last_used.isoformat(),
                        "usage_count": ku.usage_count,
                        "tags": ku.tags,
                        "metadata": ku.metadata
                    }
                    for ku in self.knowledge_store.values()
                ]
            }
            
            export_file = Path(export_path) / f"knowledge_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
            
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"📤 Knowledge Base Exported: {export_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Knowledge export failed: {e}")
            raise

    def _is_relevant(self, knowledge_unit: KnowledgeUnit, query: Dict) -> bool:
        """
        Check if knowledge unit is relevant to query
        """
        # Simple keyword matching - can be enhanced with semantic search
        query_text = str(query).lower()
        content_text = str(knowledge_unit.content).lower()
        
        # Check tags
        for tag in knowledge_unit.tags:
            if tag.lower() in query_text:
                return True
        
        # Check content keywords
        common_words = set(query_text.split()) & set(content_text.split())
        return len(common_words) > 2  # At least 2 common words

    async def _persist_knowledge(self, knowledge_unit: KnowledgeUnit):
        """
        Persist knowledge unit to disk
        """
        try:
            # Convert to serializable format
            knowledge_data = {
                "knowledge_id": knowledge_unit.knowledge_id,
                "knowledge_type": knowledge_unit.knowledge_type.value,
                "content": knowledge_unit.content,
                "confidence": knowledge_unit.confidence,
                "source": knowledge_unit.source,
                "created_date": knowledge_unit.created_date.isoformat(),
                "last_used": knowledge_unit.last_used.isoformat(),
                "usage_count": knowledge_unit.usage_count,
                "tags": knowledge_unit.tags,
                "metadata": knowledge_unit.metadata
            }
            
            # Determine storage path based on type
            type_path = self.base_path / knowledge_unit.knowledge_type.value
            storage_file = type_path / f"{knowledge_unit.knowledge_id}.json"
            
            with open(storage_file, 'w') as f:
                json.dump(knowledge_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ Knowledge persistence failed: {e}")
            raise

    async def get_knowledge_stats(self) -> Dict:
        """
        Get knowledge base statistics
        """
        stats = {
            "total_units": len(self.knowledge_store),
            "by_type": {},
            "average_confidence": 0.0,
            "total_usage": 0
        }
        
        confidences = []
        
        for knowledge_unit in self.knowledge_store.values():
            # Count by type
            ktype = knowledge_unit.knowledge_type.value
            stats["by_type"][ktype] = stats["by_type"].get(ktype, 0) + 1
            
            # Collect confidences
            confidences.append(knowledge_unit.confidence)
            
            # Total usage
            stats["total_usage"] += knowledge_unit.usage_count
        
        if confidences:
            stats["average_confidence"] = sum(confidences) / len(confidences)
        
        return stats