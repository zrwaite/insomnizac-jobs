from dotenv import dotenv_values

env = dotenv_values(".env")

if env['SNS_TOPIC_ARN'] == "":
    raise ValueError("SNS_TOPIC_ARN is not set in .env")
