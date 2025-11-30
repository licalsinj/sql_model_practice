import os
from dotenv import load_dotenv
from sqlmodel import Session, select
from sqlmodel import SQLModel, Field, Relationship, col, or_
from .db import engine, create_db_and_tables

# from .models.team_model import Team
# from .models.hero_model import Hero

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str
    # for cascade delete use cascade_delete=True
    # otherwise use passive_deletes="all" for set null
    heroes: list["Hero"] = Relationship(back_populates="team", passive_deletes="all")
    
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
    # ondelete="CASCADE" will delete from this table when fk is deleted
    # ondelete="RESTRICT" will keep you from being able to delete it if it's got relations
    team_id: int | None = Field(default=None, foreign_key="team.id", ondelete="SET NULL")
    team: Team | None = Relationship(back_populates="heroes")



# HERO CREATE
def create_hero(hero: Hero) -> Hero:
    try:
        with Session(engine) as session:
            session.add(hero)
            session.commit()
            session.refresh(hero)
            if hero.team:
                session.refresh(hero.team)
            return hero
    except Exception as e:
        raise e


def create_heroes(heroes: list[Hero]) -> bool:
    try:
        with Session(engine) as session:
            for hero in heroes:
                session.add(hero)
            session.commit()
            for hero in heroes:
                session.refresh(hero)
    except Exception as e:
        raise e
    return True

def add_hero_to_team(hero: Hero, team: Team) -> Hero:
    with Session(engine) as session:
        try:
            hero.team = team
            session.add(hero)
            session.commit()
            session.refresh(hero)
            session.refresh(team)
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
            hero.team = None
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
    

# TEAM CREATE
def create_team(team: Team) -> Team:
    try:
        with Session(engine) as session:
            session.add(team)
            session.commit()
            session.refresh(team)
            for hero in team.heroes:
                session.refresh(hero)
            return team
    except Exception as e:
        raise e
    
# TEAM DELETE
def delete_team(team: Team) -> bool:
    try:
        with Session(engine) as session:
            session.delete(team)
            session.commit()
    except Exception as e:
        raise e
    return True

# TEAM-HERO Retrieves  
def select_team_by_id(team_id: int) -> Team:
    try:
        with Session(engine) as session:
            statement = select(Team).where(Team.id == team_id)
            return session.exec(statement).one_or_none()
    except Exception as e:
        raise e

def select_heroes_in_teams() -> list[(Hero, Team)]:
    with Session(engine) as session:
        statement = select(Hero, Team).where(Hero.team_id == Team.id)
        # statement = select(Hero, Team).join(Team) # equivalent to above
        try: 
            results = session.exec(statement).all()
            return results
        except Exception as e:
            raise e
        
def select_all_heroes_and_their_teams() -> list[(Hero, Team)]:
    with Session(engine) as session:
        statement = select(Hero, Team).join(Team, isouter=True)
        try:
            return session.exec(statement).all()
        except Exception as e:
            raise e
        
def select_heroes_by_team(team: Team) -> list[Hero]:
    try:
        with Session(engine) as session:
            statement = select(Team).where(Team.id == team.id)
            return session.exec(statement).one().heroes
    except Exception as e:
        raise e


