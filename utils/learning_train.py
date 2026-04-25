import os
import shutil
from datetime import datetime

import json
import torch
from torch import nn, optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image

from utils.database import db
from utils.class_names import load_active_class_names
from utils.model import PlantDiseaseModel


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


BASE_TRAIN_ROOT_DEFAULT = (
    r"C:\Users\ma_xi\Desktop\2018 AI CHALLENGER 农作物病害识别\ai_challenger_pdr2018_trainingset_20181023"
    r"\AgriculturalDisease_trainingset"
)


def _remap_base_class_id(original_class_id: int):
    """
    复用旧代码的类别处理逻辑：过滤 44/45，并重映射到 0..58（共 59 类）。
    """
    d = int(original_class_id)
    if d in (44, 45):
        return None
    if d > 45:
        return d - 2
    if d > 43:
        # 理论上只剩下 d=44/45 会触发这里，但我们已过滤，保留兼容写法
        return d - 1
    return d


_BASE_INDEX_CACHE = None


def _load_base_class_index():
    """
    构建： {base_class_id(0..58): [abs_image_path, ...]}
    只在第一次训练作业时加载并缓存。
    """
    global _BASE_INDEX_CACHE
    if _BASE_INDEX_CACHE is not None:
        return _BASE_INDEX_CACHE

    import json
    import random

    train_root = os.environ.get("BASE_TRAIN_ROOT", BASE_TRAIN_ROOT_DEFAULT)
    images_dir = os.path.join(train_root, "images")
    annot_path = os.path.join(train_root, "AgriculturalDisease_train_annotations.json")
    if not os.path.exists(annot_path):
        # 兼容你旧代码里可能用验证集标注文件的情况
        alt = os.path.join(train_root, "AgriculturalDisease_validation_annotations.json")
        if os.path.exists(alt):
            annot_path = alt

    if not os.path.exists(images_dir):
        raise FileNotFoundError(f"base images_dir not found: {images_dir}")
    if not os.path.exists(annot_path):
        raise FileNotFoundError(f"base annotations json not found: {annot_path}")

    with open(annot_path, "r", encoding="utf-8") as f:
        annotations = json.load(f)

    class_to_paths = {i: [] for i in range(59)}
    for item in annotations:
        original_cls = item.get("disease_class")
        image_id = item.get("image_id")
        if image_id is None or original_cls is None:
            continue
        mapped = _remap_base_class_id(original_cls)
        if mapped is None:
            continue
        img_path = os.path.join(images_dir, image_id)
        if os.path.exists(img_path):
            class_to_paths[mapped].append(img_path)

    # 基于固定随机源打乱每类样本，避免每次训练顺序偏置
    seed = int(os.environ.get("INCR_REHEARSAL_INDEX_SEED", "42"))
    rng = random.Random(seed)
    for cid in class_to_paths:
        rng.shuffle(class_to_paths[cid])

    _BASE_INDEX_CACHE = class_to_paths
    return class_to_paths


def _sample_base_rehearsal_samples(per_class: int, seed: int):
    """
    为 0..58 的每个旧类采样 per_class 张作为回放数据。
    """
    import random

    index = _load_base_class_index()
    rng = random.Random(seed)
    samples = []
    for cid in range(59):
        paths = index.get(cid, [])
        if not paths:
            continue
        k = min(per_class, len(paths))
        # 不改变全局缓存顺序：对切片再随机选
        chosen = rng.sample(paths, k) if k < len(paths) else list(paths[:k])
        samples.extend([(p, cid) for p in chosen])
    return samples


