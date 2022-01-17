import random
# import task

tasks = [["WiresTask", (5235, 2400), ('Почините провода', 'Админ')],
         ["WiresTask", (4640, 2814), ('Почините провода', 'Склад')],
         ["WiresTask", (3596, 2629), ('Почините провода', 'Электрощит')],
         ["WiresTask", (4035, 303), ('Почините провода', 'Столовая')],
         ["WiresTask", (2182, 2078), ('Почините провода', 'Охрана')],
         ["WiresTask", (7600, 1982), ('Почините провода', 'Навигация')],
         ["NumbersTask", (928, 1685), ('Запустите реактор', 'Реактор')],
         ["GarbageTask", (5135, 4265), ('Выбросите мусор', 'Склад')],
         ["GarbageTask", (5790, 500), ('Выбросите мусор', 'Cтоловая')],
         ["SendEnergy", (3364, 2558), ('Отправьте энергию', 'Электрощит')],
         ["ReceiveEnergy", (1380, 1810), ('Получите энергию', 'Реактор')],
         ["ReceiveEnergy", (1883, 679), ('Получите энергию', 'Верхний двигатель')],
         ["ReceiveEnergy", (1742, 2909), ('Получите энергию', 'Нижний двигатель')],
         ["ReceiveEnergy", (7043, 874), ('Получите энергию', 'Оружейная')],
         ["ReceiveEnergy", (6496, 1695), ('Получите энергию', 'O2')],
         ["ReceiveEnergy", (7870, 1689), ('Получите энергию', 'Навигация')],
         ["ReceiveEnergy", (6918, 3070), ('Получите энергию', 'Щиты')],
         ["ReceiveEnergy", (6097, 3782), ('Получите энергию', 'Связь')]]


def generate_tasks():
    total_tasks = random.randint(4, 6)
    wires_tasks = []
    for i in range(3):
        gen = tasks[random.randint(0, 5)]
        while gen in wires_tasks:
            gen = tasks[random.randint(0, 5)]
        wires_tasks.append(gen)

    task_list = [
        wires_tasks[0],
        wires_tasks[1],
        wires_tasks[2],
        tasks[6],
        tasks[random.randint(7, 8)],
        tasks[9],
        tasks[random.randint(10, 17)]
    ]

    return task_list


def should_done_task(task, task_list):
    if task.done:
        return False

    for t in task_list:
        if task.__class__.__name__ == t[0] and task.world_pos == t[1]:
            return True

    return False


if __name__ == "__main__":
    task_list = generate_tasks()

    print(task_list)
    # print(should_done_task(task.WiresTask((0, 0), (0, 0), 0, world_pos=(5235, 2400), callback=0), task_list))
