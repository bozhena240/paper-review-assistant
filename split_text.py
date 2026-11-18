import re


def split_into_paragraphs(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]


def split_into_sections(text: str, count: int) -> list[str]:
    """Group nearby paragraphs into approximately balanced sections."""
    paragraphs = split_into_paragraphs(text)
    if not paragraphs:
        return []
    if len(paragraphs) < count:
        words = list(re.finditer(r"\S+", text))
        if len(words) < count:
            raise ValueError("There is not enough text to create that many sections.")
        boundaries = [0] + [
            words[len(words) * i // count].start() for i in range(1, count)
        ] + [len(text)]
        return [text[boundaries[i]:boundaries[i + 1]].strip() for i in range(count)]

    sections = []
    start = 0
    for i in range(count - 1):
        remaining = count - i
        target = sum(len(p) for p in paragraphs[start:]) / remaining
        last_end = len(paragraphs) - (remaining - 1)
        end = min(
            range(start + 1, last_end + 1),
            key=lambda j: abs(sum(len(p) for p in paragraphs[start:j]) - target),
        )
        sections.append("\n\n".join(paragraphs[start:end]))
        start = end
    sections.append("\n\n".join(paragraphs[start:]))
    return sections
