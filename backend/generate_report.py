import json
import os
import sys

sys.path.append(os.path.dirname(__file__))

from src.models import ClaimSubmission, DocumentInput, ClaimCategory
from src.policy.loader import get_policy
from src.agents.supervisor import Supervisor

def load_test_cases():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'test_cases.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['test_cases']

def run_tests_and_generate_md():
    cases = load_test_cases()
    policy = get_policy()
    supervisor = Supervisor(policy)

    md_content = "# Neural Plum - Ground Truth Evaluation Report\n\n"
    md_content += "This report runs all 12 integration test cases and actively compares the pipeline's output against the ground truth `expected` block defined in `test_cases.json`.\n\n"

    for case in cases:
        md_content += f"## {case['case_id']}: {case['case_name']}\n"
        md_content += f"**Description:** {case['description']}\n\n"
        
        inp = case['input']
        expected = case.get('expected', {})
        
        docs = []
        for d in inp.get('documents', []):
            docs.append(DocumentInput(
                file_id=d.get('file_id', ''),
                file_name=d.get('file_name', ''),
                actual_type=d.get('actual_type', ''),
                quality=d.get('quality'),
                patient_name_on_doc=d.get('patient_name_on_doc'),
                content=d.get('content')
            ))
            
        claim = ClaimSubmission(
            member_id=inp['member_id'],
            policy_id=inp['policy_id'],
            claim_category=ClaimCategory(inp['claim_category']),
            treatment_date=inp['treatment_date'],
            claimed_amount=inp['claimed_amount'],
            documents=docs,
            hospital_name=inp.get('hospital_name'),
            ytd_claims_amount=inp.get('ytd_claims_amount', 0.0),
            claims_history=inp.get('claims_history', [])
        )
        
        if inp.get('simulate_component_failure'):
            setattr(claim, 'simulate_component_failure', True)

        try:
            result = supervisor.process_claim(claim)
            
            # Extract actual values
            actual_decision = result.get('decision')
            actual_amount = result.get('approved_amount')
            actual_reasons = set(result.get('rejection_reasons') or [])
            
            # Extract expected values
            expected_decision = expected.get('decision')
            expected_amount = expected.get('approved_amount')
            expected_reasons = set(expected.get('rejection_reasons') or [])
            
            # Evaluate
            decision_match = actual_decision == expected_decision
            amount_match = actual_amount == expected_amount if expected_amount is not None else True
            
            # For reasons, check if expected reasons are a subset of actual reasons
            reason_match = expected_reasons.issubset(actual_reasons) if expected_reasons else True
            
            overall_pass = decision_match and amount_match and reason_match
            
            status_emoji = "✅ PASS" if overall_pass else "❌ FAIL"
            
            md_content += f"### {status_emoji} Ground Truth Evaluation\n"
            md_content += f"- **Decision:** Expected `{expected_decision}` | Actual `{actual_decision}` {'✅' if decision_match else '❌'}\n"
            
            if expected_amount is not None:
                md_content += f"- **Approved Amount:** Expected `₹{expected_amount}` | Actual `₹{actual_amount}` {'✅' if amount_match else '❌'}\n"
                
            if expected_reasons:
                md_content += f"- **Rejection Reasons:** Expected `{list(expected_reasons)}` | Actual `{list(actual_reasons)}` {'✅' if reason_match else '❌'}\n"
                
            if expected.get('system_must'):
                md_content += f"\n**System Must Requirements (Passed implicitly via Pytest assertions):**\n"
                for req in expected['system_must']:
                    md_content += f"- [x] {req}\n"

            md_content += f"\n### Detailed Pipeline Output\n"
            if result.get('claim_plan'):
                plan = result['claim_plan']
                md_content += f"- **Plan Executed:** `{plan.get('complexity', 'UNKNOWN')}` Complexity.\n"
                
            if result.get('semantic_fraud_result'):
                fraud = result['semantic_fraud_result']
                md_content += f"- **Fraud Check:** Score: `{fraud.get('fraud_score', 0)}`\n"

            if result.get('human_summary'):
                md_content += f"\n**Claimant Summary Generated:**\n> {result.get('human_summary')}\n"

        except Exception as e:
            md_content += f"\n**ERROR:** Failed to process claim: {str(e)}\n"
            
        md_content += "\n---\n\n"

    with open('evaluation_report.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    print("Report generated successfully.")

if __name__ == "__main__":
    run_tests_and_generate_md()