def main():
    load_dotenv(".venv/.env")
    try:
        os.remove(os.getenv('DB_NAME'))
    except:
        print("No database.db to delete")

    create_db_and_tables()

    team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
    
    team_z = Team(name="Z-Force", headquarters="Sister Margaret's Bar")

    # create a single hero
    hero_1: Hero
    try:
        hero_1 = create_hero(Hero(name="Deadpond", secret_name="Dive Wilson",team=team_z))
    except Exception as e:
        raise e

    # create another single hero
    hero_1: Hero
    try:
        hero_1 = create_hero(Hero(name="Hunk", secret_name="Bryce Poster"))
    except Exception as e:
        raise e
    
    my_heroes = []
    my_heroes.append(Hero(name="Spider-Boy", secret_name="Pedro Parqueador"))
    my_heroes.append(Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48, team=team_preventers))
    my_heroes.append(Hero(name="Tarantula", secret_name="Natalia Roman-on", age=32))
    my_heroes.append(Hero(name="Black Lion", secret_name="Trevor Challa", age=35))
    my_heroes.append(Hero(name="Dr. Weird", secret_name="Steve Weird", age=36))
    my_heroes.append(Hero(name="Captain North America", secret_name="Esteban Rogelios", age=93))
    my_heroes.append(Hero(name="Spider-Youngster", secret_name="Mikey Moorales", age=18))
    try:
       create_heroes(my_heroes)
    except Exception as e:
        raise e
    
    print("Add Heroes to Teams")
    add_hero_to_team(my_heroes[0],team_preventers)
    add_hero_to_team(my_heroes[2],team_preventers)
    add_hero_to_team(my_heroes[5],team_preventers)
    add_hero_to_team(my_heroes[3],team_preventers)

    print()
    print("Find Deadpond")
    for hero in select_heroes_by_name("Deadpond"):
        print(hero)
    
    print()
    print("Find everyone else")
    for hero in select_heroes_not_by_name("Deadpond"):
        print(hero)
    
    print()
    print("Older than 35")
    for hero in select_heroes_by_age(35):
        print(hero)
    
    print()
    print("Between than 35 and 50")
    for hero in select_heroes_by_age_range(30,50):
        print(hero)
    
    print()
    print("Outside 35 and 50")
    for hero in select_heroes_outside_age_range(30,50):
        print(hero)
    
    print()
    print("First hero!")
    print(select_first_hero())

    print()
    print("One or Error")
    print(select_one_hero("Dive Wilson"))

    print()
    print("Hero by ID")
    print(select_hero_by_id(4))

    print()
    print("Hero over 9,000")
    print(select_hero_by_id(9001))

    print()
    print("Selecting 3 heroes")
    for hero in select_n_heroes(3):
        print(hero)

    print()
    print("Select 3 with offset 4")
    for hero in select_n_with_offset(3,4):
        print(hero)

    print()
    print("Set Spider-Boy age to 16")
    print(update_hero_age_by_name(16,"Spider-Boy"))

    print()
    print("Fail to update because no name")
    try:
        update_hero_age_by_name(16,"spoder-boi")
    except Exception as e:
        print(f"Error: {e}")

    print()
    print("Delete Spider-Youngster")
    print(delete_hero_by_name("Spider-Youngster"))


    print()
    print("Find all heroes that belong to a team")
    heroes_on_teams = select_heroes_in_teams()
    for hero in heroes_on_teams:
        print(hero)

    print()
    print("Find all heroes and associated team info if it's there")
    heroes_on_teams = select_all_heroes_and_their_teams()
    for hero in heroes_on_teams:
        print(hero)

    print()
    print("Find a team")
    print(select_team_by_id(team_z.id))

    print()
    print("Find Heroes on Preventers")
    heroes_on_team = select_heroes_by_team(team_preventers)
    for hero in heroes_on_team:
       print(hero)

    print()
    print("Remove Black Lion from Preventers")
    print(remove_hero_from_team(my_heroes[3]))

    print()
    print("Create New Team with new hero")
    hero_sure_e = Hero(name="Princess Sure-E", secret_name="Sure-E")
    # create_hero(hero_sure_e)
    team_wakaland = Team(
        name="Wakaland",
        headquarters="Wakaland Capital City",
        # this should put hero_sure_e in the DB without a specific create hero call
        heroes=[my_heroes[3], hero_sure_e],
    )
    team_wakaland = create_team(team_wakaland)
    print(team_wakaland.name)
    for hero in team_wakaland.heroes:
        print(hero)

    former_wakaland_heroes = team_wakaland.heroes
    print()
    print("Delete team Wakaland")
    is_success = delete_team(team_wakaland)
    print("Success? " + str(is_success))
    # should clear team_id and team.
    for hero in former_wakaland_heroes:
        print(select_hero_by_id(hero.id))

if __name__ == "__main__":
    main()