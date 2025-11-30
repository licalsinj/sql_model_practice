from sqlmodel import Field, Session, SQLModel, col, create_engine, or_, select
import os

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
    team_id: int | None = Field(default=None, foreign_key="team.id")

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def create_hero(hero: Hero) -> Hero | Exception:
    try:
        with Session(engine) as session:
            session.add(hero)
            session.commit()
            session.refresh(hero)
            return hero
    except Exception as e:
        return e


def create_heroes(heroes: list[Hero]) -> bool | Exception:
    try:
        with Session(engine) as session:
            for hero in heroes:
                session.add(hero)
            session.commit()
    except Exception as e:
        return e
    return True

def create_team(team: Team) -> Team | Exception:
    try:
        with Session(engine) as session:
            session.add(team)
            session.commit()
            session.refresh(team)
            return team
    except Exception as e:
        return e


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

def select_one_hero(name: str) -> Hero | Exception:
    with Session(engine) as session:
        statement = select(Hero).where(Hero.secret_name == name)
        try:
            return session.exec(statement).one()
        except Exception as e :
            return e

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

def update_hero_age_by_name(age: int, name: str) -> Hero | Exception:
    with Session(engine) as session:
        statement = select(Hero).where(Hero.name == name)
        try:
            hero = session.exec(statement).one()
        except Exception as e:
            return e
        hero.age = age
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero
    
def delete_hero_by_name(name: str) -> str | Exception:
    with Session(engine) as session:
        statement = select(Hero).where(Hero.name == name)
        try:
            hero = session.exec(statement).one()
        except Exception as e:
            return e
        session.delete(hero)
        session.commit()
        if session.exec(statement).first() == None:
            return f"Successfully Deleted Hero {name}"
        else: 
            return RuntimeError(f"Hero {name} was NOT deleted for an unknown reason")
    


def main():
    try:
        os.remove("database.db")
        create_db_and_tables()
    except Exception as e:
        print(e)
        quit()
    
    team_1 = create_team(Team(name="Preventers", headquarters="Sharp Tower"))
    if isinstance(team_1, Exception):
        raise team_1

    team_2 = create_team(Team(name="Z-Force", headquarters="Sister Margaret's Bar"))
    if isinstance(team_1, Exception):
        raise team_2


    # create a single hero
    hero_1 = create_hero(Hero(name="Deadpond", secret_name="Dive Wilson",team_id=team_2.id))
    if isinstance(hero_1, Exception):
        raise hero_1

    my_heroes = []
    my_heroes.append(Hero(name="Spider-Boy", secret_name="Pedro Parqueador"))
    my_heroes.append(Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48, team_id=team_1.id))
    my_heroes.append(Hero(name="Tarantula", secret_name="Natalia Roman-on", age=32))
    my_heroes.append(Hero(name="Black Lion", secret_name="Trevor Challa", age=35))
    my_heroes.append(Hero(name="Dr. Weird", secret_name="Steve Weird", age=36))
    my_heroes.append(Hero(name="Captain North America", secret_name="Esteban Rogelios", age=93))
    my_heroes.append(Hero(name="Spider-Youngster", secret_name="Mikey Moorales", age=18))
    is_success = create_heroes(my_heroes)
    if is_success != True:
        raise is_success
    
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
    print(update_hero_age_by_name(16,"spoder-boi"))

    print()
    print("Delete Spider-Youngster")
    print(delete_hero_by_name("Spider-Youngster"))

if __name__ == "__main__":
    main()