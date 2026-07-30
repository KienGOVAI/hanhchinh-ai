from app.services.prompt_validator import PromptValidator

prompt = """
SYSTEM PROMPT

abc

YÊU CẦU NGƯỜI DÙNG

xyz
"""

valid, message = PromptValidator.validate(prompt)

print(valid)

print(message)