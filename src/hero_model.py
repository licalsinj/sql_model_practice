from sqlmodel import Field, Session, SQLModel, col, or_, select
from .db import engine
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .team_model import Team

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
    team_id: int | None = Field(default=None, foreign_key="team.id")

    # HERO CREATE
    def create_hero(hero: Hero) -> Hero:
        try:
            with Session(engine) as session:
                session.add(hero)
                session.commit()
                session.refresh(hero)
                return hero
        except Exception as e:
            raise e


    def create_heroes(heroes: list[Hero]) -> bool:
        try:
            with Session(engine) as session:
                for hero in heroes:
                    session.add(hero)
                session.commit()
        except Exception as e:
            raise e
        return True

    def add_hero_to_team(hero: Hero, team: Team) -> Hero:
        with Session(engine) as session:
            try:
                hero.team_id = team.id
                session.add(hero)
                session.commit()
                session.refresh(hero)
                return hero
            except Exception as e:
                raise e

    # HERO RETRIEVE 
    def select_heroes_by_name(name: str) -> list[Hero]:
        with Session(engine) as session:
            statement = select(Hero).where(Hero.name == name)
            return session.exec(statement).all()
            

    def select_heroes_not_by_name(name: str) -> list[Hero]:
        with Session(engine) as session:
            statement = select(Hero).where(Hero.name != name)
            return session.exec(statement).all()

    def select_heroes_by_age(age: int) -> list[Hero]:
        with Session(engine) as session:
            # col() handles the fact that age is potentially None for the type annotations
            statement = select(Hero).where(col(Hero.age) > age)
            return session.exec(statement).all()

    def select_heroes_by_age_range(min_age: int, max_age: int) -> list[Hero]:
        with Session(engine) as session:
            statement = select(Hero).where(Hero.age >= min_age, Hero.age <= max_age)
            return session.exec(statement).all()

    def select_heroes_outside_age_range(min_age: int, max_age: int) -> list[Hero]:
        with Session(engine) as session:
            statement = select(Hero).where(or_(Hero.age < min_age, Hero.age > max_age))
            return session.exec(statement).all()

    def select_first_hero() -> Hero:
        with Session(engine) as session:
            statement = select(Hero)
            return session.exec(statement).first()

    def select_one_hero(name: str) -> Hero:
        with Session(engine) as session:
            statement = select(Hero).where(Hero.secret_name == name)
            try:
                return session.exec(statement).one()
            except Exception as e:
                raise e

    def select_hero_by_id(id: int) -> Hero:
        with Session(engine) as session:
            return session.get(Hero, id)
        
    def select_n_heroes(n: int) -> list[Hero]:
        with Session(engine) as session:
            statement = select(Hero).limit(n)
            return session.exec(statement).all()
        
    def select_n_with_offset(n: int, o: int) ->list[Hero]:
        with Session(engine) as session:
            statement = select(Hero).offset(o).limit(n)
            return session.exec(statement).all()

    # HERO UPDATES
    def update_hero_age_by_name(age: int, name: str) -> Hero:
        with Session(engine) as session:
            statement = select(Hero).where(Hero.name == name)
            try:
                hero = session.exec(statement).one()
                hero.age = age
                session.add(hero)
                session.commit()
                session.refresh(hero)
                return hero
            except Exception as e:
                    raise e

    def remove_hero_from_team(hero: Hero) -> Hero:
        try:
            with Session(engine) as session:
                hero.team_id = None
                session.add(hero)
                session.commit()
                session.refresh(hero)
                return hero
        except Exception as e:
            raise e


    # HERO DELETE
    def delete_hero_by_name(name: str) -> str:
        with Session(engine) as session:
            statement = select(Hero).where(Hero.name == name)
            try:
                hero = session.exec(statement).one()
            except Exception as e:
                raise e
            session.delete(hero)
            session.commit()
            if session.exec(statement).first() == None:
                return f"Successfully Deleted Hero {name}"
            else: 
                raise RuntimeError(f"Hero {name} was NOT deleted for an unknown reason")
        