
# ==========SNS function ==========================================================
# SNS topic to subscribe
resource "aws_sns_topic" "call_lambdas_topic" {
  name = var.sns_topic_name
}

#resource "aws_sns_topic_subscription" "sns_email_subscription" {
#  topic_arn = aws_sns_topic.call_lambdas_topic.arn
#  protocol  = "email"
#  endpoint  = var.sns_topic_email
#}

# lambda subscribes the topic, so it should be notified when other resource publishes to the topic
resource "aws_sns_topic_subscription" "sns_lambdas_subscription" {
  topic_arn = aws_sns_topic.call_lambdas_topic.arn
  protocol  = "lambda"
  endpoint  = var.lambda_function_arn
}


resource "aws_sns_topic_policy" "default" {
  arn    = aws_sns_topic.call_lambdas_topic.arn
  policy = data.aws_iam_policy_document.sns_topic_policy.json
}

data "aws_iam_policy_document" "sns_topic_policy" {
  statement {
    sid       = "Allow CloudwatchEvents"
    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.call_lambdas_topic.arn]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
  }
}
# ==========SNS function ==========================================================