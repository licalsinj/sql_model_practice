from sqlmodel import Field, Relationship, Session, SQLModel, select
from ..db import engine
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .hero_model import Hero

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str
    heroes: list["Hero"] = Relationship(back_populates="team")
    
    # TEAM CREATE
    def create_team(team: Team) -> Team:
        try:
            with Session(engine) as session:
                session.add(team)
                session.commit()
                session.refresh(team)
                return team
        except Exception as e:
            raise e

    # TEAM RETRIEVE

    # TEAM UPDATE

    # TEAM DELETE



