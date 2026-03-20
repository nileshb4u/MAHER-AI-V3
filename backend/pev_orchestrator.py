"""
MAHER AI Plan-Execute-Verify Orchestrator
Implements the PRD-specified architecture for trustworthy, SME-driven, deterministic AI
Uses LangGraph state machine to prevent hallucinations

Model provider agnostic - uses MAHERModelClient for all AI calls.
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional, TypedDict, Literal, Annotated
from datetime import datetime
from pydantic import BaseModel, Field

# LangGraph imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)


# ============================================================================
# State Definition (Pydantic Models for Type Safety)
# ============================================================================

class SubTask(BaseModel):
    """Individual subtask in the plan"""
    id: str
    description: str
    preferred_resource_type: str
    required_capabilities: List[str]
    priority: int
    dependencies: List[str] = Field(default_factory=list)
    original_input: Optional[str] = None


class ExecutionPlan(BaseModel):
    """Plan created by the Planner"""
    subtasks: List[SubTask]
    execution_strategy: str = "sequential"
    reasoning: str


class ExecutionResult(BaseModel):
    """Result from executing a subtask"""
    subtask_id: str
    resource_id: str
    resource_name: str
    resource_type: str
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    raw_output: Optional[str] = None


class VerificationResult(BaseModel):
    """Result from the Verifier"""
    verified: bool
    confidence_score: float  # 0.0 to 1.0
    reasoning: str
    data_completeness: float  # 0.0 to 1.0
    relevance_score: float  # 0.0 to 1.0
    hallucination_detected: bool
    missing_information: List[str] = Field(default_factory=list)
    action: Literal["accept", "retry", "replan"]


class OrchestratorState(TypedDict):
    """State for the Plan-Execute-Verify graph"""
    # Input
    user_input: str
    user_id: Optional[str]
    user_role: Optional[str]
    request_id: str

    # Planning
    plan: Optional[ExecutionPlan]

    # Execution
    execution_results: List[ExecutionResult]
    raw_data: List[Dict[str, Any]]

    # Verification
    verification: Optional[VerificationResult]

    # Loop control
    retry_count: int
    max_retries: int

    # Final output
    final_answer: Optional[str]
    trace_id: str

    # Metadata
    thinking_trail: List[Dict[str, Any]]


# ============================================================================
# Plan-Execute-Verify Orchestrator
# ============================================================================

class PEVOrchestrator:
    """
    Plan-Execute-Verify Orchestrator
    Implements the architecture pattern from the PRD:
    User Input → Planner → Executor → Verifier → Response
    With loop-back capability if verification fails
    """

    def __init__(
        self,
        registry_path: str = None,
        model_client=None,
        gemini_api_key: str = None,
        max_retries: int = 2
    ):
        """
        Initialize the PEV Orchestrator

        Args:
            registry_path: Path to agent registry
            model_client: MAHERModelClient instance (preferred)
            gemini_api_key: Legacy Gemini API key (used if model_client not provided)
            max_retries: Maximum verification retry attempts
        """
        if registry_path is None:
            registry_path = os.path.join(os.path.dirname(__file__), 'registry.json')

        self.registry_path = registry_path
        self.registry = self._load_registry()
        self.max_retries = max_retries

        # Use provided model client or create one
        if model_client is not None:
            self.model_client = model_client
        else:
            from model_client import get_model_client
            self.model_client = get_model_client(gemini_api_key=gemini_api_key)

        # Build the state graph
        self.graph = self._build_graph()

    def _load_registry(self) -> Dict:
        """Load the capability registry"""
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return {"resources": {}, "capability_index": {}}

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine for Plan-Execute-Verify

        Flow:
        START → Planner → Executor → Verifier → [accept/retry decision]
                  ↑                               ↓
                  └─────────── replan ────────────┘
        """
        workflow = StateGraph(OrchestratorState)

        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("executor", self._executor_node)
        workflow.add_node("verifier", self._verifier_node)

        # Set entry point
        workflow.set_entry_point("planner")

        # Add edges
        workflow.add_edge("planner", "executor")
        workflow.add_edge("executor", "verifier")

        # Conditional edge from verifier
        workflow.add_conditional_edges(
            "verifier",
            self._should_continue,
            {
                "accept": END,
                "retry": "planner",
                "max_retries": END
            }
        )

        return workflow.compile()

    # ========================================================================
    # Node Implementations
    # ========================================================================

    def _planner_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        PLANNER NODE (Integration Hub Core)

        Responsibilities:
        1. Intent Recognition - Analyze user input
        2. Dynamic Lookup - Check available domain agents
        3. Task Decomposition - Break into dependency graph
        4. Constraint Enforcement - Only route to available agents
        """
        logger.info(f"[PLANNER] Analyzing request (attempt {state['retry_count'] + 1})")

        # Track thinking
        state['thinking_trail'].append({
            'step': 'Planning',
            'status': 'in_progress',
            'description': 'Analyzing request and creating execution plan',
            'timestamp': datetime.now().isoformat()
        })

        # Get available agents from registry
        available_agents = self._get_available_agents()

        # If this is a retry, include previous verification feedback
        retry_context = ""
        if state['retry_count'] > 0 and state.get('verification'):
            verification = state['verification']
            retry_context = f"""
