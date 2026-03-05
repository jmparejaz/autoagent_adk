"""
ADK Adapter Module - Converts parametric skills and workflows to ADK tools

This module provides the critical conversion layer between the parametric
agentic platform's skill system and Google ADK's tool system.
"""

from typing import Dict, List, Any, Callable, Optional, Union, TYPE_CHECKING
from google.adk.tools import FunctionTool
from backend.models.schemas import Skill
import inspect
import json
from datetime import datetime

# Optional import for workflow support
if TYPE_CHECKING:
    from backend.models.schemas import Workflow


def generate_args_doc(arguments: Union[List[Dict[str, Any]], Dict[str, Any]]) -> str:
    """
    Generate argument documentation from skill arguments.
    
    Args:
        arguments: List of argument dictionaries or dictionary of argument specs
        
    Returns:
        Formatted argument documentation string
    """
    if not arguments:
        return "No arguments required"
    
    args_list = []
    
    # Handle both list and dict formats
    if isinstance(arguments, list):
        for arg_spec in arguments:
            arg_name = arg_spec.get('name', 'unknown')
            arg_type = arg_spec.get('type', 'Any')
            arg_desc = arg_spec.get('description', 'No description')
            required = arg_spec.get('required', False)
            
            req_marker = " (required)" if required else " (optional)"
            args_list.append(f"{arg_name}: {arg_type} - {arg_desc}{req_marker}")
    else:  # dict format
        for arg_name, arg_spec in arguments.items():
            arg_type = arg_spec.get('type', 'Any')
            arg_desc = arg_spec.get('description', 'No description')
            required = arg_spec.get('required', False)
            
            req_marker = " (required)" if required else " (optional)"
            args_list.append(f"{arg_name}: {arg_type} - {arg_desc}{req_marker}")
    
    return "\n".join(args_list)


def markdown_skill_to_adk_tool(skill: Skill) -> FunctionTool:
    """
    Convert a markdown skill to an ADK FunctionTool.
    
    This function creates a Python callable that executes the skill's code
    and wraps it in an ADK FunctionTool for use by ADK agents.
    
    Args:
        skill: Skill object loaded from markdown
        
    Returns:
        FunctionTool that can be used by ADK agents
        
    Raises:
        ValueError: If skill is missing required fields
        ImportError: If skill code has import errors
    """
    # Validate required skill fields
    if not skill.tool_name:
        raise ValueError(f"Skill '{skill.tool_name}' is missing required 'tool_name' field")
    if not skill.execution_code:
        raise ValueError(f"Skill '{skill.tool_name}' is missing required 'execution_code' field")
    
    # Create the skill execution function
    def skill_function(**arguments):
        """Execute the skill with provided arguments"""
        # Create local context for skill execution
        local_context = {
            'arguments': arguments,
            'skill_name': skill.tool_name,
            'execution_time': datetime.now().isoformat(),
            'result': None,
            'error': None
        }
        
        try:
            # Execute the skill code in the local context
            exec(skill.execution_code, {}, local_context)
            
            # Return the result or raise error if present
            if local_context.get('error'):
                raise Exception(f"Skill execution error: {local_context['error']}")
            
            return local_context.get('result', "Skill completed successfully")
            
        except Exception as e:
            raise Exception(f"Error executing skill '{skill.tool_name}': {str(e)}")
    
    # Generate comprehensive docstring
    docstring = f"""
    {skill.description or 'No description provided'}
    
    This skill performs: {skill.tool_name}
    
    Args:
        {generate_args_doc(skill.arguments or {})}
    
    Returns:
        Result of skill execution
    """
    
    skill_function.__name__ = f"skill_{skill.tool_name.replace(' ', '_').lower()}"
    skill_function.__doc__ = docstring.strip()
    
    # Create and return FunctionTool
    return FunctionTool(skill_function)


