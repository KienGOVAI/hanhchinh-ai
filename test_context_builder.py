from app.builders.context_builder import ContextBuilder


builder = ContextBuilder()

context = builder.build(
    document_type="Công văn",
    extra_context="Đơn vị: UBND xã Yên Minh"
)

print(context)