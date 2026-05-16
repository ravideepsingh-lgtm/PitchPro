from functools import lru_cache
from pathlib import Path


class SkillRegistry:
    """Loads markdown skill instructions from app/skills."""

    _skills = {
        "seller_profile": ("01_seller_profile.md", "SKILL 01 - Seller Profile Analyzer"),
        "positive_signals": ("02_positive_signals.md", "SKILL 02 - Positive Signals Analyzer"),
        "negative_signals": ("03_negative_signals.md", "SKILL 03 - Negative Signals Analyzer"),
        "sentiment_analysis": ("04_sentiment_analysis.md", "SKILL 04 - Seller Sentiment Analysis"),
        "upsell_decision": ("05_upsell_decision.md", "SKILL 05 - Upsell Decision Engine"),
    }

    def __init__(self):
        self.skills_dir = Path(__file__).resolve().parents[1] / "skills"

    @lru_cache(maxsize=None)
    def get(self, key: str) -> str:
        if key not in self._skills:
            raise KeyError(f"Unknown skill key: {key}")

        filename, _ = self._skills[key]
        path = self.skills_dir / filename
        return path.read_text(encoding="utf-8")

    def loaded_skill_names(self) -> dict:
        return {key: name for key, (_, name) in self._skills.items()}


skill_registry = SkillRegistry()
