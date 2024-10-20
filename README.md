# DNS Management API with BIND and Flask

This project provides a DNS Management API built using Flask, which allows you to add, delete, and check DNS records dynamically. It uses BIND (Berkeley Internet Name Domain) for DNS services and includes a Prometheus exporter for monitoring.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Docker Setup](#docker-setup)
- [Prometheus Monitoring](#prometheus-monitoring)

## Requirements

- Docker
- Basic knowledge of DNS concepts

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/dns-management-api.git
   cd dns-management-api

2. Build the Docker image:
   ```bash
   docker build -t dns-management-api .

## Usage

1. Run the Docker container:
   ```bash
   docker run -d -p 5000:5000 -p 53:53/udp -p 53:53/tcp --name dns-api dns-management-api
2. Use the API to manage DNS records via curl or any HTTP client.

## API Endpoints

## Add/Delete  Records
   ```bash
   Sample CURL requests:

   Add Record:
   curl -X POST http://localhost:5000/add_record -H "Content-Type: application/json" -d '{"domain": "test.com", "type": "A", "name": "test", "value": "192.168.1.10"}'

   Delete Record:
   curl -X POST http://localhost:5000/delete_record -H "Content-Type: application/json" -d '{"domain": "test.com", "name": "test"}'

   Check Record:
   curl -X POST http://localhost:5000/check_record -H "Content-Type: application/json" -d '{"domain": "test.com"}'


## Docker Setup

This project uses a Dockerfile to create a containerized environment. The base image is Ubuntu 24.04 LTS, and the following components are installed:

    BIND9
    Python 3 and pip
    Flask
    Prometheus Bind Exporter

## Prometheus Monitoring

The Prometheus Bind Exporter is included to monitor BIND's performance metrics, running on port 9119. Configure your Prometheus instance to scrape these metrics.
