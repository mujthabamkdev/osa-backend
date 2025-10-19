from typing import Dict, Optional

from pydantic import BaseModel, Field


class AdminSettings(BaseModel):
    feature_flags: Dict[str, bool] = Field(default_factory=dict)
    role_permissions: Dict[str, Dict[str, bool]] = Field(default_factory=dict)


class AdminSettingsUpdate(BaseModel):
    feature_flags: Optional[Dict[str, bool]] = None
    role_permissions: Optional[Dict[str, Dict[str, bool]]] = None
