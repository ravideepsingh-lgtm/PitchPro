def safe_divide(numerator, denominator, default=0.0):
    try:
        num = float(numerator)
        den = float(denominator)
        if den == 0:
            return default
        return round(num / den, 2)
    except (ValueError, TypeError):
        return default

def calculate_derived_metrics(features: dict) -> dict:
    """
    Calculates derived metrics from the raw seller features.
    """
    metrics = {}
    comm = features.get('communication_profile', {})
    notif = features.get('notification_profile', {})
    act = features.get('activity_profile', {})
    cat = features.get('category_profile', {})

    # Answer Rates
    metrics['answer_rate_30'] = safe_divide(comm.get('total_ans_calls_30', 0), comm.get('totalcalls_30', 0))
    metrics['answer_rate_60'] = safe_divide(comm.get('total_ans_calls_60', 0), comm.get('totalcalls_60', 0))
    metrics['answer_rate_90'] = safe_divide(comm.get('total_ans_calls_90', 0), comm.get('totalcalls_90', 0))

    # Notification Open Rate
    metrics['notification_open_rate'] = safe_divide(notif.get('notif_open', 0), notif.get('notif_sent', 0))

    # Recent Activity Score (Simple heuristic MVP)
    try:
        txn_score = float(act.get('txn_30_days', 0) or 0)
        active_days = float(act.get('active_days_30', 0) or 0)
        metrics['recent_activity_score'] = round(txn_score * 0.5 + active_days * 0.5, 2)
    except:
        metrics['recent_activity_score'] = 0.0

    # Category Strength Score (Simple heuristic MVP)
    try:
        a_ranks = float(cat.get('rank_a_mcat_count', 0) or 0)
        b_ranks = float(cat.get('rank_b_mcat_count', 0) or 0)
        high_sold = float(cat.get('high_sold_mcat_count', 0) or 0)
        metrics['category_strength_score'] = round((a_ranks * 2) + (b_ranks * 1) + (high_sold * 1.5), 2)
    except:
        metrics['category_strength_score'] = 0.0

    # Service Status mapping
    services = features.get('service_profile', {}).get('current_services', [])
    if services:
        # Simplistic MVP check of the first service
        status = str(services[0].get('status', '')).lower()
        if 'active' in status:
            metrics['service_status'] = 'active'
        elif 'expire' in status:
            metrics['service_status'] = 'expired'
        else:
            metrics['service_status'] = 'unknown'
    else:
        metrics['service_status'] = 'unknown'

    metrics['engagement_score'] = round(metrics['answer_rate_30'] * 10 + metrics['notification_open_rate'] * 10, 2)
    
    return metrics
