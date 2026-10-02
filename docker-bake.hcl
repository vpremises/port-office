variable "IMAGE_NAMESPACE" {
  default = "ghcr.io/vpremises"
}


target "base-alpine-v3_19-p3_11_7-n20" {
  context = "./base/alpine"
  dockerfile = "v3.19-p3.11.7-n20/Dockerfile"
  tags = ["${IMAGE_NAMESPACE}/base-alpine:v3.19-p3.11.7-n20"]
}
target "base-alpine-v3_19-p3_11_7-n18" {
  context = "./base/alpine"
  dockerfile = "v3.19-p3.11.7-n18/Dockerfile"
  tags = ["${IMAGE_NAMESPACE}/base-alpine:v3.19-p3.11.7-n18"]
}
target "base-alpine-v3_18-p3_11_7-n18" {
  context = "./base/alpine"
  dockerfile = "v3.18-p3.11.7-n18/Dockerfile"
  tags = ["${IMAGE_NAMESPACE}/base-alpine:v3.18-p3.11.7-n18"]
}
target "base-debian-bookworm-p3_11_7-n18" {
  context = "./base/debian"
  dockerfile = "bookworm-p3.11.7-n18/Dockerfile"
  tags = ["${IMAGE_NAMESPACE}/base-debian:bookworm-p3.11.7-n18"]
}
target "iac-tofu-v1_6_0" {
  context = "./iac/tofu"
  dockerfile = "v1.6.0/Dockerfile"
  tags = ["${IMAGE_NAMESPACE}/iac-tofu:v1.6.0"]
}
target "iac-tofuformer-gcp-5_13_0" {
  context = "./iac/tofuformer"
  dockerfile = "gcp-5.13.0/Dockerfile"
  tags = ["${IMAGE_NAMESPACE}/iac-tofuformer:gcp-5.13.0"]
}
target "iac-tofuformer-gcp-4_59_0" {
  context = "./iac/tofuformer"
  dockerfile = "gcp-4.59.0/Dockerfile"
  tags = ["${IMAGE_NAMESPACE}/iac-tofuformer:gcp-4.59.0"]
}
target "traefik-v3_0_0-beta5-alpine" {
  context = "./traefik/v3.0.0-beta5"
  dockerfile = "alpine/Dockerfile"
  tags = ["${IMAGE_NAMESPACE}/traefik-v3.0.0-beta5:alpine"]
}
target "traefik-v3_0_0-beta5-debian" {
  context = "./traefik/v3.0.0-beta5"
  dockerfile = "debian/Dockerfile"
  tags = ["${IMAGE_NAMESPACE}/traefik-v3.0.0-beta5:debian"]
}
target "frappe-v15_11_0-alpine" {
  context = "./frappe/v15.11.0"
  dockerfile = "alpine/Dockerfile"
  tags = ["${IMAGE_NAMESPACE}/frappe-v15.11.0:alpine"]
  args = { IMAGE_NAMESPACE = IMAGE_NAMESPACE }
}
target "frappe-v15_11_0-debian" {
  context = "./frappe/v15.11.0"
  dockerfile = "debian/Dockerfile"
  tags = ["${IMAGE_NAMESPACE}/frappe-v15.11.0:debian"]
  args = { IMAGE_NAMESPACE = IMAGE_NAMESPACE }
}
group "default" {
  targets = ["base-alpine-v3_19-p3_11_7-n20","base-alpine-v3_19-p3_11_7-n18","base-alpine-v3_18-p3_11_7-n18","base-debian-bookworm-p3_11_7-n18"]
}
group "frappe" {
  targets = ["traefik-v3_0_0-beta5-alpine","traefik-v3_0_0-beta5-debian","frappe-v15_11_0-alpine","frappe-v15_11_0-debian"]
}
group "iac" {
  targets = ["iac-tofu-v1_6_0","iac-tofuformer-gcp-5_13_0","iac-tofuformer-gcp-4_59_0"]
}
