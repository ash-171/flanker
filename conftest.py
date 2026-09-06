def pytest_addoption(parser):
    parser.addoption(
        "--no-skip",
        action="store_true",
        default=False,
        help="Also run the network-dependent plugin tests that call "
        "tests.skip_if_asked() (they self-skip unless this flag is given).",
    )
