from datetime import datetime, timezone
import uuid


class NetworkSimulator:
    """
    Simulates unreliable network delivery.

    This is a local prototype, not a real telecom connection.
    """

    def __init__(self):
        self.requests = {}

    def create_request(self, event):
        request_id = str(uuid.uuid4())[:8].upper()

        self.requests[request_id] = {
            "request_id": request_id,
            "event": event,
            "status": "PENDING",
            "attempts": 0,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "delivered_at": None,
            "acknowledged_at": None,
            "result": None
        }

        return self.requests[request_id].copy()

    def attempt_delivery(self, request_id, coordinator, network_available):
        request = self.requests.get(request_id)

        if request is None:
            raise ValueError("Unknown request ID")

        if request["status"] == "ACKNOWLEDGED":
            return request.copy()

        request["attempts"] += 1

        if not network_available:
            request["status"] = "PENDING"
            return request.copy()

        if request["status"] == "PENDING":
            result = coordinator.process_event(request["event"])

            request["result"] = result
            request["status"] = "DELIVERED"
            request["delivered_at"] = datetime.now(
                timezone.utc
            ).isoformat()

        return request.copy()

    def acknowledge(self, request_id):
        request = self.requests.get(request_id)

        if request is None:
            raise ValueError("Unknown request ID")

        if request["status"] != "DELIVERED":
            raise ValueError(
                "Cannot acknowledge a request before delivery"
            )

        request["status"] = "ACKNOWLEDGED"
        request["acknowledged_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        return request.copy()
        