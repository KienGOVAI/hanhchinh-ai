from app.builders.prompt_registry import PromptRegistry

print("Danh sách mặc định:")
print(PromptRegistry.list())

print("\nĐăng ký mới...")
PromptRegistry.register(
    "bien_ban",
    "document",
    "bien_ban"
)

print(PromptRegistry.list())

print("\nThông tin bien_ban:")
print(PromptRegistry.get("bien_ban"))

print("\nXóa bien_ban...")
PromptRegistry.unregister("bien_ban")

print(PromptRegistry.list())