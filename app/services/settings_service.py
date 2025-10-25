from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.models.platform_setting import PlatformSetting

DEFAULT_SCHEDULE_CONFIG: Dict[str, int] = {
    "max_lessons_per_day": 3,
}


def merge_dict(defaults: Dict, overrides: Optional[Dict]) -> Dict:
    merged = {**defaults}
    if not overrides:
        return merged
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            nested_default = merged.get(key, {})
            merged[key] = {**nested_default, **value}
        else:
            merged[key] = value
    return merged


def get_platform_setting(db: Session, key: str, fallback: Dict) -> Dict:
    setting = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
    if not setting:
        setting = PlatformSetting(key=key, value=fallback)
        db.add(setting)
        db.commit()
        db.refresh(setting)
        return fallback
    return merge_dict(fallback, setting.value or {})


def save_platform_setting(
    db: Session,
    key: str,
    value: Dict,
    description: Optional[str] = None,
) -> Dict:
    setting = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
    if setting:
        setting.value = value
        if description is not None:
            setting.description = description
    else:
        setting = PlatformSetting(key=key, value=value, description=description)
        db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting.value
