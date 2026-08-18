# For 4xx and 5xx
1. ## API-Gateway-Access-Logs_x05o36zvli/prod      (Log groups)
    ```sql

    fields  @timestamp, @message, apiKey, requestId, ip, requestTime, httpMethod, resourcePath, status, protocol, responseLength

    #| filter (status >= 400 and status < 500) or (status >= 500 and status < 600)
    #| filter @message like /("status":"4|status":"5)/
    | filter @message like /("status":"4)/

    #| stats count(*) as Count by bin(1d) as Date, apiKey, requestId, ip, requestTime, httpMethod, resourcePath, status, protocol, responseLength
    #| stats count(*) as Count by bin(1d) as Date, httpMethod, resourcePath, status, apiKey
    | stats count(*) as Count by bin(1d) as Date, apiKey, httpMethod, resourcePath, status

    | filter !isempty(status)

    | sort Date, Count desc
    #| sort by resourcePath, httpMethod, status
    #| sort by httpMethod, resourcePath, status

    | limit 10000

    ```

    ```sql
    # To find unique count

    fields  @timestamp, @message, apiKey, requestId, ip, requestTime, httpMethod, resourcePath, status, protocol, responseLength

    #| filter (status >= 400 and status < 500) or (status >= 500 and status < 600)
    #| filter @message like /("status":"4|status":"5)/
    | filter @message like /("status":"4)/

    #| stats count(*) as Count by bin(1d) as Date, apiKey, requestId, ip, requestTime, httpMethod, resourcePath, status, protocol, responseLength
    #| stats count(*) as Count by bin(1d) as Date, httpMethod, resourcePath, status, apiKey
    | stats count(*) as Count by httpMethod, resourcePath, status

    | filter !isempty(status)

    | sort Count desc
    #| sort by resourcePath, httpMethod, status
    #| sort by httpMethod, resourcePath, status

    | limit 10000

    ```

2. ## Based on the highest `resourcePath` count we need to go to that api gateway i.e `tigo-cognito-prod-DAR-API` ID: `x05o36zvli` and go to that path and we can find the particular lambda.

- /aws/lambda/TigoID-Functional-API-prod   (example)

    ```sql

    fields @timestamp, @message

    #| filter (statusCode >= 400 and statusCode < 500) or (statusCode >= 500 and statusCode < 600)
    #| filter @message like /("status":"4|status":"5)/
    #| filter @message not like 'POST:/v4/public/auth/login/phone/he'
    | filter @message like 'error: ' and @message like /("statusCode":4)/ and  @message not like 'POST:/v4/public/auth/login/phone/he'

    | parse @message  '*: *:*:*:creationChannel:*, creationChannelType:*, apiKey:*, country:*, phone:* : *' as logType, method, path, trace, creationChannel, creationChannelType, apiKey, country, phone, errorMsg

    #| stats count(*) as Count by bin(1d) as Date, logType, method, path, trace, creationChannel,creationChannelType, apiKey, country, phone, errorMsg
    #| stats count(*) as Count by bin(1d) as Date, errorMsg

    #| sort Date, Count desc

    | parse errorMsg '*:{"statusCode":*,"headers":*,"body":{"success":*,"body":*,"status":[{"code":"*","description":"*","userMessage":"*","errorDetails":"*"}]}}' as msg, statuscode, header, success, body, code, description, userMessage, errorDetails

    #| stats count(*) as Count by bin(1d) as Date, msg, statuscode, header, success, body, code, description, userMessage, errorDetails
    | stats count(*) as Count by bin(1d) as Date, code, description, userMessage, errorDetails

    | filter !isempty(statuscode)

    | sort Date, Count desc
    #| sort by code, description, userMessage, errorDetails

    | limit 10000

    ```

    ```sql

    fields @timestamp, @message

    
    #| filter (statusCode >= 400 and statusCode < 500) or (statusCode >= 500 and statusCode < 600)
    #| filter @message like /("status":"4|status":"5)/
    #| filter @message not like 'POST:/v4/public/auth/login/phone/he'
    | filter @message like 'error: ' and  @message like /("statusCode":4)/ and  @message not like 'POST:/v4/public/auth/login/phone/he'

    | filter !isempty(statusCode)

    | stats count(*) as Count by bin(1d) as Date, @message

    | filter !isempty(@message)

    | sort Date, Count desc

    | limit 10000

    ```
    ```sql
    # To find unique logs
    
    fields @timestamp, @message

    | filter @message like 'error: ' and  @message like /("statusCode":4)/ and  @message not like 'POST:/v4/public/auth/login/phone/he'

    | filter !isempty(statusCode) and !isempty(@message)

    | parse @message /(?<Message>.*)/

    | stats count(*) as Count by Message

    | filter !isempty(@message)

    | sort Count desc, Message asc

    | limit 10000

    ```

