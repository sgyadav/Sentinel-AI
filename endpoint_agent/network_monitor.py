import psutil


def get_network_connections():

    connections = []

    try:

        for conn in psutil.net_connections(kind="inet"):

            local = ""

            remote = ""

            if conn.laddr:
                local = f"{conn.laddr.ip}:{conn.laddr.port}"

            if conn.raddr:
                remote = f"{conn.raddr.ip}:{conn.raddr.port}"

            connections.append({

                "local": local,
                "remote": remote,
                "status": conn.status,
                "pid": conn.pid

            })

    except Exception as e:

        print(e)

    return connections