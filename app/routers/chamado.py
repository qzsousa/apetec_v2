from fastapi import APIRouter, Depends, HTTPException
from app.models import Chamado
from app.database import get_session
from sqlmodel import Session, select

router = APIRouter(prefix="/chamados", tags=["Chamados"])