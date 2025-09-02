from procyclingstats.stage_scraper import Stage

def test_breakaway_win():
    # Example stage URL path
    stage_url = "race/vuelta-a-espana/2025/stage-7"
    
    stage = Stage(stage_url)
    
    result = stage.breakaway_win()
    
    # Ensure the result is an int and either 0 or 1
    assert isinstance(result, int), "breakaway_win should return an int"
    assert result in (0, 1), "breakaway_win should return 0 or 1"
    
    print(f"Breakaway win: {result}")