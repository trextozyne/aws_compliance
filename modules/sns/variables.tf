variable "sns_topic_name" {
  description = "Name to be used for SnS topic"
  type    = string
  default = ""
}

variable "sns_topic_email" {
  description = "Email to be used with SnS topic"
  type    = string
  default = ""
}

variable "lambda_function_arn" {
  description = "The lambda function arn to be used to subscribe to sns"
}