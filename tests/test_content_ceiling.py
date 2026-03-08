from analytics.content_ceiling import evaluate_episode

def test_ceiling_returns_keys():
    text = "그는 숨을 삼켰다. 왜 들켰지? 하지만 더 나쁜 일이 벌어졌다… 죽음이 다가왔다."
    r = evaluate_episode(text, {"genre_bucket":"A","platform":"kakao"})
    assert "ceiling_total" in r
    assert "events" in r and "curve" in r and "rhythm" in r
