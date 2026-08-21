data "terraform_remote_state" "foundation" {
  backend = "local"

  config = {
    path = "../foundation/terraform.tfstate"
  }
}

data "aws_caller_identity" "current" {}