from typing import Dict, Optional

from pydantic import BaseModel, Field


class AdminSettings(BaseModel):
    feature_flags: Dict[str, bool] = Field(default_factory=dict)
    role_permissions: Dict[str, Dict[str, bool]] = Field(default_factory=dict)
    schedule_config: Dict[str, int] = Field(default_factory=lambda: {"max_lessons_per_day": 3})


class AdminSettingsUpdate(BaseModel):
    feature_flags: Optional[Dict[str, bool]] = None
    role_permissions: Optional[Dict[str, Dict[str, bool]]] = None
    schedule_config: Optional[Dict[str, int]] = None
