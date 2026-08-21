import json
import subprocess
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_FILE = PROJECT_ROOT / "tests" / "evaluation_cases.json"
OUTPUT_FILE = PROJECT_ROOT / "tests" / "evaluation_results.json"

FUNCTION_NAME = "customer-support-agent-dev-ai"
REGION = "us-east-1"


def invoke_lambda(question):

    payload = json.dumps({
        "message": question
    })

    command = [
        "aws",
        "lambda",
        "invoke",
        "--function-name",
        FUNCTION_NAME,
        "--region",
        REGION,
        "--payload",
        payload,
        "--cli-binary-format",
        "raw-in-base64-out",
        "/tmp/evaluation-response.json"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    with open("/tmp/evaluation-response.json", "r") as file:
        outer_response = json.load(file)

    body = outer_response.get("body")

    if isinstance(body, str):
        body = json.loads(body)

    return body


def evaluate_case(case, result):

    category = case["category"]
    expected = case["expected"]

    answer = result.get("response", "")
    tool_used = result.get("tool_used")

    answer_lower = answer.lower()

    # ---------------------------------------------------------
    # Basic heuristic evaluation
    # ---------------------------------------------------------

    passed = True
    reason = "Passed basic evaluation"

    # Tool tests
    if category == "tool":
        if tool_used != "get_shipment":
            passed = False
            reason = "Expected get_shipment tool"

    elif category == "tool_rag":
        if tool_used != "get_shipment":
            passed = False
            reason = "Expected get_shipment tool"

        elif not result.get("sources"):
            passed = False
            reason = "Expected policy sources in addition to tool"

    # Out-of-scope test
    elif category == "out_of_scope":

       refusal_signals = [
    "don't have enough information",
    "do not have enough information",
    "not addressed",
    "not address",
    "not covered",
    "not supported by our company policies",
    "not supported by company policies",
    "not supported by our policies",
    "not supported by policy",
    "not covered by our policies",
    "not covered by company policy",
    "cannot offer",
    "cannot provide",
    "not available in our policies"
    ]

       if not any(
            signal in answer_lower
            for signal in refusal_signals
        ):
            passed = False
            reason = "Expected grounded refusal"

    # Policy tests
    else:

        expected_keywords = []

        for word in expected.lower().split():

            word = word.strip(
                ".,:;!?()[]{}\"'"
            )

            if len(word) >= 5:
                expected_keywords.append(word)

        matches = sum(
            1
            for keyword in expected_keywords
            if keyword in answer_lower
        )

        # Require at least two meaningful expected terms.
        if matches < min(2, len(expected_keywords)):

            passed = False

            reason = (
                f"Expected policy concepts not sufficiently "
                f"present. Matched {matches} keywords."
            )

    return {
        "passed": passed,
        "reason": reason,
        "expected": expected,
        "answer": answer,
        "sources": result.get("sources", []),
        "tool_used": tool_used
    }


def main():

    with open(TEST_FILE, "r") as file:
        cases = json.load(file)

    results = []

    print()
    print("=" * 70)
    print("CUSTOMER SUPPORT AI EVALUATION")
    print("=" * 70)
    print()

    for index, case in enumerate(cases, start=1):

        print(
            f"[{index:02d}/{len(cases)}] "
            f"{case['id']} - "
            f"{case['category']}"
        )

        try:

            result = invoke_lambda(
                case["question"]
            )

            evaluation = evaluate_case(
                case,
                result
            )

            passed = evaluation["passed"]

            print(
                "   PASS" if passed else "   FAIL"
            )

            results.append({
                "id": case["id"],
                "category": case["category"],
                "question": case["question"],
                **evaluation
            })

        except Exception as exc:

            print("   ERROR")

            results.append({
                "id": case["id"],
                "category": case["category"],
                "question": case["question"],
                "passed": False,
                "reason": str(exc),
                "answer": "",
                "sources": [],
                "tool_used": None
            })

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    total = len(results)

    passed = sum(
        1
        for result in results
        if result["passed"]
    )

    failed = total - passed

    pass_rate = (
        (passed / total) * 100
        if total
        else 0
    )

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(pass_rate, 2),
        "results": results
    }

    with open(OUTPUT_FILE, "w") as file:

        json.dump(
            report,
            file,
            indent=2
        )

    print()
    print("=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total Tests : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print(f"Pass Rate   : {pass_rate:.1f}%")
    print("=" * 70)
    print()
    print(f"Report: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()