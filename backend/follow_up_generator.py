"""
Follow-Up Question Generator for MAHER AI Orchestrator

Generates contextual follow-up questions based on agent responses
to create a natural conversational flow.
"""

import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def generate_follow_up_questions(
    user_input: str,
    agent_response: str,
    agent_category: str,
    model_client,
    max_questions: int = 3
) -> List[str]:
    """
    Generate follow-up questions using AI based on conversation context
    
    Args:
        user_input: Original user question
        agent_response: Agent's response text
        agent_category: Category/expertise of the agent
        model_client: MAHERModelClient instance for AI generation
        max_questions: Maximum number of follow-up questions to generate
    
    Returns:
        List of follow-up question strings
    """
    
    try:
        # Truncate response if too long (to avoid token limits)
        truncated_response = agent_response[:800] if len(agent_response) > 800 else agent_response
        
        prompt = f"""You are MAHER AI's conversation assistant. Based on the user's question and the agent's response, generate {max_questions} relevant follow-up questions that would help the user.

User Question: "{user_input}"

Agent Response: "{truncated_response}..."

Agent Category: {agent_category}

Generate {max_questions} follow-up questions that:
1. Are directly related to the topic discussed
2. Help the user take logical next steps
3. Explore related aspects they might need
4. Are actionable and specific to their domain
5. Sound natural and conversational

IMPORTANT: Return ONLY a JSON array of strings. No explanations, no markdown, just the array.
Example format: ["Question 1?", "Question 2?", "Question 3?"]
"""
        
        result = model_client.generate(
            prompt=prompt,
            temperature=0.7,
            response_mime_type='application/json'
        )
        
        if result.success:
            questions = json.loads(result.text)
            
            # Validate that we got a list
            if isinstance(questions, list):
                # Filter out empty strings and limit to max_questions
                valid_questions = [q for q in questions if isinstance(q, str) and q.strip()]
                return valid_questions[:max_questions]
            else:
                logger.warning(f"Follow-up generator returned non-list: {type(questions)}")
                return _get_fallback_questions(agent_category)
        else:
            logger.error(f"Follow-up generation failed: {result.error}")
            return _get_fallback_questions(agent_category)
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse follow-up questions JSON: {e}")
        return _get_fallback_questions(agent_category)
    except Exception as e:
        logger.error(f"Error generating follow-up questions: {e}")
        return _get_fallback_questions(agent_category)


def _get_fallback_questions(agent_category: str) -> List[str]:
    """
    Get fallback follow-up questions based on agent category
    
    Args:
        agent_category: Category of the agent
    
    Returns:
        List of generic but relevant follow-up questions
    """
    
    category_lower = agent_category.lower() if agent_category else ""
    
    # Category-specific fallback questions
    if "maintenance" in category_lower:
        return [
            "Would you like me to create a detailed maintenance schedule?",
            "Do you need troubleshooting procedures for common issues?",
            "Should I provide safety requirements for this task?"
        ]
    
    elif "safety" in category_lower:
        return [
            "Would you like a detailed safety checklist?",
            "Do you need emergency response procedures?",
            "Should I include required PPE and equipment?"
        ]
    
    elif "planning" in category_lower or "schedule" in category_lower:
        return [
            "Would you like me to create a detailed timeline?",
            "Do you need resource allocation recommendations?",
            "Should I include risk mitigation strategies?"
        ]
    
    elif "analysis" in category_lower or "report" in category_lower:
        return [
            "Would you like a more detailed analysis?",
            "Do you need recommendations based on this data?",
            "Should I create a summary report?"
        ]
    
    else:
        # Generic fallback questions
        return [
            "Would you like more detailed information on this topic?",
            "Do you need help implementing these recommendations?",
            "Should I provide additional related resources?"
        ]


def generate_contextual_follow_ups(
    conversation_history: List[Dict[str, str]],
    agent_category: str,
    model_client,
    max_questions: int = 3
) -> List[str]:
    """
    Generate follow-up questions based on entire conversation history
    
    Args:
        conversation_history: List of conversation turns [{"role": "user", "content": "..."}, ...]
        agent_category: Category of the agent
        model_client: MAHERModelClient instance
        max_questions: Maximum number of questions
    
    Returns:
        List of follow-up questions
    """
    
    try:
        # Build conversation context
        conversation_text = ""
        for turn in conversation_history[-5:]:  # Last 5 turns
            role = turn.get('role', 'unknown')
            content = turn.get('content', '')
            conversation_text += f"{role.upper()}: {content[:200]}\n"
        
        prompt = f"""You are MAHER AI's conversation assistant. Based on the conversation history, generate {max_questions} relevant follow-up questions.

Conversation History:
{conversation_text}

Agent Category: {agent_category}

Generate {max_questions} follow-up questions that:
1. Build on the conversation naturally
2. Help move the discussion forward
3. Are relevant to the user's needs
4. Sound conversational and helpful

Return ONLY a JSON array of strings.
Example: ["Question 1?", "Question 2?", "Question 3?"]
"""
        
        result = model_client.generate(
            prompt=prompt,
            temperature=0.7,
            response_mime_type='application/json'
        )
        
        if result.success:
            questions = json.loads(result.text)
            if isinstance(questions, list):
                valid_questions = [q for q in questions if isinstance(q, str) and q.strip()]
                return valid_questions[:max_questions]
        
        return _get_fallback_questions(agent_category)
        
    except Exception as e:
        logger.error(f"Error generating contextual follow-ups: {e}")
        return _get_fallback_questions(agent_category)
