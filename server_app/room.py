import random
from config import Config
import threading
from protocol import Token
from task_generator import generate_tasks
from db_funcs import add_rating

CREWMATE_WIN = 0
IMPOSTER_WIN = 1

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
        self.win_condition = (len(self.players_list) - 1) * Config.task_per_player
        self.players_votes = [0] * len(self.players_list)
        self.players_list[random.randrange(len(self.players_list))].imposter = True

    def send2all(self, token):
        for pl in self.players_list:
            pl.to_queue(token)

    def check_win(self):
        if self.tasks_progress >= self.win_condition:
            self.send2all(Token("end_game", team=CREWMATE_WIN))
            [add_rating(cl.name) for cl in self.players_list if cl.alive and not cl.imposter]
        elif len([1 for pl in self.players_list if not pl.imposter and pl.alive]) < 2:
            self.send2all(Token("end_game", team=IMPOSTER_WIN))
            [add_rating(cl.name) for cl in self.players_list if cl.imposter]
        elif len([1 for pl in self.players_list if pl.imposter and pl.alive]) < 1:
            self.send2all(Token("end_game", team=CREWMATE_WIN))
            [add_rating(cl.name) for cl in self.players_list if cl.alive and not cl.imposter]

    def start_voting(self):
        threading.Timer(60, self.end_voting).start()

    def end_voting(self):
        # most_voted_player: int = max(self.players_votes)  # количество
        out = None
        lst = sorted(self.players_votes)
        most_voted_player = lst[-1]
        if lst[-1] != lst[-2] and self.skip_votes < most_voted_player:
            out = self.players_votes.index(most_voted_player)  # индекс

        self.send2all(Token("end_voting", voted=out))
        if out is not None:
            self.players_list[out].alive = False
        # reset
        self.players_votes = [0] * len(self.players_list)
        self.skip_votes = 0

        self.check_win()

    def delete_client(self, client):
        self.players_list.remove(client)

    def __repr__(self):
        return f'Room<tok:{self.token} cnt:{len(self.players_list)} av:{self.available}>'

    def generate_tasks(self):
        self.players_tasks = [generate_tasks() for _ in range(len(self.players_list))]
        # for i in range(len(self.players_list)):
           #  self.players_list[i].to_queue(Token('generated_tasks', tasks=self.players_tasks[i]))
        return self.players_tasks

