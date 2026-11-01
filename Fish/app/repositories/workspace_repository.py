from typing import Optional
from sqlalchemy.orm import Session
from app.models.workspace import Workspace
from app.schemas.workspace_schema import WorkspacePipelineConfig


class WorkspaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, Workspace_id: int):
        return self.db.query(Workspace).filter(Workspace.id == Workspace_id).first()

    def create(self, name: str, owner_id: int, pipeline_config: Optional[dict] = None):
        cfg = pipeline_config or WorkspacePipelineConfig().model_dump()
        workspace = Workspace(name=name, owner_id=owner_id, pipeline_config=cfg)
        self.db.add(workspace)
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def list_by_owner(self, owner_id: int):
        return self.db.query(Workspace).filter(Workspace.owner_id == owner_id).all()
