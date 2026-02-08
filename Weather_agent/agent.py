from openai import OpenAI
from dotenv import load_dotenv
import json
import requests
import os

load_dotenv()

client = OpenAI()


# ---------------- TOOLS ----------------


def get_weather(city: str):
    try:
        url = f"https://wttr.in/{city.lower()}?format=%c+%t"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return f"The weather in {city} is {response.text.strip()}"
        return "something went wrong"
    except Exception as e:
        return f"Weather error: {e}"


def run_command(cmd: str):
    try:
        result = os.system(cmd)
        return f"Command executed with exit code {result}"
    except Exception as e:
        return f"Command error: {e}"


available_tools = {"get-weather": get_weather, "run_command": run_command}

# ---------------- SYSTEM PROMPT (UNCHANGED) ----------------

SYSTEM_PROMPT = """
    You are an expert Ai Assistant in resolving user queries using chain of thought 
    You work on START,PLAN and OUTPUT steps .
    You need to first Plan ehat need to be done . The PLAN can be multiple steps . 
    Once you think enough PLAN has been done, finally you can give me an OUTPUT.
    You can also call the tool if required from the list of available tools .
    for every tool call wait for the observe step which is the output from the called tool.
Rules : 
- Strickly Follow the given JSON output format
- Only run the one step at a time 
- The sequence of steps is START(where user gives an input ),PLAN (that can be multiple times) and finally OUTPUT (which is going to the displayed to the user).

    Output JSON format :
    {"step": "START | "PLAN" | "OUTPUT" | "TOOL" ,"content" : "string"  ,"tool": "string","input":"string"}

    Available Tools : 
    - get-weather(city:str):Takes the city name as an input string and returns info about the city 
    - run_command(cmd:str) : Takes a system linux command as string and excutes the command on the user's system and returns the output from that command
"""

# ---------------- AGENT LOOP ----------------

print("\n\n\n")
message_histroy = [{"role": "system", "content": SYSTEM_PROMPT}]

while True:
    user_query = input("User👤 : ")
    message_histroy.append({"role": "user", "content": user_query})

    while True:
        responce = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=message_histroy,
        )

        raw_result = responce.choices[0].message.content
        parsed_result = json.loads(raw_result)

        message_histroy.append({"role": "assistant", "content": raw_result})

        step = parsed_result.get("step")

        # ---------- START ----------
        if step == "START":
            print("🔥", parsed_result.get("content"))
            continue

        # ---------- PLAN ----------
        if step == "PLAN":
            print("🧠", parsed_result.get("content"))
            continue

        # ---------- TOOL ----------
        if step == "TOOL":
            tool_to_call = parsed_result.get("tool")
            tool_input = parsed_result.get("input")

            print(f"🎬 Calling tool: {tool_to_call}({tool_input})")

            if tool_to_call not in available_tools:
                tool_response = f"Tool '{tool_to_call}' not found"
            else:
                tool_response = available_tools[tool_to_call](tool_input)

            print(f"🎬 Tool output: {tool_response}")

            message_histroy.append(
                {
                    "role": "developer",
                    "content": json.dumps(
                        {
                            "step": "OBSERVE",
                            "tool": tool_to_call,
                            "input": tool_input,
                            "output": tool_response,
                        }
                    ),
                }
            )
            continue

        # ---------- OUTPUT ----------
        if step == "OUTPUT":
            print("🤖", parsed_result.get("content"))
            break

    print("\n\n\n")
