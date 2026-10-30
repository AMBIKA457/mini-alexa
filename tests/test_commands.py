from assistant import commands, config


def test_calc():
    assert "20" in commands.handle("calculate 12 plus 8")
    assert "6" in commands.handle("2 into 3 calculate")


def test_calc_rejects_unsafe():
    assert "samajh nahi" in commands.calc("calculate __import__('os')")


def test_time_and_date():
    assert "samay" in commands.handle("time kya hai")
    assert "tareekh" in commands.handle("aaj ki date batao")


def test_open_whitelist(monkeypatch):
    opened = []
    monkeypatch.setattr(commands.webbrowser, "open", opened.append)
    assert "allowed list" in commands.handle("open evil-site")
    assert not opened
    commands.handle("open youtube")
    assert opened == ["https://www.youtube.com"]


def test_notes(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "t.db")
    assert "save" in commands.handle("note buy milk")
    assert "buy milk" in commands.handle("show my notes")
    commands.handle("clear notes")
    assert "koi note nahi" in commands.handle("show my notes")


def test_reminder_validation():
    assert "Kitne time" in commands.handle("remind me to drink water")
    assert "24 ghante" in commands.handle("remind me in 99 hour to sleep")


def test_unknown_returns_none():
    assert commands.handle("asdf qwerty") is None


def test_calc_rejects_mixed_unsupported_input():
    assert "Sirf numbers" in commands.calc("calculate 2 + 3 __import__('os')")


def test_open_site_requires_exact_name(monkeypatch):
    opened = []
    monkeypatch.setattr(commands.webbrowser, "open", opened.append)
    assert "allowed list" in commands.handle("open notyoutube")
    assert opened == []
