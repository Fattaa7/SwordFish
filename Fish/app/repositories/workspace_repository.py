from sqlalchemy.orm import Session
from app.models.workspace import Workspace


class WorkspaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, Workspace_id: int):
        return self.db.query(Workspace).filter(Workspace.id == Workspace_id).first()

    def create(self, name: str, owner_id: int):
        workspace = Workspace(name=name, owner_id=owner_id)
        self.db.add(workspace)
        self.db.commit()
        self.db.refresh(workspace)
        return workspace
    
    def list_by_owner(self, owner_id: int):
        return self.db.query(Workspace).filter(Workspace.owner_id == owner_id).all()
