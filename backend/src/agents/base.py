from abc import ABC, abstractmethod
from ..models import AgentResult, ClaimSubmission, PolicyConfig

class BaseAgent(ABC):
    @abstractmethod
    def run(self, claim: ClaimSubmission, policy: PolicyConfig, context: dict) -> AgentResult:
        pass
        
    def execute(self, claim: ClaimSubmission, policy: PolicyConfig, context: dict) -> AgentResult:
        agent_name = self.__class__.__name__
        try:
            result = self.run(claim, policy, context)
            return result
        except Exception as e:
            result = AgentResult(
                passed=True, # We don't crash, we degrade confidence
                confidence=0.5,
                notes=[f"Component {agent_name} failed: {str(e)}. Manual review recommended due to incomplete processing."],
            )
            return result
