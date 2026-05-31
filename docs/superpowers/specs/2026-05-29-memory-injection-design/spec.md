# Memory Injection Implementation Design

## Overview
This document describes the implementation plan for updating the scout_rank skill to use the existing memory injection service. The memory injection service is already implemented and used by other LLM-calling skills, but scout_rank currently uses a different approach.

## Current State
- `backend/app/services/memory_injection.py` exists with `inject_memory_context(user_id, query, agent_id, limit=3)` function
- `analyze_and_rank` and `generate_ad_idea_tool` tools in `paperclip_tools.py` already use `inject_memory_context`
- `scout_rank` in `/app/agent_os/nodes/scout_rank.py` does NOT use memory injection
- The scout_rank function generates its own analysis report without leveraging past memories

## Goal
Modify the scout_rank skill to use the memory injection service to provide relevant past context when generating analysis reports, consistent with how other LLM-calling skills operate.

## Design

### Changes Needed
1. **Update scout_rank.py** to import and use `inject_memory_context`
2. **Modify `_generate_analysis_report` function** to accept memory context and prepend it to the analysis prompt
3. **Ensure proper error handling** - if memory injection fails, fall back to original behavior

### Implementation Details

#### File: `/app/agent_os/nodes/scout_rank.py`

##### Changes to `_generate_analysis_report` function:
1. Add `user_id` parameter to function signature
2. Import `inject_memory_context` from `...services.memory_injection`
3. At the beginning of the function, fetch memory context using the niche as query
4. Prepend the memory context to the prompt before generating the report
5. Handle exceptions gracefully - if memory injection fails, continue without context

#### Updated Function Signature:
```python
async def _generate_analysis_report(ranked_influencers: List[Dict[str, Any]], niche: str, user_id: str) -> str:
```

#### Implementation Steps:
1. At start of function, try to get memory context:
   ```python
   try:
       memory_context = await inject_memory_context(user_id, niche, agent_id=None, limit=3)
   except Exception:
       memory_context = ""
   ```
2. Modify the prompt building to include memory context:
   ```python
   if memory_context:
       full_prompt = f"{memory_context}\n\n{base_prompt}"
   else:
       full_prompt = base_prompt
   ```
3. Update the call to `_generate_analysis_report` in the main `scout_rank` function to pass `user_id`

### Error Handling
- Memory injection failures should not break the skill - fall back to no context
- Log warnings but continue execution
- Maintain existing functionality if memory service is unavailable

### Testing Approach
- Unit tests for the modified `_generate_analysis_report` function
- Tests should verify:
  - Memory context is fetched when service is available
  - Context is properly prepended to the prompt
  - Graceful fallback when memory injection fails
  - Existing functionality preserved when no memories found

## Dependencies
- No new dependencies - using existing memory injection service
- Requires importing from existing services module

## Implementation Notes
- The memory injection service already handles embedding generation and database queries
- We're reusing the existing, tested service rather than duplicating logic
- Changes are minimal and focused - only modifying how the analysis prompt is constructed
- Maintains backward compatibility - if memory injection fails, behaves exactly as before