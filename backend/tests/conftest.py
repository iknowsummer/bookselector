import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="function")
def test_engine():
    """
    テスト用のインメモリSQLiteエンジンを作成
    各テスト関数ごとに新しいデータベースを作成
    """
    from app.database import Base
    # モデルをインポートしてBaseに登録されるようにする
    from app import models  # noqa: F401

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # SQLiteで外部キー制約を有効化
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """
    テスト用のデータベースセッションを作成
    FastAPIのdependency_overridesを使用してテスト用DBに切り替え

    Note:
    - autocommit=False: トランザクションを明示的に管理
    - autoflush=False: 自動的なflushを無効化（テストの制御向上）
    - expire_on_commit=False: commit後もオブジェクトを使用可能に
    """

    from app.database import get_db
    from app.main import app

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # FastAPIのDI（Dependency Injection）をテスト用DBに切り替え
    app.dependency_overrides[get_db] = override_get_db

    # テストコード内で直接使うセッション
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # テスト終了時にオーバーライドをクリア
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_db):
    """
    テスト用のFastAPIクライアントを作成

    Note: test_dbフィクスチャに依存することで、以下が保証される：
    1. テスト用のインメモリDBが使用される
    2. app.dependency_overrides[get_db]が設定済み
    3. 各テスト関数ごとに新しいDBが作成される

    test_dbを使わないテストでも、このclientを使う場合は
    test_dbが自動的に初期化されます（フィクスチャの依存関係）
    """
    # test_dbを明示的に参照（フィクスチャの実行を保証）
    # test_db自体は使わないが、依存関係により確実にセットアップされる
    _ = test_db

    # フィクスチャ内でインポート（Pylanceエラー回避）
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


# === テストデータ作成用フィクスチャ ===


@pytest.fixture
def book_factory(test_db):
    """
    書籍作成ファクトリフィクスチャ

    デフォルト値を持ちつつ、必要な部分だけカスタマイズできる。
    DRY原則を保ちながら、テストごとに柔軟にデータを作成可能。

    使用例:
        book = book_factory(title="カスタム本", isbn="9781234567890")
    """
    from app.models import Book

    def _create_book(**kwargs):
        """書籍を作成してDBに保存"""
        # デフォルト値
        defaults = {
            "title": "テスト本",
            "author": "テスト著者",
            "description": "テスト説明",
            "shelf_id": None,
        }
        # 引数でデフォルト値を上書き
        defaults.update(kwargs)

        book = Book(**defaults)
        test_db.add(book)
        test_db.commit()
        test_db.refresh(book)  # DBから最新状態を取得（id, created_atなど）
        return book

    return _create_book


@pytest.fixture
def sample_books(book_factory):
    """
    よく使う2冊セットのサンプルデータ

    多くのテストで使える標準的なデータセット。
    個別のカスタマイズが不要な場合に便利。

    Returns:
        list[Book]: 2冊の書籍リスト
    """
    book1 = book_factory(
        title="テスト本1",
        author="著者1",
        description="説明1",
        isbn="9781234567890"
    )
    book2 = book_factory(
        title="テスト本2",
        author="著者2",
        description="説明2",
        isbn="9780987654321"
    )
    return [book1, book2]


@pytest.fixture
def shelf_factory(test_db):
    """棚データ作成用ファクトリ (user-scoped)"""
    from app.models import Shelf

    def _create_shelf(**kwargs):
        if "user_id" not in kwargs:
            raise ValueError(
                "user_id is required for shelf creation. "
                "Pass user_id explicitly or ensure admin_user fixture is loaded."
            )

        defaults = {
            "name": "living",
            "memo": "リビング棚",
        }
        defaults.update(kwargs)

        shelf = Shelf(**defaults)
        test_db.add(shelf)
        test_db.commit()
        test_db.refresh(shelf)
        return shelf

    return _create_shelf


@pytest.fixture
def sample_shelves(shelf_factory, admin_user):
    """2件分の棚データ (admin user scoped)"""
    shelf1 = shelf_factory(user_id=admin_user.id, name="living", memo="リビング")
    shelf2 = shelf_factory(user_id=admin_user.id, name="bedroom", memo="寝室")
    return [shelf1, shelf2]


@pytest.fixture
def user_factory(test_db):
    """ユーザー作成ファクトリフィクスチャ"""
    from app.models import User

    def _create_user(**kwargs):
        defaults = {
            "name": "テストユーザー",
        }
        defaults.update(kwargs)

        user = User(**defaults)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user

    return _create_user


@pytest.fixture
def admin_user(user_factory):
    """Admin user fixture (id=1) for Phase 1 user context."""
    return user_factory(name="admin")
