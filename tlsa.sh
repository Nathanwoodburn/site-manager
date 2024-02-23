#!/bin/bash

# Get domain name from arguments
domain=$1

mkdir certs/$domain

openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
    -keyout certs/$domain/cert.key -out certs/$domain/cert.crt \
    -extensions ext  -config \
  <(echo "[req]";
    echo distinguished_name=req;
    echo "[ext]";
    echo "keyUsage=critical,digitalSignature,keyEncipherment";
    echo "extendedKeyUsage=serverAuth";
    echo "basicConstraints=critical,CA:FALSE";
    echo "subjectAltName=DNS:$domain,DNS:*.$domain";
    ) -subj "/CN=*.$domain"

echo -n "3 1 1 " && openssl x509 -in certs/$domain/cert.crt -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | xxd  -p -u -c 32
