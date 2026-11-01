
import gradio as gr
from ollama import chat


def is_dangerous_request(user_input):
    dangerous_words = [
        "מחק",
        "למחוק",
        "מחקי",
        "delete",
        "delete all",
        "erase",
        "format",
        "פרמט",
        "אתחל",
        "נקה",
        "רוקן",
        "הסר",
        "הסירי",
        "remove all",
        "clean",
        "wipe",
        "כבה את המחשב"
    ]

    user_input = user_input.lower()

    for word in dangerous_words:
        if word in user_input:
            return True

    return False


def is_dangerous_command(command):
    dangerous_commands = [
        "del",
        "erase",
        "format",
        "rmdir",
        "rd",
        "shutdown",
        "diskpart",
        "remove-item",
        "clear-content",
        "stop-computer"
    ]

    command = command.lower().strip()
    parts = command.split()

    if len(parts) == 0:
        return False

    first_command = parts[0]

    if first_command in dangerous_commands:
        return True

    return False


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

Your task is to translate the user's natural language request
into correct and appropriate Windows CMD command(s).

RULES:
1. Understand the complete request before choosing a command.
2. Identify all requested actions and details.
3. Use Windows CMD syntax only. Never use PowerShell or Linux syntax.
4. Prefer standard built-in Windows CMD commands.
5. Use the simplest command that correctly fulfills the request.
6. Do not invent commands or use a command for an unrelated purpose.
7. If the request requires multiple commands, return them in the correct order.
8. If a request is ambiguous, ask for clarification instead of guessing.
9. Never provide commands that delete files, format disks, shut down
   the computer, modify system settings, or cause destructive changes.
10. If the request is dangerous, refuse to provide a command.
11. If there is no simple built-in CMD command that fulfills the request,
    state that you cannot provide an appropriate command rather than
    inventing an incorrect one.
12. Return only the command(s) or a brief refusal.
13. Do not include explanations, introductions, or Markdown formatting.

Remember: correctness and safety are more important than producing
a command for every request.
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
        return "הפלט נדחה מטעמי בטיחות: זוהו מספר פקודות או מפרידי פקודות."

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
    title="CLI Agent - Version 3",
    description="המרת הוראות בשפה טבעית לפקודות Windows"
)

app.launch()
