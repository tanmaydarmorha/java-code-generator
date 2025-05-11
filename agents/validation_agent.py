from utils.llms import llm_manager
from utils.prompts import validation_system_prompt, validation_user_prompt
import os
import json
import datetime
from typing import Dict, List, Tuple, Optional, Any
from langchain.schema import Document
from langchain_community.tools import ShellTool
from langchain.tools.file_management import FileManagementToolkit
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory

class ValidationAgent:
    """
    Validation agent responsible for compiling and validating the generated Java code.
    Uses the Gemma model with LangChain tools for file operations and shell commands.
    """
    
    def __init__(self, workspace_dir: str = "validation_workspace"):
        """
        Initialize the validation agent with the Gemma model and necessary tools.
        
        Args:
            workspace_dir: Directory where the Java files will be written and compiled
        """
        # Get the Gemma model from the LLM manager
        self.llm = llm_manager.get_gemma()
        self.workspace_dir = workspace_dir
        
        # Create workspace directory if it doesn't exist
        os.makedirs(workspace_dir, exist_ok=True)
        
        # Initialize tools for the agent
        self._initialize_tools()
        
        # Create the agent with tools
        self._create_agent()
    
    def _initialize_tools(self):
        """
        Initialize the tools needed for the validation agent.
        """
        # Shell tool for running commands
        self.shell_tool = ShellTool()
        
        # File management tools
        file_toolkit = FileManagementToolkit(
            root_dir=self.workspace_dir,
            selected_tools=["read_file", "write_file", "list_directory"]
        )
        self.file_tools = file_toolkit.get_tools()
        
        # Combine all tools
        self.tools = [self.shell_tool] + self.file_tools
    
    def _create_agent(self):
        """
        Create the LangChain agent with the tools.
        """
        # Create a prompt template for the agent
        prompt = ChatPromptTemplate.from_messages([
            ("system", validation_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create memory for the agent
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Create the agent
        agent = create_react_agent(self.llm, self.tools, prompt)
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def validate_code(self, java_files: Dict[str, str]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Compile and validate the generated Java code using the LangChain agent.
        
        Args:
            java_files: Dictionary mapping file paths to Java code
            
        Returns:
            Tuple containing (success_flag, feedback_message, detailed_results)
        """
        # Start timestamp for validation
        start_time = datetime.datetime.now()
        
        # Prepare the input for the agent
        files_info = "\n".join([f"- {filename}" for filename in java_files.keys()])
        has_pom = any(filename.lower() == "pom.xml" for filename in java_files.keys())
        build_system = "Maven" if has_pom else "javac"
        
        agent_input = f"""I need to validate the following Java files:
{files_info}

Please perform the following tasks:
1. Save these files to the workspace directory ({self.workspace_dir})
2. Compile the code using {build_system}
3. If compilation succeeds, run the code
4. Analyze any errors (compilation or runtime)
5. Provide detailed feedback

Here are the file contents:
"""
        
        # Add file contents to the input
        for filename, content in java_files.items():
            agent_input += f"\n\n# {filename}\n```java\n{content}\n```"
        
        # Run the agent
        response = self.agent_executor.invoke({"input": agent_input})
        
        # Process the agent's response
        output = response.get("output", "")
        
        # Determine success based on the output
        compilation_success = "compilation successful" in output.lower() or "compiled successfully" in output.lower()
        run_success = "ran successfully" in output.lower() or "execution successful" in output.lower()
        overall_success = compilation_success and run_success
        
        # Prepare detailed results
        detailed_results = {
            "timestamp": start_time.isoformat(),
            "end_time": datetime.datetime.now().isoformat(),
            "compilation_success": compilation_success,
            "run_success": run_success if compilation_success else False,
            "files_validated": list(java_files.keys()),
            "agent_output": output,
            "build_system": build_system
        }
        
        # Return the results
        if overall_success:
            return True, "Validation successful. Code compiled and ran without errors.", detailed_results
        elif compilation_success:
            return False, "Compilation successful but runtime errors occurred.", detailed_results
        else:
            return False, "Compilation failed with errors.", detailed_results
    
    def save_validation_results(self, results: Dict[str, Any], output_file: str = "validation_results.json") -> str:
        """
        Save validation results to a JSON file.
        
        Args:
            results: Validation results dictionary
            output_file: Name of the output file
            
        Returns:
            Path to the saved file
        """
        # Get the write file tool
        write_file_tool = next((tool for tool in self.file_tools if "write_file" in str(tool).lower()), None)
        if not write_file_tool:
            raise ValueError("Write file tool not found in file tools")
        
        # Convert results to JSON
        json_results = json.dumps(results, indent=2)
        
        # Save to file
        file_path = os.path.join(self.workspace_dir, output_file)
        result = write_file_tool.invoke({
            "file_path": output_file,
            "text": json_results
        })
        
        return result
