"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _paragraphs_with_title_merged(text: str) -> list[str]:
    """
    Split on blank lines, then reattach a bare title line to the paragraph
    that follows it instead of leaving it to stand alone.

    Every post in this corpus opens with a one-line title ("On the add/drop
    deadline", "Re: Halden Hall") followed by 1-3 body paragraphs. A title by
    itself isn't a chunk anyone could retrieve anything useful from, so it
    always travels with the first body paragraph. Everything after that is
    its own paragraph.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paragraphs) <= 1:
        return paragraphs

    title, first_body, *rest = paragraphs
    return [f"{title}\n\n{first_body}", *rest]


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks, one per paragraph (title merged into the
    first body paragraph) instead of one whole post per chunk.

    Keeping a whole post as one chunk whenever it was under 600 characters
    (the original Milestone 3 strategy) only checked length, not how many
    separate things a post talked about. Posts with 2-3 body paragraphs each
    making their own point, like `admin_add_drop_deadline.txt` (add deadline,
    drop deadline) or `health_center.txt` (walk-in hours, counselling
    intake), stayed bundled into a single chunk no matter how many distinct
    facts they held. Splitting on the blank lines the corpus already uses to
    separate one thought from the next fixes that directly, without
    resurrecting the title-stranding problem paragraph-splitting caused when
    it was first considered in Milestone 3.
    """
    chunk_size = config.CHUNK_SIZE
    overlap = config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        text = doc.text.strip()
        index = 0
        for paragraph in _paragraphs_with_title_merged(text):
            # Normal case for this corpus: a paragraph (title + first body
            # paragraph counts as one) already fits under chunk_size, so it
            # becomes one chunk and `continue` skips the oversized-paragraph
            # handling below entirely.
            if len(paragraph) <= chunk_size:
                chunks.append(
                    Chunk(
                        text=paragraph,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1
                continue

            # Rare case: a single paragraph longer than chunk_size (whole
            # posts here run 178-563 characters, so an individual paragraph
            # is expected to never actually hit this). Only reached when the
            # `if` above is false, i.e. this loop iteration's paragraph did
            # NOT `continue` past it. Falls back to fixed windows with
            # overlap rather than leaving the paragraph oversized.
            start = 0
            while start < len(paragraph):
                piece = paragraph[start : start + chunk_size].strip()
                if piece:
                    chunks.append(
                        Chunk(
                            text=piece,
                            source=doc.source,
                            index=index,
                            produced_by="chunker.py::split_documents",
                        )
                    )
                    index += 1
                start += chunk_size - overlap

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
