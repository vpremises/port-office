variable "IMAGE_NAMESPACE" {
  default = "ghcr.io/vpremises"
}
variable "IMAGE_VERSION" {
  default = "0.1.0"
}
variable "SOURCE_REVISION" {
  default = "development"
}
variable "PLATFORMS" {
  default = "linux/amd64"
}

target "base-debian" {
  context = "."
  dockerfile = "images/debian/Dockerfile"
  platforms = split(",", PLATFORMS)
  tags = ["${IMAGE_NAMESPACE}/base-debian:${IMAGE_VERSION}"]
  args = {
    IMAGE_VERSION = IMAGE_VERSION
    SOURCE_REVISION = SOURCE_REVISION
  }
}
group "default" {
  targets = ["base-debian"]
}
