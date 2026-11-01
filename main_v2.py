
import gradio as gr
from ollama import chat


def is_dangerous_request(user_input):
    dangerous_words = [
        "מחק", "למחוק", "מחקי", "delete",
        "erase", "format", "פרמט", "אתחל",
        "כבה את המחשב"
    ]

    user_input = user_input.lower()

    for word in dangerous_words:
        if word in user_input:
            return True

    return False


def is_dangerous_command(command):
    dangerous_commands = [
        "del", "erase", "format", "rmdir",
        "rd", "shutdown", "diskpart"
    ]

    parts = command.lower().strip().split()

    if len(parts) == 0:
        return False

    return parts[0] in dangerous_commands


def translate_command(user_input):
    if is_dangerous_request(user_input):
        return "הבקשה נדחתה מטעמי בטיחות."

    response = chat(
        model="qwen2.5:3b",
        messages=[
            {
                "role": "system",
                "content": """
You are a CLI command assistant for Windows CMD.

Your task is to translate natural language requests
into correct Windows CMD commands.

The user may write in Hebrew or English.

RULES:

1. Understand the user's complete request.
2. Identify the exact action the user wants to perform.
3. Use Windows CMD syntax only.
4. Never use Linux or PowerShell commands.
5. Prefer built-in Windows commands.
6. Choose the simplest command that fulfills the request.
7. Do not invent commands.
8. If the request is unclear, ask the user for clarification.
9. If multiple commands are needed, return them in the correct order.
10. Return only the command or commands.
11. Do not include explanations or Markdown formatting.

Your priority is to return a command that correctly
matches the user's request.
"""
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    command = response.message.content.strip()

    if any(separator in command for separator in ["&", "|", "\n"]):
        return "הפלט נדחה מטעמי בטיחות."

    if is_dangerous_command(command):
        return "הפקודה נדחתה מטעמי בטיחות."

    return command


app = gr.Interface(
    fn=translate_command,
    inputs=gr.Textbox(
        label="ההוראה שלך",
        placeholder="לדוגמה: הצג את הקבצים בתיקייה הנוכחית"
    ),
    outputs=gr.Textbox(label="פקודת CLI"),
    title="CLI Agent - Version 2",
    description="המרת הוראות בשפה טבעית לפקודות Windows"
)

app.launch()
