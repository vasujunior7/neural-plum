import json
import os
from ..models import PolicyConfig, MemberInfo

_policy_config = None

def load_policy(file_path: str = None) -> PolicyConfig:
    global _policy_config
    if _policy_config is not None:
        return _policy_config
        
    if file_path is None:
        file_path = os.path.join(os.path.dirname(__file__), "../../../policy_terms.json")
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        _policy_config = PolicyConfig(**data)
        
    return _policy_config

def get_policy() -> PolicyConfig:
    return load_policy()

def get_member(member_id: str) -> MemberInfo:
    policy = get_policy()
    if not member_id:
        return None
        
    clean_search_id = member_id.replace("-", "").replace(" ", "").upper()
    for member in policy.members:
        clean_member_id = member.member_id.replace("-", "").replace(" ", "").upper()
        if clean_member_id == clean_search_id:
            return member
    return None