def workflow_to_adk_tool(workflow: Any) -> FunctionTool:  # Type: Workflow when available
    """
    Convert a workflow to an ADK FunctionTool.
    
    This function creates a Python callable that executes the workflow
    and wraps it in an ADK FunctionTool for use by ADK agents.
    
    Args:
        workflow: Workflow object to convert
        
    Returns:
        FunctionTool that can be used by ADK agents
        
    Raises:
        ValueError: If workflow is missing required fields
    """
    # Validate required workflow fields
    if not workflow.name:
        raise ValueError(f"Workflow '{workflow.name}' is missing required 'name' field")
    if not workflow.steps or len(workflow.steps) == 0:
        raise ValueError(f"Workflow '{workflow.name}' has no steps defined")
    
    def workflow_function(**inputs):
        """Execute the workflow with provided inputs"""
        results = {}
        execution_log = []
        
        try:
            # Execute each step in the workflow
            for step_index, step in enumerate(workflow.steps):
                step_name = step.get('name', f'step_{step_index + 1}')
                step_type = step.get('type', 'unknown')
                
                # Execute the step
                step_result = execute_workflow_step(step, inputs, results)
                
                # Store results and log execution
                results[step_name] = step_result
                execution_log.append({
                    'step': step_name,
                    'type': step_type,
                    'result': step_result,
                    'timestamp': datetime.now().isoformat()
                })
            
            return {
                'final_result': results.get(workflow.steps[-1].get('name', 'final_step')),
                'all_results': results,
                'execution_log': execution_log
            }
            
        except Exception as e:
            raise Exception(f"Error executing workflow '{workflow.name}': {str(e)}")
    
    def execute_workflow_step(step: Dict[str, Any], inputs: Dict[str, Any], 
                            previous_results: Dict[str, Any]) -> Any:
        """Execute a single workflow step"""
        step_type = step.get('type', 'unknown')
        
        if step_type == 'skill':
            skill_name = step.get('skill', '')
            skill_args = step.get('arguments', {})
            
            # Resolve arguments from inputs and previous results
            resolved_args = {}
            for arg_name, arg_value in skill_args.items():
                if isinstance(arg_value, str) and arg_value.startswith('${{') and arg_value.endswith('}}'):
                    # Variable reference
                    var_path = arg_value[3:-3]
                    if var_path.startswith('inputs.'):
                        var_name = var_path[7:]
                        resolved_args[arg_name] = inputs.get(var_name)
                    elif var_path.startswith('results.'):
                        var_name = var_path[8:]
                        resolved_args[arg_name] = previous_results.get(var_name)
                    else:
                        resolved_args[arg_name] = arg_value
                else:
                    resolved_args[arg_name] = arg_value
            
            # Execute the skill (this would use the actual skill execution)
            # For now, return a mock result
            return f"Executed skill '{skill_name}' with args: {resolved_args}"
            
        elif step_type == 'conditional':
            condition = step.get('condition', '')
            true_step = step.get('true_step', {})
            false_step = step.get('false_step', {})
            
            # Evaluate condition (simplified for now)
            condition_result = eval(condition, {}, {**inputs, **previous_results})
            
            if condition_result:
                return execute_workflow_step(true_step, inputs, previous_results)
            else:
                return execute_workflow_step(false_step, inputs, previous_results)
                
        elif step_type == 'parallel':
            parallel_steps = step.get('steps', [])
            parallel_results = {}
            
            for parallel_step in parallel_steps:
                step_result = execute_workflow_step(parallel_step, inputs, previous_results)
                parallel_results[parallel_step.get('name', 'parallel_step')] = step_result
            
            return parallel_results
            
        else:
            return f"Executed {step_type} step: {step.get('description', 'no description')}"
    
    # Generate workflow docstring
    step_descriptions = []
    for i, step in enumerate(workflow.steps):
        step_descriptions.append(f"{i+1}. {step.get('name', 'unnamed_step')} ({step.get('type', 'unknown')}): {step.get('description', 'no description')}")
    
    joined_descriptions = "\n".join(step_descriptions)
    args_doc = generate_args_doc(workflow.inputs or {})
    
    workflow_doc = f"""
    {workflow.description or 'No description provided'}
    
    This workflow executes the following steps:
    
    {joined_descriptions}
    
    Args:
        {args_doc}
    
    Returns:
        Dictionary containing final result, all intermediate results, and execution log
    """
    
    workflow_function.__name__ = f"workflow_{workflow.name.replace(' ', '_').lower()}"
    workflow_function.__doc__ = workflow_doc.strip()
    
    return FunctionTool(workflow_function)


