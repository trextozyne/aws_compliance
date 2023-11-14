
output "cloudtrail_arn" {
    value = try(aws_cloudtrail.cloud_trail_compliance.arn, "")
}

output "cloudwatch_log_group_name" {
    value = try(aws_cloudwatch_log_group.log_group.name, "")
}

output "cloudwatch_log_group_arn" {
    value = try(aws_cloudwatch_log_group.log_group.arn, "")
}

output "cloudwatch_event_rule_arn" {
    value = try(aws_cloudwatch_event_rule.cloudwatch_event.arn, "")
}

output "caller_identity" {
    value = data.aws_caller_identity.current
}

output "account_id" {
    value = local.account_id
}
