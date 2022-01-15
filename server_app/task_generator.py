import random

tasks = [["WiresTask", (5235, 2400)],
         ["WiresTask", (4640, 2814)],
         ["WiresTask", (3596, 2629)],
         ["WiresTask", (4035, 303)],
         ["WiresTask", (2182, 2078)],
         ["WiresTask", (7600, 1982)],
         ["NumbersTask", (928, 1685)],
         ["GarbageTask", (5141, 4270)],
         ["GarbageTask", (5761, 543)],
         ["SendEnergy", (3364, 2558)],
         ["ReceiveEnergy", (1380, 1810)],
         ["ReceiveEnergy", (1883, 679)],
         ["ReceiveEnergy", (1742, 2909)],
         ["ReceiveEnergy", (7043, 874)],
         ["ReceiveEnergy", (6496, 1695)],
         ["ReceiveEnergy", (7870, 1689)],
         ["ReceiveEnergy", (6918, 3070)],
         ["ReceiveEnergy", (6097, 3782)]]


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
        if task.type == t[0] and task.world_pos == t[1]:
            return True

    return False


if __name__ == "__main__":
    task_list = generate_tasks()

    print(task_list)
    # print(should_done_task(task.WiresTask((0, 0), (0, 0), 0, world_pos=(5235, 2400), callback=0), task_list))
