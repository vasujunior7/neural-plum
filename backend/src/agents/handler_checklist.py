from ..models import ChecklistItem, ManualReviewChecklist


def generate_handler_checklist(
    context: dict,
    decision_notes: list = None,
    rejection_reasons: list = None
) -> ManualReviewChecklist:
    """
    Generate a prioritized handler checklist for MANUAL_REVIEW claims.
    Scans context for low-confidence fields, fraud flags, and high-value items.
    """
    items = []
    priority_counter = 1
    
    # 1. Low-confidence extraction fields
    field_confidences = context.get("field_confidences", {})
    for field_name, field_data in field_confidences.items():
        confidence = field_data.get("confidence", 1.0)
        if confidence < 0.6:
            items.append(ChecklistItem(
                priority=priority_counter,
                action=f"Verify '{field_name.replace('_', ' ')}' on the submitted documents",
                reason=f"Low extraction confidence: {confidence:.2f}",
                source_agent="ExtractionAgent",
                estimated_minutes=3
            ))
            priority_counter += 1
    
    # 2. Semantic fraud flags
    semantic_fraud = context.get("semantic_fraud_result", {})
    fraud_flags = semantic_fraud.get("flags", [])
    for flag in fraud_flags:
        severity_minutes = {"high": 10, "medium": 5, "low": 3}
        items.append(ChecklistItem(
            priority=priority_counter,
            action=f"Review fraud flag: {flag.get('signal', 'Unknown signal')}",
            reason=f"Severity: {flag.get('severity', 'unknown')} — Fields: {', '.join(flag.get('fields_involved', []))}",
            source_agent="SemanticFraudAgent",
            estimated_minutes=severity_minutes.get(flag.get("severity", "low"), 5)
        ))
        priority_counter += 1
    
    # 3. High-value claim threshold
    claim_plan = context.get("claim_plan", {})
    if claim_plan.get("complexity_score", 0) > 0.6:
        items.append(ChecklistItem(
            priority=priority_counter,
            action="Verify claim amount against hospital rate card for this procedure",
            reason=f"High complexity score: {claim_plan.get('complexity_score', 0):.2f}",
            source_agent="PlannerAgent",
            estimated_minutes=5
        ))
        priority_counter += 1
    
    # 4. Rejection reasons that need human judgment
    if rejection_reasons:
        for reason in rejection_reasons:
            if reason == "MANUAL_REVIEW":
                continue  # Skip the generic MANUAL_REVIEW reason
            items.append(ChecklistItem(
                priority=priority_counter,
                action=f"Evaluate flagged issue: {reason.replace('_', ' ').title()}",
                reason="Automated system flagged for human review",
                source_agent="FraudDetectorAgent",
                estimated_minutes=5
            ))
            priority_counter += 1
    
    # 5. Notes-based checks
    if decision_notes:
        for note in decision_notes:
            if "manual review" in note.lower() or "bypassed" in note.lower():
                items.append(ChecklistItem(
                    priority=priority_counter,
                    action=f"Review: {note[:100]}",
                    reason="System note requires human attention",
                    source_agent="Supervisor",
                    estimated_minutes=3
                ))
                priority_counter += 1
    
    total_minutes = sum(item.estimated_minutes for item in items)
    
    # If no specific items found, add a generic review item
    if not items:
        items.append(ChecklistItem(
            priority=1,
            action="Perform general review of claim documents and extracted data",
            reason="Claim routed to manual review due to low system confidence",
            source_agent="Supervisor",
            estimated_minutes=15
        ))
        total_minutes = 15
    
    return ManualReviewChecklist(
        items=items,
        total_estimated_minutes=total_minutes
    )
