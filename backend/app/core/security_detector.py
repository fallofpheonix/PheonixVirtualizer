def detect_behavior_change(benign: dict, attack: dict) -> bool:
    """
    Behavioral diff over process outputs.
    No regex, no LLM, no vulnerability typing.
    """
    if attack["timeout"]:
        return True

    if benign["stdout"] != attack["stdout"]:
        return True

    if "error" in attack["stderr"].lower():
        return True

    if len(attack["stdout"]) > 2 * len(benign["stdout"]):
        return True

    return False
