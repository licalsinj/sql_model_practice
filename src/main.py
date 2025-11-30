import os
from dotenv import load_dotenv
from sqlmodel import Session, select
from .db import engine, create_db_and_tables
from .hero_model import Hero
from .team_model import Team

# TEAM-HERO Retrieves  
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
    with Session(engine) as session:
        try:
            statement = select(Hero).join(Team).where(Hero.team_id == team.id)
            return session.exec(statement).all()
        except Exception as e:
            raise e


def main():
    load_dotenv(".venv/.env")
    try:
        os.remove(os.getenv('DB_NAME'))
    except:
        print("No database.db to delete")

    create_db_and_tables()

    team_1 = Team.create_team(Team(name="Preventers", headquarters="Sharp Tower"))
    if isinstance(team_1, Exception):
        raise team_1

    team_2 = Team.create_team(Team(name="Z-Force", headquarters="Sister Margaret's Bar"))
    if isinstance(team_1, Exception):
        raise team_2


    # create a single hero
    hero_1: Hero
    try:
        hero_1 = Hero.create_hero(Hero(name="Deadpond", secret_name="Dive Wilson",team_id=team_2.id))
    except Exception as e:
        raise e

    my_heroes = []
    my_heroes.append(Hero(name="Spider-Boy", secret_name="Pedro Parqueador"))
    my_heroes.append(Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48, team_id=team_1.id))
    my_heroes.append(Hero(name="Tarantula", secret_name="Natalia Roman-on", age=32))
    my_heroes.append(Hero(name="Black Lion", secret_name="Trevor Challa", age=35))
    my_heroes.append(Hero(name="Dr. Weird", secret_name="Steve Weird", age=36))
    my_heroes.append(Hero(name="Captain North America", secret_name="Esteban Rogelios", age=93))
    my_heroes.append(Hero(name="Spider-Youngster", secret_name="Mikey Moorales", age=18))
    try:
       Hero.create_heroes(my_heroes)
    except Exception as e:
        raise e
    
    print("Add Heroes to Teams")
    Hero.add_hero_to_team(my_heroes[0],team_1)
    Hero.add_hero_to_team(my_heroes[2],team_1)
    Hero.add_hero_to_team(my_heroes[5],team_1)
    Hero.add_hero_to_team(my_heroes[3],team_1)

    print()
    print("Find Deadpond")
    for hero in Hero.select_heroes_by_name("Deadpond"):
        print(hero)
    
    print()
    print("Find everyone else")
    for hero in Hero.select_heroes_not_by_name("Deadpond"):
        print(hero)
    
    print()
    print("Older than 35")
    for hero in Hero.select_heroes_by_age(35):
        print(hero)
    
    print()
    print("Between than 35 and 50")
    for hero in Hero.select_heroes_by_age_range(30,50):
        print(hero)
    
    print()
    print("Outside 35 and 50")
    for hero in Hero.select_heroes_outside_age_range(30,50):
        print(hero)
    
    print()
    print("First hero!")
    print(Hero.select_first_hero())

    print()
    print("One or Error")
    print(Hero.select_one_hero("Dive Wilson"))

    print()
    print("Hero by ID")
    print(Hero.select_hero_by_id(4))

    print()
    print("Hero over 9,000")
    print(Hero.select_hero_by_id(9001))

    print()
    print("Selecting 3 heroes")
    for hero in Hero.select_n_heroes(3):
        print(hero)

    print()
    print("Select 3 with offset 4")
    for hero in Hero.select_n_with_offset(3,4):
        print(hero)

    print()
    print("Set Spider-Boy age to 16")
    print(Hero.update_hero_age_by_name(16,"Spider-Boy"))

    print()
    print("Fail to update because no name")
    try:
        Hero.update_hero_age_by_name(16,"spoder-boi")
    except Exception as e:
        print(f"Error: {e}")

    print()
    print("Delete Spider-Youngster")
    print(Hero.delete_hero_by_name("Spider-Youngster"))


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
    print("Find Heroes on Preventers")
    heroes_on_team = select_heroes_by_team(team_1)
    for hero in heroes_on_team:
        print(hero)

    print()
    print("Remove Black Lion from Preventers")
    print(Hero.remove_hero_from_team(my_heroes[3]))

if __name__ == "__main__":
    main()