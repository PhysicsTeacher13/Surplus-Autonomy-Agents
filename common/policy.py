from typing import Dict, Set

DISALLOWED_ACTIONS_BY_MODE: Dict[str, Set[str]] = {
    "TEST": {"send_email", "submit_form", "place_call", "send_fax", "ship_fedex"},
    "DRY_RUN": {"send_email", "submit_form", "place_call", "send_fax", "ship_fedex"},
    "LIVE": set(),
}

def assert_allowed(run_config: Dict, action: str) -> None:
    mode = run_config.get("mode", "TEST")
    blocked = DISALLOWED_ACTIONS_BY_MODE.get(mode, set())
    if action in blocked:
        raise PermissionError(f"Action '{action}' blocked in mode={mode}.")
