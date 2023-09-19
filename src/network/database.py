from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from time import time
import os
import sqlite3


Base = declarative_base()

class Player(Base):
    __tablename__ = 'Players'
    ip = Column(String, primary_key=True)
    name = Column(String)


class Game(Base):
    __tablename__ = 'Games'
    id = Column(String, primary_key=True)
    player1_ip = Column(String, ForeignKey('Players.ip'))
    player2_ip = Column(String, ForeignKey('Players.ip'))
    winner = Column(String)
    state = Column(String)


class PlayedGames(Base):
    __tablename__ = 'PlayedGames'
    id = Column(Integer, primary_key=True)
    player_ip = Column(String, ForeignKey('Players.ip'))
    game_id = Column(String, ForeignKey('Games.id'))


class Database:
    def __init__(self):
        root_dir = os.path.dirname(os.path.abspath(__file__))

        if not os.path.exists(root_dir + '\\chess_database.db'):
            create_database()

        self.engine = create_engine(f'sqlite:///{root_dir}\\chess_database.db', echo=True)
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get_player_from_name(self, player_name) -> Player | None:
        return self.session.query(Player).filter_by(name=player_name).first()

    def get_game_by_id(self, game_id) -> Game | None:
        return self.session.query(Game).filter_by(id=game_id).first()

    def get_played_games(self, player: Player) -> list[Game]:
        games = []
        played_games = self.session.query(PlayedGames).filter_by(player_ip=player.ip).all()

        for game in played_games:
            games.append(self.get_game_by_id(game.game_id))

        return games

    def get_all_games(self):
        return self.session.query(Game).all()

    def get_player_wins_losses(self, player_name) -> (int, int):
        player = self.get_player_from_name(player_name)
        games_played = self.get_played_games(player)
        total_games = len(games_played)
        wins = len([game for game in games_played if game.winner == player.ip])
        losses = total_games - wins
        return wins, losses

    def get_head_to_head(self, player1_name: str, player2_name: str) -> (int, int):
        player1 = self.get_player_from_name(player1_name)
        player2 = self.get_player_from_name(player2_name)

        player1_games_played = self.get_played_games(player1)

        games_against_opponent = [
            game for game in player1_games_played
            if (game.player1_ip == player2.ip or
                game.player2_ip == player2.ip)
        ]

        wins = len([game for game in games_against_opponent if game.winner == player1.name])
        losses = len(games_against_opponent) - wins

        return wins, losses

    def add_player(self, player_name: str, player_ip: str) -> bool:
        # Lookup by name first, if name exists don't add the player. Then if IP exists, change name instead of inserting
        player = self.get_player_from_name(player_name)
        if player is not None:
            return False

        player = self.session.query(Player).filter_by(ip=player_ip).first()
        if player is not None:
            player.name = player_name
        else:
            player = Player(name=player_name, ip=player_ip)
            self.session.add(player)

        self.session.commit()
        return True

    def add_played_games(self, player: Player, *games: Game):
        index = len(self.session.query(PlayedGames).all()) + 1
        for game in games:
            played_game = PlayedGames(id=index, player_ip=player.ip, game_id=game.id)
            self.session.add(played_game)
            index += 1

    def add_game(self, player1_name: str, player2_name: str, winner: str, state: str) -> None:
        if winner != player1_name and winner != player2_name:
            return

        player1 = self.get_player_from_name(player1_name)
        player2 = self.get_player_from_name(player2_name)
        if player1 is None or player2 is None:
            return

        game_id = str(time())
        game = Game(id=game_id, player1_ip=player1.ip, player2_ip=player2.ip, winner=winner, state=state)
        self.session.add(game)
        self.add_played_games(player1, game)
        self.add_played_games(player2, game)
        self.session.commit()

    def get_players(self):
        return self.session.query(Player).all()

    def close_database(self):
        self.session.close()


def create_database():
    sql_commands = [
        """
        CREATE TABLE Players (
            ip TEXT PRIMARY KEY,
            name TEXT
        )
        """,
        """
        CREATE TABLE Games (
            id TEXT PRIMARY KEY,
            player1_ip TEXT,
            player2_ip TEXT,
            winner TEXT,
            state TEXT,
            FOREIGN KEY (player1_ip) REFERENCES Players (ip),
            FOREIGN KEY (player2_ip) REFERENCES Players (ip)
        )
        """,
        """
        CREATE TABLE PlayedGames (
            id TEXT PRIMARY KEY,
            player_ip TEXT,
            game_id TEXT,
            FOREIGN KEY (player_ip) REFERENCES Players (ip),
            FOREIGN KEY (game_id) REFERENCES Games (ip)
        )
        """
    ]

    root_dir = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(root_dir + '\\' +'chess_database.db')
    cursor = conn.cursor()

    for command in sql_commands:
        cursor.execute(command)

    conn.commit()
    conn.close()
