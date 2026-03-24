from typing import Dict, Any, List


def classify_fragmentation(psd: Dict[str, Any], target_p80: float = 150.0) -> Dict[str, Any]:
    p80 = psd.get("p80", 0)
    p50 = psd.get("p50", 0)
    fines_pct = psd.get("fines_percentage", 0)
    cu = psd.get("uniformity_coefficient", 0)

    if p80 <= target_p80 * 0.7:
        quality = "fine"
        quality_label = "Fine Fragmentation"
        quality_color = "blue"
    elif p80 <= target_p80:
        quality = "optimal"
        quality_label = "Optimal Fragmentation"
        quality_color = "green"
    elif p80 <= target_p80 * 1.3:
        quality = "slightly_coarse"
        quality_label = "Slightly Coarse"
        quality_color = "yellow"
    else:
        quality = "coarse"
        quality_label = "Coarse Fragmentation"
        quality_color = "red"

    score = _compute_quality_score(p80, p50, fines_pct, cu, target_p80)

    return {
        "quality": quality,
        "quality_label": quality_label,
        "quality_color": quality_color,
        "quality_score": round(score, 1),
        "target_p80": target_p80,
        "p80_deviation": round(((p80 - target_p80) / target_p80) * 100, 1),
        "within_target": p80 <= target_p80,
    }


def _compute_quality_score(
    p80: float, p50: float, fines_pct: float, cu: float, target_p80: float
) -> float:
    p80_ratio = p80 / target_p80 if target_p80 > 0 else 1.0

    if p80_ratio <= 1.0:
        p80_score = 100 - (1.0 - p80_ratio) * 30
    else:
        p80_score = max(0, 100 - (p80_ratio - 1.0) * 80)

    if fines_pct < 5:
        fines_score = 100
    elif fines_pct < 15:
        fines_score = 80
    elif fines_pct < 30:
        fines_score = 50
    else:
        fines_score = max(0, 50 - (fines_pct - 30))

    if 2 <= cu <= 5:
        uniformity_score = 100
    elif cu < 2:
        uniformity_score = 70
    else:
        uniformity_score = max(0, 100 - (cu - 5) * 15)

    score = p80_score * 0.5 + fines_score * 0.25 + uniformity_score * 0.25
    return max(0, min(100, score))


def generate_insights(
    psd: Dict[str, Any], classification: Dict[str, Any]
) -> List[Dict[str, str]]:
    insights = []
    p80 = psd.get("p80", 0)
    p50 = psd.get("p50", 0)
    fines_pct = psd.get("fines_percentage", 0)
    target = classification.get("target_p80", 150)
    quality = classification.get("quality", "unknown")

    if quality == "coarse":
        insights.append({
            "type": "warning",
            "title": "Coarse Fragmentation Detected",
            "message": f"P80 = {p80:.1f} mm exceeds target ({target:.0f} mm) by {classification['p80_deviation']:.1f}%. "
                       f"This will likely increase crushing energy and reduce throughput.",
        })
    elif quality == "slightly_coarse":
        insights.append({
            "type": "caution",
            "title": "Slightly Coarse Fragmentation",
            "message": f"P80 = {p80:.1f} mm is {classification['p80_deviation']:.1f}% above target. "
                       f"Monitor for downstream processing impacts.",
        })
    elif quality == "fine":
        insights.append({
            "type": "info",
            "title": "Fine Fragmentation",
            "message": f"P80 = {p80:.1f} mm is well below target ({target:.0f} mm). "
                       f"Consider reducing explosive energy to optimize cost.",
        })
    else:
        insights.append({
            "type": "success",
            "title": "Optimal Fragmentation",
            "message": f"P80 = {p80:.1f} mm is within target range. "
                       f"Current blast parameters are performing well.",
        })

    if fines_pct > 20:
        insights.append({
            "type": "warning",
            "title": "High Fines Ratio",
            "message": f"Fines percentage is {fines_pct:.1f}%. "
                       f"Excessive fines may indicate over-blasting or geological weakness zones.",
        })
    elif fines_pct > 10:
        insights.append({
            "type": "caution",
            "title": "Moderate Fines Present",
            "message": f"Fines percentage is {fines_pct:.1f}%. Within acceptable range but worth monitoring.",
        })

    if p80 > 0 and p50 > 0:
        ratio = p80 / p50
        if ratio > 3.0:
            insights.append({
                "type": "warning",
                "title": "Wide Size Distribution",
                "message": f"P80/P50 ratio = {ratio:.1f} indicates highly variable fragmentation. "
                           f"Check for inconsistent geology or blast timing issues.",
            })

    if p80 > target * 1.4:
        insights.append({
            "type": "warning",
            "title": "Crushing Performance Risk",
            "message": f"Expected {((p80 - target) / target * 20):.0f}% increase in crushing energy consumption. "
                       f"Primary crusher may experience frequent bridging.",
        })

    return insights


def generate_recommendations(
    psd: Dict[str, Any], classification: Dict[str, Any]
) -> List[Dict[str, str]]:
    recommendations = []
    quality = classification.get("quality", "unknown")
    p80 = psd.get("p80", 0)
    fines_pct = psd.get("fines_percentage", 0)
    target = classification.get("target_p80", 150)

    if quality in ("coarse", "slightly_coarse"):
        deviation = (p80 - target) / target
        if deviation > 0.3:
            recommendations.append({
                "priority": "high",
                "category": "Explosives",
                "action": "Increase Powder Factor",
                "detail": f"Increase powder factor by {min(deviation * 30, 25):.0f}% to improve fragmentation. "
                          f"Current P80 ({p80:.0f} mm) significantly exceeds target ({target:.0f} mm).",
            })
            recommendations.append({
                "priority": "high",
                "category": "Drill Pattern",
                "action": "Reduce Burden and Spacing",
                "detail": "Reduce burden by 10-15% and spacing by 5-10% to increase energy distribution. "
                          "Consider tighter drill patterns in harder rock zones.",
            })
        else:
            recommendations.append({
                "priority": "medium",
                "category": "Explosives",
                "action": "Moderate Powder Factor Increase",
                "detail": f"Increase powder factor by {deviation * 20:.0f}% for marginal improvement.",
            })

        recommendations.append({
            "priority": "medium",
            "category": "Timing",
            "action": "Review Delay Timing",
            "detail": "Optimize inter-hole and inter-row delays to improve fragmentation uniformity. "
                      "Consider electronic detonators for precise timing control.",
        })

    if quality == "fine" and fines_pct > 15:
        recommendations.append({
            "priority": "medium",
            "category": "Explosives",
            "action": "Reduce Powder Factor",
            "detail": f"Reduce powder factor by 10-15% to decrease excessive fines ({fines_pct:.1f}%). "
                      f"Current fragmentation is finer than necessary.",
        })
        recommendations.append({
            "priority": "low",
            "category": "Cost",
            "action": "Cost Optimization Opportunity",
            "detail": "Over-fragmentation suggests potential cost savings by reducing explosive consumption "
                      "while maintaining adequate fragmentation.",
        })

    if fines_pct > 25:
        recommendations.append({
            "priority": "high",
            "category": "Geology",
            "action": "Geological Assessment",
            "detail": "High fines ratio may indicate geological weakness zones. "
                      "Conduct geotechnical survey to identify weak zones and adjust blast design accordingly.",
        })

    if quality == "optimal":
        recommendations.append({
            "priority": "low",
            "category": "Monitoring",
            "action": "Maintain Current Parameters",
            "detail": "Current blast parameters are producing optimal fragmentation. "
                      "Continue monitoring to ensure consistency across different geological zones.",
        })

    return recommendations
