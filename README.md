# alarm2slack

- AWS cloudwatch(alarm) -> topic -> lambda
- python3.8

## local

```
docker run --rm --env-file .env -v ${PWD}:/var/task:ro lambci/lambda:python3.8 test.lambda_handler $(printf '%s' $(cat alart.json))
```

