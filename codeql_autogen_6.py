import asyncio
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools
from autogen_core.tools import FunctionTool
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
import zipfile
from pathlib import Path
from datetime import datetime


async def extract_code_snippet(db_path: str, file_path: str, start_line: int, end_line: int):
    """Asynchronously extracts the code snippet for a registered CodeQL database's src.zip file."""
    try:
        # Resolve the database path and locate the src.zip
        db_path_resolved = Path(db_path).resolve()
        src_zip_path = db_path_resolved / "src.zip"

        # Check if the src.zip exists
        if not src_zip_path.exists():
            return f"src.zip not found in: {db_path}"

        # Extract the specified file from src.zip
        modified_file_path = file_path.replace(":", "_")
        with zipfile.ZipFile(src_zip_path, 'r') as zip_file:
            # Check if the specified file exists in the zip
            if modified_file_path not in zip_file.namelist():
                return f"File {file_path} not found in src.zip"

            # Extract the file content as a list of lines
            with zip_file.open(modified_file_path) as file:
                lines = file.readlines()

                # Decode lines for processing
                lines = [line.decode('utf-8') for line in lines]

                # Extract the snippet based on line numbers
                snippet = ''.join(lines[start_line - 1:end_line])

                return snippet
    except Exception as e:
        return f"Failed to extract code: {e}"

def view_codeql_templates(template_folder: str):
    """View all Codeql templates in the specified folder."""
    template_path = Path(template_folder)

    if not template_path.exists():
        return f"Template file not found: {template_path}"

    # Read all template files in the specified folder
    # with template_path.open('r', encoding='utf-8') as template_file:
    #     template = template_file.read()
    for file in template_path.glob('*.ql'):
        template = file.read_text(encoding='utf-8')

    return template


def write_query(query: str, template_folder: str):
    """Write the generated query to a ql file."""
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"{current_time}.ql"
    file_path = Path(template_folder) / file_name
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(query)
    except Exception as e:
        print(f"Failed to write query to file: {e}")

async def main() -> None:
    # Setup server params for remote service
    server_params = SseServerParams(url="http://localhost:8000/sse")

    # Get all available tools
    codeql_tools = await mcp_server_tools(server_params)
    extract_code_snippet_tool = FunctionTool(extract_code_snippet,
                                             description="Extracts the code snippet between start line number and end line number from the registered CodeQL database's src.zip file .")
    view_codeql_templates_tool = FunctionTool(view_codeql_templates,
                                             description="View all Codeql templates in the specified folder.")
    write_query_tool = FunctionTool(write_query,
                                    description="Write the generated query to a ql file.")

    # Create an agent for each tool
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        base_url="https://aiproxy.lmzgc.cn:8080/v1",
        api_key="sk-DMjWyJWEDCHDesBK8d6756Bf6520445e9eD065E82c72A532"
    )

    agents = []

    planning_agent = AssistantAgent(
        name="PlanningAgent",
        model_client=model_client,
        description="An agent for planning tasks, this agent should be the first to engage when given a new task.",
        system_message="""
        You are a planning agent.
        Your job is to break down complex tasks into smaller, manageable subtasks.
        Your team members are:
            register_database_Agent: Registers a CodeQL database given a path
            quick_evaluate_Agent: Ruick_evaluate either a class or a predicate in a codeql query
            decode_bqrs_Agent: Decode CodeQL results, format is either csv for problem queries or json for path-problems
            evaluate_query_Agent: Runs a CodeQL query on a given database
            code_snippet_agent: Extract the code snippet from a specific file between start line number and end line number.
            codeql_query_generate_agent: Generate CodeQL query according to user-provided Codeql templates based on your requst.

        You only plan and delegate tasks - you do not execute them yourself.

        When assigning tasks, use this format:
        1. <agent> : <task>

        After all tasks are complete, summarize the findings and end with "TERMINATE".
        """,
        reflect_on_tool_use=True
    )
    agents.append(planning_agent)

    for tool in codeql_tools:
        # For each tool, create an agent
        if tool.name in ["register_database", "quick_evaluate", "decode_bqrs", "evaluate_query"]:
            agent = AssistantAgent(
                name=f"{tool.name}_Agent",
                model_client=model_client,
                tools=[tool],
                description=tool.description,
                system_message=f"""
                You are a {tool.name} agent.
                Your only tool is {tool.name} - {tool.description}.
                """,
                reflect_on_tool_use=True
            )
            agents.append(agent)

    code_snippet_agent = AssistantAgent(
        name="Code_Snippet_Agent",
        model_client=model_client,
        tools=[extract_code_snippet_tool],
        description="Extract the code snippet from a specific file between start line number and end line number.",
        system_message="""
                You are a code snippet extract agent.
                Your only tool is extract_code_snippet_tool - Extract the code snippet from a specific file between start line number and end line number.
                """,
        reflect_on_tool_use=True
    )
    agents.append(code_snippet_agent)

    codeql_query_generate_agent = AssistantAgent(
        name="Codeql_Query_Generate_Agent",
        model_client=model_client,
        tools=[view_codeql_templates_tool]+[write_query_tool],
        description="Generate CodeQL query based on user-provided Codeql templates.",
        system_message="""
                You are a codeql query generate agent.
                You have super administrator permissions to access the folders.
                Your tools are:
                    view_codeql_templates_tool - View all Codeql templates in the specified folder.
                    write_query_tool - Write the generated query to a ql file.
                Your task is to take into consideration the request, and generate a CodeQL query based on user-provided Codeql templates.
                """,
        reflect_on_tool_use=True
    )
    agents.append(codeql_query_generate_agent)


    # Define a termination condition that stops the task if the planning agent TERMINATE.
    termination = TextMentionTermination("TERMINATE")
    selector_prompt = """Select an agent to perform task.

    {roles}

    Current conversation context:
    {history}

    Read the above conversation, then select an agent from {participants} to perform the next task.
    Make sure the planner agent has assigned tasks before other agents start working.
    Only select one agent.
    """

    team = SelectorGroupChat(
        agents,
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True,  # Allow an agent to speak multiple turns in a row.
    )

    # Start the conversation with the team
    stream = team.run_stream(
        task=(
            "Your task is to handle my request step by step."
            r"First, register the code database C:\works\calltargets\bzip2\build\bzipDB."
            r"Second, generate a query to find function boundaries for target call site in the codebase. The target call site is in the decompress.c, line 212. Codeql templates are in the folder QueryTemplate of database."
            "Third, run the generated query to find the function boundaries."
            "Fourth, decode the generated '.bqrs' file to csv."
            "Fifth, output the code snippet of the function in csv."
        )
    )
    await Console(stream)

    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())