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
- `GET /health` — kiểm tra trạng thái, model, workspace đang dùng (không cần token)

## Connect từ xa (CLI)

Để code từ một máy/thiết bị khác qua CLI thay vì `curl`:

1. **Bật xác thực** trước khi mở ra ngoài `127.0.0.1` — bắt buộc, không có bước
   này thì bất kỳ ai nối được tới port đều có thể đọc/ghi file + chạy lệnh shell
   trên máy bạn:
   ```powershell
   $env:AGENT_TOKEN = "một-chuỗi-bí-mật-tự-đặt"
   uvicorn main:app --host 0.0.0.0 --port 8787
   ```
2. **Mở firewall** cho port đó (chỉ cần nếu client ở máy khác trong cùng LAN):
   ```powershell
   New-NetFirewallRule -DisplayName "coding-agent-server" -Direction Inbound -Protocol TCP -LocalPort 8787 -Action Allow
   ```
3. **Từ máy client**, chạy CLI đi kèm (`cli.py`), trỏ tới IP LAN của máy server:
   ```powershell
   $env:AGENT_URL = "http://<IP-máy-server>:8787"
   $env:AGENT_TOKEN = "cùng chuỗi bí mật ở bước 1"
   python cli.py
   ```
   Gõ thẳng tin nhắn ở prompt `you>` để agent code trên máy server; `/reset` để
   xoá hội thoại.

Nếu client ở **ngoài Internet** (không cùng LAN), không port-forward thẳng ra
ngoài — dùng một mạng riêng như Tailscale/ZeroTier để nối hai máy, rồi trỏ
`AGENT_URL` vào IP nội bộ do nó cấp.

## Giới hạn / lưu ý bảo mật

- Nếu không set `AGENT_TOKEN`, server không xác thực request nào cả — chỉ chấp
  nhận khi vẫn bind `127.0.0.1`. Một khi bind `0.0.0.0` (cho remote), **luôn**
  set `AGENT_TOKEN`.
- Agent có toàn quyền đọc/ghi file và chạy lệnh shell trong `WORKSPACE_ROOT` —
  coi token như một mật khẩu root, đừng commit nó vào git.
- Một tiến trình server = một hội thoại/agent duy nhất (không tách theo
  session_id). Muốn nhiều workspace song song thì chạy nhiều instance ở port
  khác nhau, mỗi cái set `WORKSPACE_ROOT` riêng.
- `permission_mode="acceptEdits"` nghĩa là sửa file được tự động chấp nhận,
  không có người duyệt từng edit — vì server chạy không tương tác. Nếu muốn
  chặt hơn, đổi giá trị này hoặc thêm `allowed_tools` trong `main.py`.
- Claude là model đóng của Anthropic — server này (và bất kỳ cách dùng Claude
  nào khác) luôn cần gọi ra Internet tới Anthropic để suy nghĩ/sinh code. Phần
  "chạy trên máy bạn" chỉ là tác vụ file/bash/orchestration, không phải
  inference.

## Tham khảo mã nguồn mở khác

Nếu muốn so sánh cách người khác dựng agent coding local:

- [anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) — SDK chính thức dùng ở đây
- [anthropics/claude-agent-sdk-demos](https://github.com/anthropics/claude-agent-sdk-demos) — các demo chính thức (TypeScript): email agent, research agent, chat app WebSocket...
- [coder/agentapi](https://github.com/coder/agentapi) — HTTP API chung cho nhiều agent (Claude Code, Aider, Goose, Codex...)
- [OpenHands](https://www.openhands.dev/) — nền tảng mã nguồn mở dựng/chạy coding agent, có giao diện riêng
