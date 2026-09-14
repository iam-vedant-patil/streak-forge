from backend.app.services.category import classify_task


def test_classify_programming_task():
    assert classify_task("Complete Python FastAPI project") == "Programming"


def test_classify_fitness_task():
    assert classify_task("Go for a 5km run") == "Fitness"


def test_classify_learning_task():
    assert classify_task("Read a book") == "Learning"


def test_classify_work_task():
    assert classify_task("Prepare the project report") == "Work"


def test_classify_unknown_task():
    assert classify_task("Buy groceries") == "Other"


def test_classify_using_description():
    assert (
        classify_task(
            "Complete today's task",
            "Practice Python programming",
        )
        == "Programming"
    )

def test_classify_case_insensitive():
    assert classify_task("LEARN PYTHON") == "Programming"


def test_classify_with_punctuation():
    assert classify_task("Build Python, FastAPI!") == "Programming"
