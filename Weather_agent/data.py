# from openai import OpenAI
# from dotenv import load_dotenv
# load_dotenv()
# import json
# import requests
# client = OpenAI(
#     api_key="",
# )
# def get_weather(city:str):
#     url = f"https://wttr.in/{city.lower()}?format=%c+%t"
#     response = requests.get(url)
#     if response.status_code == 200:
#         return f"The weather in {city} is {response.text}"
#     return "something went wrong"


# avaiable_tools ={

# "get-weather":get_weather
# }




# SYSTEM_PROMPT = """
#     You are an expert Ai Assistant in resolving user queries using chain of thought 
#     You work on START,PLAN and OUTPUT steps .
#     You need to first Plan ehat need to be done . The PLAN can be multiple steps . 
#     Once you think enough PLAN has been done, finally you can give me an OUTPUT.
#     You can also call the tool if required from the list of available tools .
#     for every tool call wait for the observe step which is the output from the called tool.
# Rules : 
# - Strickly Follow the given JSON output format
# - Only run the one step at a time 
# - The sequence of steps is START(where user gives an input ),PLAN (that can be multiple times) and finally OUTPUT (which is going to the displayed to the user).

#     Output JSON format :
#     {"step": "START | "PLAN" | "OUTPUT" | "TOOL" ,"content" : "string"  ,"tool": "string","input":"string"}

#     Available Tools : 
#     - get-weather(city:str):Takes the city name as an input string and returns info about the city 

#     Example 1: 
#     START : Hey , Can you solve 2+3*5/10
#     PLAN : {"step": "PLAN" : "content" : "Seems like user is interested in math problem "}
#     PLAN : {"step": "PLAN" : "content" : "Looking at the problem , we should solve this using BODMAS method "}
#     PLAN : {"step": "PLAN" : "content" : "Yes, The BODMAS is correct thing to be done here"}
#     PLAN : {"step": "PLAN" : "content" : "first we must multiply 3*5 which is 15 "}
#     PLAN : {"step": "PLAN" : "content" : "Now the new equation is 2+15/10 =1.5"}
#     PLAN : {"step": "PLAN" : "content" : "Now the new equation is 2+1.5 "}
#     PLAN : {"step": "PLAN" : "content" : "Now finally lets perform the add 3.5"}
#     PLAN : {"step": "PLAN" : "content" : "Great we have solved and finally left with 3.5 as ans "}
#     PLAN : {"step": "OUTPUT" : "content" : "3.5 "}

#     Example 2: 
#     START : What is the weather in Lahore? 
#     PLAN : {"step": "PLAN" : "content" : "Seems like user is interested in getting the weather of Lahore in pakistan  "}
#     PLAN : {"step": "PLAN" : "content" : "lets see if we have the any available tools from the list of available loops. "}
#     PLAN : {"step": "PLAN" : "content" : "Great,  we have get the get_weather tool available for htis query"}
#     PLAN : {"step": "PLAN" : "content" : "I need to call the get_weather tool for lahore as input for city "}
#     PLAN : {"step": "TOOL" : "tool" : "get_weather" "input": "Lahore"}
#     PLAN : {"step": "OBSERVE" : "tool" : "get_weather" "output": "The temp of lahore is cloudy with 20C"}
#     PLAN : {"step": "PLAN" : "content": "Great i got the weather info about the lahore}
#     PLAN : {"step": "OUTPUT" : "content" : "The current weather in lahore is 20C with some cloudy sky"}

# """
# print("\n\n\n")
# message_histroy = [ {"role":"system", "content":SYSTEM_PROMPT}]
# while True:
#     user_query = input("User👤 : ")
#     message_histroy.append({"role":"user","content":user_query})


#     while True:
#         responce = client.chat.completions.create(
#         model="gpt-4o",
#         response_format={"type":"json_object"},
#         messages = message_histroy
#     )

#     raw_result = responce.choices[0].message.content
#     message_histroy.append({"role":"assistant","content":raw_result})
#     parsed_result = json.loads(raw_result)

#     if parsed_result.get("step")== "START":
#         print("🔥",parsed_result.get("content"))
#         continue
#     if parsed_result.get("step")== "PLAN":
#         print("🧠",parsed_result.get("content"))
#         continue
#     if parsed_result.get("step") == "TOOL":
#         tool_to_call = parsed_result.get("tool")
#         tool_input = parsed_result.get("input")
#         print(f"🎬:{tool_to_call} ({tool_input})")

#     tool_response = avaiable_tools[tool_to_call](tool_input)
#     print(f"🎬:{tool_to_call} ({tool_input})= {tool_response}")
#     message_histroy.append({"role":"developer", "content": json.dumps(
#         {"step":"OBSERVE","tool":tool_to_call,"input": tool_input,"output":tool_response}
#     )})
#     continue

#     if parsed_result.get("step") == "OUTPUT":
#         print("🤖",parsed_result.get("content"))
#         break
#     print("\n\n\n")
     

import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# OpenAI client (API key safely loaded)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# ------------------ TOOLS ------------------

def get_weather(city: str):
    try:
        url = f"https://wttr.in/{city.lower()}?format=%c+%t"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return f"The weather in {city} is {response.text.strip()}"
    except Exception as e:
        return f"Weather fetch failed: {e}"

available_tools = {
    "get-weather": get_weather
}

# ------------------ SYSTEM PROMPT ------------------

SYSTEM_PROMPT = """
You are an expert AI Assistant that resolves user queries step-by-step.

You must strictly follow these steps:
START → PLAN (can repeat) → TOOL (if needed) → OBSERVE → OUTPUT

Rules:
- Output must always be valid JSON
- Execute only ONE step at a time
- Never skip steps
- OUTPUT is final and shown to the user

JSON Output Format:
{
  "step": "START | PLAN | TOOL | OUTPUT",
  "content": "string",
  "tool": "string",
  "input": "string"
}

Available Tools:
- get-weather(city: str)
"""

# ------------------ CHAT LOOP ------------------

print("\n\nAgent Started 🚀\n")

message_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

while True:
    user_query = input("User👤: ")
    message_history.append({"role": "user", "content": user_query})

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=message_history
        )

        raw_result = response.choices[0].message.content
        parsed_result = json.loads(raw_result)

        message_history.append(
            {"role": "assistant", "content": raw_result}
        )

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
            tool_name = parsed_result.get("tool")
            tool_input = parsed_result.get("input")

            print(f"🎬 Calling Tool: {tool_name}({tool_input})")

            if tool_name not in available_tools:
                tool_output = f"Tool '{tool_name}' not found"
            else:
                tool_output = available_tools[tool_name](tool_input)

            print(f"🎬 Tool Output: {tool_output}")

            # OBSERVE step fed back to model
            message_history.append({
                "role": "developer",
                "content": json.dumps({
                    "step": "OBSERVE",
                    "tool": tool_name,
                    "input": tool_input,
                    "output": tool_output
                })
            })
            continue

        # ---------- OUTPUT ----------
        if step == "OUTPUT":
            print("🤖", parsed_result.get("content"))
            break

    print("\n-------------------------\n")