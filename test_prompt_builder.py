from app.builders.prompt_builder import PromptBuilder


builder = PromptBuilder()

prompt = builder.build(
    category="document",
    prompt_name="cong_van",
    user_input="Soạn công văn về tăng cường chuyển đổi số tại UBND xã."
)

print(prompt)