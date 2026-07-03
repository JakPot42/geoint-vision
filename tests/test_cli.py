from click.testing import CliRunner

from main import cli


def _run(*args):
    runner = CliRunner()
    return runner.invoke(cli, list(args))


def test_demo_command_runs_clean():
    result = _run("demo")
    assert result.exit_code == 0
    assert "Change Analysis" in result.output
    assert "Saved PDF brief" in result.output


def test_search_command_runs_clean():
    result = _run("search", "--lat", "11.59265", "--lon", "43.06049", "--start", "2018-01-01", "--end", "2018-06-30")
    assert result.exit_code == 0
    assert "S2" in result.output


def test_analyze_command_runs_clean():
    result = _run(
        "analyze", "--lat", "11.59265", "--lon", "43.06049",
        "--before-start", "2018-01-01", "--before-end", "2018-06-30",
        "--after-start", "2019-09-01", "--after-end", "2019-12-31",
        "--name", "CLI test",
    )
    assert result.exit_code == 0
    assert "Change Analysis" in result.output


def test_analyze_command_no_scenes_exits_nonzero():
    result = _run(
        "analyze", "--lat", "11.59265", "--lon", "43.06049",
        "--before-start", "2000-01-01", "--before-end", "2000-01-02",
        "--after-start", "2019-09-01", "--after-end", "2019-12-31",
    )
    assert result.exit_code != 0
