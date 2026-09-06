group "pose-arm64" {
  targets = [
    "pose-web-arm64",
    "pose-api-arm64",
  ]
}

target "pose-web-arm64" {
  context    = "web"
  dockerfile = "Dockerfile"
  tags       = ["pose-web"]
  platforms  = ["linux/arm64"]
}

target "pose-api-arm64" {
  context    = "app"
  dockerfile = "Dockerfile"
  tags       = ["pose-api"]
  platforms  = ["linux/arm64"]
}
