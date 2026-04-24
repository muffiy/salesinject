from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..models import PaperclipItem

def write_paperclip_items(
    db: Session, 
    user_id: str, 
    task_id: str, 
    influencers: List[Dict[str, Any]], 
    report: str, 
    ad_copy: str
) -> None:
    """
    Writes three types of rows to the `paperclip_items` table:
    1. A single 'mission_log' containing the overall expert report.
    2. Multiple 'pinned_profile' rows, one for each influencer found.
    3. A single 'ad_copy' draft.
    
    Utilizes the passed-in Session to ensure integrity with Celery's 
    ongoing transaction stack (flushes/commits handled by caller).
    """

    # 1. Mission Log
    log_item = PaperclipItem(
        user_id=user_id,
        task_id=task_id,
        item_type="mission_log",
        content={"report": report}
    )
    db.add(log_item)

    # 2. Pinned Profiles
    for inf in influencers:
        profile_item = PaperclipItem(
            user_id=user_id,
            task_id=task_id,
            item_type="pinned_profile",
            content=inf
        )
        db.add(profile_item)

    # 3. Ad Copy Draft
    copy_item = PaperclipItem(
        user_id=user_id,
        task_id=task_id,
        item_type="ad_copy",
        content={"draft": ad_copy}
    )
    db.add(copy_item)
    
    # We do NOT commit here. We simply flush or let the parent task orchestrate the commit
    db.flush()