PREVIOUS ATTEMPT FAILED VERIFICATION:
- Reason: {verification.reasoning}
- Missing Information: {', '.join(verification.missing_information)}
- Data Completeness: {verification.data_completeness * 100}%
- Relevance Score: {verification.relevance_score * 100}%

You MUST create a BETTER plan that addresses these issues.
"""

        # Create planning prompt
        planning_prompt = f"""You are the MAHER AI Planner - the architect of the Integration Hub Core.

Your mission: Analyze the user's request and create a precise execution plan.

USER REQUEST: "{state['user_input']}"
USER ROLE: {state.get('user_role', 'Unknown')}

{retry_context}

AVAILABLE DOMAIN AGENTS (The Library):
{json.dumps(available_agents, indent=2)}

YOUR PLANNING PROCESS:

STEP 1: INTENT RECOGNITION
- What is the user trying to accomplish?
- What domain(s) does this fall under?
- Is this a question, command, or analysis request?

STEP 2: DYNAMIC LOOKUP
- Which domain agents from the library can handle this?
- What specific capabilities are needed?
- Are there any dependencies between tasks?

STEP 3: TASK DECOMPOSITION
- Break the request into atomic subtasks
- Each subtask = ONE specific action
- Define clear dependencies
- Order by priority

STEP 4: CONSTRAINT ENFORCEMENT
- ONLY use agents/tools from the available list above
- Do NOT invent capabilities that don't exist
- If no perfect match, use the closest available agent

OUTPUT FORMAT (strict JSON):
{{
  "subtasks": [
    {{
      "id": "subtask_1",
      "description": "Specific, actionable task description",
      "preferred_resource_type": "ai_agent|tool|workflow",
      "required_capabilities": ["capability1", "capability2"],
      "priority": 1,
      "dependencies": []
    }}
  ],
  "execution_strategy": "sequential|parallel",
  "reasoning": "WHY this plan will successfully answer the user's request with ZERO hallucination"
}}

