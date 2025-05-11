from utils.llms import llm_manager
from utils.prompts import code_generation_system_prompt, code_generation_user_prompt
import re
import os
import json
import datetime
from typing import Dict, List, Any, Callable, Optional
from langchain.schema import Document
from langchain.tools.file_management import FileManagementToolkit
from langchain.tools.file_management.read import ReadFileTool
from langchain.tools.file_management.write import WriteFileTool
from langchain.tools.file_management.list_dir import ListDirectoryTool

class CodeGenerationAgent:
    """
    Code generation agent responsible for generating Java source files from a structured operation plan.
    Uses the CodeLlama model for code generation and provides file system tools for saving files.
    """
    
    def __init__(self, output_dir: str = "generated_code"):
        """
        Initialize the code generation agent with the CodeLlama model and file system tools.
        
        Args:
            output_dir: Directory where generated Java files will be saved
        """
        # Get the CodeLlama model from the LLM manager
        self.model = llm_manager.get_codellama()
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize file system tools using LangChain's FileManagementToolkit
        toolkit = FileManagementToolkit(
            root_dir=self.output_dir,
            selected_tools=["read_file", "write_file", "list_directory"]
        )
        
        # Get the tools
        self.file_tools = toolkit.get_tools()
        
        # Extract individual tools for easier access
        self.read_file_tool = next((tool for tool in self.file_tools if isinstance(tool, ReadFileTool)), None)
        self.write_file_tool = next((tool for tool in self.file_tools if isinstance(tool, WriteFileTool)), None)
        self.list_dir_tool = next((tool for tool in self.file_tools if isinstance(tool, ListDirectoryTool)), None)
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        StateGraph compatible run method that generates Java code based on the operation plan in the state.
        
        Args:
            state: The current state containing the operation plan
            
        Returns:
            Updated state with generated Java files and file paths
        """
        # Extract operation plan from state
        operation_plan = state.get("operation_plan", "")
        
        # Generate Java code
        java_files = self.generate_code(operation_plan)
        
        # Update state with generated files
        state["java_files"] = java_files
        state["file_count"] = len(java_files)
        
        # Create a list of Document objects for each file (useful for retrieval and other LangChain tools)
        documents = []
        for filename, content in java_files.items():
            doc = Document(
                page_content=content,
                metadata={
                    "filename": filename,
                    "type": "java_source",
                    "generated_at": state.get("timestamp", datetime.datetime.now().isoformat())
                }
            )
            documents.append(doc)
        
        state["java_documents"] = documents
        
        # Save files to disk
        if state.get("save_to_disk", True):
            file_paths = self.save_all_files(java_files)
            state["file_paths"] = file_paths
            state["output_dir"] = self.output_dir
            
            # List the contents of the output directory using LangChain's ListDirectoryTool
            dir_contents = self.list_dir_tool.invoke({})
            state["directory_contents"] = dir_contents
        
        return state
    
    def generate_code(self, operation_plan: str) -> Dict[str, str]:
        """
        Generate Java source files based on the structured operation plan.
        
        Args:
            operation_plan: The structured operation plan in markdown format
            
        Returns:
            Dictionary mapping file paths to generated Java code
        """
        system_prompt = code_generation_system_prompt
        user_prompt = code_generation_user_prompt.format(input=operation_plan)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Use the CodeLlama model to generate Java code
        response = self.model.invoke(messages)
        response_content = response.content
        
        # Parse the response to extract individual Java files
        return self._extract_java_files(response_content)
    
    def _extract_java_files(self, response_content: str) -> Dict[str, str]:
        """
        Extract Java files from the LLM response.
        
        Args:
            response_content: The LLM response containing Java code blocks
            
        Returns:
            Dictionary mapping file paths to Java code
        """
        files = {}
        current_file = None
        current_content = []
        
        # First try to extract files using the filename comments
        for line in response_content.split('\n'):
            # Check for filename markers
            if line.strip().startswith('// Filename:') or line.strip().startswith('// filename:'):
                # Save previous file if exists
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content)
                    current_content = []
                
                # Extract new filename
                current_file = line.split(':', 1)[1].strip()
                continue
            
            # If we have a current file, collect its content
            if current_file is not None:
                current_content.append(line)
        
        # Save the last file
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content)
        
        # If no files were extracted using filename comments, try to extract using code blocks
        if not files:
            pattern = r'```java\s*(?:\(([^)]+)\))?\s*\n([\s\S]*?)```'
            matches = re.finditer(pattern, response_content)
            
            for match in matches:
                filename = match.group(1) if match.group(1) else self._infer_filename(match.group(2))
                content = match.group(2).strip()
                files[filename] = content
        
        return files
    
    def _infer_filename(self, content: str) -> str:
        """
        Infer a filename from Java code content.
        
        Args:
            content: Java code content
            
        Returns:
            Inferred filename with .java extension
        """
        # Try to extract class or interface name
        class_match = re.search(r'(public|private)?\s+(class|interface|enum)\s+(\w+)', content)
        if class_match:
            return f"{class_match.group(3)}.java"
        
        # Fallback to a generic name
        return "JavaFile.java"
    
    # Custom methods removed as we're now using LangChain's file tools
    
    def save_all_files(self, java_files: Dict[str, str]) -> Dict[str, str]:
        """
        Save all generated Java files to disk using LangChain's file tools.
        
        Args:
            java_files: Dictionary mapping file paths to Java code
            
        Returns:
            Dictionary mapping file paths to their saved locations
        """
        results = {}
        
        for filename, content in java_files.items():
            # Extract package name to create directory structure
            package_match = re.search(r'package\s+([\w.]+);', content)
            if package_match:
                # Create package directory structure
                package_path = package_match.group(1).replace('.', os.path.sep)
                package_dir = os.path.join(self.output_dir, package_path)
                os.makedirs(package_dir, exist_ok=True)
                
                # Use LangChain's WriteFileTool to write the file
                file_path = os.path.join(package_path, filename)
                result = self.write_file_tool.invoke({
                    "file_path": file_path,
                    "text": content
                })
            else:
                # Use LangChain's WriteFileTool to write the file directly in output_dir
                result = self.write_file_tool.invoke({
                    "file_path": filename,
                    "text": content
                })
            
            results[filename] = result
        
        # Create a summary file with metadata
        summary = {
            "generated_at": str(datetime.datetime.now()),
            "file_count": len(java_files),
            "files": list(java_files.keys())
        }
        
        # Use LangChain's WriteFileTool to write the summary file
        self.write_file_tool.invoke({
            "file_path": "generation_summary.json",
            "text": json.dumps(summary, indent=2)
        })
        
        return results
    
    # Factory method for creating a runnable for StateGraph
    @classmethod
    def create_runnable(cls, output_dir: str = "generated_code") -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Create a runnable function for use with LangChain's StateGraph.
        
        Args:
            output_dir: Directory where generated Java files will be saved
            
        Returns:
            A callable that can be used as a node in a StateGraph
        """
        agent = cls(output_dir=output_dir)
        return agent.run
