def format_review_report(filename: str, reviews: list[dict]) -> str:
    """Format the generated reviews and their original prompts as plain text."""
    lines = ["Paper Review Assistant", f"Paper: {filename}", ""]
    for review in reviews:
        lines.append(review["label"])
        lines.append("=" * len(review["label"]))
        if review["changed"]:
            lines.append("Note: The text or prompt was changed after this review was generated.")
            lines.append("")
        lines.extend(["Prompt used:", review["prompt"], "", "Review:", review["text"], ""])
    return "\n".join(lines)
