import pytest
import os
import tempfile
from app import app, init_db

TEST_DATE = "2026-04-24"
TEST_MONTH = "2026-04"


@pytest.fixture
def client(tmp_path, monkeypatch):
    """테스트용 임시 DB를 사용하는 Flask 테스트 클라이언트"""
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("app.DB_PATH", db_path)
    init_db()

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── index ──────────────────────────────────────────────────────────────────

def test_index_기본접속(client):
    """오늘 날짜로 메인 페이지 접속"""
    res = client.get("/")
    assert res.status_code == 200

def test_index_날짜_파라미터(client):
    """특정 날짜로 메인 페이지 접속"""
    res = client.get(f"/?date={TEST_DATE}")
    assert res.status_code == 200

def test_index_월_파라미터(client):
    """특정 월로 메인 페이지 접속"""
    res = client.get(f"/?month={TEST_MONTH}")
    assert res.status_code == 200

def test_index_잘못된_날짜(client):
    """잘못된 날짜 형식이어도 오류 없이 처리"""
    res = client.get("/?date=invalid-date")
    assert res.status_code == 200


# ── add ────────────────────────────────────────────────────────────────────

def test_add_할일_추가(client):
    """할 일 추가 후 리다이렉트"""
    res = client.post("/add", data={
        "todo_date": TEST_DATE,
        "content": "pytest 테스트 작성"
    })
    assert res.status_code == 302
    assert f"date={TEST_DATE}" in res.headers["Location"]

def test_add_빈_내용(client):
    """내용이 빈 경우 DB에 저장되지 않고 리다이렉트"""
    res = client.post("/add", data={
        "todo_date": TEST_DATE,
        "content": "   "
    })
    assert res.status_code == 302


# ── toggle ─────────────────────────────────────────────────────────────────

def test_toggle_완료_상태_전환(client):
    """할 일 추가 후 toggle → 완료 상태 전환"""
    client.post("/add", data={"todo_date": TEST_DATE, "content": "토글 테스트"})

    res = client.post("/toggle/1", data={"todo_date": TEST_DATE})
    assert res.status_code == 302

def test_toggle_존재하지_않는_id(client):
    """존재하지 않는 id toggle → 오류 없이 리다이렉트"""
    res = client.post("/toggle/9999", data={"todo_date": TEST_DATE})
    assert res.status_code == 302


# ── delete ─────────────────────────────────────────────────────────────────

def test_delete_할일_삭제(client):
    """할 일 추가 후 삭제 → 리다이렉트"""
    client.post("/add", data={"todo_date": TEST_DATE, "content": "삭제 테스트"})

    res = client.post("/delete/1", data={"todo_date": TEST_DATE})
    assert res.status_code == 302

def test_delete_존재하지_않는_id(client):
    """존재하지 않는 id 삭제 → 오류 없이 리다이렉트"""
    res = client.post("/delete/9999", data={"todo_date": TEST_DATE})
    assert res.status_code == 302