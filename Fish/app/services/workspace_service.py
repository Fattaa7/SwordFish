from sqlalchemy.orm import Session
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace_schema import WorkspaceCreate, WorkspaceResponse

class WorkspaceService:
    @staticmethod
    def create_workspace(db: Session, workspace: WorkspaceCreate, owner_id: int) -> WorkspaceResponse:
        repo = WorkspaceRepository(db)

        # Create workspace via repository
        return repo.create(name=workspace.name, owner_id=owner_id)

    @staticmethod
    def get_workspace(db: Session, workspace_id: int, owner_id: int):
        repo = WorkspaceRepository(db)
        workspace = repo.get_by_id(workspace_id)

        if not workspace:
            raise ValueError("Workspace not found")

        if workspace.owner_id != owner_id:
            raise ValueError("You do not have permission to access this workspace")

        return workspace
