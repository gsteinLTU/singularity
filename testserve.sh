#!/bin/bash

# Zip the ./singularity/ directory into singularity.zip
zip -r singularity.zip ./singularity/

# Run http-server on port 8080
http-server -p 8080