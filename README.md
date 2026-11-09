# coding-agent-server

Con "server AI nhỏ" để code trên máy, dựa trên [`claude-agent-sdk`](https://github.com/anthropics/claude-agent-sdk-python)
chính thức của Anthropic — bản SDK này dùng chính engine của Claude Code (đọc/ghi
file, chạy bash, tìm kiếm trong repo...), bọc lại thành một HTTP server nhỏ bằng
FastAPI để bạn gọi qua `curl`/script thay vì gõ trong terminal.

## Cài đặt

```powershell
cd C:\Users\jacob.nguyen\Documents\coding-agent-server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`claude-agent-sdk` tự kèm theo Claude Code CLI, cần Node.js đã cài sẵn (bạn đã có
v20).

## Auth

Chọn một trong hai:

- `ant auth login` (khuyến nghị — không cần quản lý key thủ công), hoặc
- set biến môi trường `ANTHROPIC_API_KEY` trước khi chạy server.

## Chạy

```powershell
$env:WORKSPACE_ROOT = "C:\Users\jacob.nguyen\Documents\app\TrackIt-App"  # thư mục project muốn agent làm việc
uvicorn main:app --host 127.0.0.1 --port 8787 --reload
```

Mặc định `WORKSPACE_ROOT` là thư mục hiện tại khi chạy lệnh; model mặc định là
`claude-opus-4-8` (đổi qua biến `CLAUDE_MODEL`).

## Gọi thử

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8787/chat `
  -ContentType "application/json" `
  -Body (@{ message = "Liệt kê các file trong thư mục hiện tại" } | ConvertTo-Json)
```

Các endpoint khác:

- `POST /reset` — xoá hội thoại, bắt đầu phiên mới
- `POST /interrupt` — dừng tác vụ agent đang chạy dở
- `GET /health` — kiểm tra trạng thái, model, workspace đang dùng

## Giới hạn / lưu ý bảo mật

- Server này **chỉ nên bind `127.0.0.1`**, không expose ra mạng — agent có toàn
  quyền đọc/ghi file và chạy lệnh shell trong `WORKSPACE_ROOT`.
- Một tiến trình server = một hội thoại/agent duy nhất (không tách theo
  session_id). Muốn nhiều workspace song song thì chạy nhiều instance ở port
  khác nhau, mỗi cái set `WORKSPACE_ROOT` riêng.
- `permission_mode="acceptEdits"` nghĩa là sửa file được tự động chấp nhận,
  không có người duyệt từng edit — vì server chạy không tương tác. Nếu muốn
  chặt hơn, đổi giá trị này hoặc thêm `allowed_tools` trong `main.py`.

## Tham khảo mã nguồn mở khác

Nếu muốn so sánh cách người khác dựng agent coding local:

- [anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) — SDK chính thức dùng ở đây
- [anthropics/claude-agent-sdk-demos](https://github.com/anthropics/claude-agent-sdk-demos) — các demo chính thức (TypeScript): email agent, research agent, chat app WebSocket...
- [coder/agentapi](https://github.com/coder/agentapi) — HTTP API chung cho nhiều agent (Claude Code, Aider, Goose, Codex...)
- [OpenHands](https://www.openhands.dev/) — nền tảng mã nguồn mở dựng/chạy coding agent, có giao diện riêng
