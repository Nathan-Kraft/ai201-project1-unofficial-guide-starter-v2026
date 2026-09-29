def judge(question: str,expects: str,answer: str,results)->bool:
    """
    Check if the expected answer phrase appears in the generated answer.

    Returns True if expects is found in answer (case-insensitive).
    Returns False if expects is empty or not found.
    """
    
    if not expects:
        return False
    return expects.strip().lower() in (answer or "").lower()