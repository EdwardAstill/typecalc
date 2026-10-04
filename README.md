# typecalc

Equation parsing and solving, with a command-line runner for text files.
Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

| Distribution | Purpose | Dependencies |
| --- | --- | --- |
| `typecalc` | Python library in `package/typecalc` | SymPy |
| `typecalc-cli` | CLI in `cli`; provides the `typecalc` command | typecalc |

The workspace contains the library and CLI. The experimental TUI and its
equation catalog remain in `tui`, outside the active workspace.

## Add the library to your Python project

Run this in your own project:

```sh
uv add "typecalc @ git+https://github.com/EdwardAstill/typecalc.git#subdirectory=package/typecalc"
```

uv builds the library from that subdirectory and records the Git source
and resolved commit in your project. Installing the library does not
install the CLI or Textual. Plain `uv add typecalc` searches a package
index; it does not discover this GitHub repository.

```python
from typecalc import solve

print(solve(["A + B = 10", "A = 6"]))
# {'A': 6.0, 'B': 4.0}
```

For a local clone, add its library directory instead:

```sh
uv add /path/to/typecalc/package/typecalc
```

## Run an equation file from a clone

```sh
git clone https://github.com/EdwardAstill/typecalc.git
cd typecalc
uv run --package typecalc-cli typecalc equations.txt
```

The CLI passes the file's lines to the solver. For an `equations.txt` containing:

```text
A + B = 10
A = 6
```

the terminal output is:

```text
A = 6.0
B = 4.0
```

Files use UTF-8 and one equation per line; blank lines are allowed. Results
print sorted by variable name. Errors go to stderr and return a nonzero exit
code; parse errors preserve the original file line numbers. Quote paths
containing spaces, such as `typecalc "my equations.txt"`.

To solve literal text instead of a file, use `--text`:

```sh
typecalc --text 'A + B = 10
A = 6'
```

Pass either a file path or `--text`, one input source at a time.

## Install the terminal command

From the repository root, install the CLI and supply its local library:

```sh
uv tool install ./cli --with ./package/typecalc --force
typecalc equations.txt
```

For an editable development installation:

```sh
uv tool install --editable ./cli --with-editable ./package/typecalc --force
```

The CLI's workspace source applies when developing in this repository.
For a standalone tool installation, `--with` supplies the library source.
The `--force` flag replaces an existing `typecalc` launcher, including the
earlier TUI launcher. If uv reports that the tool's
bin directory is missing from your PATH, run `uv tool update-shell` and
restart your shell.

## Development

```sh
uv sync --all-packages
uv run --package typecalc python -m unittest discover -s package/typecalc/tests
uv run --package typecalc-cli python -m unittest discover -s cli/tests
```

See the [API reference](docs/reference.md) and [backend notes](docs/backend.md).

## Neovim integration

The [Neovim plugin](typecalc.nvim/README.md) provides `:TypecalcAdd` to insert
library equations. In the local Neovim configuration, `Space r` in a `.txt`
file saves and runs it through the CLI in the tmux runner popup. With text
highlighted, `Space r` runs only the selection without saving the file.
