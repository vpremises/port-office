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
variable "OCI_ARCHIVE" {
  default = ".artifacts/base-debian.oci.tar"
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

# Keep attestations in the OCI index. The runtime test imports the exact image blobs
# from this archive; Docker's classic exporter cannot load an attested manifest list.
target "candidate" {
  inherits = ["base-debian"]
  output = ["type=oci,dest=${OCI_ARCHIVE}"]
  attest = ["type=sbom", "type=provenance,mode=max,version=v0.2"]
}
