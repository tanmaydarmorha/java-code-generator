from utils.llms import llm_manager
from utils.prompts import planning_agent_system_prompt, planning_agent_user_prompt

class PlanningAgent:
    """
    Planning agent responsible for planning actions based on the input and system prompt.
    """
    
    def __init__(self):
        """
        Initialize the planning agent with the Qwen model.
        """
        # Get the Qwen model from the LLM manager
        self.model = llm_manager.get_qwen()
    
    def plan_action(self, input: str) -> str:
        """
        Plan an action based on the input and system prompt.
        
        Args:
            input: The input string
            
        Returns:
            String containing the plan
        """
        system_prompt = planning_agent_system_prompt
        
        user_prompt = planning_agent_user_prompt.format(input=input)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Use the Qwen model to analyze the cURL command
        response = self.model.invoke(messages)
        response_content = response.content
        
        return response_content