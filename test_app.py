import pytest
from OptimisticOptimizer import process_response, summarize_chunk

def test_process_response():
    response = "hello world"
    processed = process_response(response)
    assert processed.startswith("Take a look at this!\n\n") or \
           processed.startswith("Check this out:\n\n") or \
           processed.startswith("Hmmm, this might just do the trick:\n\n")

def test_summarize_chunk():
    chunk = "This is a long text that needs to be shortened."
    summarized = summarize_chunk(chunk)
    assert isinstance(summarized, str)
