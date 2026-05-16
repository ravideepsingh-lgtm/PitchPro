import logging
import pandas as pd
from typing import Dict, Any
from app.data.excel_loader import excel_loader
from app.data.derived_metrics import calculate_derived_metrics

logger = logging.getLogger(__name__)

def safe_get(df: pd.DataFrame, glid: int, col: str, default: Any = "Unknown") -> Any:
    if df is None or df.empty or col not in df.columns:
        return default
    record = df[df['glusr_usr_id'] == glid]
    if record.empty:
        return default
    val = record.iloc[0][col]
    if pd.isna(val):
        return default
    return val

def clean_value(value: Any, default: Any = "Unknown") -> Any:
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        pass
    return value

def percent_value(value: Any) -> Any:
    value = clean_value(value, 0)
    if isinstance(value, str):
        return value
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return value
    if 0 <= numeric <= 1:
        return f"{round(numeric * 100, 2)}%"
    return f"{round(numeric, 2)}%"

def number_value(value: Any, default: Any = 0) -> Any:
    value = clean_value(value, default)
    if value == "Unknown":
        return default
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return value
    if numeric.is_integer():
        return int(numeric)
    return numeric

def safe_get_list(df: pd.DataFrame, glid: int, cols: list) -> list:
    if df is None or df.empty:
        return []
    records = df[df['glusr_usr_id'] == glid]
    if records.empty:
        return []
    
    results = []
    for _, row in records.iterrows():
        item = {}
        for col in cols:
            if col in df.columns and not pd.isna(row[col]):
                item[col] = row[col]
            else:
                item[col] = "Unknown"
        results.append(item)
    return results

