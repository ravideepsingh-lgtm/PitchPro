import asyncio
import json
import logging
import os
from datetime import datetime
from app.core.config import settings
from app.core.json_utils import NumpyEncoder, clean_text_encoding
from app.data.seller_repository import seller_repository
from app.data.excel_loader import excel_loader
from app.data.feature_builder import feature_builder
from app.agents.skill_registry import skill_registry
from app.agents.profile_agent import profile_agent
from app.agents.positive_agent import positive_agent
from app.agents.negative_agent import negative_agent
from app.agents.sentiment_agent import sentiment_agent
from app.agents.final_decision_agent import final_decision_agent

logger = logging.getLogger(__name__)

class BatchProfileOrchestrator:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_llm_calls)

    def _stabilize_final_decision(self, final_result: dict, feature_sets: dict) -> dict:
        final_result = clean_text_encoding(final_result)
        positive_inputs = feature_sets.get("positive_signals", {})
        usage = str(positive_inputs.get("bl_usage_percent", ""))
        saturated = usage.startswith("100") or usage.startswith("9") or usage.startswith("8")

        brief = final_result.get("sales_call_brief")
        if isinstance(brief, dict):
            handle_risk = str(brief.get("handle_risk", ""))
            unsupported_claim = "sellers at your plan" in handle_risk.lower()
            contradiction = "haven't maxed out" in handle_risk.lower() and saturated
            if unsupported_claim or contradiction:
                brief["handle_risk"] = (
                    "No major friction is visible. If the seller asks about fit, anchor on "
                    f"{usage} BL usage, 30/30 active days, and low NI/QRF friction."
                )
        return final_result

    async def analyze_single_glid(self, glid: int, dry_run: bool = False) -> dict:
        feature_sets = feature_builder.build_skill_feature_sets(glid)
        source = excel_loader.get_source_metadata()
        loaded_skills = skill_registry.loaded_skill_names()

        if dry_run:
            return {
                "success": True,
                "glid": int(glid),
                "source": source,
                "loaded_skills": loaded_skills,
                "agents": {
                    "seller_profile": {"dry_run": True, "feature_json": feature_sets["seller_profile"]},
                    "positive_signals": {"dry_run": True, "feature_json": feature_sets["positive_signals"]},
                    "negative_signals": {"dry_run": True, "feature_json": feature_sets["negative_signals"]},
                    "sentiment_analysis": {"dry_run": True, "feature_json": feature_sets["sentiment_analysis"]},
                    "upsell_decision": {"dry_run": True, "feature_json": feature_sets["upsell_decision"]},
                },
                "final_analysis": {
                    "dry_run": True,
                    "note": "LLM calls skipped. Feature JSONs assembled from Client Base."
                }
            }

        async with self.semaphore:
            logger.info(f"[GLID {glid}] Single API: Running Seller Profile + Positive + Negative in parallel...")
            profile_result, positive_result, negative_result = await asyncio.gather(
                profile_agent.run(feature_sets["seller_profile"]),
                positive_agent.run(feature_sets["positive_signals"]),
                negative_agent.run(feature_sets["negative_signals"])
            )

            logger.info(f"[GLID {glid}] Single API: Running Sentiment Analysis...")
            sentiment_context = dict(feature_sets["sentiment_analysis"])
            sentiment_context["seller_profile_analysis"] = profile_result
            sentiment_result = await sentiment_agent.run(
                feature_json=sentiment_context,
                positive_result=positive_result,
                negative_result=negative_result
            )

            logger.info(f"[GLID {glid}] Single API: Running Upsell Decision...")
            combined_agent_outputs = {
                "glusr_usr_id": str(glid),
                "seller_context": feature_sets["upsell_decision"],
                "raw_skill_inputs": {
                    "seller_profile": feature_sets["seller_profile"],
                    "positive_signals": feature_sets["positive_signals"],
                    "negative_signals": feature_sets["negative_signals"],
                    "sentiment_analysis": feature_sets["sentiment_analysis"],
                },
                "profile_status": profile_result,
                "positive_engagement": positive_result,
                "negative_engagement": negative_result,
                "sentiment_analysis": sentiment_result
            }
            final_result = await final_decision_agent.run(
                agent_outputs=combined_agent_outputs,
                prior_segment=str(feature_sets["upsell_decision"].get("prime_segment", "Unknown"))
            )
            final_result = self._stabilize_final_decision(final_result, feature_sets)

        return {
            "success": True,
            "glid": int(glid),
            "source": source,
            "loaded_skills": loaded_skills,
            "agents": {
                "seller_profile": profile_result,
                "positive_signals": positive_result,
                "negative_signals": negative_result,
                "sentiment_analysis": sentiment_result,
                "upsell_decision": final_result,
            },
            "final_analysis": final_result
        }
        
    async def process_single_glid(self, glid: int, dry_run: bool) -> dict:
        try:
            # 1. Build Feature JSONs for all agents
            profile_features = feature_builder.build(glid)
            positive_features = feature_builder.build_positive_features(glid)
            negative_features = feature_builder.build_negative_features(glid)
            sentiment_features = feature_builder.build_sentiment_features(glid)
            prior_segment = feature_builder.get_prior_segment(glid)
            
            if dry_run:
                return {
                    "glusr_usr_id": glid,
                    "profile_status": {"dry_run": True, "feature_json": profile_features},
                    "positive_engagement": {"dry_run": True, "feature_json": positive_features},
                    "negative_engagement": {"dry_run": True, "feature_json": negative_features},
                    "sentiment_analysis": {"dry_run": True, "feature_json": sentiment_features},
                    "final_decision": {"dry_run": True, "prior_segment": prior_segment, "note": "Skipped in dry run"}
                }
                
            async with self.semaphore:
                # ── PHASE 1: Profile + Positive + Negative (PARALLEL) ──
                logger.info(f"[GLID {glid}] Phase 1: Running Profile + Positive + Negative in parallel...")
                
                profile_result, positive_result, negative_result = await asyncio.gather(
                    profile_agent.run(profile_features),
                    positive_agent.run(positive_features),
                    negative_agent.run(negative_features)
                )
                logger.info(f"[GLID {glid}] Phase 1 complete.")
                
                # ── PHASE 2: Sentiment (SEQUENTIAL - needs P+N outputs) ──
                logger.info(f"[GLID {glid}] Phase 2: Running Sentiment Agent with P+N context...")
                
                sentiment_result = await sentiment_agent.run(
                    feature_json=sentiment_features,
                    positive_result=positive_result,
                    negative_result=negative_result
                )
                logger.info(f"[GLID {glid}] Phase 2 complete.")
                
                # ── PHASE 3: Final Decision (SEQUENTIAL - needs all 4) ──
                logger.info(f"[GLID {glid}] Phase 3: Running Final Upsell Decision Agent...")
                
                combined_agent_outputs = {
                    "glusr_usr_id": str(glid),
                    "profile_status": profile_result,
                    "positive_engagement": positive_result,
                    "negative_engagement": negative_result,
                    "sentiment_analysis": sentiment_result
                }
                
                final_result = await final_decision_agent.run(
                    agent_outputs=combined_agent_outputs,
                    prior_segment=prior_segment
                )
                logger.info(f"[GLID {glid}] Phase 3 complete. Final decision rendered.")
                
            return {
                "glusr_usr_id": glid,
                "profile_status": profile_result,
                "positive_engagement": positive_result,
                "negative_engagement": negative_result,
                "sentiment_analysis": sentiment_result,
                "final_decision": final_result
            }
        except Exception as e:
            logger.error(f"Error processing GLID {glid}: {e}")
            return {
                "glusr_usr_id": glid,
                "error": str(e)
            }

    async def run_batch(self, limit: int = 100, offset: int = 0, glids: list = None, save_output: bool = True, dry_run: bool = False):
        """Runs the full 5-agent pipeline across a batch of GLIDs."""
        # 1. Resolve GLIDs
        selected_glids = seller_repository.get_glids(limit=limit, offset=offset, specific_glids=glids)
        total_available = seller_repository.get_total_count()
        
        logger.info(f"Starting batch process. Dry run: {dry_run}, GLIDs to process: {len(selected_glids)}")
        
        # 2. Execute concurrently (each GLID runs its own 5-agent pipeline)
        tasks = [self.process_single_glid(glid, dry_run) for glid in selected_glids]
        completed_results = await asyncio.gather(*tasks)
        
        # 3. Segregate results and errors
        results = []
        errors = []
        for r in completed_results:
            if "error" in r:
                errors.append(r)
            else:
                results.append(r)
                
        output_path = None
        if save_output and results:
            output_path = self._save_results(results, dry_run)
            
        # 4. Sanitize numpy types for FastAPI/Pydantic serialization
        clean_results = json.loads(json.dumps(results, cls=NumpyEncoder))
        clean_errors = json.loads(json.dumps(errors, cls=NumpyEncoder))
        
        return {
            "success": True,
            "total_glids_available": int(total_available),
            "processed_count": len(clean_results),
            "error_count": len(clean_errors),
            "offset": offset,
            "limit": limit,
            "results": clean_results,
            "errors": clean_errors,
            "output_path": output_path
        }
        
    def _save_results(self, results: list, dry_run: bool) -> str:
        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = "dryrun_" if dry_run else ""
        filename = f"outputs/{prefix}full_pipeline_batch_{timestamp}.jsonl"
        
        with open(filename, 'w', encoding='utf-8') as f:
            for res in results:
                f.write(json.dumps(res, cls=NumpyEncoder) + "\n")
                
        logger.info(f"Saved batch results to {filename}")
        return filename

batch_orchestrator = BatchProfileOrchestrator()
