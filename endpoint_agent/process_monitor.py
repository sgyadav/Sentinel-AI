import psutil


def get_running_processes():

    processes = []

    for process in psutil.process_iter(
        ['pid', 'name', 'username', 'cpu_percent', 'memory_percent']
    ):

        try:

            processes.append({

                "pid": process.info["pid"],

                "name": process.info["name"],

                "username": process.info["username"],

                "cpu": process.info["cpu_percent"],

                "memory": round(
                    process.info["memory_percent"], 2
                )

            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    return processes