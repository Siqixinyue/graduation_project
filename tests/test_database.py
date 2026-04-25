import os
import tempfile
import shutil

import pytest

from utils import database


@pytest.fixture(autouse=True)
def temp_db_path(monkeypatch):
    temp_dir = tempfile.mkdtemp()
    temp_db = os.path.join(temp_dir, "test_data.db")

    monkeypatch.setattr(database, "DB_PATH", temp_db)

    yield temp_db

    shutil.rmtree(temp_dir)


def test_register_and_login_user():
    db = database.Database()
    result, msg = db.register_user("user1", "pass123", "user1@example.com")
    assert result is True
    assert "成功" in msg

    # 重复用户名失败
    result2, msg2 = db.register_user("user1", "pass123", "user1a@example.com")
    assert result2 is False

    # 正确登录
    user = db.login_user("user1", "pass123")
    assert user is not None
    assert user["username"] == "user1"

    # 错误密码
    user_fail = db.login_user("user1", "wrongpass")
    assert user_fail is None


def test_farm_crud_and_queries():
    db = database.Database()
    _, _ = db.register_user("farmer", "farm123", "farm@example.com")
    user = db.login_user("farmer", "farm123")
    user_id = user["id"]

    farm_id = db.add_farm(user_id, "示范农场", "山东泰安", 10.5, "壤土", "喷灌")
    assert isinstance(farm_id, int)

    farms = db.get_farms(user_id)
    assert len(farms) == 1
    assert farms[0]["name"] == "示范农场"

    db.add_crop_plan(farm_id, "小麦", "春季", "2026-03-25", "2026-09-01", "育苗期")
    plans = db.get_crop_plans(farm_id)
    assert len(plans) == 1
    assert plans[0]["crop_name"] == "小麦"

    db.add_task(farm_id, "施肥", "2026-04-01", "高", "及时肥")
    tasks = db.get_tasks(farm_id)
    assert len(tasks) == 1
    assert tasks[0]["title"] == "施肥"


def test_auto_alerts_management():
    db = database.Database()
    _, _ = db.register_user("alert_user", "alert123", "alert@example.com")
    user = db.login_user("alert_user", "alert123")
    user_id = user["id"]

    # 添加预警
    db.add_auto_alert(user_id, "test_image.jpg", 1, "测试病害", 0.95)
    db.add_auto_alert(user_id, "test_image2.jpg", 2, "另一种病害", 0.88)

    alerts = db.get_auto_alerts(user_id)
    assert len(alerts) == 2

    # 清除单个预警
    first_alert_id = alerts[0]["id"]
    cleared = db.clear_single_auto_alert(first_alert_id, user_id)
    assert cleared == 1

    alerts_after_single = db.get_auto_alerts(user_id)
    assert len(alerts_after_single) == 1

    # 清除所有预警
    cleared_all = db.clear_auto_alerts(user_id)
    assert cleared_all == 1

    alerts_after_all = db.get_auto_alerts(user_id)
    assert len(alerts_after_all) == 0
