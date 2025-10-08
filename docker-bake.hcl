group "pose-arm64" {
  targets = [
    "pose-web-arm64"
  ]
}

target "pose-web-arm64" {
  context    = "web"
  dockerfile = "Dockerfile"
  tags       = ["pose-web"]
  platforms  = ["linux/arm64"]
}
