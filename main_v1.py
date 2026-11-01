
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
You are a command-line assistant for Windows.

Your job is to convert a user's natural language request
into a suitable Windows CMD command.

The user may write in Hebrew or English.

Return the command that best matches the user's request.

Use Windows CMD commands only.

Do not provide explanations.
Return only the command.
"""
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    command = response.message.content.strip()

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
    title="CLI Agent - Version 1",
    description="המרת הוראות בשפה טבעית לפקודות Windows"
)

app.launch()
