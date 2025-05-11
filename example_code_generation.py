import os
import datetime
from agents.code_generation_agent import CodeGenerationAgent

def main():
    # Example operation plan in markdown format (as would be produced by the planning agent)
    operation_plan = """
    # API: `https://api.example.com/users`
    # Operation: `createUser`
    # HTTP Method: `POST`
    # Request Body: `{ "name": "John Doe", "email": "john@example.com", "age": 30 }`
    # Response Body: `{ "id": "123e4567-e89b-12d3-a456-426614174000", "createdAt": "2023-01-01T12:00:00Z" }`
    """
    
    # Create output directory
    output_dir = os.path.join(os.getcwd(), "generated_code")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Creating CodeGenerationAgent with output directory: {output_dir}")
    
    # Create the code generation agent
    agent = CodeGenerationAgent(output_dir=output_dir)
    
    # Create initial state
    state = {
        "operation_plan": operation_plan,
        "timestamp": datetime.datetime.now().isoformat(),
        "save_to_disk": True
    }
    
    print("Generating Java code from operation plan...")
    
    # Run the agent
    result_state = agent.run(state)
    
    # Print the results
    print(f"\nGenerated {result_state['file_count']} Java files:")
    for filename in result_state['java_files'].keys():
        print(f"- {filename}")
    
    print("\nFiles saved to disk:")
    print(result_state['directory_contents'])
    
    return result_state

if __name__ == "__main__":
    main()
