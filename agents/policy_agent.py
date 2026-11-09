from datetime import datetime, timezone


class PolicyAgent:

    def compare_jurisdictions(self, query, top_k=5):
        """
        Compare UAE federal, Dubai, and global evidence.
        """
        kb = getattr(self.search, "__self__", None)

        if kb is None or not hasattr(
            kb, "search_by_jurisdiction"
        ):
            raise RuntimeError(
                "Jurisdiction-aware KB is required."
            )

        federal = kb.search_by_jurisdiction(
            query,
            jurisdiction="UAE_FEDERAL",
            top_k=top_k
        )

        dubai = kb.search_by_jurisdiction(
            query,
            jurisdiction="DUBAI",
            top_k=top_k
        )

        global_sources = kb.search_by_jurisdiction(
            query,
            jurisdiction="GLOBAL",
            top_k=top_k
        )

        return {
            "query": query,
            "uae_evidence": federal + dubai,
            "uae_federal_evidence": federal,
            "dubai_evidence": dubai,
            "global_evidence": global_sources,
            "comparison_status": "EVIDENCE_COMPARISON",
            "legal_gap_confirmed": False,
            "requires_human_verification": True
        }
        """
        Compare UAE and international policy evidence.
        Human verification is required.
        """

        kb = getattr(self.search, "__self__", None)

        if kb is None or not hasattr(
            kb, "search_by_jurisdiction"
        ):
            raise RuntimeError(
                "Jurisdiction-aware knowledge base is required."
            )

        uae = kb.search_by_jurisdiction(
            query,
            jurisdiction="UAE",
            top_k=top_k
        )

        global_sources = kb.search_by_jurisdiction(
            query,
            jurisdiction="GLOBAL",
            top_k=top_k
        )

        return {
            "query": query,
            "uae_evidence": uae,
            "global_evidence": global_sources,
            "comparison_status": "EVIDENCE_COMPARISON",
            "legal_gap_confirmed": False,
            "requires_human_verification": True
        }

    def __init__(self, knowledge_search):
        self.search = knowledge_search
        self.agent_id = "policy_agent"

    def analyze(self, event):

        event_type = event.get("event_type", "unknown")

        if event_type == "help_request":
            query = (
                "child online protection accessible reporting "
                "mechanisms children requesting help privacy"
            )

            policy_focus = "ACCESSIBLE_REPORTING"

        elif event_type == "new_information":
            query = (
                "child online sexual exploitation threats "
                "to publish images safeguarding urgent reporting"
            )

            policy_focus = "URGENT_SAFEGUARDING"

        elif event_type == "data_request":
            query = (
                "children privacy data minimization sensitive "
                "images protection personal information"
            )

            policy_focus = "DATA_MINIMIZATION"

        else:
            query = "children online safety protection rights"
            policy_focus = "GENERAL_CHILD_PROTECTION"

        evidence = self.search(query, top_k=3)

        return {
            "agent_id": self.agent_id,
            "event_type": event_type,
            "policy_focus": policy_focus,
            "decision": "EVIDENCE_RETRIEVED",
            "reason": (
                "Relevant document passages were retrieved "
                "for human review. Their relevance and legal "
                "applicability have not been independently verified."
            ),
            "evidence": evidence,
            "evidence_status": "RETRIEVED_NOT_VERIFIED",
            "requires_human_verification": True,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        }


    def compare_policies(self, query, top_k=10):
        evidence = self.search(query, top_k=top_k)

        groups = {
            "uae_evidence": [],
            "global_evidence": [],
            "unclassified_evidence": []
        }

        for item in evidence:
            jurisdiction = str(
                item.get("jurisdiction") or ""
            ).upper()

            if jurisdiction in {"UAE", "UAE_FEDERAL", "DUBAI"}:
                groups["uae_evidence"].append(item)

            elif jurisdiction in {"GLOBAL", "INTERNATIONAL"}:
                groups["global_evidence"].append(item)

            else:
                groups["unclassified_evidence"].append(item)

        return {
            "query": query,
            **groups,
            "comparison_status": "RETRIEVED_NOT_LEGALLY_VERIFIED",
            "requires_human_verification": True
        }

    def detect_policy_gaps(self, event):
        event_type = event.get("event_type", "unknown")

        queries = {
            "help_request": "child accessible reporting safeguarding",
            "new_information": "child online threats urgent protection",
            "data_request": "child privacy data minimization disclosure",
            "cross_border": "cross border child protection data sharing"
        }

        query = queries.get(
            event_type,
            "child online safety policy governance"
        )

        comparison = self.compare_policies_v2(query, top_k=10)

        flags = []

        if not comparison["uae_evidence"]:
            flags.append({
                "type": "UAE_EVIDENCE_NOT_RETRIEVED",
                "description": "No UAE policy evidence retrieved.",
                "recommendation": "Verify UAE policy coverage and indexing."
            })

        if not comparison["global_evidence"]:
            flags.append({
                "type": "GLOBAL_EVIDENCE_NOT_RETRIEVED",
                "description": "No global policy evidence retrieved.",
                "recommendation": "Review global source coverage."
            })

        if comparison["unclassified_evidence"]:
            flags.append({
                "type": "UNCLASSIFIED_EVIDENCE",
                "description": "Some evidence lacks verified jurisdiction metadata.",
                "recommendation": "Review source classification."
            })

        if event_type == "cross_border":
            flags.append({
                "type": "CROSS_BORDER_REVIEW_REQUIRED",
                "description": "Jurisdiction and data-sharing authority need review.",
                "recommendation": "Verify applicable rules and procedures."
            })

        return {
            "agent_id": self.agent_id,
            "event_type": event_type,
            "comparison": comparison,
            "review_flags": flags,
            "gap_status": "POTENTIAL_GAPS_REQUIRE_VERIFICATION",
            "requires_human_verification": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def compare_policies_v2(self, query, top_k=10):
        results = self.search(
            query,
            top_k=max(top_k * 5, 50)
        )

        groups = {
            "uae_evidence": [],
            "global_evidence": [],
            "unclassified_evidence": []
        }

        for item in results:
            jurisdiction = str(
                item.get("jurisdiction") or "UNCLASSIFIED"
            ).upper()

            if jurisdiction in {"UAE", "UAE_FEDERAL", "DUBAI"}:
                groups["uae_evidence"].append(item)

            elif jurisdiction in {"GLOBAL", "INTERNATIONAL"}:
                groups["global_evidence"].append(item)

            else:
                groups["unclassified_evidence"].append(item)

        return {
            "query": query,
            **{
                key: values[:top_k]
                for key, values in groups.items()
            },
            "comparison_status": "EVIDENCE_GROUPED_NOT_VERIFIED",
            "requires_human_verification": True
        }
