variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "aws_access_key_id" {
    description = "AWS access key id"
    type        = string
}

variable "aws_secret_access_key" {
    description = "AWS secret access key"
    type        = string
}

variable "phone_number" {
  description = "Phone number to receive SMS notifications (E.164 format)"
  type        = string
} 
