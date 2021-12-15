import random
from config import Config


class Room:
    def __init__(self, token, name, max_players):
        self.name, self.max_players = name, max_players
        self.token = token
        self.players_list = []
        self.new_player_id = 1
        self.available = True
        self.colors_list = random.sample(Config.colors, self.max_players)

    def delete_client(self, client):
        self.players_list.remove(client)

    def __repr__(self):
        return f'{self.token} cnt:{len(self.players_list)} av:{self.available}'
