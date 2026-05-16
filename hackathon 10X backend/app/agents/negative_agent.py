import json
import logging
from app.agents.base_agent import BaseAgent
from app.agents.skill_registry import skill_registry
from app.core.json_utils import NumpyEncoder

logger = logging.getLogger(__name__)

class NegativeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="NegativeEngagementAgent",
            system_prompt="You are a Negative Engagement Analysis Agent. Always return strict JSON."
        )
        
    async def run(self, feature_json: dict) -> dict:
        """
        Executes the Negative Engagement Agent logic.
        """
        logger.info(f"[{self.name}] Analyzing GLID: {feature_json.get('glusr_usr_id')}")
        
        skill = skill_registry.get("negative_signals")
        prompt = f"""
Use the following markdown skill as your analysis instructions:

{skill}

Seller Negative Signals JSON:
{json.dumps(feature_json, indent=2, cls=NumpyEncoder)}

Return strict JSON only in this schema:
{{
  "glusr_usr_id": "",
  "ni_qrf_gate": "MET / NOT MET",
  "friction_penalty": 0,
  "risk_flags": [],
  "score_breakdown": {{
    "total_ni_qrf": 0,
    "wrong_category": 0,
    "location": 0,
    "retail": 0,
    "complaints": 0
  }},
  "primary_issue_type": "",
  "risk_insights": [],
  "negative_summary": "",
  "evidence_fields": []
}}
"""
        
        # Call LLM
        return await self._call_llm(prompt)

negative_agent = NegativeAgent()
