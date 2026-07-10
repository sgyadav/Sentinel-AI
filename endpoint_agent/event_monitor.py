try:
    import win32evtlog
except ImportError:
    win32evtlog = None


def get_security_events(limit=20):

    events = []

    if win32evtlog is None:
        return events

    try:

        server = "localhost"

        logtype = "Security"

        hand = win32evtlog.OpenEventLog(server, logtype)

        flags = (
            win32evtlog.EVENTLOG_BACKWARDS_READ
            | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        )

        total = 0

        while total < limit:

            records = win32evtlog.ReadEventLog(
                hand,
                flags,
                0
            )

            if not records:
                break

            for event in records:

                events.append({

                    "event_id": event.EventID & 0xFFFF,

                    "source": event.SourceName,

                    "time": str(event.TimeGenerated)

                })

                total += 1

                if total >= limit:
                    break

    except Exception as e:

        print("Event Log Error:", e)

    return events
