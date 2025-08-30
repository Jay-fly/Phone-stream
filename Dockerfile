# 第一階段：使用 PDM 安裝依賴
FROM python:3.11-slim AS builder

RUN pip install -U pdm
ENV PDM_CHECK_UPDATE=false

COPY pyproject.toml pdm.lock /app/
WORKDIR /app
RUN pdm install --no-self --no-editable

# 第二階段：最終映像
FROM python:3.11-slim

# 複製虛擬環境
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# 複製應用程式檔案
COPY main.py .
COPY templates/ ./templates/
COPY static/ ./static/

# 暴露端口
EXPOSE 8000

# 啟動應用程式
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]