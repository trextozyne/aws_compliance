variable "aws_caller_identity_accountid" {
  description = "The account id performing the request"
}
variable "filename" {
  description = "The name of the written lambda code"
  default = ""
}
variable "function_name" {
  description = "The name the file or folder would be call on AWS lambda"
  default = ""
}
variable "runtime" {
  description = "The runtime environment the code is run i.e python3.8"
  default = ""
}

variable "lambda_iam_role_name" {
  description = "The name provided for the lambda iam role"
  default = ""
}

variable "folder_name" {
  description = "The folder of the written code resides"
  default = ""
}

variable "lambda_filename" {
  description = "The name of the written lambda code"
  default = ""
}
#
variable "cloudwatch_event_rule_arn" {
  description = "The cloudwatch event rule arm"
}

variable "sns_call_lambda_arn" {
  description = "The sns that invokes lambda arm"
}