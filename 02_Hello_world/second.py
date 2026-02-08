from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
import json

client = OpenAI()

SYSTEM_PROMPT = """
    You are an expert Ai Assistant in resolving user queries using chain of thought 
    You work on START,PLAN and OUTPUT steps .
    You need to first Plan ehat need to be done . The PLAN can be multiple steps . 
    Once you think enough PLAN has been done, finally you can give me an OUTPUT.

Rules : 
- Strickly Follow the given JSON output format
- Only run the one step at a time 
- The sequence of steps is START(where user gives an input ),PLAN (that can be multiple times) and finally OUTPUT (which is going to the displayed to the user).

    Output JSON format :
    {"step": "START | "PLAN" | "OUTPUT" ,"content" : "string" }


    Example: 
    START : Hey , Can you solve 2+3*5/10
    PLAN : {"step": "PLAN" : "content" : "Seems like user is interested in math problem "}
    PLAN : {"step": "PLAN" : "content" : "Looking at the problem , we should solve this using BODMAS method "}
    PLAN : {"step": "PLAN" : "content" : "Yes, The BODMAS is correct thing to be done here"}
    PLAN : {"step": "PLAN" : "content" : "first we must multiply 3*5 which is 15 "}
    PLAN : {"step": "PLAN" : "content" : "Now the new equation is 2+15/10 =1.5"}
    PLAN : {"step": "PLAN" : "content" : "Now the new equation is 2+1.5 "}
    PLAN : {"step": "PLAN" : "content" : "Now finally lets perform the add 3.5"}
    PLAN : {"step": "PLAN" : "content" : "Great we have solved and finally left with 3.5 as ans "}
    PLAN : {"step": "OUTPUT" : "content" : "3.5 "}

"""
print("\n\n\n")
message_histroy = [{"role": "system", "content": SYSTEM_PROMPT}]
user_query = input("User👤 : ")
message_histroy.append({"role": "user", "content": user_query})
while True:
    responce = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=message_histroy,
    )

    raw_result = responce.choices[0].message.content
    message_histroy.append({"role": "assistant", "content": raw_result})
    parsed_result = json.loads(raw_result)

    if parsed_result.get("step") == "START":
        print("🔥", parsed_result.get("content"))
        continue
    if parsed_result.get("step") == "PLAN":
        print("🧠", parsed_result.get("content"))
        continue
    if parsed_result.get("step") == "OUTPUT":
        print("🤖", parsed_result.get("content"))
        break
    print("\n\n\n")
    responce = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={"type": "json_object"},
        messages=[
            {"role": "user", "content": "Hey write a code to add n numbers in js?"},
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "step": "START",
                        "content": "User has requested help with writing a JavaScript code to add n numbers.",
                    }
                ),
            },
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "step": "PLAN",
                        "content": "We need to write a JavaScript function that can accept an array of numbers and return their sum.",
                    }
                ),
            },
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "step": "PLAN",
                        "content": "I will create a function named 'addNumbers' that takes one parameter, which is an array of numbers.",
                    }
                ),
            },
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "step": "PLAN",
                        "content": "Inside the function, I'll use the JavaScript array method 'reduce' to sum up all the elements in the array.",
                    }
                ),
            },
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "step": "PLAN",
                        "content": "Inside the function, I'll use the JavaScript array method 'reduce' to sum up all the elements in the array.",
                    }
                ),
            },
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "step": "PLAN",
                        "content": "The reduce method will take a callback function that continuously updates the sum starting from an initial value of 0.",
                    }
                ),
            },
        ],
    )
