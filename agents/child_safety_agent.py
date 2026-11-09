from datetime import datetime, timezone


class ChildSafetyAgent:

    def __init__(self, knowledge_search):
        self.search = knowledge_search
        self.agent_id = "child_safety_agent"

    def analyze(self, signal):

        signal_id = signal["signal_id"]

        # The child can request help without explaining everything.
        threat_type = signal.get("threat_type")
        urgency = signal.get("urgency", "unknown")

        # Explicit image-based threat triggers urgent review.
        if threat_type == "image_threat":
            priority = "urgent"
            reason = (
                "The child reported a threat to publish an image. "
                "Urgent human safeguarding review is required."
            )

        elif urgency == "high":
            priority = "urgent"
            reason = "The reported situation indicates high urgency."

        elif urgency == "low":
            priority = "standard"
            reason = (
                "The child requested help. Support should remain "
                "available without requiring additional details."
            )

        else:
            priority = "standard"
            reason = (
                "The request for help was received. "
                "The child does not need to disclose the full story "
                "to begin the support process."
            )

        query = (
            "Child online protection reporting mechanisms, "
            "threats to share intimate images, "
            "child safeguarding, privacy, "
            "accessible support and human review"
        )

        evidence = self.search(query, top_k=5)

        return {
            "signal_id": signal_id,
            "agent_id": self.agent_id,
            "priority": priority,
            "decision_reason": reason,
            "requires_human_review": priority == "urgent",
            "help_request_accepted": True,
            "full_story_required": False,
            "original_image_required": False,
            "recommendations": [
                "Acknowledge the child's request for help.",
                "Do not require the child to explain the full incident.",
                "Do not automatically request or collect the original image.",
                "Provide age-appropriate support.",
                "Refer urgent safeguarding concerns to a trained human reviewer."
            ],
            "policy_evidence": evidence,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }