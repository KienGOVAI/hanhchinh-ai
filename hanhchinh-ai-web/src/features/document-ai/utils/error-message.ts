import axios from "axios";

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;

    switch (status) {
      case 400:
        return "Yêu cầu không hợp lệ.";

      case 401:
        return "Bạn chưa đăng nhập.";

      case 403:
        return "Bạn không có quyền sử dụng chức năng này.";

      case 404:
        return "Không tìm thấy dịch vụ AI.";

      case 408:
        return "Yêu cầu đã hết thời gian chờ.";

      case 429:
        return "AI đang quá tải hoặc đã hết quota.";

      case 500:
        return "Máy chủ AI đang gặp sự cố.";

      case 502:
      case 503:
        return "Dịch vụ AI hiện không khả dụng.";

      default:
        break;
    }

    if (error.code === "ECONNABORTED") {
      return "AI phản hồi quá lâu, vui lòng thử lại.";
    }

    if (error.message === "Network Error") {
      return "Không thể kết nối tới máy chủ AI. Hãy kiểm tra FastAPI hoặc kết nối mạng.";
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Đã xảy ra lỗi không xác định.";
}