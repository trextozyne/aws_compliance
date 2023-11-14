#!/bin/bash

cd env/$1

read -r -p "Are you sure to destroy Terraform state for $1 env? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY]) 
        for resource in $(terraform state list); do terraform state rm "$resource"; done
        ;;
    *)
        echo "Terraform destroy cancelled for $1 env"
        ;;
esac