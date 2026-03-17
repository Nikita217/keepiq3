from app.services.date_parsing import DateParsingService


def test_date_parsing_defaults_time_for_date_without_time():
    result = DateParsingService().parse("12 апреля позвонить маме", "Europe/Moscow")

    assert result.due_date is not None
    assert result.due_time == "10:00"


def test_date_parsing_understands_relative_time():
    result = DateParsingService().parse("напомни завтра в 19:00", "Europe/Moscow")

    assert result.due_at is not None
    assert result.due_time == "19:00"
