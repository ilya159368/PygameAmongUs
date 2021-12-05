import player
import engine


player_list = [player.Player()]


def sv_move(byt: bytes): # как только получаем обновление, вызываем эту функцию, а вот как передать без потерь аргументы, Илья, Гриша, разбирайтесьь, я в сокетах не шарю
    cmd = engine.UserCmd().from_bytes(byt)
    player = player_list[cmd.owner_id]