class FeatureBuilder:
    def _load_all_dfs(self, glid: int):
        """Load all dataframes and return them as a dict for reuse."""
        return {
            "cb": excel_loader.get_df("Client Base"),
            "cs": excel_loader.get_df("customer services 1st may"),
            "mw": excel_loader.get_df("MCAT Rank"),
            "sm": excel_loader.get_df("seller_mcat data"),
            "bl": excel_loader.get_df("BL Data 1"),
            "pns": excel_loader.get_df("pns_csd_daily_cron"),
            "sc": excel_loader.get_df("Scorecard"),
            "dsr": excel_loader.get_df("DSR Summary"),
            "csd": excel_loader.get_df("csd_kcd_active_seller"),
            "ima": excel_loader.get_df("ima_cron_daily"),
            "ni": excel_loader.get_df("NI"),
            "qrf": excel_loader.get_df("QRF"),
            "notif": excel_loader.get_df("Notif"),
        }

    def build(self, glusr_usr_id: int) -> Dict[str, Any]:
        """
        Builds the compact seller feature JSON from multiple cached dataframes.
        """
        glid = int(glusr_usr_id)
        dfs = self._load_all_dfs(glid)
        
        cb = dfs["cb"]
        cs = dfs["cs"]
        mw = dfs["mw"]
        sm = dfs["sm"]
        bl = dfs["bl"]
        pns = dfs["pns"]
        sc = dfs["sc"]
        dsr = dfs["dsr"]
        csd = dfs["csd"]
        ima = dfs["ima"]

        features = {
            "glusr_usr_id": str(glid),
            
            "customer_profile": {
                "custtype_name": safe_get(cb, glid, "custtype_name", "Unknown"),
                "ownership_type": safe_get(csd, glid, "ownership_type", "Unknown"),
                "me_flag": safe_get(csd, glid, "me_flag", "Unknown"),
                "client_since": safe_get(cb, glid, "client_since", "Unknown"),
                "client_vintage": safe_get(cb, glid, "client_vintage", "Unknown"),
                "creationdate": safe_get(csd, glid, "creationdate", "Unknown"),
                "industry": safe_get(csd, glid, "industry", "Unknown"),
                "company_type": safe_get(cb, glid, "Company Type", "Unknown"),
                "annual_turnover": safe_get(cb, glid, "ANNUAL_TURNOVER", "Unknown"),
                "gst_turnover": safe_get(ima, glid, "gst_turnover", "Unknown")
            },
            
            "location_profile": {
                "city": safe_get(cb, glid, "city"),
                "state": safe_get(cb, glid, "STATE"),
                "pincode": safe_get(cb, glid, "pin"),
                "location_pref": safe_get(cb, glid, "location_pref")
            },
            
            "service_profile": {
                "catalog_service": safe_get(cb, glid, "catalog_service"),
                "ive_service": safe_get(cb, glid, "ive_service"),
                "service_mode": safe_get(cb, glid, "service_mode"),
                "enabled": safe_get(cb, glid, "enabled"),
                "current_services": safe_get_list(cs, glid, [
                    "service_name", "service_id", "status", "st_dt", "end_dt", 
                    "st_dt_renewal_enddate", "monthly_type", "ptype", 
                    "ar_invoice_total_amount", "ar_invoice_os_amount", "ar_recpt_status"
                ])
            },
            
            "trust_profile": {
                "gst_available": safe_get(csd, glid, "flag_gst"),
                "tan_available": safe_get(csd, glid, "flag_tan"),
                "tin_available": safe_get(csd, glid, "flag_tin"),
                "iec_available": safe_get(csd, glid, "flag_iec")
            },
            
            "category_profile": {
                "count_mcats": safe_get(csd, glid, "count_mcats"),
                "rank_a_mcat_count": safe_get(mw, glid, "rank_a_mcat_count"),
                "rank_b_mcat_count": safe_get(mw, glid, "rank_b_mcat_count"),
                "high_sold_mcat_count": safe_get(mw, glid, "high_sold_mcat_count"),
                "medium_sold_mcat_count": safe_get(mw, glid, "medium_sold_mcat_count"),
                "top_mcats": safe_get_list(sm, glid, ["mcat_id", "mcat_name", "rank", "sold_type"])[:5]
            },
            
            "activity_profile": {
                "txn_30_days": safe_get(bl, glid, "txn_30_days"),
                "txn_14_days": safe_get(bl, glid, "txn_14_days"),
                "txn_7_days": safe_get(bl, glid, "txn_7_days"),
                "active_days_30": safe_get(bl, glid, "active_days_30"),
                "active_days_14": safe_get(bl, glid, "active_days_14"),
                "active_days_7": safe_get(bl, glid, "active_days_7"),
                "last_catalog_update_date": safe_get(csd, glid, "last_catalog_update_date"),
                "last_call_date": safe_get(csd, glid, "last_call_date"),
                "dsr_meeting_last_date": safe_get(csd, glid, "dsr_meeting_last_date")
            },
            
            "communication_profile": {
                "totalcalls_30": safe_get(csd, glid, "totalcalls_30"),
                "totalcalls_60": safe_get(csd, glid, "totalcalls_60"),
                "total_ans_calls_30": safe_get(csd, glid, "total_ans_calls_30"),
                "pns_call": safe_get(pns, glid, "pns_call"),
                "success_call": safe_get(pns, glid, "success_call"),
                "seller_rating": safe_get(pns, glid, "seller_rating")
            },
            
            "internal_business_context": {
                "sales_vertical_name": safe_get(csd, glid, "sales_vertical_name"),
                "prime_final_rag_score": safe_get(csd, glid, "prime_final_rag_score"),
                "highest_service": safe_get(sc, glid, "highest_service")
            },
            
            "latest_dsr_summary": {
                "summary": safe_get(dsr, glid, "summary"),
                "status": safe_get(dsr, glid, "status")
            }
        }
        
        # Add derived metrics
        features["derived_metrics"] = calculate_derived_metrics(features)
        
        return features

    def build_positive_features(self, glusr_usr_id: int) -> Dict[str, Any]:
        """
        Builds the positive engagement feature JSON.
        Sources: ima_cron_daily (BL consumption), pns_csd_daily_cron (LMS, enq, ast_buy),
                 Scorecard (ast_buy_enq), Notif (notifications), BL Data 1 (activity).
        """
        glid = int(glusr_usr_id)
        dfs = self._load_all_dfs(glid)
        
        ima = dfs["ima"]
        pns = dfs["pns"]
        sc = dfs["sc"]
        notif = dfs["notif"]
        bl = dfs["bl"]
        cb = dfs["cb"]

        return {
            "glusr_usr_id": str(glid),
            
            "bl_consumption": {
                "total_used": safe_get(ima, glid, "total_used"),
                "total_active": safe_get(ima, glid, "total_active"),
                "total_bl_active": safe_get(ima, glid, "total_bl_active"),
                "total_cv_active": safe_get(ima, glid, "total_cv_active"),
                "in_total_active": safe_get(ima, glid, "in_total_active"),
                "in_bl_active": safe_get(ima, glid, "in_bl_active"),
                "fl_total_active": safe_get(ima, glid, "fl_total_active"),
                "fl_bl_active": safe_get(ima, glid, "fl_bl_active"),
                "total_cons_indian": safe_get(ima, glid, "total_cons_indian"),
                "bl_cons_indian": safe_get(ima, glid, "bl_cons_indian"),
                "cv_cons_indian": safe_get(ima, glid, "cv_cons_indian"),
                "total_cons_foreign": safe_get(ima, glid, "total_cons_foreign"),
                "bl_cons_foreign": safe_get(ima, glid, "bl_cons_foreign"),
                "cv_cons_foreign": safe_get(ima, glid, "cv_cons_foreign"),
                "bl_cred_indian": safe_get(ima, glid, "bl_cred_indian"),
                "bl_cred_foreign_daily": safe_get(ima, glid, "bl_cred_foreign_daily"),
                "bl_cred_foreign_weekly": safe_get(ima, glid, "bl_cred_foreign_weekly")
            },
            
            "lms_engagement": {
                "lms_total": safe_get(pns, glid, "lms_total"),
                "lms_indian": safe_get(pns, glid, "lms_indian"),
                "lms_foreign": safe_get(pns, glid, "lms_foreign")
            },
            
            "enquiry_engagement": {
                "total_enq": safe_get(pns, glid, "total_enq"),
                "total_astbuy": safe_get(pns, glid, "total_astbuy"),
                "ast_buy_enq": safe_get(sc, glid, "ast_buy_enq"),
                "callbacks_total": safe_get(pns, glid, "callbacks_total"),
                "callbacks_indian": safe_get(pns, glid, "callbacks_indian"),
                "callbacks_foreign": safe_get(pns, glid, "callbacks_foreign")
            },
            
            "bl_activity": {
                "txn_30_days": safe_get(bl, glid, "txn_30_days"),
                "txn_14_days": safe_get(bl, glid, "txn_14_days"),
                "txn_7_days": safe_get(bl, glid, "txn_7_days"),
                "active_days_30": safe_get(bl, glid, "active_days_30"),
                "active_days_14": safe_get(bl, glid, "active_days_14"),
                "active_days_7": safe_get(bl, glid, "active_days_7")
            },
            
            "notification_engagement": {
                "notif_trig": safe_get(notif, glid, "notif_trig"),
                "notif_sent": safe_get(notif, glid, "notif_sent"),
                "notif_del": safe_get(notif, glid, "notif_del"),
                "notif_open": safe_get(notif, glid, "notif_open"),
                "notif_swiped": safe_get(notif, glid, "notif_swiped"),
                "uniq_seller_notif_open": safe_get(notif, glid, "uniq_seller_notif_open")
            },
            
            "service_context": {
                "catalog_service": safe_get(cb, glid, "catalog_service"),
                "highest_service": safe_get(sc, glid, "highest_service"),
                "seller_rating": safe_get(pns, glid, "seller_rating"),
                "avg_ratings": safe_get(sc, glid, "avg_ratings"),
                "connect_duration": safe_get(sc, glid, "connect_duration")
            }
        }

    def build_negative_features(self, glusr_usr_id: int) -> Dict[str, Any]:
        """
        Builds the negative engagement feature JSON.
        Sources: NI (not interested), QRF (quality rejection), BL Data 1 (city-level negatives).
        """
        glid = int(glusr_usr_id)
        dfs = self._load_all_dfs(glid)
        
        ni = dfs["ni"]
        qrf = dfs["qrf"]
        bl = dfs["bl"]
        pns = dfs["pns"]
        cb = dfs["cb"]

        return {
            "glusr_usr_id": str(glid),
            
            "ni_signals": {
                "total_ni": safe_get(ni, glid, "total_ni"),
                "wrong_category_ni": safe_get(ni, glid, "wrong_category_ni"),
                "location_ni": safe_get(ni, glid, "location_ni"),
                "retail_ni": safe_get(ni, glid, "retail_ni"),
                "other_ni": safe_get(ni, glid, "other_ni")
            },
            
            "qrf_signals": {
                "total_irr_qrf_count": safe_get(qrf, glid, "total_irr_qrf_count"),
                "wrong_category": safe_get(qrf, glid, "wrong_category"),
                "location_mismatch": safe_get(qrf, glid, "location_mismatch"),
                "retail_qrf": safe_get(qrf, glid, "retail_qrf"),
                "other_qrf": safe_get(qrf, glid, "other_qrf")
            },
            
            "negative_city_signals": {
                "city_name": safe_get(bl, glid, "city_name"),
                "state_name": safe_get(bl, glid, "state_name"),
                "location_pref": safe_get(bl, glid, "location_pref"),
                "txn_30_days": safe_get(bl, glid, "txn_30_days"),
                "txn_7_days": safe_get(bl, glid, "txn_7_days")
            },
            
            "churn_indicators": {
                "pns_call": safe_get(pns, glid, "pns_call"),
                "success_call": safe_get(pns, glid, "success_call"),
                "seller_rating": safe_get(pns, glid, "seller_rating"),
                "catalog_service": safe_get(cb, glid, "catalog_service"),
                "enabled": safe_get(cb, glid, "enabled")
            }
        }

    def build_sentiment_features(self, glusr_usr_id: int) -> Dict[str, Any]:
        """
        Builds the sentiment analysis feature JSON.
        Sources: DSR Summary (conversation text), communication profile, Scorecard.
        """
        glid = int(glusr_usr_id)
        dfs = self._load_all_dfs(glid)
        
        dsr = dfs["dsr"]
        csd = dfs["csd"]
        pns = dfs["pns"]
        sc = dfs["sc"]
        cb = dfs["cb"]

        return {
            "glusr_usr_id": str(glid),
            
            "latest_dsr_summary": {
                "summary": safe_get(dsr, glid, "summary"),
                "status": safe_get(dsr, glid, "status"),
                "insertion_date": safe_get(dsr, glid, "insertion_date"),
                "updated_on": safe_get(dsr, glid, "updated_on")
            },
            
            "communication_context": {
                "totalcalls_30": safe_get(csd, glid, "totalcalls_30"),
                "totalcalls_60": safe_get(csd, glid, "totalcalls_60"),
                "total_ans_calls_30": safe_get(csd, glid, "total_ans_calls_30"),
                "pns_call": safe_get(pns, glid, "pns_call"),
                "success_call": safe_get(pns, glid, "success_call"),
                "seller_rating": safe_get(pns, glid, "seller_rating"),
                "avg_ratings": safe_get(sc, glid, "avg_ratings"),
                "connect_duration": safe_get(sc, glid, "connect_duration"),
                "last_call_date": safe_get(csd, glid, "last_call_date"),
                "dsr_meeting_last_date": safe_get(csd, glid, "dsr_meeting_last_date")
            },
            
            "seller_context": {
                "custtype_name": safe_get(cb, glid, "custtype_name"),
                "catalog_service": safe_get(cb, glid, "catalog_service"),
                "highest_service": safe_get(sc, glid, "highest_service")
            }
        }

    def get_prior_segment(self, glusr_usr_id: int) -> str:
        """
        Gets the prior upsell segment recommendation from the Upsell sheet.
        """
        glid = int(glusr_usr_id)
        upsell_df = excel_loader.get_df("Upsell")
        return safe_get(upsell_df, glid, "Segment Recommendation", "No prior recommendation")

    def get_client_base_record(self, glusr_usr_id: int) -> Dict[str, Any]:
        glid = int(glusr_usr_id)
        cb = excel_loader.get_df("Client Base")
        if cb.empty or "glusr_usr_id" not in cb.columns:
            raise ValueError("Client Base sheet is not loaded. Call /api/data/load first or check EXCEL_DATA_FOLDER.")

        records = cb[cb["glusr_usr_id"] == glid]
        if records.empty:
            raise LookupError(f"GLID {glid} not found in Client Base.")

        return {key: clean_value(value) for key, value in records.iloc[0].to_dict().items()}

    def build_skill_feature_sets(self, glusr_usr_id: int) -> Dict[str, Any]:
        row = self.get_client_base_record(glusr_usr_id)
        glid = int(glusr_usr_id)

        profile_features = {
            "glusr_usr_id": glid,
            "company": row.get("company", "Unknown"),
            "city": row.get("city", "Unknown"),
            "STATE": row.get("STATE", "Unknown"),
            "company_type": row.get("company_type", "Unknown"),
            "gst": number_value(row.get("gst"), 0),
            "tan": number_value(row.get("tan"), 0),
            "iec": number_value(row.get("iec"), 0),
            "Turnover": row.get("Turnover", "Unknown"),
            "preferred_location": row.get("preferred_location", "Unknown"),
            "client_vintage_days": number_value(row.get("client_vintage_days"), 0),
            "vintage": row.get("vintage", "Unknown"),
            "avg_ratings": number_value(row.get("avg_ratings"), 0),
            "ratings_count": number_value(row.get("ratings_count"), 0),
            "prime_segment": number_value(row.get("prime_segment"), 0),
            "industry": row.get("industry", "Unknown"),
            "highest_service": row.get("highest_service", "Unknown"),
            "custtype_name": row.get("custtype_name", "Unknown"),
            "sales_vertical": row.get("sales_vertical", "Unknown"),
        }

        positive_features = {
            "glusr_usr_id": glid,
            "bl_active_days_30": number_value(row.get("bl_active_days_30"), 0),
            "bl_usage_percent": percent_value(row.get("bl_usage_percent")),
            "total_consumed": number_value(row.get("total_consumed"), 0),
            "success_call": number_value(row.get("success_call"), 0),
            "call_success_percent": percent_value(row.get("call_success_percent")),
            "bl_notif_open": number_value(row.get("bl_notif_open"), 0),
            "bl_notif_open_percent": percent_value(row.get("bl_notif_open_percent")),
            "rank_a_mcat": number_value(row.get("rank_a_mcat"), 0),
            "rank_d_mcat": number_value(row.get("rank_d_mcat"), 0),
            "high_sold_a_rank": number_value(row.get("high_sold_a_rank"), 0),
            "high_sold_d_rank": number_value(row.get("high_sold_d_rank"), 0),
            "major_cities": number_value(row.get("major_cities"), 0),
            "lms_active_days": number_value(row.get("lms_active_days"), 0),
        }

        negative_features = {
            "glusr_usr_id": glid,
            "total_ni_qrf": number_value(row.get("total_ni_qrf"), 0),
            "wrong_category_ni_qrf": number_value(row.get("wrong_category_ni_qrf"), 0),
            "location_ni_qrf": number_value(row.get("location_ni_qrf"), 0),
            "retail_ni_qrf": number_value(row.get("retail_ni_qrf"), 0),
            "complaints_count": number_value(row.get("complaints_count"), 0),
            "complaints_not_satisfied": number_value(row.get("complaints_not_satisfied"), 0),
        }

        sentiment_features = {
            "glusr_usr_id": glid,
            "prime_segment": profile_features["prime_segment"],
        }

        decision_features = {
            "glusr_usr_id": glid,
            "company": profile_features["company"],
            "city": profile_features["city"],
            "STATE": profile_features["STATE"],
            "industry": profile_features["industry"],
            "highest_service": profile_features["highest_service"],
            "prime_segment": profile_features["prime_segment"],
        }

        return {
            "seller_profile": profile_features,
            "positive_signals": positive_features,
            "negative_signals": negative_features,
            "sentiment_analysis": sentiment_features,
            "upsell_decision": decision_features,
            "source_row": row,
        }

feature_builder = FeatureBuilder()
