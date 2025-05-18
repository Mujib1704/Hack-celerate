from groq import Groq  # Importing the Groq library to use its API.
from json import load, dump  # Importing functions to read and write JSON files.
import datetime  # Importing the datetime module for real-time date-and-time information.
from dotenv import dotenv_values  # Importing dotenv_values to read environment variables.
import os

# Load environment variables from the .env file.
env_vars = dotenv_values('.env')

# Retrieve specific environment variables for username, assistant name, and API key.
Username = env_vars.get('Username')
Assistantname = env_vars.get('Assistantname')
GroqAPIKey = env_vars.get('GroqAPIKey')

# Initialize the Groq client using the provided API key.
Client = Groq(api_key=GroqAPIKey)

# Initialize an empty list to store chat messages.
messages = []

# Define a system message that provides context to the AI chatbot about its role and behavior.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# A list of system instructions for the chatbot.
SystemChatBot = [
    {"role": "system", "content": System}
]

# Attempt to load the chat logs from a JSON file.
try:
    if not os.path.exists("Data/ChatLog.json") or os.stat("Data/ChatLog.json").st_size == 0:
        # If the file doesn't exist or is empty, initialize with an empty list
        with open("Data/ChatLog.json", "w") as f:
            dump([], f)

    # Now safely load
    with open("Data/ChatLog.json", "r") as f:
        messages = load(f)
except Exception as e:
    print(f"Error loading ChatLog.json: {e}")
    messages = []

# Function to get real-time date and time information.
def RealtimeInformation():
    current_date_time = datetime.datetime.now()  # Get the current date and time.
    day = current_date_time.strftime("%A")
    date=current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = "Please use this real-time information if needed.\n"
    data += f"Day: {day} \nDate: {date} Month: {month} | Year: {year}\n"
    data += f"Time: {hour} hours {minute} minutes {second} seconds.\n"
    return data

# Function to modify the chatbot's response for better formatting.
def AnswerModifier(answer):
    lines = answer.split("\n")  # Split the response into lines.
    non_empty_lines = [line for line in lines if line.strip()]  # Remove empty lines.
    modified_answer = "\n".join(non_empty_lines)  # Join the cleaned lines back together.
    return modified_answer

# Main chatbot function to handle user queries.
def ChatBot(Query):
    """This function sends the user's query to the chatbot and returns the AI's response."""

    try:
        # Load the existing chat log from the JSON file.
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        # Append the user's query to the messages list.
        messages.append({"role": "user", "content": Query})

        # Make a request to the Groq API for a response.
        completion = Client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.6,
            top_p=1,
            stream=True,
            stop=None
        )

        # Initialize an empty string to store the AI's response.
        Answer = ""

        # Process the streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content:  # Check if there's content in the current chunk.
                Answer += chunk.choices[0].delta.content  # Append the content to the answer.

        Answer = Answer.replace("</s>", "")  # Clean up any unwanted tokens from the response.

        # Append the chatbot's response to the messages list.
        messages.append({"role": "assistant", "content": Answer})

        # Save the updated chat log to the JSON file.
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        # Return the formatted response.
        return AnswerModifier(answer=Answer)

    except Exception as e:
        # Handle errors by printing the exception and resetting the chat log.
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)  # Retry the query after resetting the log.

# Main program entry point.
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")  # Prompt the user for a question.
        print(ChatBot(user_input))
