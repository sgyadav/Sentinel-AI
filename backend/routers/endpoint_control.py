from fastapi import APIRouter
from storage import isolated_devices

router = APIRouter(
    prefix="/endpoint",
    tags=["Endpoint Control"]
)


@router.post("/isolate/{hostname}")
def isolate_device(hostname: str):

    isolated_devices[hostname] = True

    return {
        "message": f"{hostname} isolated successfully"
    }


@router.post("/restore/{hostname}")
def restore_device(hostname: str):

    isolated_devices[hostname] = False

    return {
        "message": f"{hostname} restored successfully"
    }


@router.get("/status/{hostname}")
def endpoint_status(hostname: str):

    return {
        "hostname": hostname,
        "isolated": isolated_devices.get(hostname, False)
    }