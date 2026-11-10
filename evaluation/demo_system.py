import json
from datetime import datetime, timezone
from pathlib import Path

from knowledge_base.kb_engine import ChildNetKnowledgeBase
from agents.child_safety_agent import ChildSafetyAgent
from agents.telecom_agent import TelecomSafetyAgent
from agents.privacy_agent import PrivacyAgent
from agents.policy_agent import PolicyAgent

# ==========================================
# CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

AUDIT_FILE = (
    PROJECT_ROOT
    / "knowledge_base"
    / "processed"
    / "demo_audit_log.json"
)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


# ==========================================
# COORDINATOR
# ==========================================

class ChildNetCoordinator:

    def __init__(self):

        print("Loading CHILDNET 360 Knowledge Base...")

        self.kb = ChildNetKnowledgeBase()

        self.child_agent = ChildSafetyAgent(
            self.kb.search
        )

        self.telecom_agent = TelecomSafetyAgent(
            self.kb.search
        )

        self.privacy_agent = PrivacyAgent(
            self.kb.search
        )

        self.policy_agent = PolicyAgent(
            self.kb.search
        )

        self.case_id = "CASE-001"

        self.history = []

        print("All agents initialized successfully.")

    def process_event(self, event):

        event_type = event["event_type"]

        # ----------------------------------
        # EVENT 1: HELP REQUEST
        # ----------------------------------

        if event_type == "help_request":

            child_result = self.child_agent.analyze({
                "signal_id": self.case_id,
                "urgency": "unknown"
            })

            # Simulated network delivery:
            # This event is processed only after
            # the request reaches the server.
            telecom_result = self.telecom_agent.analyze({
                "incident_id": self.case_id,
                "network_indicators": {}
            })

            privacy_result = self.privacy_agent.analyze(
                event
            )

            policy_result = self.policy_agent.analyze(
                event
            )

            decision = {
                "status": "RECEIVED",
                "priority": "standard",
                "human_review": False,
                "reason": (
                    "The child's help request was received. "
                    "A complete story is not required."
                )
            }

        # ----------------------------------
        # EVENT 2: IMAGE THREAT
        # ----------------------------------

        elif event_type == "new_information":

            child_result = self.child_agent.analyze({
                "signal_id": self.case_id,
                "threat_type": "image_threat"
            })

            telecom_result = None

            privacy_result = self.privacy_agent.analyze(
                event
            )

            policy_result = self.policy_agent.analyze(
                event
            )

            decision = {
                "status": "ESCALATED",
                "priority": child_result["priority"],
                "human_review": True,
                "reason": child_result["decision_reason"]
            }

        # ----------------------------------
        # EVENT 3: REQUEST ORIGINAL IMAGE
        # ----------------------------------

        elif event_type == "data_request":

            child_result = None
            telecom_result = None

            privacy_result = self.privacy_agent.analyze(
                event
            )

            policy_result = self.policy_agent.analyze(
                event
            )

            decision = {
                "status": "DATA_REQUEST_UNDER_REVIEW",
                "priority": "urgent",
                "human_review": True,
                "initial_referral_continues": True,
                "original_image_collected": False,
                "reason": (
                    "The original image will not be "
                    "collected automatically. The request "
                    "requires authorized human review."
                )
            }

        elif event_type == "unauthorized_access":

            child_result = None
            telecom_result = None

            privacy_result = self.privacy_agent.analyze(event)
            policy_result = self.policy_agent.analyze(event)

            decision = {
                "status": "ACCESS_DENIED_PENDING_REVIEW",
                "priority": "urgent",
                "human_review": True,
                "access_granted": False,
                "reason": (
                    "Unauthorized access attempt detected. "
                    "No case information is released by "
                    "this simulated workflow. "
                    "Human review is required."
                )
            }

        else:
            raise ValueError(
                f"Unknown event type: {event_type}"
            )

        record = {
            "case_id": self.case_id,
            "event_type": event_type,
            "event_time": timestamp(),
            "decision": decision,
            "agents": {
                "child_safety": child_result,
                "telecom": telecom_result,
                "privacy": privacy_result,
                "policy": policy_result
            }
        }

        self.history.append(record)

        return record

    def save_audit_log(self):

        AUDIT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            AUDIT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.history,
                file,
                ensure_ascii=False,
                indent=2
            )

        print("\nAudit log saved successfully.")


# ==========================================
# DEMO TIMELINE
# ==========================================

def run_demo():

    system = ChildNetCoordinator()

    events = [
        {
            "event_type": "help_request",
            "description": (
                "A 13-year-old child requests help "
                "without providing details."
            ),
            "network": "weak",
            "delivered": True
        },
        {
            "event_type": "new_information",
            "description": (
                "The child reports a threat "
                "to publish an image."
            ),
            "threat_type": "image_threat"
        },
        {
            "event_type": "data_request",
            "description": (
                "An external party requests "
                "the original image."
            ),
            "request_original_image": True
        }
    ]

    for number, event in enumerate(events, 1):

        print("\n" + "=" * 55)
        print(f"EVENT {number}: {event['event_type']}")
        print("=" * 55)

        result = system.process_event(event)

        decision = result["decision"]

        print("Status:", decision["status"])
        print("Priority:", decision["priority"])
        print(
            "Human review:",
            decision["human_review"]
        )
        print("Reason:", decision["reason"])

        policy = result["agents"]["policy"]

        if policy["evidence"]:

            source = policy["evidence"][0]

            print("\nRetrieved evidence:")
            print("Document:", source["document"])
            print("Page:", source["page"])
            print("Score:", source["score"])

    system.save_audit_log()

    print("\nCHILDNET 360 DEMO COMPLETED")


if __name__ == "__main__":
    run_demo()



def run_progressive_scenario(coordinator):
    """Run progressive risk scenarios using existing agents."""

    events = [
        {
            "event_type": "help_request",
            "description": "A child requests help."
        },
        {
            "event_type": "new_information",
            "threat_type": "image_threat",
            "description": "A threat to publish a private image."
        },
        {
            "event_type": "data_request",
            "requested_data": "original_image",
            "requester_role": "external_party",
            "description": "An external party requests the image."
        },
        {
            "event_type": "unauthorized_access",
            "requested_resource": "child_case_record",
            "requester_role": "unauthorized",
            "description": "Unauthorized access to case information."
        }
    ]

    stages = []

    for number, event in enumerate(events, start=1):

        result = coordinator.process_event(event)

        stages.append({
            "stage": number,
            "scenario": event["description"],
            "event_type": event["event_type"],
            "decision": result["decision"],
            "agents": result["agents"],
            "event_time": result["event_time"]
        })

    return {
        "case_id": coordinator.case_id,
        "stages": stages,
        "total_stages": len(stages),
        "human_review_required": any(
            stage["decision"].get("human_review", False)
            for stage in stages
        )
    }
