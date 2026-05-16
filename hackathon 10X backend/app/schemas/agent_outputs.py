from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ProfileLocation(BaseModel):
    city: str
    state: str
    location_preference: str

class ProfileTrust(BaseModel):
    gst_available: bool
    tan_available: bool
    tin_available: bool
    iec_available: bool

class ProfileStatusOutput(BaseModel):
    seller_profile_type: str
    business_maturity: str
    client_vintage: str
    current_customer_type: str
    service_status: str
    business_category_strength: str
    catalog_completeness: str
    engagement_level: str
    location_profile: ProfileLocation
    trust_profile: ProfileTrust
    profile_risks: List[str]
    evidence_fields: List[str]
    profile_summary: str

class PositiveEngagementOutput(BaseModel):
    bl_consumption_level: str
    lms_engagement_level: str
    enquiry_responsiveness: str
    bl_activity_level: str
    notification_engagement: str
    overall_positive_score: str
    positive_signals: List[str]
    evidence_fields: List[str]
    positive_summary: str

class NegativeEngagementOutput(BaseModel):
    ni_severity: str
    qrf_severity: str
    city_mismatch_risk: str
    churn_risk: str
    overall_negative_score: str
    negative_signals: List[str]
    evidence_fields: List[str]
    negative_summary: str

class SentimentAnalysisOutput(BaseModel):
    customer_tone: str
    issue_severity: str
    resolution_status: str
    escalation_risk: str
    upsell_receptiveness: str
    overall_sentiment: str
    sentiment_signals: List[str]
    evidence_fields: List[str]
    sentiment_summary: str

class EvidenceSummary(BaseModel):
    from_profile: str
    from_positive: str
    from_negative: str
    from_sentiment: str

class FinalDecisionOutput(BaseModel):
    upsell_decision: str
    confidence_score: float
    recommended_service: str
    current_service: str
    upgrade_path: str
    key_positive_factors: List[str]
    key_negative_factors: List[str]
    key_sentiment_factors: List[str]
    risk_assessment: str
    timing_recommendation: str
    decision_rationale: str
    evidence_summary: EvidenceSummary
