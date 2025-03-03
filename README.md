# Insomnizac Jobs

## Infra

Use `terraform` directory

Create a `terraform.tfvars` file with aws details and phone number

### Deployment

```
./package.sh
```


## Infrastructure Components

- AWS Lambda function that runs every 10 minutes
- DynamoDB table to store show information
- SNS Topic for notifications
- CloudWatch Event Rule for scheduling
- IAM roles and policies
- SMS subscription for notifications

## Local Development

To test the scraper locally:

1. Install dependencies:
```bash
pip install -r jobs/comedy_scraper/requirements.txt
```

2. Set environment variables:

3. Run the script:
```bash
python3 -m jobs.comedy_scraper.comedy_scraper
```
