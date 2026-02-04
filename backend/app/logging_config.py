"""
ロギング設定モジュール

日次ローテーション＋月別ディレクトリ構成のログファイル出力を提供。
"""

import os
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class MonthlyDirectoryFileHandler(TimedRotatingFileHandler):
    """
    月別ディレクトリに日次ログファイルを出力するハンドラー

    出力例:
        logs/2026-02/2026-02-01.log
        logs/2026-02/2026-02-02.log
        logs/2026-03/2026-03-01.log
    """

    def __init__(
        self,
        base_dir: str = "logs",
        when: str = "midnight",
        backup_count: int = 90,
        encoding: str = "utf-8",
    ):
        self.base_dir = Path(base_dir)
        self.backup_count = backup_count
        self.encoding = encoding

        # 初期ファイルパスを設定
        self._current_month = None
        filepath = self._get_current_filepath()

        super().__init__(
            filename=str(filepath),
            when=when,
            backupCount=backup_count,
            encoding=encoding,
        )

    def _get_current_filepath(self) -> Path:
        """現在の日付に基づいたファイルパスを取得"""
        now = datetime.now()
        month_dir = self.base_dir / now.strftime("%Y-%m")
        month_dir.mkdir(parents=True, exist_ok=True)
        self._current_month = now.strftime("%Y-%m")
        return month_dir / f"{now.strftime('%Y-%m-%d')}.log"

    def doRollover(self):
        """ローテーション時に月別ディレクトリを確認・作成"""
        now = datetime.now()
        new_month = now.strftime("%Y-%m")

        # 月が変わった場合、新しいディレクトリを作成
        if new_month != self._current_month:
            self._current_month = new_month
            month_dir = self.base_dir / new_month
            month_dir.mkdir(parents=True, exist_ok=True)

        # 新しいファイルパスを設定
        new_filepath = self.base_dir / new_month / f"{now.strftime('%Y-%m-%d')}.log"
        self.baseFilename = str(new_filepath)

        super().doRollover()


def setup_logging(
    log_dir: str | None = None,
    log_level: str | None = None,
    backup_count: int | None = None,
) -> None:
    """
    アプリケーション全体のロギングを設定

    Args:
        log_dir: ログ出力ディレクトリ（デフォルト: backend/logs）
        log_level: ログレベル（デフォルト: INFO）
        backup_count: ログ保持日数（デフォルト: 0=無制限）
    """
    # 環境変数またはデフォルト値を使用
    log_dir = log_dir or os.getenv("LOG_DIR", "logs")
    log_level_str = log_level or os.getenv("LOG_LEVEL", "INFO")
    log_level_value = getattr(logging, log_level_str.upper(), logging.INFO)
    if backup_count is None:
        backup_count = int(os.getenv("LOG_BACKUP_COUNT", "0"))

    # フォーマッター
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # ルートロガーを取得
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level_value)

    # 既存のハンドラーをクリア
    root_logger.handlers.clear()

    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level_value)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # ファイルハンドラー（月別ディレクトリ）
    file_handler = MonthlyDirectoryFileHandler(
        base_dir=log_dir,
        backup_count=backup_count,
    )
    file_handler.setLevel(log_level_value)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
