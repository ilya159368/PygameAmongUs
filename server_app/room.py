import random
from config import Config
import threading
from protocol import Token


class Room:
    def __init__(self, token, name, max_players):
        self.name, self.max_players = name, max_players
        self.token = token
        self.players_list = []
        self.new_player_id = 1
        self.available = True
        self.colors_list = random.sample(Config.colors, self.max_players)
        self.tasks_progress = 0
        self.imposter_count = 1
        self.skip_votes = 0

    def init(self):
        self.win_condition = len(self.players_list) * Config.task_per_player
        self.players_votes = [0] * len(self.players_list)
        self.players_list[random.randrange(len(self.players_list))].imposter = True

    def check_win(self):
        if self.tasks_progress >= self.win_condition:
            ...
        elif len([1 for pl in self.players_list if not pl.imposter]) < 3:
            ...

    def start_voting(self):
        threading.Timer(60, self.end_voting).start()

    def end_voting(self):
        # most_voted_player: int = max(self.players_votes)  # количество
        out = None
        lst = sorted(self.players_votes)
        most_voted_player = lst[-1]
        if lst[-1] != lst[-2] and self.skip_votes < most_voted_player:
            out = self.players_votes.index(most_voted_player)  # индекс
        for pl in self.players_list:
            pl.to_queue(Token('end_voting', voted=out))

    def delete_client(self, client):
        self.players_list.remove(client)

    def __repr__(self):
        return f'Room<tok:{self.token} cnt:{len(self.players_list)} av:{self.available}>'
