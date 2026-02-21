FROM python:3.12-slim

WORKDIR /app

# 依存関係ファイルを先にコピー（レイヤーキャッシュ活用）
COPY app/pyproject.toml ./app/

# 依存関係インストール
RUN pip install --no-cache-dir ./app

# アプリケーションソースをコピー
COPY app/ ./app/

# ログ・データ用ディレクトリを作成
RUN mkdir -p /data /app/logs

# 非rootユーザーで実行
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app /data
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
