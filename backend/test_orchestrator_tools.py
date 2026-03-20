#!/usr/bin/env python3
"""
Comprehensive test to verify the Hybrid Orchestrator can access and use all 35 tools
Tests tool registration, import, capability matching, and execution
"""

import json
import os
import sys
import importlib
from typing import Dict, List, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class OrchestratorToolTester:
    """Tests if orchestrator can access and use all registered tools"""

    def __init__(self, registry_path: str = None):
        if registry_path is None:
            registry_path = os.path.join(os.path.dirname(__file__), 'registry.json')

        self.registry_path = registry_path
        self.registry = self._load_registry()
        self.results = {
            'total_tools': 0,
            'importable': 0,
            'not_importable': 0,
            'callable': 0,
            'not_callable': 0,
            'capability_indexed': 0,
            'not_indexed': 0,
            'failed_tools': [],
            'success_tools': []
        }

    def _load_registry(self) -> Dict:
        """Load registry.json"""
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load registry: {e}")
            sys.exit(1)

    def print_header(self, title: str):
        """Print section header"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)

    def test_registry_structure(self):
        """Test if registry has correct structure"""
        self.print_header("1. Registry Structure Check")

        has_resources = 'resources' in self.registry
        has_tools = 'tools' in self.registry.get('resources', {})
        has_workflows = 'workflows' in self.registry.get('resources', {})
        has_ai_agents = 'ai_agents' in self.registry.get('resources', {})
        has_capability_index = 'capability_index' in self.registry

        print(f"✓ Registry loaded from: {self.registry_path}")
        print(f"✓ Has 'resources' section: {has_resources}")
        print(f"✓ Has 'tools' section: {has_tools}")
        print(f"✓ Has 'workflows' section: {has_workflows}")
        print(f"✓ Has 'ai_agents' section: {has_ai_agents}")
        print(f"✓ Has 'capability_index': {has_capability_index}")

        return has_resources and has_tools

    def count_all_resources(self):
        """Count all registered resources"""
        self.print_header("2. Resource Count")

        resources = self.registry.get('resources', {})

        tools = resources.get('tools', [])
        workflows = resources.get('workflows', [])
        ai_agents = resources.get('ai_agents', [])

        self.results['total_tools'] = len(tools)

        print(f"Tools registered: {len(tools)}")
        print(f"Workflows registered: {len(workflows)}")
        print(f"AI Agents registered: {len(ai_agents)}")
        print(f"\nTotal tools to test: {len(tools)}")

        return tools

    def test_tool_import_and_call(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Test if a tool can be imported and called"""
        tool_id = tool.get('id', 'unknown')
        tool_name = tool.get('name', 'Unknown')
        tool_type = tool.get('type', 'local_function')
        module_path = tool.get('module_path')
        function_name = tool.get('function')

        result = {
            'id': tool_id,
            'name': tool_name,
            'importable': False,
            'callable': False,
            'error': None,
            'type': tool_type
        }

        # REST API tools don't need module_path/function
        if tool_type == 'rest_api':
            endpoint = tool.get('endpoint')
            if endpoint:
                result['importable'] = True
                result['callable'] = True
                result['error'] = 'REST API tool (no import needed)'
            else:
                result['error'] = 'REST API tool missing endpoint'
            return result

        if not module_path or not function_name:
            result['error'] = 'Missing module_path or function'
            return result

        # Try to import the module
        try:
            module = importlib.import_module(module_path)
            result['importable'] = True

            # Try to get the function
            if hasattr(module, function_name):
                func = getattr(module, function_name)
                result['callable'] = callable(func)

                if not result['callable']:
                    result['error'] = f'{function_name} is not callable'
            else:
                result['error'] = f'Function {function_name} not found in module'

        except ImportError as e:
            result['error'] = f'Import error: {str(e)}'
        except Exception as e:
            result['error'] = f'Unexpected error: {str(e)}'

        return result

    def test_all_tools_import(self, tools: List[Dict[str, Any]]):
        """Test if all tools can be imported and called"""
        self.print_header("3. Tool Import and Callable Test")

        print(f"Testing {len(tools)} tools...\n")

        for idx, tool in enumerate(tools, 1):
            result = self.test_tool_import_and_call(tool)

            status = "✓" if result['importable'] and result['callable'] else "✗"
            print(f"{status} [{idx:2d}] {result['name']}")

            if result['importable']:
                self.results['importable'] += 1
            else:
                self.results['not_importable'] += 1

            if result['callable']:
                self.results['callable'] += 1
                self.results['success_tools'].append(result)
            else:
                self.results['not_callable'] += 1
                self.results['failed_tools'].append(result)

            if result['error']:
                print(f"    ⚠ {result['error']}")

    def test_capability_index(self, tools: List[Dict[str, Any]]):
        """Test if tools are properly indexed by capabilities"""
        self.print_header("4. Capability Index Test")

        capability_index = self.registry.get('capability_index', {})

        print(f"Total capabilities indexed: {len(capability_index)}\n")

        # Show all capabilities
        print("Capabilities available:")
        for capability, resource_ids in sorted(capability_index.items()):
            print(f"  • {capability}: {len(resource_ids)} resources")

        # Check each tool is in at least one capability
        print("\nChecking tool indexing:")
        for tool in tools:
            tool_id = tool.get('id')
            tool_name = tool.get('name')
            tool_caps = tool.get('capabilities', [])

            # Check if tool appears in any capability index
            found_in_index = False
            for capability in tool_caps:
                if tool_id in capability_index.get(capability, []):
                    found_in_index = True
                    break

            if found_in_index:
                self.results['capability_indexed'] += 1
                print(f"  ✓ {tool_name} - indexed")
            else:
                self.results['not_indexed'] += 1
                print(f"  ✗ {tool_name} - NOT indexed")

    def test_orchestrator_integration(self):
        """Test if HybridOrchestrator can load tools"""
        self.print_header("5. Orchestrator Integration Test")

        try:
            from hybrid_orchestrator import HybridOrchestrator

            orchestrator = HybridOrchestrator(registry_path=self.registry_path)

            print("✓ HybridOrchestrator imported successfully")
            print(f"✓ Registry loaded by orchestrator")
            print(f"✓ Total resources in registry: {len(orchestrator.registry.get('resources', {}).get('tools', []))}")

            # Test capability matching
            test_subtask = {
                'description': 'Convert Word document to PDF',
                'required_capabilities': ['word_processing', 'document_conversion'],
                'preferred_resource_type': 'tool'
            }

            matched = orchestrator.match_resources(test_subtask)

            print(f"\nTest capability matching:")
            print(f"  Query: {test_subtask['description']}")
            print(f"  Required capabilities: {test_subtask['required_capabilities']}")
            print(f"  Matched resources: {len(matched)}")

            if matched:
                print(f"  Best match: {matched[0].get('name')}")
                return True
            else:
                print(f"  ⚠ No matches found")
                return False

        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def test_sample_tool_execution(self):
        """Test actual execution of a sample tool"""
        self.print_header("6. Sample Tool Execution Test")

        # Test equipment lookup (should always be available)
        try:
            from tools.equipment_lookup import equipment_lookup

            print("Testing equipment_lookup tool...")
            result = equipment_lookup(equipment_id="PUMP-001")

            if result.get('success'):
                print(f"✓ Tool executed successfully")
                print(f"  Equipment: {result.get('name')}")
                print(f"  Type: {result.get('type')}")
                return True
            else:
                print(f"✗ Tool execution failed: {result.get('error')}")
                return False

        except Exception as e:
            print(f"✗ Error executing tool: {e}")
            return False

    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")

        total = self.results['total_tools']
        importable = self.results['importable']
        callable_count = self.results['callable']
        indexed = self.results['capability_indexed']

        print(f"Total tools registered: {total}")
        print(f"Importable tools: {importable}/{total} ({100*importable//total if total > 0 else 0}%)")
        print(f"Callable tools: {callable_count}/{total} ({100*callable_count//total if total > 0 else 0}%)")
        print(f"Indexed in capabilities: {indexed}/{total} ({100*indexed//total if total > 0 else 0}%)")

        if self.results['failed_tools']:
            print(f"\n⚠ Failed tools ({len(self.results['failed_tools'])}):")
            for failed in self.results['failed_tools']:
                print(f"  • {failed['name']}: {failed['error']}")

        print("\n" + "=" * 80)

        if callable_count == total:
            print("🎉 SUCCESS: All tools are accessible to the orchestrator!")
        elif callable_count >= total * 0.9:
            print("✓ MOSTLY WORKING: Most tools accessible (>90%)")
        else:
            print("⚠ ISSUES DETECTED: Some tools cannot be accessed")

        print("=" * 80)

    def run_all_tests(self):
        """Run all tests"""
        print("=" * 80)
        print("  MAHER ORCHESTRATOR - TOOL ACCESSIBILITY TEST")
        print("  Testing if orchestrator can access and use all 35 tools")
        print("=" * 80)

        # Test 1: Registry structure
        if not self.test_registry_structure():
            print("\n❌ Registry structure invalid. Aborting.")
            return

        # Test 2: Count resources
        tools = self.count_all_resources()

        if not tools:
            print("\n❌ No tools found in registry. Aborting.")
            return

        # Test 3: Import and callable test
        self.test_all_tools_import(tools)

        # Test 4: Capability index
        self.test_capability_index(tools)

        # Test 5: Orchestrator integration
        self.test_orchestrator_integration()

        # Test 6: Sample execution
        self.test_sample_tool_execution()

        # Summary
        self.print_summary()


def main():
    """Main entry point"""
    tester = OrchestratorToolTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
