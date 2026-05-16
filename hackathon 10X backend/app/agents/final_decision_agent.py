import json
import logging
from app.agents.base_agent import BaseAgent
from app.agents.skill_registry import skill_registry
from app.core.json_utils import NumpyEncoder

logger = logging.getLogger(__name__)

class FinalDecisionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="FinalUpsellDecisionAgent",
            system_prompt="You are the Final Upsell Decision Agent. Synthesize all agent outputs and return strict JSON."
        )
        
    async def run(self, agent_outputs: dict, prior_segment: str = "Unknown") -> dict:
        """
        Executes the Final Upsell Decision Agent.
        Receives the combined outputs from Profile, Positive, Negative, and Sentiment agents.
        """
        glid = agent_outputs.get("glusr_usr_id", "Unknown")
        logger.info(f"[{self.name}] Making final decision for GLID: {glid}")
        
        skill = skill_registry.get("upsell_decision")
        prompt = f"""
Use the following markdown skill as your final decision instructions:

{skill}

Agent Outputs JSON:
{json.dumps(agent_outputs, indent=2, cls=NumpyEncoder)}

Prior Segment Recommendation:
{prior_segment}

Non-negotiable output rules:
- Use only numbers present in Agent Outputs JSON. Do not invent benchmark claims such as "85% of sellers" or "40% more leads".
- If BL usage is 85% or higher, do not say the seller has not maxed out. Treat it as quota saturation.
- Keep risk handling consistent with the actual risk fields. If no major risks exist, use the weakest real gap.
- Return frontend-ready plain text. Do not use markdown bold markers.

Return strict JSON only in this schema:
{{
  "glusr_usr_id": "",
  "decision": "UPSELL / CONDITIONAL / MONITOR / DO NOT UPSELL / HOLD",
  "recommended_next_tier": "",
  "current_plan": "",
  "seller_sentiment_score": 0,
  "sentiment_class": "",
  "seller_intent_type": "",
  "score_breakdown": {{
    "profile_strength": 0,
    "engagement_score": 0,
    "friction_penalty": 0,
    "prime_segment_boost": 0,
    "total_sss": 0
  }},
  "why_upsell": [],
  "why_not_risks": [],
  "sales_call_brief": {{
    "pitch_angle": "",
    "key_hook": "",
    "handle_risk": ""
  }},
  "final_recommendation": ""
}}
"""
        
        # Call LLM
        return await self._call_llm(prompt)

final_decision_agent = FinalDecisionAgent()
