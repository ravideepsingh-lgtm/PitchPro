import json
import logging
from app.agents.base_agent import BaseAgent
from app.agents.skill_registry import skill_registry
from app.core.json_utils import NumpyEncoder

logger = logging.getLogger(__name__)

class SentimentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SentimentAnalysisAgent",
            system_prompt="You are a Sentiment Analysis Agent. Always return strict JSON."
        )
        
    async def run(self, feature_json: dict, positive_result: dict = None, negative_result: dict = None) -> dict:
        """
        Executes the Sentiment Analysis Agent logic.
        Receives DSR summary + communication context + outputs from Positive & Negative agents.
        """
        logger.info(f"[{self.name}] Analyzing GLID: {feature_json.get('glusr_usr_id')}")
        
        # Combine sentiment features with agent outputs
        combined_input = dict(feature_json)
        if positive_result:
            combined_input["positive_engagement_analysis"] = positive_result
        if negative_result:
            combined_input["negative_engagement_analysis"] = negative_result
        
        skill = skill_registry.get("sentiment_analysis")
        prompt = f"""
Use the following markdown skill as your analysis instructions:

{skill}

Seller Sentiment Context JSON:
{json.dumps(combined_input, indent=2, cls=NumpyEncoder)}

Return strict JSON only in this schema:
{{
  "glusr_usr_id": "",
  "seller_sentiment_score": 0,
  "score_breakdown": {{
    "profile_strength": 0,
    "engagement_score": 0,
    "friction_penalty": 0,
    "prime_segment_boost": 0
  }},
  "hard_block_check": "NONE / CHURN RISK / COMPLAINT OPEN",
  "sentiment_class": "",
  "seller_intent_type": "",
  "top_positive_drivers": [],
  "top_risk_signals": [],
  "sentiment_summary": ""
}}
"""
        
        # Call LLM
        return await self._call_llm(prompt)

sentiment_agent = SentimentAgent()
