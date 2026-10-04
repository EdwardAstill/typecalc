local M = {}

function M.add_equation()
  local buffer = vim.api.nvim_get_current_buf()
  local row = vim.api.nvim_win_get_cursor(0)[1]
  if vim.bo[buffer].buftype ~= "" or not vim.bo[buffer].modifiable then
    vim.notify("Typecalc: open an editable text buffer first", vim.log.levels.ERROR)
    return
  end

  local items = {}
  local library = require("typecalc.library")
  for topic, equations in pairs(library) do
    for name, equation in pairs(equations) do
      items[#items + 1] = { topic = topic, name = name, equation = equation }
    end
  end
  table.sort(items, function(a, b)
    if a.topic == b.topic then return a.name < b.name end
    return a.topic < b.topic
  end)

  vim.ui.select(items, {
    prompt = "Add equation:",
    format_item = function(item)
      return item.topic .. " / " .. item.name:gsub("_", " ") .. ": " .. item.equation
    end,
  }, function(item)
    if not item or not vim.api.nvim_buf_is_valid(buffer) or not vim.bo[buffer].modifiable then
      return
    end
    row = math.min(row, vim.api.nvim_buf_line_count(buffer))
    local line = vim.api.nvim_buf_get_lines(buffer, row - 1, row, false)[1]
    local start = line:match("^%s*$") and row - 1 or row
    vim.api.nvim_buf_set_lines(buffer, start, row, false, { item.equation })
  end)
end

return M
