import json
import logging
from app.agents.base_agent import BaseAgent
from app.agents.skill_registry import skill_registry
from app.core.json_utils import NumpyEncoder

logger = logging.getLogger(__name__)

class ProfileAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ProfileStatusAgent",
            system_prompt="You are a Seller Profiling Agent. Always return strict JSON."
        )
        
    async def run(self, feature_json: dict) -> dict:
        """
        Executes the Profile Agent logic.
        """
        logger.info(f"[{self.name}] Analyzing GLID: {feature_json.get('glusr_usr_id')}")
        
        skill = skill_registry.get("seller_profile")
        prompt = f"""
Use the following markdown skill as your analysis instructions:

{skill}

Seller Data JSON:
{json.dumps(feature_json, indent=2, cls=NumpyEncoder)}

Return strict JSON only in this schema:
{{
  "glusr_usr_id": "",
  "seller_profile_score": 0,
  "profile_flags": [],
  "score_breakdown": {{
    "compliance_trust": 0,
    "business_scale": 0,
    "platform_vintage": 0,
    "reputation": 0,
    "company_type_bonus": 0
  }},
  "seller_snapshot": {{
    "company": "",
    "location": "",
    "industry": "",
    "company_type": "",
    "current_plan": "",
    "vintage": "",
    "turnover": "",
    "preferred_market": ""
  }},
  "profile_summary": "",
  "evidence_fields": []
}}
"""
        
        # Call LLM
        return await self._call_llm(prompt)

profile_agent = ProfileAgent()
