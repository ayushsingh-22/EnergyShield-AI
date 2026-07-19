from orchestration.job_status import JobStatus, JobStatusTracker


def test_start_and_finish_success():
    tracker = JobStatusTracker()
    run = tracker.start("job_a")
    assert run.status == JobStatus.RUNNING

    tracker.finish(run, details={"count": 3})

    assert run.status == JobStatus.SUCCESS
    assert run.finished_at is not None
    assert run.details["count"] == 3
    assert tracker.latest("job_a") is run


def test_finish_with_error_marks_failed():
    tracker = JobStatusTracker()
    run = tracker.start("job_b")
    tracker.finish(run, error="boom")
    assert run.status == JobStatus.FAILED
    assert run.error == "boom"


def test_history_caps_at_max_entries():
    tracker = JobStatusTracker(max_history_per_job=2)
    for _ in range(5):
        tracker.start("job_c")
    assert len(tracker.history("job_c")) == 2


def test_all_latest_returns_one_per_job():
    tracker = JobStatusTracker()
    tracker.start("job_a")
    tracker.start("job_b")
    latest = tracker.all_latest()
    assert {run.job_name for run in latest} == {"job_a", "job_b"}
