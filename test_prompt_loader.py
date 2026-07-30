from app.services.prompt_loader import PromptLoader


print("=" * 50)

print("Kiểm tra Prompt tồn tại:")

print(
    PromptLoader.exists(
        "document",
        "cong_van"
    )
)

print("=" * 50)

prompt = PromptLoader.load(
    "document",
    "cong_van"
)

print(prompt)

print("=" * 50)