CRITICAL: Your plan MUST be backed by actual data sources. Do NOT create tasks that will require making up information."""

        try:
            # Use model client for planning
            result = self.model_client.generate(
                prompt=planning_prompt,
                temperature=0.1,
                response_mime_type='application/json',
            )

            if not result.success:
                raise Exception(f"Planning model call failed: {result.error}")

            plan_dict = json.loads(result.text)

            # Convert to Pydantic model
            subtasks = [SubTask(**st) for st in plan_dict.get('subtasks', [])]
            for subtask in subtasks:
                subtask.original_input = state['user_input']

            plan = ExecutionPlan(
                subtasks=subtasks,
                execution_strategy=plan_dict.get('execution_strategy', 'sequential'),
                reasoning=plan_dict.get('reasoning', '')
            )

            state['plan'] = plan

            # Update thinking trail
            state['thinking_trail'][-1]['status'] = 'completed'
            state['thinking_trail'][-1]['result'] = {
                'subtasks_count': len(plan.subtasks),
                'execution_strategy': plan.execution_strategy,
                'reasoning': plan.reasoning
            }

            logger.info(f"[PLANNER] Created plan with {len(plan.subtasks)} subtasks")

        except Exception as e:
            logger.error(f"[PLANNER] Failed: {e}")
            state['thinking_trail'][-1]['status'] = 'failed'
            state['thinking_trail'][-1]['error'] = str(e)
            # Create minimal fallback plan
            state['plan'] = ExecutionPlan(
                subtasks=[SubTask(
                    id="fallback_1",
                    description=state['user_input'],
                    preferred_resource_type="ai_agent",
                    required_capabilities=["natural_language_processing"],
                    priority=1
                )],
                execution_strategy="sequential",
                reasoning="Fallback plan due to planning error"
            )

        return state

    def _executor_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        EXECUTOR NODE (Task Manager)

        Responsibilities:
        1. Routing - Dispatch tasks to correct Domain Agents
        2. Data Aggregation - Collect raw outputs (JSON, SQL results, logs)
        3. Context Passing - Pass output from Agent A to Agent B
        """
        logger.info(f"[EXECUTOR] Executing {len(state['plan'].subtasks)} subtasks")

        state['thinking_trail'].append({
            'step': 'Execution',
            'status': 'in_progress',
            'description': f'Executing {len(state["plan"].subtasks)} subtasks',
            'timestamp': datetime.now().isoformat()
        })

        execution_results = []
        raw_data = []

        # Import execution logic from HybridOrchestrator
        from hybrid_orchestrator import HybridOrchestrator
        executor = HybridOrchestrator(
            registry_path=self.registry_path,
            model_client=self.model_client,
        )

        # Execute each subtask
        for subtask in state['plan'].subtasks:
            try:
                # Match resources
                matched_resources = executor.match_resources(subtask.dict())

                if not matched_resources:
                    logger.warning(f"[EXECUTOR] No resource matched for subtask: {subtask.id}")
                    execution_results.append(ExecutionResult(
                        subtask_id=subtask.id,
                        resource_id="none",
                        resource_name="No Match",
                        resource_type="none",
                        success=False,
                        error="No matching resource found"
                    ))
                    continue

                # Execute with best matched resource
                resource = matched_resources[0]

                # Use asyncio to execute
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        executor.execute_resource(resource, subtask.dict())
                    )
                finally:
                    loop.close()

                # Convert to ExecutionResult
                result_data = result.get('result', {})
                execution_results.append(ExecutionResult(
                    subtask_id=subtask.id,
                    resource_id=result.get('resource_id', ''),
                    resource_name=result.get('resource_name', ''),
                    resource_type=result.get('resource_type', ''),
                    success=result_data.get('success', False),
                    data=result_data,
                    raw_output=result_data.get('response', result_data.get('message', ''))
                ))

                # Collect raw data for verification
                raw_data.append({
                    'subtask': subtask.description,
                    'data': result_data,
                    'source': result.get('resource_name', '')
                })

            except Exception as e:
                logger.error(f"[EXECUTOR] Error executing subtask {subtask.id}: {e}")
                execution_results.append(ExecutionResult(
                    subtask_id=subtask.id,
                    resource_id="error",
                    resource_name="Error",
                    resource_type="error",
                    success=False,
                    error=str(e)
                ))

        state['execution_results'] = execution_results
        state['raw_data'] = raw_data

        # Update thinking trail
        successful = sum(1 for r in execution_results if r.success)
        state['thinking_trail'][-1]['status'] = 'completed'
        state['thinking_trail'][-1]['result'] = {
            'total': len(execution_results),
            'successful': successful,
            'failed': len(execution_results) - successful
        }

        logger.info(f"[EXECUTOR] Completed: {successful}/{len(execution_results)} successful")

        return state

    def _verifier_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        VERIFIER NODE (Quality Control - Hallucination Prevention)

        Responsibilities:
        1. Self-Correction - Compare raw data against original question
        2. Looping - Reject insufficient/irrelevant data, send back to Planner
        3. Citation Enforcement - Ensure claims backed by data

        This is the KEY component that prevents hallucinations.
        """
        logger.info("[VERIFIER] Verifying execution results against original request")

        state['thinking_trail'].append({
            'step': 'Verification',
            'status': 'in_progress',
            'description': 'Verifying results for hallucinations and completeness',
            'timestamp': datetime.now().isoformat()
        })

        # Prepare verification prompt
        verification_prompt = f"""You are the MAHER AI Verifier - the Quality Control Auditor.

Your critical mission: PREVENT HALLUCINATIONS by rigorously verifying execution results.

ORIGINAL USER REQUEST: "{state['user_input']}"

EXECUTION PLAN THAT WAS EXECUTED:
{json.dumps([st.dict() for st in state['plan'].subtasks], indent=2)}

RAW DATA COLLECTED FROM DOMAIN AGENTS:
{json.dumps(state['raw_data'], indent=2)}

EXECUTION RESULTS:
{json.dumps([r.dict() for r in state['execution_results']], indent=2)}

YOUR VERIFICATION CHECKLIST:

1. DATA COMPLETENESS (0.0 to 1.0):
   - Does the raw data contain enough information to answer the user's question?
   - Are there any critical pieces of information missing?
   - Rate: 1.0 = Complete, 0.0 = No useful data

2. RELEVANCE SCORE (0.0 to 1.0):
   - Is the collected data actually relevant to the user's request?
   - Does it address what the user asked for?
   - Rate: 1.0 = Perfectly relevant, 0.0 = Completely irrelevant

