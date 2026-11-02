import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Snake, Species, User
from app.schemas import SnakeCreate, SnakeOut, SnakeUpdate, SpeciesOut

router = APIRouter(prefix="/api", tags=["snakes"])


def get_own_snake(db: Session, snake_id: uuid.UUID, user: User) -> Snake:
    """Zwraca węża tylko jeśli należy do użytkownika (używane też w carelog)."""
    snake = db.get(Snake, snake_id)
    if snake is None or snake.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie znaleziono węża")
    return snake


@router.get("/species", response_model=list[SpeciesOut])
def list_species(db: Session = Depends(get_db)):
    return db.scalars(select(Species).order_by(Species.name)).all()


@router.get("/snakes", response_model=list[SnakeOut])
def list_snakes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(
        select(Snake).where(Snake.user_id == user.id).order_by(Snake.name)
    ).all()


@router.post("/snakes", response_model=SnakeOut, status_code=status.HTTP_201_CREATED)
def create_snake(
    data: SnakeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if db.get(Species, data.species_id) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Nieznany gatunek")
    snake = Snake(user_id=user.id, **data.model_dump())
    db.add(snake)
    db.commit()
    db.refresh(snake)
    return snake


@router.get("/snakes/{snake_id}", response_model=SnakeOut)
def get_snake(
    snake_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_own_snake(db, snake_id, user)


@router.patch("/snakes/{snake_id}", response_model=SnakeOut)
def update_snake(
    snake_id: uuid.UUID,
    data: SnakeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    snake = get_own_snake(db, snake_id, user)
    changes = data.model_dump(exclude_unset=True)
    if "species_id" in changes and db.get(Species, changes["species_id"]) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Nieznany gatunek")
    for field, value in changes.items():
        setattr(snake, field, value)
    db.commit()
    db.refresh(snake)
    return snake


@router.delete("/snakes/{snake_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snake(
    snake_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    snake = get_own_snake(db, snake_id, user)
    db.delete(snake)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)