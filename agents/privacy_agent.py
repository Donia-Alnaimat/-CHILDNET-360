from datetime import datetime, timezone


class PrivacyAgent:

    def __init__(self, knowledge_search):
        self.search = knowledge_search
        self.agent_id = "privacy_agent"

    def analyze(self, event):

        image_requested = event.get(
            "request_original_image", False
        )

        # Minimum data needed for initial referral
        required_data = [
            "case_id",
            "event_type"
        ]

        if image_requested:

            decision = "HUMAN_REVIEW_REQUIRED"

            reason = (
                "The original image is sensitive material. "
                "The initial safeguarding referral can continue "
                "without automatically collecting it. "
                "The additional data request requires "
                "authorized human review."
            )

            query = (
                "Children digital privacy data minimization "
                "sensitive images personal data protection "
                "child online safeguarding"
            )

        else:

            decision = "MINIMUM_DATA"

            reason = (
                "The initial help request can be processed "
                "using minimal information without requiring "
                "the child's full story."
            )

            query = (
                "Children online safety privacy by design "
                "data minimization reporting mechanisms"
            )

        evidence = self.search(
            query,
            top_k=3
        )

        return {
            "agent_id": self.agent_id,
            "decision": decision,
            "reason": reason,
            "required_data": required_data,
            "collect_original_image": False,
            "initial_referral_continues": True,
            "requires_human_review": image_requested,
            "policy_evidence": evidence,
            "evidence_status": "RETRIEVED_NOT_VERIFIED",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        }