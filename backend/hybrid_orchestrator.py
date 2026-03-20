"""
MAHER AI Hybrid Orchestrator
Intelligently routes requests to AI Agents, Workflows, or Tools

Model provider agnostic - uses MAHERModelClient for all AI calls.
"""

import json
import os
import asyncio
import importlib
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from models import Agent, AgentStatus, SessionLocal

logger = logging.getLogger(__name__)


class HybridOrchestrator:
    """
    Hybrid Orchestrator that can leverage:
    - AI Agents (from database)
    - Workflows (Python modules)
    - Tools (local functions or REST APIs)
    """

    def __init__(self, registry_path: str = None, model_client=None, gemini_api_key: str = None):
        """
        Initialize the hybrid orchestrator

        Args:
            registry_path: Path to registry.json file
            model_client: MAHERModelClient instance (preferred)
            gemini_api_key: Legacy Gemini API key (used if model_client not provided)
        """
        if registry_path is None:
            registry_path = os.path.join(os.path.dirname(__file__), 'registry.json')

        self.registry_path = registry_path
        self.registry = self._load_registry()

        # Use provided model client or create one
        if model_client is not None:
            self.model_client = model_client
        else:
            from model_client import get_model_client
            self.model_client = get_model_client(gemini_api_key=gemini_api_key)

        # Feedback storage
        self.feedback_path = os.path.join(os.path.dirname(__file__), 'feedback_store.json')

    def _load_registry(self) -> Dict:
        """Load the capability registry"""
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return {"resources": {}, "capability_index": {}}

    def _get_ai_agents_from_db(self) -> List[Dict[str, Any]]:
        """Load published AI agents from database"""
        try:
            db = SessionLocal()
            published_agents = db.query(Agent).filter(
                Agent.status == AgentStatus.PUBLISHED
            ).all()

            agents_list = []
            for agent in published_agents:
                agents_list.append({
                    'id': agent.agent_id,
                    'name': agent.name,
                    'description': agent.description,
                    'category': agent.category,
                    'system_prompt': agent.system_prompt,
                    'capabilities': [agent.category.lower().replace(' ', '_')]
                })

            db.close()
            return agents_list
        except Exception as e:
            logger.error(f"Error loading agents from database: {e}")
            return []

    async def decompose_task(self, user_input: str) -> Dict[str, Any]:
        """
        Decompose user request into subtasks and identify required capabilities
        Uses the unified model client for reasoning and planning.

        Args:
            user_input: User's request

        Returns:
            Task decomposition with subtasks and required capabilities
        """
        decomposition_prompt = f"""You are an expert task decomposition system for MAHER AI orchestrator.

Your job: Analyze the user's request and create an execution plan.

USER REQUEST: "{user_input}"

STEP 1: DETECT FILES FIRST
Look for "Files provided:" in the request above. If present, extract:
- Filename and extension (.xlsx, .docx, .pdf, etc.)
- File path
If files are present, this is a DOCUMENT OPERATION, not a general question!

STEP 2: ANALYZE THE REQUEST
- What does the user want to do with the file(s)?
- If .xlsx/.xls file: This is an Excel file
- If .docx/.doc file: This is a Word file
- If .pdf file: This is a PDF file

STEP 3: MATCH TO OPERATION
Common operations:
- "convert to PDF" + Excel file (.xlsx) = Use excel_to_pdf capability
- "convert to PDF" + Word file (.docx) = Use word_to_pdf capability
- "convert to Word" + PDF file (.pdf) = Use pdf_to_word capability
- "read" or "extract" + any file = Use appropriate reader tool

STEP 4: CREATE SUBTASKS
- Each subtask = ONE tool operation
- Include the actual file path from the request in the description
- Choose MOST SPECIFIC capability

AVAILABLE CAPABILITIES:

DOCUMENT PROCESSING (use 'tool' resource type):
- excel_to_pdf: Convert Excel (.xlsx/.xls) to PDF ← Use this for Excel → PDF
- excel_processing: Read, create, modify Excel files
- word_to_pdf: Convert Word (.docx/.doc) to PDF ← Use this for Word → PDF
- word_processing: Create, edit Word documents
- pdf_to_word: Convert PDF to Word ← Use this for PDF → Word
- pdf_processing: Merge, split, extract from PDFs
- document_conversion: General document format conversions
- ocr: Extract text from images/scanned documents
- email_automation: Draft, send, parse emails

CRITICAL RULES FOR FILE OPERATIONS:
1. If you see "Files provided:" → This is a FILE OPERATION, use 'tool' resource type
2. Extract file extension → .xlsx = Excel, .docx = Word, .pdf = PDF
3. Match operation + file type:
   - Excel + "PDF" → excel_to_pdf capability
   - Word + "PDF" → word_to_pdf capability
   - PDF + "Word" → pdf_to_word capability
4. Include file path in subtask description
5. NEVER use ai_agent for file conversions!

For general questions (NO files): Use ai_agent with natural_language_processing

OUTPUT FORMAT (JSON):
{{
  "subtasks": [
    {{
      "id": "subtask_1",
      "description": "SPECIFIC description with file path if applicable",
      "preferred_resource_type": "tool|ai_agent",
      "required_capabilities": ["most_specific_capability", "backup_capability"],
      "priority": 1,
      "dependencies": []
    }}
  ],
  "execution_strategy": "sequential",
  "reasoning": "WHY you chose these subtasks and capabilities"
}}

EXAMPLES:

Example 1 (File Upload - Excel to PDF):
User: "convert the attached file into pdf

Files provided:
- sales_data.xlsx (.xlsx, 15234 bytes) at path: /tmp/maher_123/sales_data.xlsx

Use the file paths above to process the documents."

Output:
{{
  "subtasks": [{{
    "id": "subtask_1",
    "description": "Convert Excel file at /tmp/maher_123/sales_data.xlsx to PDF format",
    "preferred_resource_type": "tool",
    "required_capabilities": ["excel_to_pdf", "document_conversion", "excel_processing"],
    "priority": 1,
    "dependencies": []
  }}],
  "execution_strategy": "sequential",
  "reasoning": "File detected: Excel (.xlsx). User wants PDF conversion. Using excel_to_pdf capability with tool resource type."
}}

Example 2 (No File - General Question):
User: "How do I maintain a centrifugal pump?"

Output:
{{
  "subtasks": [{{
    "id": "subtask_1",
    "description": "Provide maintenance guidance for centrifugal pump",
    "preferred_resource_type": "ai_agent",
    "required_capabilities": ["natural_language_processing", "maintenance_planning"],
    "priority": 1,
    "dependencies": []
  }}],
  "execution_strategy": "sequential",
  "reasoning": "No files provided. General maintenance question. Using AI agent."
}}

NOW ANALYZE THE USER REQUEST ABOVE AND RESPOND IN JSON FORMAT:"""

        try:
            # Use model client for task decomposition
            result = self.model_client.generate(
                prompt=decomposition_prompt,
                temperature=0.1,
                response_mime_type='application/json',
            )

            if not result.success:
                raise Exception(f"Task decomposition failed: {result.error}")

            decomposition = json.loads(result.text)

            # Validate decomposition
            if not decomposition.get('subtasks'):
                logger.warning("Decomposition returned no subtasks, creating default")
                decomposition = {
                    "subtasks": [{
                        "id": "subtask_1",
                        "description": user_input,
                        "preferred_resource_type": "ai_agent",
                        "required_capabilities": ["natural_language_processing"],
                        "priority": 1,
                        "dependencies": []
                    }],
                    "execution_strategy": "sequential",
                    "reasoning": "Default fallback task"
                }

            return decomposition

        except Exception as e:
            logger.error(f"Task decomposition failed: {e}")
            # Fallback: treat as single task
            return {
                "subtasks": [{
                    "id": "subtask_1",
                    "description": user_input,
                    "preferred_resource_type": "ai_agent",
                    "required_capabilities": ["natural_language_processing"],
                    "priority": 1,
                    "dependencies": []
                }],
                "execution_strategy": "sequential",
                "reasoning": "Fallback to simple AI agent processing"
            }

    async def adaptive_replan(self, user_input: str, failed_subtasks: List[Dict[str, Any]], available_tools: List[str]) -> Dict[str, Any]:
        """
        Re-plan the task when initial tool matching fails

        Args:
            user_input: Original user request
            failed_subtasks: Subtasks that couldn't be matched to tools
            available_tools: List of available tool names

        Returns:
            Revised task decomposition
        """
        replan_prompt = f"""URGENT: The original task plan failed because some capabilities weren't available.

ORIGINAL REQUEST: "{user_input}"

FAILED SUBTASKS (no tools found):
{json.dumps(failed_subtasks, indent=2)}

AVAILABLE TOOLS IN SYSTEM:
{', '.join(available_tools[:50])}  # Show sample of available tools

YOUR JOB: Create a NEW plan that uses ONLY available tools OR uses AI to answer directly.

DECISION TREE:
1. Is this a document conversion request?
   - If Excel→PDF AND "Excel to PDF Converter" is available: Use it
   - If Word→PDF AND "Word to PDF Converter" is available: Use it
   - If PDF→Word AND "PDF to Word Converter" is available: Use it

2. Is this a general question/explanation request?
   - Use ai_agent with natural_language_processing capability

3. Is this a document processing task?
   - Match to available document tools (PDF, Word, Excel tools)

4. Can't match to any tool?
   - Fall back to AI agent for general response

OUTPUT (JSON):
{{
  "subtasks": [{{
    "id": "subtask_1",
    "description": "Revised subtask description",
    "preferred_resource_type": "tool|ai_agent",
    "required_capabilities": ["available_capability"],
    "priority": 1,
    "dependencies": []
  }}],
  "execution_strategy": "sequential",
  "reasoning": "Why this revised plan works with available tools"
}}

BE PRACTICAL: If no tool can handle it, use AI agent to answer the user's question directly."""

        try:
            result = self.model_client.generate(
                prompt=replan_prompt,
                temperature=0.2,
                response_mime_type='application/json',
            )

            if not result.success:
                raise Exception(f"Replanning failed: {result.error}")

            revised_plan = json.loads(result.text)
            return revised_plan

        except Exception as e:
            logger.error(f"Adaptive replanning failed: {e}")
            # Ultra fallback - just use AI
            return {
                "subtasks": [{
                    "id": "subtask_1",
                    "description": user_input,
                    "preferred_resource_type": "ai_agent",
                    "required_capabilities": ["natural_language_processing"],
                    "priority": 1,
                    "dependencies": []
                }],
                "execution_strategy": "sequential",
                "reasoning": "Fallback to AI after replanning failure"
            }

    def match_resources(self, subtask: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Match a subtask to appropriate resources from registry

        Args:
            subtask: Subtask dictionary with required capabilities

        Returns:
            List of matched resources sorted by priority
        """
        required_caps = subtask.get('required_capabilities', [])
        preferred_type = subtask.get('preferred_resource_type', 'ai_agent')

        matched_resources = []

        # Search in capability index
        for capability in required_caps:
            resource_ids = self.registry.get('capability_index', {}).get(capability, [])

            for resource_id in resource_ids:
                # Check if already matched
                if any(r['id'] == resource_id for r in matched_resources):
                    continue

                # Find resource in registry
                resource = self._find_resource_by_id(resource_id)

                if resource:
                    matched_resources.append(resource)

        # If no matches, fall back to AI agents
        if not matched_resources:
            ai_agents = self._get_ai_agents_from_db()
            if ai_agents:
                matched_resources.append({
                    'id': ai_agents[0]['id'],
                    'name': ai_agents[0]['name'],
                    'type': 'ai_agent',
                    'system_prompt': ai_agents[0].get('system_prompt', ''),
                    'priority': 3
                })

        # Sort by priority (lower number = higher priority) and preferred type
        matched_resources.sort(key=lambda x: (
            0 if x.get('type', x.get('resource_type')) == preferred_type else 1,
            x.get('priority', 99)
        ))

        return matched_resources

    def _find_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Find a resource in the registry by ID"""
        resources = self.registry.get('resources', {})

        # Check workflows
        for workflow in resources.get('workflows', []):
            if workflow.get('id') == resource_id:
                return {**workflow, 'type': 'workflow'}

        # Check tools
        for tool in resources.get('tools', []):
            if tool.get('id') == resource_id:
                return {**tool, 'type': 'tool'}

        # Check AI agents
        if resource_id == 'dynamic':
            ai_agents = self._get_ai_agents_from_db()
            if ai_agents:
                return {
                    'id': 'ai_agents_db',
                    'name': 'AI Agents',
                    'type': 'ai_agent_pool',
                    'agents': ai_agents,
                    'priority': 3
                }

        return None

    async def execute_resource(self, resource: Dict[str, Any], subtask: Dict[str, Any],
                               retry_count: int = 0, max_retries: int = 2) -> Dict[str, Any]:
        """
        Execute a resource (workflow, tool, or AI agent)

        Args:
            resource: Resource definition
            subtask: Subtask to execute
            retry_count: Current retry attempt
            max_retries: Maximum number of retries

        Returns:
            Execution result
        """
        resource_type = resource.get('type', 'ai_agent')

        try:
            if resource_type == 'workflow':
                result = await self._execute_workflow(resource, subtask)
            elif resource_type == 'tool':
                result = await self._execute_tool(resource, subtask)
            elif resource_type in ['ai_agent', 'ai_agent_pool']:
                result = await self._execute_ai_agent(resource, subtask)
            else:
                result = {
                    'success': False,
                    'error': f'Unknown resource type: {resource_type}'
                }

            return {
                'subtask_id': subtask.get('id'),
                'resource_id': resource.get('id'),
                'resource_name': resource.get('name'),
                'resource_type': resource_type,
                'result': result,
                'retry_count': retry_count
            }

        except Exception as e:
            logger.error(f"Error executing resource {resource.get('name')}: {e}")

            # Retry logic
            if retry_count < max_retries:
                logger.info(f"Retrying {resource.get('name')} (attempt {retry_count + 1}/{max_retries})")
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self.execute_resource(resource, subtask, retry_count + 1, max_retries)

            return {
                'subtask_id': subtask.get('id'),
                'resource_id': resource.get('id'),
                'resource_name': resource.get('name'),
                'resource_type': resource_type,
                'result': {
                    'success': False,
                    'error': str(e),
                    'status': 'incomplete'
                },
                'retry_count': retry_count
            }

    async def _execute_workflow(self, resource: Dict[str, Any], subtask: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Python workflow module"""
        module_path = resource.get('module_path')
        function_name = resource.get('function')

        if not module_path or not function_name:
            raise ValueError("Workflow missing module_path or function")

        # Import the module
        module = importlib.import_module(module_path)
        func = getattr(module, function_name)

        # Extract parameters from subtask or use defaults
        params = self._extract_parameters(subtask, resource.get('parameters', {}))

        # Execute the workflow function
        if asyncio.iscoroutinefunction(func):
            result = await func(**params)
        else:
            result = func(**params)

        return result

    async def _execute_tool(self, resource: Dict[str, Any], subtask: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool (local function or REST API)"""
        tool_type = resource.get('type_detail', resource.get('tool_type', 'local_function'))

        if tool_type == 'rest_api':
            return await self._execute_rest_api_tool(resource, subtask)
        else:
            return await self._execute_local_function_tool(resource, subtask)

    async def _execute_local_function_tool(self, resource: Dict[str, Any], subtask: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a local function tool"""
        module_path = resource.get('module_path')
        function_name = resource.get('function')

        if not module_path or not function_name:
            raise ValueError("Tool missing module_path or function")

        # Import the module
        module = importlib.import_module(module_path)
        func = getattr(module, function_name)

        # Extract parameters
        params = self._extract_parameters(subtask, resource.get('parameters', {}))

        # Execute
        if asyncio.iscoroutinefunction(func):
            result = await func(**params)
        else:
            # Run synchronous function in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: func(**params))

        return result

    async def _execute_rest_api_tool(self, resource: Dict[str, Any], subtask: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a REST API tool"""
        endpoint = resource.get('endpoint')
        method = resource.get('method', 'POST').upper()

        # In production, this would call actual REST endpoints
        # For now, return mock response
        return {
            'success': True,
            'message': f'REST API call to {endpoint} would be made here',
            'method': method,
            'note': 'Implement actual REST API integration in production'
        }

    async def _execute_ai_agent(self, resource: Dict[str, Any], subtask: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an AI agent using the unified model client"""
        # Get agent details
        if resource.get('type') == 'ai_agent_pool':
            agents = resource.get('agents', [])
            if not agents:
                raise ValueError("No agents available")
            agent = agents[0]
            system_prompt = agent.get('system_prompt', '')
        else:
            system_prompt = resource.get('system_prompt', '')

        # Use unified model client
        result = self.model_client.generate(
            prompt=subtask.get('description', ''),
            system_instruction=system_prompt if system_prompt else None,
        )

        if not result.success:
            return {
                'success': False,
                'error': result.error or 'AI agent execution failed',
            }

        return {
            'success': True,
            'response': result.text
        }

    def _extract_parameters(self, subtask: Dict[str, Any], param_schema: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract parameters from subtask description using AI

        This is a simplified version - in production, you'd use more sophisticated
        parameter extraction
        """
        import re

        params = {}

        description = subtask.get('description', '')
        description_lower = description.lower()

        # Get original input if available (contains file paths)
        original_input = subtask.get('original_input', '')

        logger.debug(f"Extracting parameters from subtask description: {description[:200]}...")

        # Extract file paths from description first, then fallback to original input
        # Looks for patterns like: "at path: /path/to/file.ext" or "at path: C:\path\to\file.ext"
        # Updated regex to handle paths with spaces and both Unix and Windows paths
        file_path_pattern = r'at path:\s*([^\n]+?)(?=\s*(?:Use the file|\n|$))'
        file_paths = re.findall(file_path_pattern, description)

        # If no file paths found in description, search in original input
        if not file_paths and original_input:
            logger.debug("No file paths in subtask description, searching original input...")
            file_paths = re.findall(file_path_pattern, original_input)

        # Additional fallback: try to find temp directory paths (more generic pattern)
        if not file_paths:
            logger.debug("Trying alternative file path patterns...")
            # Match temp paths or absolute paths with file extensions
            alt_pattern = r'(/tmp/[^\s\n]+\.[a-zA-Z0-9]+|[A-Za-z]:[\\\/][^\s\n]+\.[a-zA-Z0-9]+)'
            search_text = original_input if original_input else description
            file_paths = re.findall(alt_pattern, search_text)

        # Strip trailing whitespace and punctuation from extracted paths
        file_paths = [path.strip().rstrip('.,;:)') for path in file_paths]

        logger.info(f"Extracted {len(file_paths)} file paths: {file_paths}")

        for param_name, param_type in param_schema.items():
            # Handle file path parameters
            if 'file' in param_name or 'path' in param_name:
                if file_paths:
                    # Assign file paths based on parameter name
                    if 'input' in param_name and len(file_paths) > 0:
                        params[param_name] = file_paths[0]
                        logger.debug(f"Set {param_name} = {file_paths[0]}")
                    elif 'output' in param_name:
                        # Generate output path based on input file
                        if file_paths:
                            import os
                            import tempfile
                            input_path = file_paths[0]
                            base_name = os.path.splitext(os.path.basename(input_path))[0]
                            # Determine output extension based on param name or description
                            if 'pdf' in param_name.lower() or 'pdf' in description_lower:
                                ext = '.pdf'
                            elif 'word' in param_name.lower() or 'docx' in description_lower or 'doc' in description_lower:
                                ext = '.docx'
                            elif 'excel' in param_name.lower() or 'xlsx' in description_lower:
                                ext = '.xlsx'
                            elif 'csv' in param_name.lower():
                                ext = '.csv'
                            else:
                                ext = '.pdf'  # Default to PDF
                            temp_dir = tempfile.gettempdir()
                            output_path = os.path.join(temp_dir, f"{base_name}_output{ext}")
                            params[param_name] = output_path
                            logger.debug(f"Set {param_name} = {output_path}")
                        else:
                            logger.warning(f"Cannot generate output path for {param_name} - no input files found")
                    elif 'pdf' in param_name and file_paths:
                        params[param_name] = file_paths[0]
                        logger.debug(f"Set {param_name} = {file_paths[0]}")
                    elif 'image' in param_name and file_paths:
                        params[param_name] = file_paths[0]
                        logger.debug(f"Set {param_name} = {file_paths[0]}")
                    elif file_paths:
                        params[param_name] = file_paths[0]
                        logger.debug(f"Set {param_name} = {file_paths[0]}")
                else:
                    logger.warning(f"No file paths found for required parameter '{param_name}'. This may cause tool execution to fail.")
                    logger.debug(f"Searched in description: {description[:100]}...")
                    if original_input:
                        logger.debug(f"Searched in original input: {original_input[:100]}...")
                continue

            if 'equipment_type' in param_name:
                # Try to extract equipment type
                if 'pump' in description_lower:
                    params[param_name] = 'pump'
                elif 'compressor' in description_lower:
                    params[param_name] = 'compressor'
                elif 'motor' in description_lower:
                    params[param_name] = 'motor'
                else:
                    params[param_name] = 'pump'  # Default

            elif 'maintenance_level' in param_name or 'maintenance_type' in param_name:
                if 'routine' in description_lower:
                    params[param_name] = 'routine'
                elif 'corrective' in description_lower:
                    params[param_name] = 'corrective'
                else:
                    params[param_name] = 'preventive'  # Default

            elif 'query' in param_name:
                params[param_name] = subtask.get('description', '')

            elif param_type == 'int':
                params[param_name] = 30  # Default

            elif param_type == 'float':
                params[param_name] = 2.0  # Default

            elif param_type == 'boolean' or param_type == 'bool':
                params[param_name] = True

            elif param_type == 'list':
                params[param_name] = []

            elif param_type == 'dict':
                params[param_name] = {'description': subtask.get('description', '')}

            else:
                params[param_name] = subtask.get('description', '')

        logger.info(f"Extracted parameters for tool: {params}")
        return params

    async def execute_parallel(self, resources_and_subtasks: List[tuple]) -> List[Dict[str, Any]]:
        """Execute multiple resources in parallel"""
        tasks = [
            self.execute_resource(resource, subtask)
            for resource, subtask in resources_and_subtasks
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Parallel execution error: {result}")
                processed_results.append({
                    'success': False,
                    'error': str(result)
                })
            else:
                processed_results.append(result)

        return processed_results

    async def execute_sequential(self, resources_and_subtasks: List[tuple]) -> List[Dict[str, Any]]:
        """Execute resources sequentially"""
        results = []

        for resource, subtask in resources_and_subtasks:
            result = await self.execute_resource(resource, subtask)
            results.append(result)

        return results

    def compile_answers(self, results: List[Dict[str, Any]], original_request: str) -> str:
        """
        Compile the actual answers from all subtask results into a coherent response

        Args:
            results: List of execution results
            original_request: Original user request

        Returns:
            Compiled answer string ready for user display
        """
        successful_results = [r for r in results if r.get('result', {}).get('success', False)]

        if not successful_results:
            return "I apologize, but I encountered difficulties processing your request. Please try rephrasing or contact support."

        compiled_parts = []

        for result in successful_results:
            result_data = result.get('result', {})
            resource_type = result.get('resource_type', '')

            # Extract the actual answer/response based on resource type
            if resource_type in ['ai_agent', 'ai_agent_pool']:
                # AI agent response
                response_text = result_data.get('response', '')
                if response_text:
                    compiled_parts.append(response_text)

            elif resource_type == 'tool':
                # Tool execution result - could be file path, data, or message
                if 'output_file' in result_data:
                    # File conversion/generation tool
                    output_file = result_data.get('output_file', '')
                    message = result_data.get('message', '')
                    compiled_parts.append(f"{message}\nOutput file: {output_file}")
                elif 'message' in result_data:
                    compiled_parts.append(result_data.get('message', ''))
                elif 'data' in result_data:
                    # Structured data result
                    import json
                    compiled_parts.append(f"Result:\n{json.dumps(result_data.get('data'), indent=2)}")
                else:
                    # Generic success message
                    compiled_parts.append(f"Task completed successfully using {result.get('resource_name', 'tool')}")

            elif resource_type == 'workflow':
                # Workflow result
                if 'output' in result_data:
                    compiled_parts.append(result_data.get('output', ''))
                elif 'message' in result_data:
                    compiled_parts.append(result_data.get('message', ''))
                else:
                    compiled_parts.append(f"Workflow completed successfully")

        # Combine all parts into a coherent answer
        if len(compiled_parts) == 1:
            return compiled_parts[0]
        elif len(compiled_parts) > 1:
            # Multiple subtasks - combine with clear separation
            return "\n\n".join(compiled_parts)
        else:
            return "Task completed successfully."

    def integrate_results(self, results: List[Dict[str, Any]], original_request: str) -> Dict[str, Any]:
        """
        Integrate multiple results into a unified response

        Args:
            results: List of execution results
            original_request: Original user request

        Returns:
            Integrated response with user-friendly messaging
        """
        # Separate successful and failed results
        successful = [r for r in results if r.get('result', {}).get('success', False)]
        failed = [r for r in results if not r.get('result', {}).get('success', False)]

        # Build integrated response
        integration = {
            'total_subtasks': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'results': []
        }

        # Add successful results with better formatting
        for result in successful:
            result_data = result.get('result', {})
            integration['results'].append({
                'resource': result.get('resource_name'),
                'type': result.get('resource_type'),
                'data': result_data,
                'status': 'completed'
            })

        # If there are failures, add them with detailed context
        if failed:
            integration['incomplete_tasks'] = [
                {
                    'resource': r.get('resource_name'),
                    'error': r.get('result', {}).get('error', 'Unknown error'),
                    'retry_count': r.get('retry_count', 0),
                    'status': 'failed'
                }
                for r in failed
            ]

            # Add user-friendly summary message
            if len(successful) > 0:
                integration['summary'] = f"Partially completed: {len(successful)} out of {len(results)} tasks succeeded. Some tools encountered errors."
            else:
                integration['summary'] = f"All {len(results)} tasks failed. The system will attempt to help using AI capabilities."

        else:
            # All successful
            integration['summary'] = f"All {len(results)} tasks completed successfully."

        return integration

    def save_feedback(self, request_id: str, rating: int, feedback_text: str = "") -> Dict[str, Any]:
        """
        Save user feedback

        Args:
            request_id: Unique request ID
            rating: Rating from 1-5 stars
            feedback_text: Optional feedback text

        Returns:
            Confirmation
        """
        try:
            # Load existing feedback
            if os.path.exists(self.feedback_path):
                with open(self.feedback_path, 'r') as f:
                    feedback_store = json.load(f)
            else:
                feedback_store = {'feedback': []}

            # Add new feedback
            feedback_entry = {
                'request_id': request_id,
                'rating': rating,
                'feedback_text': feedback_text,
                'timestamp': datetime.now().isoformat()
            }

            feedback_store['feedback'].append(feedback_entry)

            # Save
            with open(self.feedback_path, 'w') as f:
                json.dump(feedback_store, f, indent=2)

            logger.info(f"Saved feedback for request {request_id}: {rating} stars")

            return {
                'success': True,
                'message': 'Feedback saved successfully'
            }

        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get feedback statistics"""
        try:
            if not os.path.exists(self.feedback_path):
                return {
                    'total_feedback': 0,
                    'average_rating': 0,
                    'rating_distribution': {}
                }

            with open(self.feedback_path, 'r') as f:
                feedback_store = json.load(f)

            feedback_list = feedback_store.get('feedback', [])

            if not feedback_list:
                return {
                    'total_feedback': 0,
                    'average_rating': 0,
                    'rating_distribution': {}
                }

            ratings = [f['rating'] for f in feedback_list]
            avg_rating = sum(ratings) / len(ratings)

            distribution = {}
            for i in range(1, 6):
                distribution[i] = ratings.count(i)

            return {
                'total_feedback': len(feedback_list),
                'average_rating': round(avg_rating, 2),
                'rating_distribution': distribution
            }

        except Exception as e:
            logger.error(f"Error getting feedback stats: {e}")
            return {
                'total_feedback': 0,
                'average_rating': 0,
                'error': str(e)
            }

    async def _handle_with_ai_fallback(
        self,
        request_id: str,
        user_input: str,
        reason: str,
        failure_context: str = None,
        decomposition: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Gracefully handle requests using AI when tools are unavailable or fail

        Args:
            request_id: Unique request ID
            user_input: Original user request
            reason: Why we're falling back to AI
            failure_context: Details about tool failures (if any)
            decomposition: Original task decomposition (if available)

        Returns:
            AI-generated response with clear indication of fallback
        """
        logger.info(f"Using AI fallback for request {request_id}: {reason}")

        # Construct AI prompt with context
        ai_prompt = f"""You are MAHER AI Assistant. The user has made a request, but the specialized tools for this task are currently unavailable or failed to execute.

User Request: "{user_input}"

Reason for AI fallback: {reason}
"""

        if failure_context:
            ai_prompt += f"""
Tool Execution Failures:
{failure_context}
"""

        ai_prompt += """
Please respond to the user's request using your general knowledge and capabilities. Be helpful and provide the best answer you can.

IMPORTANT: At the start of your response, briefly acknowledge that specialized tools weren't available for this task, then proceed to help the user with your AI capabilities."""

        try:
            # Use unified model client for AI fallback
            result = self.model_client.generate(
                prompt=ai_prompt,
                system_instruction='Be professional, clear, and helpful.',
                temperature=0.7,
            )

            if not result.success:
                raise Exception(result.error or 'AI fallback generation failed')

            ai_response = result.text

            return {
                'success': True,
                'request_id': request_id,
                'answer': ai_response,  # <<< THE ACTUAL COMPILED ANSWER FOR THE USER
                'handled_by': 'ai_fallback',
                'fallback_reason': reason,
                'response': ai_response,  # Keep for backwards compatibility
                'execution_summary': {
                    'total_subtasks': 0,
                    'successful': 0,
                    'failed': 0,
                    'strategy': 'ai_fallback',
                    'message': 'Request handled by AI due to unavailable or failed tools'
                },
                'results': {
                    'total_subtasks': 0,
                    'successful': 0,
                    'failed': 0,
                    'results': [{
                        'resource': f'AI Agent ({self.model_client.get_active_provider()})',
                        'type': 'ai_agent',
                        'data': {
                            'success': True,
                            'response': ai_response,
                            'note': f'Handled by AI because: {reason}'
                        }
                    }]
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"AI fallback also failed: {e}")
            return {
                'success': False,
                'request_id': request_id,
                'error': 'Both tool execution and AI fallback failed',
                'details': {
                    'tool_failure_reason': reason,
                    'ai_failure_reason': str(e)
                },
                'suggestion': 'Please try rephrasing your request or contact support',
                'timestamp': datetime.now().isoformat()
            }

    async def process_request(self, user_input: str) -> Dict[str, Any]:
        """
        Main orchestration method - processes user request end-to-end

        Args:
            user_input: User's request

        Returns:
            Complete orchestrated response with thinking process
        """
        request_id = f"REQ-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        logger.info(f"Processing request {request_id}: {user_input[:100]}...")

        # Initialize thinking trail for transparency
        thinking_trail = []

        thinking_trail.append({
            'step': 'Task Analysis',
            'status': 'in_progress',
            'description': 'Analyzing your request and breaking it down into subtasks...',
            'timestamp': datetime.now().isoformat()
        })

        # Step 1: Decompose task
        decomposition = await self.decompose_task(user_input)

        subtasks = decomposition.get('subtasks', [])
        execution_strategy = decomposition.get('execution_strategy', 'sequential')

        logger.info(f"Decomposed into {len(subtasks)} subtasks with {execution_strategy} execution")

        thinking_trail[-1]['status'] = 'completed'
        thinking_trail[-1]['result'] = {
            'subtasks_identified': len(subtasks),
            'execution_strategy': execution_strategy,
            'reasoning': decomposition.get('reasoning', ''),
            'subtasks': [
                {
                    'id': st.get('id'),
                    'description': st.get('description'),
                    'required_capabilities': st.get('required_capabilities', []),
                    'preferred_resource': st.get('preferred_resource_type')
                }
                for st in subtasks
            ]
        }

        # Step 2: Match resources for each subtask
        thinking_trail.append({
            'step': 'Tool Selection',
            'status': 'in_progress',
            'description': 'Searching for the best tools and agents to handle each subtask...',
            'timestamp': datetime.now().isoformat()
        })

        execution_plan = []
        tool_matches = []

        for subtask in subtasks:
            matched_resources = self.match_resources(subtask)

            if matched_resources:
                # Use the best match (first in sorted list)
                # Store original user input in subtask for parameter extraction
                subtask['original_input'] = user_input
                execution_plan.append((matched_resources[0], subtask))

                tool_matches.append({
                    'subtask': subtask.get('description'),
                    'selected_tool': matched_resources[0].get('name'),
                    'tool_type': matched_resources[0].get('type'),
                    'reason': f"Best match for capabilities: {', '.join(subtask.get('required_capabilities', []))}"
                })
            else:
                logger.warning(f"No resource matched for subtask: {subtask.get('description')}")
                tool_matches.append({
                    'subtask': subtask.get('description'),
                    'selected_tool': 'None',
                    'tool_type': 'no_match',
                    'reason': 'No suitable tool found for required capabilities'
                })

        thinking_trail[-1]['status'] = 'completed'
        thinking_trail[-1]['result'] = {
            'tools_matched': len(execution_plan),
            'tools_needed': len(subtasks),
            'matches': tool_matches
        }

        # ADAPTIVE REPLANNING: If some/all tools didn't match, try to replan
        if len(execution_plan) < len(subtasks):
            logger.warning(f"Only {len(execution_plan)}/{len(subtasks)} tools matched. Attempting adaptive replanning...")

            thinking_trail.append({
                'step': 'Adaptive Replanning',
                'status': 'in_progress',
                'description': 'Initial tool selection incomplete. Revising plan based on available tools...',
                'timestamp': datetime.now().isoformat()
            })

            # Get list of failed subtasks
            failed_subtasks = [st for st in subtasks if st not in [ep[1] for ep in execution_plan]]

            # Get available tool names from registry
            available_tools = []
            for tool in self.registry.get('resources', {}).get('tools', []):
                available_tools.append(tool.get('name', ''))

            # Try adaptive replanning
            try:
                revised_plan = await self.adaptive_replan(user_input, failed_subtasks, available_tools)

                # Re-match with revised plan
                revised_execution_plan = []
                for revised_subtask in revised_plan.get('subtasks', []):
                    matched = self.match_resources(revised_subtask)
                    if matched:
                        revised_subtask['original_input'] = user_input
                        revised_execution_plan.append((matched[0], revised_subtask))

                if revised_execution_plan:
                    logger.info(f"Adaptive replanning successful! Matched {len(revised_execution_plan)} tools")
                    execution_plan = revised_execution_plan
                    subtasks = revised_plan.get('subtasks', [])
                    decomposition = revised_plan

                    thinking_trail[-1]['status'] = 'completed'
                    thinking_trail[-1]['result'] = {
                        'replanning_successful': True,
                        'revised_subtasks': len(subtasks),
                        'tools_matched': len(execution_plan),
                        'reasoning': revised_plan.get('reasoning', '')
                    }
                else:
                    thinking_trail[-1]['status'] = 'completed'
                    thinking_trail[-1]['result'] = 'Replanning attempted but no tools matched revised plan'

            except Exception as e:
                logger.error(f"Adaptive replanning failed: {e}")
                thinking_trail[-1]['status'] = 'failed'
                thinking_trail[-1]['result'] = f'Replanning error: {str(e)}'

        # Final fallback to AI if still no tools matched
        if not execution_plan:
            logger.warning(f"No tools matched after replanning. Falling back to AI agent.")

            thinking_trail.append({
                'step': 'AI Fallback',
                'status': 'in_progress',
                'description': 'No specialized tools available after replanning. Using AI knowledge to answer your request...',
                'reason': 'No suitable tools found for this request',
                'timestamp': datetime.now().isoformat()
            })

            result = await self._handle_with_ai_fallback(
                request_id,
                user_input,
                reason="No suitable tools found for this request (even after replanning)",
                decomposition=decomposition
            )

            thinking_trail[-1]['status'] = 'completed'
            thinking_trail[-1]['result'] = 'AI provided response using general knowledge'

            result['thinking_process'] = thinking_trail
            return result

        # Step 3: Execute resources
        thinking_trail.append({
            'step': 'Execution',
            'status': 'in_progress',
            'description': f'Executing {len(execution_plan)} task(s) using selected tools...',
            'execution_strategy': execution_strategy,
            'timestamp': datetime.now().isoformat()
        })

        if execution_strategy == 'parallel' and len(execution_plan) > 1:
            results = await self.execute_parallel(execution_plan)
        else:
            results = await self.execute_sequential(execution_plan)

        # Step 4: Integrate results
        integrated = self.integrate_results(results, user_input)

        thinking_trail[-1]['status'] = 'completed'
        thinking_trail[-1]['result'] = {
            'successful': integrated['successful'],
            'failed': integrated['failed'],
            'summary': integrated.get('summary', '')
        }

        # Check if all tasks failed - if so, fall back to AI
        if integrated['successful'] == 0 and integrated['failed'] > 0:
            logger.warning(f"All tool executions failed. Falling back to AI agent.")

            thinking_trail.append({
                'step': 'AI Fallback (After Tool Failure)',
                'status': 'in_progress',
                'description': 'All tools encountered errors. Using AI to help with your request...',
                'reason': 'Tools were found but all executions failed',
                'failures': integrated.get('incomplete_tasks', []),
                'timestamp': datetime.now().isoformat()
            })

            failure_context = "\n".join([
                f"- {task['resource']}: {task['error']}"
                for task in integrated.get('incomplete_tasks', [])
            ])

            result = await self._handle_with_ai_fallback(
                request_id,
                user_input,
                reason=f"Tools were found but all executions failed",
                failure_context=failure_context,
                decomposition=decomposition
            )

            thinking_trail[-1]['status'] = 'completed'
            thinking_trail[-1]['result'] = 'AI provided alternative response'

            result['thinking_process'] = thinking_trail
            return result

        # Step 5: Compile the final answer from all subtask results
        compiled_answer = self.compile_answers(results, user_input)

        return {
            'success': True,
            'request_id': request_id,
            'answer': compiled_answer,  # <<< THE ACTUAL COMPILED ANSWER FOR THE USER
            'decomposition': decomposition,
            'execution_summary': {
                'total_subtasks': len(subtasks),
                'successful': integrated['successful'],
                'failed': integrated['failed'],
                'strategy': execution_strategy
            },
            'results': integrated,
            'thinking_process': thinking_trail,
            'timestamp': datetime.now().isoformat()
        }
