from fastapi import APIRouter

from app.services.agent_service import AgentService

router = APIRouter()

service = AgentService()


@router.post("/chat")

def chat(request: dict):

    result = service.execute(

        prompt=request["prompt"],

        session_id=request.get(
            "session_id",
            "default",
        ),
    )

    return {

        "success": result.success,

        "output": result.final_output,
    }