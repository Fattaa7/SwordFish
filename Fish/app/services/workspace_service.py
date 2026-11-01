from sqlalchemy.orm import Session
from app.core.rag_pipeline import get_rag_pipeline
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace_schema import WorkspaceCreate, WorkspacePipelineConfig, WorkspaceResponse


class WorkspaceService:
    @staticmethod
    def create_workspace(
        db: Session, workspace: WorkspaceCreate, owner_id: int
    ) -> WorkspaceResponse:
        repo = WorkspaceRepository(db)
        cfg = (
            workspace.pipeline_config.model_dump()
            if workspace.pipeline_config
            else WorkspacePipelineConfig().model_dump()
        )
        return repo.create(name=workspace.name, owner_id=owner_id, pipeline_config=cfg)

    @staticmethod
    def get_workspace(db: Session, workspace_id: int, owner_id: int):
        repo = WorkspaceRepository(db)
        workspace = repo.get_by_id(workspace_id)

        if not workspace:
            raise ValueError("Workspace not found")

        if workspace.owner_id != owner_id:
            raise ValueError("You do not have permission to access this workspace")

        return workspace

    @staticmethod
    def list_workspaces(db: Session, owner_id: int):
        repo = WorkspaceRepository(db)
        return repo.list_by_owner(owner_id)

    @staticmethod
    def query_workspace(db: Session, workspace_id: int, query: str, owner_id: int):
        workspace = WorkspaceService.get_workspace(db, workspace_id, owner_id)
        cfg = workspace.pipeline_config or {}
        pipeline = get_rag_pipeline(cfg)
        answer = pipeline.ask(
            query=query,
            top_k=int(cfg.get("top_k", 20)),
            rerank_top_k=int(cfg.get("rerank_top_k", 10)),
            filters={"workspace_id": str(workspace_id)},
        )
        return {
            "query": query,
            "response": answer.answer,
            "citations": [c.model_dump() for c in answer.citations],
            "metadata": answer.metadata,
        }
