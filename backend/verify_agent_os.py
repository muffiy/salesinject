#!/usr/bin/env python3
"""
Verification script for Agent OS v2 implementation.
Checks that all components are properly structured.
"""

import os
import sys
import importlib

def check_file_exists(path):
    """Check if file exists."""
    if os.path.exists(path):
        print(f"✓ {path}")
        return True
    else:
        print(f"✗ {path} - MISSING")
        return False

def check_import(module_name, class_name=None):
    """Try to import a module or class."""
    try:
        if class_name:
            module = importlib.import_module(module_name)
            getattr(module, class_name)
            print(f"✓ {module_name}.{class_name}")
        else:
            importlib.import_module(module_name)
            print(f"✓ {module_name}")
        return True
    except ImportError as e:
        print(f"✗ {module_name} - Import error: {e}")
        return False
    except AttributeError as e:
        print(f"✗ {module_name}.{class_name} - Attribute error: {e}")
        return False

def main():
    print("=" * 70)
    print("Agent OS v2 Implementation Verification")
    print("=" * 70)

    # Base directory
    base_dir = "/root/salesinject/backend/app"

    # Check core files
    print("\n1. Core Components:")
    core_files = [
        "agent_os/runtime.py",
        "agent_os/budget.py",
        "agent_os/cost_engine.py",
        "agent_os/concurrency.py",
        "agent_os/tracer.py",
        "agent_os/event_bus.py",
        "agent_os/router.py",
        "agent_os/market.py",
        "agent_os/missions.py",
        "agent_os/engine_v2.py",
        "agent_os/war_engine.py",
        "agent_os/__init__.py",
    ]

    for file_path in core_files:
        check_file_exists(os.path.join(base_dir, file_path))

    # Check nodes
    print("\n2. Node Implementations:")
    node_files = [
        "agent_os/nodes/__init__.py",
        "agent_os/nodes/hermes_plan.py",
        "agent_os/nodes/scout_collect.py",
        "agent_os/nodes/scout_rank.py",
        "agent_os/nodes/map_render.py",
    ]

    for file_path in node_files:
        check_file_exists(os.path.join(base_dir, file_path))

    # Check API integration
    print("\n3. API Integration:")
    api_files = [
        "api/v1/ws/stream.py",
        "api/v1/ws/telemetry.py",
        "api/v1/endpoints/scout.py",
    ]

    for file_path in api_files:
        check_file_exists(os.path.join(base_dir, file_path))

    # Check configuration
    print("\n4. Configuration:")
    config_files = [
        "../docker-compose.prod.yml",
        "../.env",
        "worker.py",
        "core/config.py",
    ]

    for file_path in config_files:
        check_file_exists(os.path.join(base_dir, file_path))

    # Check Docker compose for Redpanda
    print("\n5. Docker Compose Check:")
    docker_file = "/root/salesinject/docker-compose.prod.yml"
    if os.path.exists(docker_file):
        with open(docker_file, 'r') as f:
            content = f.read()
            if "redpanda:" in content:
                print("✓ Redpanda service configured")
            else:
                print("✗ Redpanda service not found")

            if "celery-scout:" in content:
                print("✓ Scout worker configured")
            else:
                print("✗ Scout worker not found")
    else:
        print("✗ Docker compose file not found")

    # Check requirements
    print("\n6. Dependencies Check:")
    req_file = "/root/salesinject/backend/requirements.txt"
    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            content = f.read()
            if "kafka-python" in content:
                print("✓ kafka-python in requirements.txt")
            else:
                print("✗ kafka-python missing from requirements.txt")
    else:
        print("✗ requirements.txt not found")

    print("\n" + "=" * 70)
    print("Verification Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Run Alembic migrations for new models (agent_sessions, agent_messages, etc.)")
    print("2. Update AgentMemory model to include session_id (optional)")
    print("3. Build and deploy with: docker-compose -f docker-compose.prod.yml up --build")
    print("4. Test mission launch: POST /api/v1/scout/mission/v2")
    print("5. Monitor events via WebSocket: /ws/stream/{trace_id}")

if __name__ == "__main__":
    main()