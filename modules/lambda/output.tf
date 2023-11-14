output "aws_lambda_function_arn" {
  value = try(aws_lambda_function.resource_compliance_function.arn, "")
}

output "aws_lambda_function_name" {
  value = try(aws_lambda_function.resource_compliance_function.function_name, "")
}

output "aws_iam_role_arn" {
  value = try(aws_iam_role.lambda.arn, "")
}
