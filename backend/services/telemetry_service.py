import json

from db.telemetry_models import TelemetryDB


def save_telemetry(db, data):

    telemetry = TelemetryDB(

        hostname=data.hostname,

        username=data.username,

        ip_address=data.ip_address,

        operating_system=data.operating_system,

        cpu_usage=data.cpu_usage,

        ram_usage=data.ram_usage,

        disk_usage=data.disk_usage,

        status=data.status,

        raw_json=json.dumps(data.model_dump())

    )

    db.add(telemetry)

    db.commit()

    db.refresh(telemetry)

    return telemetry