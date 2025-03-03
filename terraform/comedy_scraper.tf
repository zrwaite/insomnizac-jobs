# Lambda function
resource "aws_lambda_function" "comedy_scraper" {
  filename         = "comedy_scraper.zip"
  function_name    = "comedy-scraper"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 128

  source_code_hash = filebase64sha256("comedy_scraper.zip")

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.shows_table.name
      SNS_TOPIC_ARN  = aws_sns_topic.new_shows.arn
    }
  }
}

# DynamoDB table
resource "aws_dynamodb_table" "shows_table" {
  name           = "comedy-mothership-shows"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

# SNS Topic
resource "aws_sns_topic" "new_shows" {
  name = "new-comedy-shows"
}

# SNS Topic subscription
resource "aws_sns_topic_subscription" "sms" {
  topic_arn = aws_sns_topic.new_shows.arn
  protocol  = "sms"
  endpoint  = var.phone_number
}

# CloudWatch Event Target
resource "aws_cloudwatch_event_target" "check_shows" {
  rule      = aws_cloudwatch_event_rule.every_ten_minutes.name
  target_id = "CheckComedyShows"
  arn       = aws_lambda_function.comedy_scraper.arn
}

# Lambda permission for CloudWatch Events
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.comedy_scraper.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_ten_minutes.arn
}

# IAM policy for the Lambda role
resource "aws_iam_role_policy" "lambda_policy" {
  name = "comedy_scraper_lambda_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:BatchGetItem",
          "sns:Publish",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          aws_dynamodb_table.shows_table.arn,
          aws_sns_topic.new_shows.arn,
          "arn:aws:logs:*:*:*"
        ]
      }
    ]
  })
}
