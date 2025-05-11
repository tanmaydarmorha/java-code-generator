import os
import json
from typing import Dict, Any, List, Optional, Tuple
from agents.planning_agent import PlanningAgent
from agents.code_generation_agent import CodeGenerationAgent
from agents.validation_agent import ValidationAgent

class JavaCodeGeneratorOrchestrator:
    """
    Orchestrator for the Java code generation process.
    Coordinates the planning, code generation, and validation agents.
    """
    
    def __init__(self, workspace_dir: str = "workspace"):
        """
        Initialize the orchestrator with the necessary agents.
        
        Args:
            workspace_dir: Directory where generated code will be stored
        """
        self.planning_agent = PlanningAgent()
        self.code_generation_agent = CodeGenerationAgent()
        self.validation_agent = ValidationAgent()
        self.workspace_dir = workspace_dir
        
        # Create workspace directory if it doesn't exist
        os.makedirs(workspace_dir, exist_ok=True)
    
    def generate_from_curl(self, curl_command: str, max_attempts: int = 3) -> Tuple[bool, Dict[str, str], str]:
        """
        Generate Java code from a cURL command.
        
        Args:
            curl_command: The cURL command to generate code from
            max_attempts: Maximum number of attempts to generate valid code
            
        Returns:
            Tuple containing (success_flag, generated_files, feedback_message)
        """
        print(f"Starting Java code generation from cURL command...")
        
        # Step 1: Planning - Parse cURL command and create operation plan
        print("Step 1: Planning - Parsing cURL command...")
        operation_plan = self.planning_agent.plan_action(curl_command)
        print(f"Operation plan created:\n{operation_plan}\n")
        
        # Step 2: Code Generation - Generate Java code from operation plan
        print("Step 2: Code Generation - Generating Java code...")
        java_files = self.code_generation_agent.generate_code(operation_plan)
        print(f"Generated {len(java_files)} Java files.")
        
        # Step 3: Validation - Compile and validate the generated code
        print("Step 3: Validation - Compiling and validating code...")
        
        attempt = 1
        success = False
        feedback = ""
        
        while not success and attempt <= max_attempts:
            print(f"Validation attempt {attempt}/{max_attempts}...")
            success, feedback = self.validation_agent.validate_code(java_files, self.workspace_dir)
            
            if success:
                print("Validation successful!")
                break
            
            print(f"Validation failed. Feedback:\n{feedback}\n")
            
            if attempt < max_attempts:
                print("Regenerating code based on feedback...")
                # Use the feedback to improve the code generation
                enhanced_prompt = f"""
                Operation Plan:
                {operation_plan}
                
                Previous code had compilation errors. Please fix the following issues:
                {feedback}
                """
                java_files = self.code_generation_agent.generate_code(enhanced_prompt)
                print(f"Regenerated {len(java_files)} Java files.")
            
            attempt += 1
        
        # Return the results
        return success, java_files, feedback
    
    def save_results(self, success: bool, java_files: Dict[str, str], feedback: str) -> str:
        """
        Save the generation results to disk.
        
        Args:
            success: Whether the code generation was successful
            java_files: Dictionary mapping file paths to Java code
            feedback: Feedback from the validation process
            
        Returns:
            Path to the results directory
        """
        # Create a results directory
        results_dir = os.path.join(self.workspace_dir, "results")
        os.makedirs(results_dir, exist_ok=True)
        
        # Save the Java files
        for filename, content in java_files.items():
            file_path = os.path.join(results_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
        
        # Save the validation feedback
        with open(os.path.join(results_dir, "validation_feedback.txt"), 'w') as f:
            f.write(feedback)
        
        # Save the generation status
        with open(os.path.join(results_dir, "generation_status.json"), 'w') as f:
            json.dump({
                "success": success,
                "file_count": len(java_files),
                "files": list(java_files.keys())
            }, f, indent=2)
        
        return results_dir

# Example usage
if __name__ == "__main__":
    # Example cURL command
    curl_command = '''
    curl -X POST "https://api.example.com/users" \
      -H "Content-Type: application/json" \
      -d '{"name": "John Doe", "email": "john@example.com", "age": 30}'
    '''
    
    # Create the orchestrator
    orchestrator = JavaCodeGeneratorOrchestrator()
    
    # Generate Java code from the cURL command
    success, java_files, feedback = orchestrator.generate_from_curl(curl_command)
    
    # Save the results
    results_dir = orchestrator.save_results(success, java_files, feedback)
    
    # Print the results
    print(f"\nJava code generation {'successful' if success else 'failed'}.")
    print(f"Results saved to: {results_dir}")
    print(f"Generated {len(java_files)} Java files.")
    
    if not success:
        print(f"\nValidation feedback:\n{feedback}")
