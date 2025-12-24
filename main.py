# main.py
from __future__ import annotations

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, Dict

from auth import init_firebase, require_user
from datastorage import load_user, get_child_profile, update_child_profile, load_lessons, load_challenges

app = FastAPI(title="CodeCadet API", version="1.0")

# Allow Javascript frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  #Allow the requests from the frontend to go to the backend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialise Firebase
init_firebase("serviceAccountKey.json")


class ProfileUpdate(BaseModel):
    nickname: str | None = None
    ageRange: str | None = None
    currentLesson: int | None = None
    lessonsCompleted: list[int] | None = None
    challengesCompleted: list[str] | None = None
    badgesEarned: list[str] | None = None
    coins: int | None = None
    points: int | None = None


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/me")
def me(uid: str = Depends(require_user)) -> Dict[str, Any]:
    """
    Confirms token is valid and returns server-side user record summary.
    """
    user = load_user(uid)
    return {"uid": uid, "children": list(user.get("children", {}).keys())}


@app.get("/progress/{child_id}")
def get_progress(child_id: str, uid: str = Depends(require_user)) -> Dict[str, Any]:
    """
    Protected route: returns progress for chosen child profile.
    """
    profile = get_child_profile(uid, child_id)
    return {"uid": uid, "childId": child_id, "profile": profile}


@app.put("/progress/{child_id}")
def put_progress(child_id: str, update: ProfileUpdate, uid: str = Depends(require_user)) -> Dict[str, Any]:
    """
    Protected route: updates progress for chosen child profile.
    """
    updated = update_child_profile(uid, child_id, update.model_dump(exclude_none=True))
    return {"uid": uid, "childId": child_id, "profile": updated}


@app.get("/lessons")
def get_lessons(uid: str = Depends(require_user)) -> Dict[str, Any]:
    """
    Returns all available lessons.
    """
    return load_lessons()


@app.get("/challenges")
def get_challenges(uid: str = Depends(require_user)) -> Dict[str, Any]:
    """
    Returns all available challenges.
    """
    return load_challenges()
