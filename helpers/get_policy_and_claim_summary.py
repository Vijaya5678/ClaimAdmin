from pymongo import MongoClient
from dotenv import load_dotenv
import os

def get_policy_and_claim_summary(policy_id):
    client = MongoClient(os.getenv("MONGO_URL"))
    db = client.claim_db
    policies_col = db.policies
    policy_types_col = db.policy_types
    claims_col = db.claims

    # Fetch the policy
    policy = policies_col.find_one({"policy_id": policy_id})
    if not policy:
        return {"error": f"Policy ID {policy_id} not found"}

    # Get policy type
    policy_type = policy_types_col.find_one({"policy_type": policy["policy_type"]})
    if not policy_type:
        return {"error": f"Policy type {policy['policy_type']} not found"}

    # Extract policy-level details
    total_insured_amount = policy_type.get("max_claims_per_year", 0)
    eligible_diseases = [
        cond["condition"] for cond in policy_type.get("covered_conditions", [])
        if cond.get("covered", False)
    ]

    # Gather all claims for this policy
    claims = list(claims_col.find({"policy_id": policy_id}))

    used_amount = 0
    claims_summary_list = []
    eligible_cases = []

    for claim in claims:
        if claim["claim_status"] == "approved":
            used_amount += claim["amount_paid"]

        claims_summary_list.append({
            "claim_id": claim["claim_id"],
            "diagnosis": claim["diagnosis"],
            "amount_billed": claim["amount_billed"],
            "amount_paid": claim["amount_paid"],
            "claim_status": claim["claim_status"]
        })

        if claim["diagnosis"] in eligible_diseases:
            eligible_cases.append(claim["claim_id"])

    remaining_amount = total_insured_amount - used_amount

    # Summary structures
    policy_summary = {
        "policy_id": policy["policy_id"],
        "policy_holder": policy.get("patient", {}).get("name", "N/A"),
        "total_insured_amount": total_insured_amount,
        "used_amount": used_amount,
        "remaining_amount": remaining_amount,
        "eligible_diseases": eligible_diseases
    }

    claims_summary = {
        "number_of_claims": len(claims),
        "claims": claims_summary_list,
        "eligible_cases": eligible_cases
    }

    return policy_summary, claims_summary
