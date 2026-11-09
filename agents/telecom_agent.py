
from datetime import datetime, timezone


class TelecomSafetyAgent:

    def __init__(self, knowledge_search):
        self.search = knowledge_search
        self.agent_id = "telecom_safety_agent"

    def analyze(self, incident):

        indicators = incident.get("network_indicators", {})

        detected = []

        if indicators.get("repeated_contact"):
            detected.append("Repeated unwanted contact")

        if indicators.get("possible_spoofing"):
            detected.append("Possible identity spoofing")

        if indicators.get("unusual_frequency"):
            detected.append("Unusual communication frequency")

        if len(detected) >= 2:
            risk_level = "high"
        elif len(detected) == 1:
            risk_level = "medium"
        else:
            risk_level = "undetermined"

        query = (
            "Telecommunications industry responsibilities "
            "for child online protection, reporting, "
            "safety measures and incident response"
        )

        evidence = self.search(query, top_k=5)

        recommendations = [
            "Refer the report to a trained safeguarding reviewer.",
            "Preserve only necessary and authorized incident metadata.",
            "Avoid inspecting private communications without authorization.",
            "Provide an accessible reporting and support channel."
        ]

        return {
            "incident_id": incident["incident_id"],
            "agent_id": self.agent_id,
            "risk_level": risk_level,
            "detected_indicators": detected,
            "recommendations": recommendations,
            "policy_evidence": evidence,
            "requires_human_review": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
