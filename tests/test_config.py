import os

from config import Config


def test_config_defaults():
    assert Config.HOST == "0.0.0.0"
    assert Config.PORT == 8501
    assert isinstance(Config.AUTO_DETECTION_ENABLED, bool)


def test_init_folders(tmp_path, monkeypatch):
    # 通过临时目录覆盖默认路径，避免影响真实目录
    monkeypatch.setattr(Config, "DATABASE_PATH", str(tmp_path / "data" / "data.db"))
    monkeypatch.setattr(Config, "MODEL_PATH", str(tmp_path / "models" / "model.pth"))
    monkeypatch.setattr(Config, "UPLOAD_FOLDER", str(tmp_path / "uploads"))
    monkeypatch.setattr(Config, "AUTO_IMAGE_SOURCE_FOLDER", str(tmp_path / "auto_images"))
    monkeypatch.setattr(Config, "PROCESSED_IMAGE_FOLDER", str(tmp_path / "processed_images"))
    monkeypatch.setattr(Config, "LOG_FILE", str(tmp_path / "logs" / "app.log"))
    monkeypatch.setattr(Config, "BACKUP_DIR", str(tmp_path / "backups"))

    Config.init_folders()

    assert (tmp_path / "data").exists()
    assert (tmp_path / "models").exists()
    assert (tmp_path / "uploads").exists()
    assert (tmp_path / "auto_images").exists()
    assert (tmp_path / "processed_images").exists()
    assert (tmp_path / "logs").exists()
    assert (tmp_path / "backups").exists()


def test_validate_config(tmp_path, monkeypatch):
    # 使用无效模型路径触发错误
    monkeypatch.setattr(Config, "MODEL_PATH", str(tmp_path / "missing_model.pth"))
    monkeypatch.setattr(Config, "UPLOAD_FOLDER", str(tmp_path / "uploads"))
    monkeypatch.setattr(Config, "AUTO_IMAGE_SOURCE_FOLDER", str(tmp_path / "auto_images"))
    monkeypatch.setattr(Config, "PROCESSED_IMAGE_FOLDER", str(tmp_path / "processed_images"))
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.AUTO_IMAGE_SOURCE_FOLDER, exist_ok=True)
    os.makedirs(Config.PROCESSED_IMAGE_FOLDER, exist_ok=True)

    errors = Config.validate_config()
    assert any("模型文件不存在" in message for message in errors)
