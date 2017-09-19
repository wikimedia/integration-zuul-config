lintr:::read_settings("/src")
files <- list.files(path="/src", pattern="*.R", full.names=T, recursive=TRUE)
lapply(files, function(x) {
    lintr::lint(x)
})