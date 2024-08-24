provider "aws" {
  region = "us-west-2"  
}

resource "aws_instance" "app_server" {
  ami           = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2 AMI ID 
  instance_type = "t2.micro"

  tags = {
    Name = "TextToSpeechAppServer-${var.environment}"
  }

  user_data = <<-EOF
              #!/bin/bash
              sudo yum update -y
              sudo yum install -y python3 python3-pip
              sudo pip3 install flask flask-cors google-cloud-texttospeech PyPDF2 pydub
              sudo yum install -y ffmpeg
              echo "${var.google_credentials}" > /home/ec2-user/google_credentials.json
              export GOOGLE_APPLICATION_CREDENTIALS="/home/ec2-user/google_credentials.json"
              # Clone your repository and start the application
              git clone https://github.com/Serpantiner/text-to-speech-app.git /home/ec2-user/app
              cd /home/ec2-user/app
              chmod +x run.py
              nohup python3 -c "from run import app; app.run(host='0.0.0.0', port=80)" > /home/ec2-user/app.log 2>&1 &
              EOF

  vpc_security_group_ids = [aws_security_group.allow_http.id]
}

resource "aws_security_group" "allow_http" {
  name        = "allow_http"
  description = "Allow HTTP inbound traffic"

  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "allow_http"
  }
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "google_credentials" {
  description = "Google Cloud credentials JSON"
  type        = string
}

output "public_ip" {
  value = aws_instance.app_server.public_ip
}