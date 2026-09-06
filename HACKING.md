Hacking
=======

### Installing

See the [Quickstart Guide](README.md) for instructions on how to install Flanker.

### Running Tests

Install the test dependencies and run `pytest` from the repository root. Some
(network-based) tests use `unittest.mock`.

```bash
$ pip install -e ".[tests,validator]"
$ pytest -q
```

A handful of plugin tests hit the network and self-skip; pass `--no-skip` to run
them too.

```bash
$ pytest -q --no-skip
```

### Discussion

Please use GitHub issues to discuss bugs, feature requests, and any other issues you may have with Flanker.

### Code Style Guidelines

Try to stick as close as possible to PEP8.

### Sending Pull Requests

Please ensure that any changes you make to Flanker are covered by tests.
