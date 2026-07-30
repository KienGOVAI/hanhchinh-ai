from app.services.ai_service import AIService


def main():

    ai = AIService()

    result = ai.generate_document(
        document_type="cong_van",
        title="Tăng cường chuyển đổi số",
        content="""
Đề nghị các đơn vị tăng cường triển khai chuyển đổi số
trong giải quyết thủ tục hành chính.
""",
        extra_context="UBND xã Yên Minh"
    )

    print("=" * 80)
    print(result)
    print("=" * 80)


if __name__ == "__main__":
    main()