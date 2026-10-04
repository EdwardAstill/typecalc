if vim.g.loaded_typecalc then
  return
end
vim.g.loaded_typecalc = true

vim.api.nvim_create_user_command("TypecalcAdd", function()
  require("typecalc").add_equation()
end, { desc = "Insert an equation from the library" })