def export_approved_task_dataset(task_id: int, export_root: str) -> str:
    """
    导出“已审核通过”的新增病虫害数据集。
    这里先做工程层面的数据导出与校验，不直接替换主模型文件，以保证系统可运行与可演示。
    """
    task = db.get_learning_task(task_id)
    if not task:
        raise ValueError(f"task not found: {task_id}")
    images = db.get_learning_images(task_id)
    if not images:
        raise ValueError("该学习任务没有上传任何图片。")

    disease_name = task["disease_name"]
    crop_type = task["crop_type"]

    export_dir = os.path.join(export_root, f"task_{task_id}")
    _ensure_dir(export_dir)

    images_out_dir = os.path.join(export_dir, "images", disease_name)
    _ensure_dir(images_out_dir)

    exported_images = []
    for img in images:
        src = img["storage_path"]
        if not os.path.isabs(src):
            # 兼容相对路径写入
            src = os.path.join(os.getcwd(), src)
        if not os.path.exists(src):
            # 不让整次导出因个别缺失中断
            continue
        dst = os.path.join(images_out_dir, img["file_name"])
        shutil.copy2(src, dst)
        exported_images.append(
            {
                "src": src,
                "dst": dst,
                "file_name": img["file_name"],
                "uploaded_at": img["created_at"],
            }
        )

    if not exported_images:
        raise ValueError("导出失败：源图片文件缺失。")

    manifest = {
        "exported_at": datetime.now().isoformat(),
        "task_id": task_id,
        "crop_type": crop_type,
        "disease_name": disease_name,
        "description": task.get("description") or "",
        "symptoms": task.get("symptoms") or "",
        "prevention": task.get("prevention") or "",
        "treatment": task.get("treatment") or "",
        "image_count": len(exported_images),
        "images": [{"file_name": x["file_name"]} for x in exported_images],
    }
    with open(os.path.join(export_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    return export_dir


class _PathsDataset(Dataset):
    def __init__(self, samples, transform):
        # samples: List[Tuple[str, int]]
        self.samples = samples
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        image = Image.open(path).convert("RGB")
        image = self.transform(image)
        return image, int(label)


def _read_active_model_path() -> str:
    active_model_path = os.path.join("models", "active_model.json")
    if os.path.exists(active_model_path):
        import json

        with open(active_model_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        p = data.get("model_path")
        if p and os.path.exists(p):
            return p
    return os.path.join("models", "model.pth")


def run_learning_training_job(job_id: int) -> str:
    """
    训练作业执行（微调增量训练）：
    - 仅训练分类头（冻结骨干），扩展输出维度 +1
    - 自定义类会做“自定义回放”（已训练过的自定义类）
    - 如果你还拥有旧 59 类的回放数据，可以继续在后续版本接入（当前实现先保证可跑通闭环）
    """
    job = db.get_train_job(job_id)
    if not job:
        raise ValueError(f"job not found: {job_id}")
    task_id = job["task_id"]
    task = db.get_learning_task(task_id)

    log_root = os.path.join(os.getcwd(), "training_logs")
    _ensure_dir(log_root)
    log_path = os.path.join(log_root, f"job_{job_id}.log")

    def log(msg: str) -> None:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n")

    db.set_train_job_status(job_id, "running", message="开始执行导出与校验…", log_path=log_path)
    log(f"job_id={job_id}, task_id={task_id}, task_status={task['status'] if task else None}")

    if not task or task["status"] != "approved":
        msg = "任务未通过审核，无法导出训练集。"
        log(msg)
        db.set_train_job_status(job_id, "failed", message=msg, log_path=log_path)
        return msg

    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        log(f"device={device}")

        # 导出（主要用于可视化/答辩留证；训练也会直接从 storage_path 读图）
        export_root = os.path.join(os.getcwd(), "datasets", "learning_exports")
        export_dir = export_approved_task_dataset(task_id, export_root)
        log(f"dataset_exported: {export_dir}")

        active_names = load_active_class_names()
        old_num = len(active_names)
        new_class_name = str(task["disease_name"]).strip()
        if not new_class_name:
            raise ValueError("disease_name 不能为空")

        # 如果已经训练过该 task，直接返回
        class_map = db.get_learning_task_class_map(task_id)
        if class_map:
            msg = f"该学习任务已训练过（class_id={class_map['class_id']}），跳过。"
            log(msg)
            db.set_train_job_status(job_id, "succeeded", message=msg, log_path=log_path)
            return msg

        new_class_id = old_num
        new_names = list(active_names) + [new_class_name]
        new_num = len(new_names)
        log(f"class expansion: {old_num} -> {new_num}, new_class_id={new_class_id}")

        # 收集训练样本：新类 + 已训练自定义回放（防遗忘）+ 旧 59 类回放（防遗忘）
        pending_samples = []
        with db.get_connection() as conn:
            rows = conn.execute(
                "SELECT storage_path FROM learning_images WHERE task_id = ?",
                (task_id,),
            ).fetchall()
        for r in rows:
            p = r["storage_path"]
            if os.path.exists(p):
                pending_samples.append((p, new_class_id))

        replay_samples = []
        maps = db.get_trained_learning_task_class_maps(exclude_task_id=task_id)
        for m in maps:
            t_id = m["task_id"]
            class_id = m["class_id"]
            with db.get_connection() as conn:
                r2 = conn.execute(
                    "SELECT storage_path FROM learning_images WHERE task_id = ?",
                    (t_id,),
                ).fetchall()
            for rr in r2:
                pp = rr["storage_path"]
                if os.path.exists(pp):
                    replay_samples.append((pp, class_id))

        # 旧 59 类回放：从你给的 2018 AI Challenger 训练集读取并做类别过滤/重映射
        rehearsal_per_class = int(os.environ.get("INCR_REHEARSAL_PER_CLASS", "5"))
        rehearsal_seed = int(os.environ.get("INCR_REHEARSAL_SEED", "123"))
        base_replay_samples = _sample_base_rehearsal_samples(
            per_class=rehearsal_per_class, seed=rehearsal_seed
        )

        samples = pending_samples + replay_samples + base_replay_samples
        if not samples:
            raise ValueError("未找到有效的训练图片文件（storage_path 不存在）")
        log(
            "samples: "
            f"new={len(pending_samples)}, "
            f"custom_replay={len(replay_samples)}, "
            f"base_replay={len(base_replay_samples)}, "
            f"total={len(samples)}"
        )

        # 训练超参（小步快跑，保证毕设演示）
        epochs = int(os.environ.get("INCR_EPOCHS", "5"))
        lr = float(os.environ.get("INCR_LR", "0.0005"))
        batch_size = int(os.environ.get("INCR_BATCH", "16"))
        log(f"hyperparams: epochs={epochs}, lr={lr}, batch_size={batch_size}")

        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        dataset = _PathsDataset(samples, transform)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)

        model = PlantDiseaseModel(num_classes=new_num).to(device)

        # 加载旧模型权重并“扩展 head”
        base_path = _read_active_model_path()
        base_state = torch.load(base_path, map_location="cpu")
        base_old_num = old_num
        new_state = model.state_dict()
        for k, v in base_state.items():
            if k in new_state and hasattr(v, "shape") and new_state[k].shape == v.shape:
                new_state[k] = v

        # 只复制 fc 的前 old_num 行，剩余行保持随机初始化
        w_key = "base_model.fc.weight"
        b_key = "base_model.fc.bias"
        if w_key in base_state and w_key in new_state:
            new_state[w_key][:base_old_num] = base_state[w_key]
        if b_key in base_state and b_key in new_state:
            new_state[b_key][:base_old_num] = base_state[b_key]

        model.load_state_dict(new_state, strict=False)

        # 冻结骨干，只训练分类头
        for p in model.parameters():
            p.requires_grad = False
        for p in model.base_model.fc.parameters():
            p.requires_grad = True

        optimizer = optim.Adam(model.base_model.fc.parameters(), lr=lr)
        criterion = nn.CrossEntropyLoss()

        model.train()
        for ep in range(epochs):
            running_loss = 0.0
            for images, labels in loader:
                images = images.to(device)
                labels = labels.to(device)
                optimizer.zero_grad()
                outputs = model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                running_loss += loss.item()
            log(f"epoch {ep+1}/{epochs} loss={running_loss/ max(1, len(loader)):.6f}")

        # 保存新模型并发布为 active
        versions_dir = os.path.join("models", "versions")
        _ensure_dir(versions_dir)
        model_v_path = os.path.join(versions_dir, f"model_v{job_id}.pth")
        torch.save(model.state_dict(), model_v_path)

        # 备份旧模型
        backup_path = os.path.join(versions_dir, f"model_backup_before_v{job_id}.pth")
        if os.path.exists(os.path.join("models", "model.pth")):
            shutil.copy2(os.path.join("models", "model.pth"), backup_path)
        shutil.copy2(model_v_path, os.path.join("models", "model.pth"))

        # 更新 active_class_names
        active_class_names_path = os.path.join("models", "active_class_names.json")
        with open(active_class_names_path, "w", encoding="utf-8") as f:
            import json

            json.dump(new_names, f, ensure_ascii=False, indent=2)

        # 写 active_model.json（可选）
        active_model_path = os.path.join("models", "active_model.json")
        with open(active_model_path, "w", encoding="utf-8") as f:
            import json

            json.dump({"model_path": os.path.join("models", "model.pth")}, f, ensure_ascii=False, indent=2)

        # 记录版本与映射
        source = f"learning_task:{task_id}"
        notes = f"incremental_finetune; expanded classes {old_num}->{new_num}; new='{new_class_name}'"
        model_version_id = None
        with db.get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO model_versions (source, model_path, status, notes)
                VALUES (?, ?, 'active', ?)
                """,
                (source, os.path.join("models", "model.pth"), notes),
            )
            model_version_id = cur.lastrowid

        db.assign_learning_task_class(
            task_id=task_id,
            class_id=new_class_id,
            class_name=new_class_name,
            model_version_id=model_version_id,
        )

        msg = f"增量训练完成：已将学习任务映射到 class_id={new_class_id}，并发布新模型。"
        log(msg)
        db.set_train_job_status(job_id, "succeeded", message=msg, log_path=log_path)
        return msg
    except Exception as e:
        msg = f"训练作业失败：{e}"
        log(msg)
        db.set_train_job_status(job_id, "failed", message=msg, log_path=log_path)
        return msg

