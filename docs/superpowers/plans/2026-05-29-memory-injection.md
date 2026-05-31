# Memory Injection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modify the scout_rank skill to use the existing memory injection service for providing relevant past context when generating analysis reports.

**Architecture:** Update the `_generate_analysis_report` function in scout_rank.py to fetch memory context using the inject_memory_context service and prepend it to the analysis prompt, maintaining backward compatibility through graceful error handling.

**Tech Stack:** Python, FastAPI, SQLAlchemy, pgvector, OpenRouter LLM

---

### Task 1: Update scout_rank.py to import memory injection service

**Files:**
- Modify: `/root/salesinject/backend/app/agent_os/nodes/scout_rank.py:1-10`

- [ ] **Step 1: Write the failing test**

Since this is an import change, we'll verify the import works by running the module.

```bash
cd /root/salesinject/backend && python -c "from app.agent_os.nodes.scout_rank import scout_rank; print('Import successful')"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /root/salesinject/backend && python -c "from app.agent_os.nodes.scout_rank import scout_rank; print('Import successful')"`
Expected: FAIL with ImportError if inject_memory_context import doesn't exist

- [ ] **Step 3: Write minimal implementation**

```python
# Add this import after the existing imports in scout_rank.py
from ...services.memory_injection import inject_memory_context
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /root/salesinject/backend && python -c "from app.agent_os.nodes.scout_rank import scout_rank; print('Import successful')"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /root/salesinject/backend
git add app/agent_os/nodes/scout_rank.py
git commit -m "feat: add memory injection import to scout_rank"
```

### Task 2: Modify _generate_analysis_report function signature and add memory context fetching

**Files:**
- Modify: `/root/salesinject/backend/app/agent_os/nodes/scout_rank.py:120-150` (approximately)

- [ ] **Step 1: Write the failing test**

We'll create a simple test to verify the function signature change:
```python
import inspect
from app.agent_os.nodes.scout_rank import _generate_analysis_report

# Check that function now accepts user_id parameter
sig = inspect.signature(_generate_analysis_report)
params = list(sig.parameters.keys())
assert 'user_id' in params, f"user_id parameter not found in {params}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /root/salesinject/backend && python -c "
import inspect
from app.agent_os.nodes.scout_rank import _generate_analysis_report
sig = inspect.signature(_generate_analysis_report)
params = list(sig.parameters.keys())
assert 'user_id' in params, f'user_id parameter not found in {params}'
"
Expected: FAIL (function doesn't have user_id parameter yet)

- [ ] **Step 3: Write minimal implementation**

```python
# Modify the function definition from:
# async def _generate_analysis_report(ranked_influencers: List[Dict[str, Any]], niche: str) -> str:
# To:
async def _generate_analysis_report(ranked_influencers: List[Dict[str, Any]], niche: str, user_id: str) -> str:
    """
    Generate analysis report.

    Args:
        ranked_influencers: Ranked influencer list
        niche: Target niche
        user_id: User ID for memory context

    Returns:
        Analysis report text
    """
    # Fetch memory context at the start of the function
    memory_context = ""
    try:
        memory_context = await inject_memory_context(user_id, niche, agent_id=None, limit=3)
    except Exception:
        # Fail gracefully - continue without memory context
        pass
    
    # ... rest of existing function remains unchanged for now ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /root/salesinject/backend && python -c "
import inspect
from app.agent_os.nodes.scout_rank import _generate_analysis_report
sig = inspect.signature(_generate_analysis_report)
params = list(sig.parameters.keys())
assert 'user_id' in params, f'user_id parameter not found in {params}'
"
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /root/salesinject/backend
git add app/agent_os/nodes/scout_rank.py
git commit -m "feat: add user_id parameter and memory context fetching to _generate_analysis_report"
```

### Task 3: Update _generate_analysis_report to use memory context in prompt

**Files:**
- Modify: `/root/salesinject/backend/app/agent_os/nodes/scout_rank.py:150-200` (approximately, where the prompt is built)

- [ ] **Step 1: Write the failing test**

We'll test that when memory context is available, it gets prepended to the prompt:
```python
# This test will be conceptual since we're testing internal behavior
# We'll verify by checking the source contains our expected pattern
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /root/salesinject/backend && grep -n "memory_context" app/agent_os/nodes/scout_rank.py | head -5`
Expected: FAIL (no memory_context usage in prompt building yet)

- [ ] **Step 3: Write minimal implementation**

Find where the base_prompt is constructed (around line where "report_lines = [" starts) and modify it to:
```python
# After fetching memory_context and before building the report
if memory_context:
    # Prepend memory context to influence the analysis
    enhanced_niche = f"{niche} (considering past context: {memory_context[:200]}...)"
else:
    enhanced_niche = niche