3. HALLUCINATION DETECTION:
   - Can the user's question be answered SOLELY using the raw data above?
   - Would answering require making up ANY information not present in the data?
   - If YES to making up info → hallucination_detected = true

4. CITATION ENFORCEMENT:
   - Can every claim in a potential answer be backed by the raw data?
   - Are all sources clearly identifiable?

5. QUALITY DECISION:
   - If data_completeness >= 0.7 AND relevance_score >= 0.7 AND hallucination_detected = false → action = "accept"
   - If retry_count < max_retries AND (data_completeness < 0.7 OR relevance_score < 0.7) → action = "retry"
   - Otherwise → action = "accept" (with warning about limitations)

OUTPUT FORMAT (strict JSON):
{{
  "verified": true|false,
  "confidence_score": 0.0-1.0,
  "reasoning": "Detailed explanation of verification decision",
  "data_completeness": 0.0-1.0,
  "relevance_score": 0.0-1.0,
  "hallucination_detected": true|false,
  "missing_information": ["list", "of", "missing", "items"],
  "action": "accept|retry"
}}

CURRENT RETRY COUNT: {state['retry_count']}
MAX RETRIES: {state['max_retries']}

BE RUTHLESS: Better to retry than to hallucinate!"""

        try:
            # Use model client for verification
            result = self.model_client.generate(
                prompt=verification_prompt,
                temperature=0.0,
                response_mime_type='application/json',
            )

            if not result.success:
                raise Exception(f"Verification model call failed: {result.error}")

            verification_dict = json.loads(result.text)

            # Convert to Pydantic model
            verification = VerificationResult(**verification_dict)
            state['verification'] = verification

            # Update thinking trail
            state['thinking_trail'][-1]['status'] = 'completed'
            state['thinking_trail'][-1]['result'] = {
                'verified': verification.verified,
                'confidence': verification.confidence_score,
                'data_completeness': verification.data_completeness,
                'relevance': verification.relevance_score,
                'hallucination_detected': verification.hallucination_detected,
                'action': verification.action
            }

            logger.info(f"[VERIFIER] Result: {verification.action} (confidence: {verification.confidence_score})")

        except Exception as e:
            logger.error(f"[VERIFIER] Failed: {e}")
            state['thinking_trail'][-1]['status'] = 'failed'
            state['thinking_trail'][-1]['error'] = str(e)
            # Fallback: accept but with low confidence
            state['verification'] = VerificationResult(
                verified=True,
                confidence_score=0.5,
                reasoning=f"Verification failed: {str(e)}. Accepting results with caution.",
                data_completeness=0.5,
                relevance_score=0.5,
                hallucination_detected=False,
                action="accept"
            )

        return state

    def _should_continue(self, state: OrchestratorState) -> str:
        """
        Conditional edge: Decide whether to accept, retry, or stop

        Returns:
            "accept" - Results verified, proceed to final answer
            "retry" - Need to replan and retry
            "max_retries" - Hit max retries, accept anyway with warning
        """
        verification = state.get('verification')

        if not verification:
            return "accept"

        if verification.action == "retry" and state['retry_count'] < state['max_retries']:
            logger.warning(f"[VERIFIER] Retry requested. Incrementing retry count.")
            state['retry_count'] += 1
            return "retry"
        elif verification.action == "retry" and state['retry_count'] >= state['max_retries']:
            logger.warning(f"[VERIFIER] Max retries reached. Accepting anyway.")
            return "max_retries"
        else:
            return "accept"

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agents from registry"""
        agents = []

        # Get AI agents from database
        try:
            from models import Agent, AgentStatus, SessionLocal
            db = SessionLocal()
            published_agents = db.query(Agent).filter(
                Agent.status == AgentStatus.PUBLISHED
            ).all()

            for agent in published_agents:
                agents.append({
                    'id': agent.agent_id,
                    'name': agent.name,
                    'type': 'ai_agent',
                    'description': agent.description,
                    'category': agent.category,
                    'capabilities': [agent.category.lower().replace(' ', '_')]
                })

            db.close()
        except Exception as e:
            logger.error(f"Error loading agents from database: {e}")

        # Get tools and workflows from registry
        for tool in self.registry.get('resources', {}).get('tools', []):
            agents.append({
                'id': tool.get('id'),
                'name': tool.get('name'),
                'type': 'tool',
                'description': tool.get('description'),
                'capabilities': tool.get('capabilities', [])
            })

        for workflow in self.registry.get('resources', {}).get('workflows', []):
            agents.append({
                'id': workflow.get('id'),
                'name': workflow.get('name'),
                'type': 'workflow',
                'description': workflow.get('description'),
                'capabilities': workflow.get('capabilities', [])
            })

        return agents

    def _compile_final_answer(self, state: OrchestratorState) -> str:
        """
        Compile the final answer from verified execution results

        This is called ONLY after verification passes.
        All claims MUST be backed by raw data.
        """
        logger.info("[COMPILER] Compiling final answer with citation enforcement")

        # Prepare compilation prompt
        compilation_prompt = f"""You are the MAHER AI Response Compiler.

Your mission: Create a user-friendly answer using ONLY the verified data below.

ORIGINAL USER REQUEST: "{state['user_input']}"

VERIFIED RAW DATA (These are your ONLY sources):
{json.dumps(state['raw_data'], indent=2)}

VERIFICATION RESULT:
- Data Completeness: {state['verification'].data_completeness * 100}%
- Relevance Score: {state['verification'].relevance_score * 100}%
- Confidence: {state['verification'].confidence_score * 100}%

RULES FOR COMPILATION:
1. ONLY use information present in the verified raw data above
2. If the data is incomplete, ACKNOWLEDGE the limitations
3. Cite sources where appropriate (mention which agent/tool provided the data)
4. Be clear, professional, and helpful
5. NEVER make up information not present in the raw data
6. If verification shows low confidence, include a disclaimer

OUTPUT: Natural language response (NOT JSON)"""

        try:
            result = self.model_client.generate(
                prompt=compilation_prompt,
                system_instruction='Be professional, clear, and NEVER hallucinate.',
                temperature=0.3,
            )

            if not result.success:
                raise Exception(f"Compilation failed: {result.error}")

            final_answer = result.text

            # Add warning if verification had issues
            if state['verification'].confidence_score < 0.7:
                final_answer = f"⚠️ Note: This response is based on limited data (confidence: {state['verification'].confidence_score * 100:.0f}%)\n\n{final_answer}"

            if state['retry_count'] >= state['max_retries'] and state['verification'].action == "retry":
                final_answer = f"⚠️ Note: Maximum verification attempts reached. Response may be incomplete.\n\n{final_answer}"

            return final_answer

        except Exception as e:
            logger.error(f"[COMPILER] Failed: {e}")
            return f"I encountered an error while compiling the response: {str(e)}"

    # ========================================================================
    # Main Processing Method
    # ========================================================================

    def process_request(
        self,
        user_input: str,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point: Process user request through Plan-Execute-Verify cycle

        Args:
            user_input: User's request
            user_id: Optional user ID
            user_role: Optional user role (for context)

        Returns:
            Response with verified answer and trace information
        """
        request_id = f"REQ-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        trace_id = f"TRACE-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}"

        logger.info(f"[PEV] Processing request {request_id}: {user_input[:100]}...")

        # Initialize state
        initial_state: OrchestratorState = {
            'user_input': user_input,
            'user_id': user_id,
            'user_role': user_role,
            'request_id': request_id,
            'plan': None,
            'execution_results': [],
            'raw_data': [],
            'verification': None,
            'retry_count': 0,
            'max_retries': self.max_retries,
            'final_answer': None,
            'trace_id': trace_id,
            'thinking_trail': []
        }

        try:
            # Run through the state graph
            final_state = self.graph.invoke(initial_state)

            # Compile final answer
            final_answer = self._compile_final_answer(final_state)
            final_state['final_answer'] = final_answer

            # Calculate hallucination rate metric
            hallucination_detected = final_state['verification'].hallucination_detected if final_state.get('verification') else False

            return {
                'success': True,
                'request_id': request_id,
                'trace_id': trace_id,
                'answer': final_answer,
                'verification': {
                    'verified': final_state['verification'].verified if final_state.get('verification') else False,
                    'confidence_score': final_state['verification'].confidence_score if final_state.get('verification') else 0.0,
                    'data_completeness': final_state['verification'].data_completeness if final_state.get('verification') else 0.0,
                    'relevance_score': final_state['verification'].relevance_score if final_state.get('verification') else 0.0,
                    'hallucination_detected': hallucination_detected,
                    'retry_count': final_state['retry_count']
                },
                'execution_summary': {
                    'total_subtasks': len(final_state['plan'].subtasks) if final_state.get('plan') else 0,
                    'successful': sum(1 for r in final_state['execution_results'] if r.success),
                    'failed': sum(1 for r in final_state['execution_results'] if not r.success),
                    'strategy': final_state['plan'].execution_strategy if final_state.get('plan') else 'unknown'
                },
                'thinking_process': final_state['thinking_trail'],
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"[PEV] Error processing request: {e}")
            return {
                'success': False,
                'request_id': request_id,
                'trace_id': trace_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
