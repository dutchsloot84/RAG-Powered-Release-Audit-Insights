from app.core import llm_client


def test_summarize_missing(monkeypatch):
    monkeypatch.setattr(llm_client, "_chat", lambda prompt: "summary")
    assert llm_client.summarize_missing(["A-1"]) == "summary"
    assert llm_client.summarize_missing([]).startswith("All stories")
