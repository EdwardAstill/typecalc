# typecalc.nvim

Use `:TypecalcAdd` to choose a Motion or Electricity equation and insert it
into the current buffer. An empty line is filled; otherwise the equation
is added below the cursor. Canceling leaves the buffer unchanged.

The library is a Lua dictionary in [library.lua](lua/typecalc/library.lua).
Use consistent SI units and choose formulas that apply to your problem.
Motion formulas assume constant acceleration where relevant; electricity
formulas describe DC circuits and ideal components.

## Local setup

Your Neovim configuration loads this local plugin through lazy.nvim.
The picker uses `vim.ui.select`, including your Telescope dropdown.

Running files belongs to your Neovim runner configuration: `Space r` in a
plain text file (`.txt`) saves it and runs `typecalc <file>` in the existing
tmux runner popup. In Visual mode, the same shortcut runs only the highlighted
text using `--text`, without saving the file. Start Neovim inside tmux and install
the [CLI](../README.md#install-the-terminal-command) on Neovim's PATH.

The plugin only inserts equations; it has no runner command.

## Verify

From the repository root:

```sh
nvim --headless -u NONE -l typecalc.nvim/tests/run.lua
```
