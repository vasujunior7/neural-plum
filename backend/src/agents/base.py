from abc import ABC, abstractmethod
from ..models import AgentResult, ClaimSubmission, PolicyConfig
# pyrefly: ignore [missing-import]
from langfuse.decorators import observe, langfuse_context

class BaseAgent(ABC):
    @abstractmethod
    def run(self, claim: ClaimSubmission, policy: PolicyConfig, context: dict) -> AgentResult:
        pass
        
    @observe()
    def execute(self, claim: ClaimSubmission, policy: PolicyConfig, context: dict) -> AgentResult:
        agent_name = self.__class__.__name__
        langfuse_context.update_current_observation(
            name=agent_name,
            input=claim.model_dump(),
            metadata={"member_id": claim.member_id}
        )
        try:
            result = self.run(claim, policy, context)
            langfuse_context.update_current_observation(
                output=result.model_dump(),
                level="ERROR" if not result.passed else "DEFAULT"
            )
            return result
        except Exception as e:
            result = AgentResult(
                passed=True, # We don't crash, we degrade confidence
                confidence=0.5,
                notes=[f"Component {agent_name} failed: {str(e)}. Manual review recommended due to incomplete processing."],
            )
            langfuse_context.update_current_observation(
                output=result.model_dump(),
                level="ERROR"
            )
            return result
