#!/usr/bin/env python3
"""
Example script demonstrating how to use the ValidationAgent to validate Java code.
"""

import os
import json
from agents.validation_agent import ValidationAgent

def main():
    # Create a validation agent with a specific workspace directory
    workspace_dir = "validation_example_workspace"
    validation_agent = ValidationAgent(workspace_dir=workspace_dir)
    
    # Sample Java files to validate
    java_files = {
        "Main.java": """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        
        // Create a user and print details
        User user = new User("John Doe", "john@example.com");
        System.out.println("User created: " + user.getName() + " (" + user.getEmail() + ")");
    }
}
""",
        "User.java": """
public class User {
    private String name;
    private String email;
    
    public User(String name, String email) {
        this.name = name;
        this.email = email;
    }
    
    public String getName() {
        return name;
    }
    
    public String getEmail() {
        return email;
    }
    
    @Override
    public String toString() {
        return "User{name='" + name + "', email='" + email + "'}";
    }
}
"""
    }
    
    # Example with valid code
    print("Validating valid Java code...")
    success, feedback, details = validation_agent.validate_code(java_files)
    
    print(f"Validation successful: {success}")
    print(f"Feedback: {feedback}")
    
    # Save validation results to a file
    result_file = validation_agent.save_validation_results(details)
    print(f"Validation results saved to: {result_file}")
    
    # Example with invalid code (introducing a compilation error)
    print("\nValidating invalid Java code...")
    java_files_with_error = {
        "Main.java": """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        
        // Create a user and print details
        User user = new User("John Doe", "john@example.com");
        System.out.println("User created: " + user.getName() + " (" + user.getEmail() + ")");
        
        // Introduce a compilation error
        int x = "This should be a number"; // Type mismatch error
    }
}
""",
        "User.java": """
public class User {
    private String name;
    private String email;
    
    public User(String name, String email) {
        this.name = name;
        this.email = email;
    }
    
    // Missing return type for method (another error)
    getName() {
        return name;
    }
    
    public String getEmail() {
        return email;
    }
}
"""
    }
    
    success, feedback, details = validation_agent.validate_code(java_files_with_error)
    
    print(f"Validation successful: {success}")
    print(f"Feedback: {feedback}")
    
    # Save validation results to a file
    error_result_file = validation_agent.save_validation_results(
        details, 
        output_file="validation_error_results.json"
    )
    print(f"Error validation results saved to: {error_result_file}")

if __name__ == "__main__":
    main()
