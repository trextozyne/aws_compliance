#!/bin/bash
cd ../AWS_NINJA/Compliance_lambdas/ || exit

zip -r aws_services_compliance.zip -- ./*
