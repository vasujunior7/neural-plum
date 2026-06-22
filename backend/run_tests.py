import sys
import os
import json

# Setup path so we can import from src
sys.path.insert(0, os.path.dirname(__file__))

from src.models import ClaimSubmission
from src.policy.loader import get_policy
from src.agents.supervisor import Supervisor
from src.config import settings

# Force mock extraction since test_cases.json uses structured mock content instead of real base64 images
settings.MOCK_EXTRACTION = True

def run_all_tests():
    test_cases_file = os.path.join(os.path.dirname(__file__), '../test_cases.json')
    with open(test_cases_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    policy = get_policy()
    
    total_tests = len(data['test_cases'])
    passed_tests = 0
    
    # We will build the details section first, then prepend the summary
    details_content = ""
    
    for case in data['test_cases']:
        print(f"Running {case['case_id']}...")
        input_data = case['input']
        expected = case['expected']
        
        # Build the model
        claim = ClaimSubmission(**input_data)
        
        supervisor = Supervisor(policy)
        
        try:
            res = supervisor.process_claim(claim)
            status = "SUCCESS"
            error = None
        except Exception as e:
            import traceback
            res = None
            status = "ERROR"
            error = traceback.format_exc()
            
        is_valid = False
        validation_msgs = []
        
        if status == "SUCCESS":
            is_valid = True
            if expected.get('decision') != res.get('decision'):
                is_valid = False
                validation_msgs.append(f"Decision mismatch: Expected {expected.get('decision')} but got {res.get('decision')}")
                
            if "rejection_reasons" in expected:
                exp_reasons = set(expected["rejection_reasons"])
                actual_reasons = set(res.get("rejection_reasons", []))
                if not exp_reasons.issubset(actual_reasons):
                    is_valid = False
                    validation_msgs.append(f"Rejection reasons mismatch: Expected {list(exp_reasons)} but got {list(actual_reasons)}")
                    
            if "approved_amount" in expected:
                if expected["approved_amount"] != res.get("approved_amount"):
                    is_valid = False
                    validation_msgs.append(f"Approved amount mismatch: Expected {expected['approved_amount']} but got {res.get('approved_amount')}")
                    
        if is_valid:
            passed_tests += 1
            
        pass_label = "✅ PASS" if is_valid else "❌ FAIL"
            
        details_content += f"## {pass_label} | {case['case_id']}: {case['case_name']}\n"
        details_content += f"**Description:** {case['description']}\n\n"
        
        if not is_valid and validation_msgs:
            details_content += "**Validation Failures:**\n"
            for msg in validation_msgs:
                details_content += f"- {msg}\n"
            details_content += "\n"
        
        details_content += "### Expected\n"
        details_content += f"- **Decision:** {expected.get('decision')}\n"
        if "rejection_reasons" in expected:
            details_content += f"- **Rejection Reasons:** {', '.join(expected['rejection_reasons'])}\n"
        if "approved_amount" in expected:
            details_content += f"- **Approved Amount:** ₹{expected['approved_amount']}\n"
        
        details_content += "\n### Actual Result\n"
        if status == "ERROR":
            details_content += f"**System Error:**\n```python\n{error}\n```\n"
        else:
            details_content += f"- **Final State:** {res.get('final_state')}\n"
            details_content += f"- **Decision:** {res.get('decision')}\n"
            
            reasons = res.get('rejection_reasons', [])
            if reasons:
                details_content += f"- **Rejection Reasons:** {', '.join(reasons)}\n"
                
            amount = res.get('approved_amount')
            if amount is not None:
                details_content += f"- **Approved Amount:** ₹{amount}\n"
                
            details_content += f"- **Confidence Score:** {(res.get('confidence', 0)*100):.1f}%\n"
            
            details_content += "\n**Processing Notes:**\n"
            for note in res.get('notes', []):
                details_content += f"- {note}\n"
                
            details_content += "\n**Execution Traces:**\n"
            for trace in res.get('traces', []):
                details_content += f"- `{trace['state']}`: {trace['result'].get('notes', [])}\n"
                
        details_content += "\n---\n\n"
        
    md_content = "# Test Cases Evaluation Report\n\n"
    md_content += f"**Total Tests:** {total_tests} | **Passed:** {passed_tests} | **Failed:** {total_tests - passed_tests}\n\n"
    if passed_tests == total_tests:
        md_content += "🎉 **All tests passed!** The pipeline conforms exactly to expected behaviors.\n"
    else:
        md_content += "⚠️ **Some tests failed.** Review the validation messages below.\n"
    
    md_content += "\n> *Note: TC011 purposefully simulates an error in the system to verify graceful degradation, so an `ERROR:root:Fraud component failed` trace in the python execution logs is expected.*\n\n"
    md_content += "---\n\n"
    md_content += details_content
        
    with open("test_results.md", "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print("Done! Wrote test_results.md")

if __name__ == "__main__":
    run_all_tests()
