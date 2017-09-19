lintr:::read_settings("/src")
files <- list.files(path="/src", pattern="*.R$", all.files=TRUE, full.names=TRUE, recursive=TRUE)
lapply(files, function(x) {
    lintr::lint(x)
})