# Then use enhanced_niche wherever niche is used in the prompt generation
# Or more directly, modify the report generation to include context:
# We'll modify the report header to include context awareness
```

Actually, looking at the existing _generate_analysis_report function, it builds a report lines list. The best place to inject context is at the beginning or by influencing how the analysis is framed. Let's modify the approach:

```python
# At the very beginning of _generate_analysis_report, after fetching memory_context:
analysis_niche = niche
if memory_context:
    analysis_niche = f"{niche} (with consideration of past successful campaigns)"
    # Or we could add a note at the start of the report
    report_lines.insert(0, f"## Context from Past Memories")
    report_lines.insert(1, memory_context)
    report_lines.insert(2, "")  # blank line
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /root/salesinject/backend && grep -A5 -B5 "memory_context" app/agent_os/nodes/scout_rank.py`
Expected: PASS (should see our memory_context usage)

- [ ] **Step 5: Commit**

```bash
cd /root/salesinject/backend
git add app/agent_os/nodes/scout_rank.py
git commit -m "feat: integrate memory context into analysis report generation"
```

### Task 4: Update the call to _generate_analysis_report in scout_rank function to pass user_id

**Files:**
- Modify: `/root/salesinject/backend/app/agent_os/nodes/scout_rank.py:70-90` (approximately, where _generate_analysis_report is called)

- [ ] **Step 1: Write the failing test**

We'll verify the function call now passes user_id:
```python
# Conceptual test - we'll check the source
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /root/salesinject/backend && grep -n "_generate_analysis_report" app/agent_os/nodes/scout_rank.py`
Expected: FAIL (call doesn't pass user_id yet)

- [ ] **Step 3: Write minimal implementation**

Find the line where _generate_analysis_report is called and modify it from:
```python
report = await _generate_analysis_report(ranked_influencers, niche)
```
to:
```python
report = await _generate_analysis_report(ranked_influencers, niche, user_id)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /root/salesinject/backend && grep -n "_generate_analysis_report" app/agent_os/nodes/scout_rank.py`
Expected: PASS (should see user_id being passed)

- [ ] **Step 5: Commit**

```bash
cd /root/salesinject/backend
git add app/agent_os/nodes/scout_rank.py
git commit -m "feat: update scout_rank to pass user_id to _generate_analysis_report"
```

### Task 5: Create unit tests for the memory injection integration

**Files:**
- Create: `/root/salesinject/tests/test_scout_rank_memory.py`

- [ ] **Step 1: Write the failing test**

```python
"""
Unit tests for scout_rank memory injection integration.
"""
import pytest
from unittest.mock import Mock, patch
from app.agent_os.nodes.scout_rank import _generate_analysis_report

@pytest.mark.asyncio
async def test_generate_analysis_report_with_memory_context():
    """Test that memory context is used when available."""
    # Mock ranked influencers data
    ranked_influencers = [
        {"name": "Test Influencer", "followers": 10000, "engagement": 5.0}
    ]
    niche = "fitness"
    user_id = "test-user-id"
    
    # Mock the inject_memory_context function to return test context
    with patch('app.agent_os.nodes.scout_rank.inject_memory_context') as mock_inject:
        mock_inject.return_value = "Past context: User prefers video content"
        
        # Call the function
        result = await _generate_analysis_report(ranked_influencers, niche, user_id)
        
        # Verify memory injection was called
        mock_inject.assert_called_once_with(user_id, niche, None, 3)
        
        # Verify the result contains some indication of context usage
        # (exact content may vary, but function should not fail)
        assert isinstance(result, str)
        assert len(result) > 0

@pytest.mark.asyncio
async def test_generate_analysis_report_without_memory_context():
    """Test that function works when no memory context is available."""
    # Mock ranked influencers data
    ranked_influencers = [
        {"name": "Test Influencer", "followers": 10000, "engagement": 5.0}
    ]
    niche = "fitness"
    user_id = "test-user-id"
    
    # Mock the inject_memory_context function to raise an exception
    with patch('app.agent_os.nodes.scout_rank.inject_memory_context') as mock_inject:
        mock_inject.side_effect = Exception("Memory service unavailable")
        
        # Call the function - should not crash
        result = await _generate_analysis_report(ranked_influencers, niche, user_id)
        
        # Verify memory injection was attempted
        mock_inject.assert_called_once_with(user_id, niche, None, 3)
        
        # Verify the function still produces a result
        assert isinstance(result, str)
        assert len(result) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /root/salesinject/backend && pytest tests/test_scout_rank_memory.py -v`
Expected: FAIL (test file doesn't exist yet or imports fail)

- [ ] **Step 3: Write minimal implementation**

Create the test file with the content above.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /root/salesinject/backend && pytest tests/test_scout_rank_memory.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /root/salesinject/backend
git add tests/test_scout_rank_memory.py
git commit -m "feat: add unit tests for scout_rank memory injection integration"
```

### Task 6: Run existing tests to ensure no regressions

**Files:**
- Modify: None (just running tests)

- [ ] **Step 1: Write the failing test**

We'll run the existing test suite to make sure we didn't break anything.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /root/salesinject/backend && pytest -x`
Expected: Might FAIL if our changes broke existing functionality

- [ ] **Step 3: Write minimal implementation**

If tests fail, we'll need to fix our implementation. But assuming we made minimal, backward-compatible changes, they should pass.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /root/salesinject/backend && pytest -x`
Expected: PASS (all existing tests still pass)

- [ ] **Step 5: Commit**

```bash
cd /root/salesinject/backend
# Only commit if tests pass and we want to capture a clean state
git commit -m "test: verify no regressions from memory injection changes" || echo "Tests passed, no commit needed"
```