class HybridToolRegistry:
    """
    Hybrid tool registry that manages both static ADK tools and dynamically
    converted skills/workflows.
    
    This registry provides a unified interface for tool management across
    the parametric agentic platform and Google ADK.
    """
    
    def __init__(self):
        self.static_tools: Dict[str, FunctionTool] = {}
        self.dynamic_tools: Dict[str, FunctionTool] = {}
        self.skill_tools: Dict[str, FunctionTool] = {}
        self.workflow_tools: Dict[str, FunctionTool] = {}
    
    def register_static_tool(self, name: str, tool: FunctionTool):
        """Register a static ADK tool"""
        self.static_tools[name] = tool
    
    def register_skill_tool(self, skill: Skill) -> FunctionTool:
        """Register a skill by converting it to an ADK tool"""
        tool = markdown_skill_to_adk_tool(skill)
        self.skill_tools[skill.tool_name] = tool
        self.dynamic_tools[skill.tool_name] = tool
        return tool
    
    def register_workflow_tool(self, workflow: Any) -> FunctionTool:  # Type: Workflow when available
        """Register a workflow by converting it to an ADK tool"""
        tool = workflow_to_adk_tool(workflow)
        self.workflow_tools[workflow.name] = tool
        self.dynamic_tools[workflow.name] = tool
        return tool
    
    def get_tool(self, name: str) -> Optional[FunctionTool]:
        """Get a tool by name from any category"""
        return self.static_tools.get(name) or \
               self.skill_tools.get(name) or \
               self.workflow_tools.get(name) or \
               self.dynamic_tools.get(name)
    
    def get_all_tools(self) -> List[FunctionTool]:
        """Get all tools from all categories"""
        all_tools = []
        all_tools.extend(self.static_tools.values())
        all_tools.extend(self.skill_tools.values())
        all_tools.extend(self.workflow_tools.values())
        all_tools.extend(self.dynamic_tools.values())
        return all_tools
    
    def get_tools_by_category(self, category: str) -> List[FunctionTool]:
        """Get tools by category (static, skill, workflow, dynamic)"""
        if category == 'static':
            return list(self.static_tools.values())
        elif category == 'skill':
            return list(self.skill_tools.values())
        elif category == 'workflow':
            return list(self.workflow_tools.values())
        elif category == 'dynamic':
            return list(self.dynamic_tools.values())
        else:
            return []
    
    def clear_category(self, category: str):
        """Clear all tools from a specific category"""
        if category == 'static':
            self.static_tools.clear()
        elif category == 'skill':
            self.skill_tools.clear()
        elif category == 'workflow':
            self.workflow_tools.clear()
        elif category == 'dynamic':
            self.dynamic_tools.clear()
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get comprehensive information about all registered tools"""
        return {
            'total_tools': len(self.get_all_tools()),
            'static_tools': len(self.static_tools),
            'skill_tools': len(self.skill_tools),
            'workflow_tools': len(self.workflow_tools),
            'dynamic_tools': len(self.dynamic_tools),
            'tool_names': list(self.static_tools.keys()) + \
                          list(self.skill_tools.keys()) + \
                          list(self.workflow_tools.keys())
        }


def create_hybrid_tool_registry() -> HybridToolRegistry:
    """
    Create and initialize a HybridToolRegistry with default tools.
    
    Returns:
        Initialized HybridToolRegistry instance
    """
    registry = HybridToolRegistry()
    
    # Add some basic static tools
    def echo_tool(text: str) -> str:
        """Echo the input text back"""
        return text
    
    def get_timestamp() -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()
    
    registry.register_static_tool('echo', FunctionTool(echo_tool))
    registry.register_static_tool('get_timestamp', FunctionTool(get_timestamp))
    
    return registry