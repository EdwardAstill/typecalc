local root = vim.fn.fnamemodify(debug.getinfo(1, "S").source:sub(2), ":p:h:h")
vim.opt.runtimepath:append(root)
vim.cmd("runtime plugin/typecalc.lua")

local function lines()
  return vim.api.nvim_buf_get_lines(0, 0, -1, false)
end

local ok, error = xpcall(function()
  assert(vim.api.nvim_get_commands({}).Typecalc == nil, "plugin still owns the runner")
  assert(vim.fn.exists(":TypecalcAdd") == 2, "picker command missing")
  local callback, chosen
  vim.ui.select = function(items, options, on_choice)
    assert(#items == 18, "library equations missing")
    for _, item in ipairs(items) do
      if item.topic == "Motion" and item.name == "final_velocity" then
        chosen = item
      end
    end
    assert(options.format_item(chosen):find("v = u + a * t", 1, true), "equation not visible")
    callback = on_choice
  end

  vim.cmd("TypecalcAdd")
  callback(chosen)
  assert(vim.deep_equal(lines(), { "v = u + a * t" }), "empty line not filled")
  vim.cmd("TypecalcAdd")
  callback(chosen)
  assert(vim.deep_equal(lines(), { "v = u + a * t", "v = u + a * t" }), "line not inserted")
  vim.cmd("TypecalcAdd")
  callback(nil)
  assert(#lines() == 2, "cancel changed buffer")

  vim.cmd("TypecalcAdd")
  local original = vim.api.nvim_get_current_buf()
  vim.cmd("enew!")
  callback(chosen)
  assert(vim.deep_equal(lines(), { "" }), "picker wrote into another buffer")
  assert(vim.api.nvim_buf_line_count(original) == 3, "original buffer did not receive equation")

  vim.cmd("TypecalcAdd")
  vim.bo.modifiable = false
  callback(chosen)
  assert(vim.deep_equal(lines(), { "" }), "unmodifiable buffer was changed")
  local notice
  vim.notify = function(message) notice = message end
  vim.cmd("TypecalcAdd")
  assert(notice:find("editable", 1, true), "missing uneditable-buffer error")
end, debug.traceback)

if not ok then
  io.stderr:write(error .. "\n")
  vim.cmd("cquit 1")
end
print("typecalc.nvim: equation picker checks passed")
vim.cmd("qa!")
