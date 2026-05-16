import json
import logging
from app.agents.base_agent import BaseAgent
from app.agents.skill_registry import skill_registry
from app.core.json_utils import NumpyEncoder

logger = logging.getLogger(__name__)

class PositiveAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="PositiveEngagementAgent",
            system_prompt="You are a Positive Engagement Analysis Agent. Always return strict JSON."
        )
        
    async def run(self, feature_json: dict) -> dict:
        """
        Executes the Positive Engagement Agent logic.
        """
        logger.info(f"[{self.name}] Analyzing GLID: {feature_json.get('glusr_usr_id')}")
        
        skill = skill_registry.get("positive_signals")
        prompt = f"""
Use the following markdown skill as your analysis instructions:

{skill}

Seller Positive Signals JSON:
{json.dumps(feature_json, indent=2, cls=NumpyEncoder)}

Return strict JSON only in this schema:
{{
  "glusr_usr_id": "",
  "engagement_score": 0,
  "engagement_flags": [],
  "score_breakdown": {{
    "platform_activity": 0,
    "buy_lead_consumption": 0,
    "call_performance": 0,
    "notification_engagement": 0,
    "category_opportunity": 0,
    "geographic_reach": 0
  }},
  "top_engagement_insights": [],
  "positive_summary": "",
  "evidence_fields": []
}}
"""
        
        # Call LLM
        return await self._call_llm(prompt)

positive_agent = PositiveAgent()
