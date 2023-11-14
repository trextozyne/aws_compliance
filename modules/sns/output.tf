
output "sns_topic_arn" {
    value = try(aws_sns_topic.call_lambdas_topic.arn, "")
}

output "sns_topic_name" {
    value = try(aws_sns_topic.call_lambdas_topic.name, "")
}

output "sns_topic_id" {
    value = try(aws_sns_topic.call_lambdas_topic.id, "")
}

output "sns_topic_owner" {
    value = try(aws_sns_topic.call_lambdas_topic.owner, "")
}