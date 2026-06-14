#!/bin/bash
pg_dump -h server -U postgres -s -f "/Users/tomwattley/Code/projects/learning_app/backend/learning_api_schema.sql" learning-api
