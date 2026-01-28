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
        # テスト終了時にget_dbのオーバーライドのみ削除
        # （他のオーバーライドを壊さないよう、clear()は使わない）
        app.dependency_overrides.pop(get_db, None)


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
def book_factory(test_db, admin_user):
    """
    書籍作成ファクトリフィクスチャ（UserBook も自動作成）

    デフォルトでは admin_user に紐付く UserBook を作成。
    user_id を指定することで別ユーザーの UserBook を作成可能。

    使用例:
        book = book_factory(title="カスタム本", isbn="9781234567890")
        book = book_factory(title="他ユーザーの本", user_id=other_user.id)
    """
    from app.models import Book, UserBook
    from app.schemas import BookStatus

    def _create_book(**kwargs):
        """書籍と UserBook を作成してDBに保存"""
        # UserBook 用パラメータを分離
        user_id = kwargs.pop("user_id", admin_user.id)
        note = kwargs.pop("note", None)
        status = kwargs.pop("status", BookStatus.UNREAD.value)
        shelf_id = kwargs.pop("shelf_id", None)

        # Book 用デフォルト値
        book_defaults = {
            "title": "テスト本",
            "author": "テスト著者",
            "description": "テスト説明",
        }
        book_defaults.update(kwargs)

        # Book 作成
        book = Book(**book_defaults)
        test_db.add(book)
        test_db.flush()  # ID を取得

        # UserBook 作成
        user_book = UserBook(
            user_id=user_id,
            book_id=book.id,
            note=note,
            status=status,
            shelf_id=shelf_id,
        )
        test_db.add(user_book)
        test_db.commit()
        test_db.refresh(book)
        test_db.refresh(user_book)

        # テストで使いやすくするため UserBook 情報を保存
        book._user_book = user_book
        return book

    return _create_book


@pytest.fixture
def sample_books(book_factory):
    """
    よく使う2冊セットのサンプルデータ（admin user scoped）

    多くのテストで使える標準的なデータセット。
    個別のカスタマイズが不要な場合に便利。

    Returns:
        list[Book]: 2冊の書籍リスト（各 Book に _user_book 属性あり）
    """
    book1 = book_factory(
        title="テスト本1", author="著者1", description="説明1", isbn="9781234567890"
    )
    book2 = book_factory(
        title="テスト本2", author="著者2", description="説明2", isbn="9780987654321"
    )
    return [book1, book2]


@pytest.fixture
def user_book_factory(test_db):
    """UserBook 作成ファクトリフィクスチャ"""
    from app.models import UserBook
    from app.schemas import BookStatus

    def _create_user_book(**kwargs):
        if "user_id" not in kwargs or "book_id" not in kwargs:
            raise ValueError("user_id and book_id are required for UserBook creation")

        defaults = {
            "note": None,
            "status": BookStatus.UNREAD.value,
            "shelf_id": None,
        }
        defaults.update(kwargs)

        user_book = UserBook(**defaults)
        test_db.add(user_book)
        test_db.commit()
        test_db.refresh(user_book)
        return user_book

    return _create_user_book


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

    _counter = [0]  # ユニークなauth0_sub生成用カウンター

    def _create_user(**kwargs):
        _counter[0] += 1
        defaults = {
            "name": "テストユーザー",
            "auth0_sub": f"auth0|test_user_{_counter[0]}",
            "email": f"test{_counter[0]}@example.com",
        }
        defaults.update(kwargs)

        user = User(**defaults)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user

    return _create_user


@pytest.fixture
def mock_jwt_payload():
    """モックJWTペイロード"""
    return {
        "sub": "auth0|test_admin_user",
        "email": "admin@example.com",
        "name": "Test Admin",
    }


@pytest.fixture(autouse=True)
def override_jwt_bearer(mock_jwt_payload):
    """全テストでJWT検証をバイパス"""
    from app.auth import jwt_bearer
    from app.main import app

    # jwt_bearerインスタンスの__call__をオーバーライド
    app.dependency_overrides[jwt_bearer] = lambda: mock_jwt_payload
    yield
    app.dependency_overrides.pop(jwt_bearer, None)


@pytest.fixture
def admin_user(user_factory, mock_jwt_payload):
    """Admin user fixture - mock_jwt_payloadのsubと一致するユーザーを作成"""
    return user_factory(
        name="admin",
        auth0_sub=mock_jwt_payload["sub"],
        email=mock_jwt_payload["email"],
    )
