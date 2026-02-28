# llm_entity_extractor.py - Enhanced Version
"""
LLM-Powered Entity and Relation Extraction
Supports Ollama (Llama3, Qwen), OpenAI, and Anthropic
"""

import logging
import json
from typing import List, Dict, Tuple, Any
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import re

logger = logging.getLogger(__name__)

class LLMEntityExtractor:
    """Extract entities and relations using LLMs"""
    
    # Cybersecurity entity types
    ENTITY_TYPES = [
        "Technique", "Tactic", "ThreatGroup", "Malware", "Tool",
        "CVE", "CWE", "Protocol", "Indicator", "Asset", "Mitigation"
    ]
    
    def __init__(self, model: str = "llama3", temperature: float = 0.1):
        """Initialize with specified LLM model"""
        self.model = model
        self.llm = Ollama(
            model=model,
            temperature=temperature
        )
        
        logger.info(f"Initialized LLM Entity Extractor with model: {model}")
    
    async def extract_all(self, text: str) -> Tuple[List[Dict], List[Dict]]:
        """Extract both entities and relations from text"""
        
        entities = await self.extract_entities(text)
        relations = await self.extract_relations(text, entities)
        
        return entities, relations
    
    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract cybersecurity entities from text"""
        
        prompt = f"""Extract cybersecurity entities from the following text.

Entity types: {', '.join(self.ENTITY_TYPES)}

Text:
{text[:3000]}

Return ONLY a JSON array of entities in this exact format:
[
  {{"entity": "APT29", "type": "ThreatGroup", "confidence": 0.95}},
  {{"entity": "Phishing", "type": "Technique", "confidence": 0.90}}
]

JSON output:"""
        
        try:
            response = self.llm(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                entities = json.loads(json_match.group())
                logger.info(f"Extracted {len(entities)} entities")
                return entities
            else:
                logger.warning("No JSON found in response")
                return []
                
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
    
    async def extract_relations(self, text: str, entities: List[Dict]) -> List[Dict[str, Any]]:
        """Extract relationships between entities"""
        
        if len(entities) < 2:
            return []
        
        entity_names = [e['entity'] for e in entities[:20]]  # Limit for context
        
        prompt = f"""Identify relationships between these cybersecurity entities based on the text.

Entities: {', '.join(entity_names)}

Text:
{text[:3000]}

Return ONLY a JSON array of relationships:
[
  {{"source": "APT29", "relation": "USES", "target": "Phishing", "confidence": 0.85}},
  {{"source": "Phishing", "relation": "EXPLOITS", "target": "CVE-2021-1234", "confidence": 0.90}}
]

JSON output:"""
        
        try:
            response = self.llm(prompt)
            
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                relations = json.loads(json_match.group())
                logger.info(f"Extracted {len(relations)} relations")
                return relations
            else:
                return []
                
        except Exception as e:
            logger.error(f"Relation extraction failed: {e}")
            return []
