# For 4xx and 5xx
1. ## API-Gateway-Access-Logs_etmsu5l0ak/prod      (Log groups)
    ```sql

    fields  @timestamp, @message, path, requestId, ip, caller, user, requestTime, httpMethod, resourcePath, status, protocol, responseLength, accessKey

    #| filter (status >= 400 and status < 500) or (status >= 500 and status < 600)
    #| filter @message like /("status":"4|status":"5)/
    | filter @message like /("status":"5)/

    #| stats count(*) as Count by bin(1d) as Date, path, requestId, ip, caller, user, requestTime, httpMethod, resourcePath, status, protocol, responseLength, accessKey
    | stats count(*) as Count by bin(1d) as Date, httpMethod, resourcePath, status


    | filter !isempty(status)

    | sort Date, Count desc
    #| sort by resourcePath, httpMethod, status
    #| sort by httpMethod, resourcePath, status

    | limit 10000

    ```

    ```sql
    # To find unique count
    
    fields  @timestamp, @message, path, requestId, ip, caller, user, requestTime, httpMethod, resourcePath, status, protocol, responseLength, accessKey

    #| filter (status >= 400 and status < 500) or (status >= 500 and status < 600)
    #| filter @message like /("status":"4|status":"5)/
    | filter @message like /("status":"5)/

    #| stats count(*) as Count by path, requestId, ip, caller, user, requestTime, httpMethod, resourcePath, status, protocol, responseLength, accessKey
    | stats count(*) as Count by httpMethod, resourcePath, status


    | filter !isempty(status)

    | sort Count desc
    #| sort by resourcePath, httpMethod, status
    #| sort by httpMethod, resourcePath, status

    | limit 10000


    ```

2. ## Based on the highest `resourcePath` count we need to go to that api gateway i.e `PaymentGateway-prod` ID: `etmsu5l0ak` and go to that path and we can find the particular lambda.

- PaymentGateway-prod-Orders-Microservice (example)

    ```sql

    fields @timestamp, @message

    #| filter ((httpStatusCode >= 400 and httpStatusCode < 500) or (httpStatusCode >= 500 and httpStatusCode < 600)) and @message like /("errors")/
    #| filter (httpStatusCode >= 400 and httpStatusCode < 500) or (httpStatusCode >= 500 and httpStatusCode < 600)
    #| filter @message like /("httpStatusCode":"4|httpStatusCode":"5)/
    | filter @message like /("httpStatusCode":5)/ and  @message like /("errors")/

    # | parse @message '"httpStatusCode":*,"body":*,"errors":"[{\"httpStatusCode\":*,\"code\":*,\"description\":\"*\",\"userMessage\":\"*\",\"errorDetail\":\"*\",\"externalErrorCode\":*}]","applicationName":*}:*' as Httpstatuscode, body, httpstatuscode,code, description, usermessage, errorDetails, externalErrorcode, applicationName,ExceptionClass_Json_Packages

    | filter !isempty(httpStatusCode)

    | stats count(*) as Count by bin(1d) as Date, @message

    | filter !isempty(@message)

    | sort Date, Count desc

    | limit 10000

    ```

    ```sql
    # Date wise count
    fields @timestamp, @message

    | filter ((httpStatusCode >= 400 and httpStatusCode < 500) or (httpStatusCode >= 500 and httpStatusCode < 600)) and @message like /("errors")/
    | filter !isempty(httpStatusCode)

    | parse @message /(?<Message>.*)/

    | stats count(*) as Count by bin(1d) as Date, Message

    | filter !isempty(Message)

    | sort Date asc, Count desc

    | limit 10000

    ```
    ```sql
    # To find unique logs
    
    fields @timestamp, @message

    | filter ((httpStatusCode >= 400 and httpStatusCode < 500) or (httpStatusCode >= 500 and httpStatusCode < 600)) and @message like /("errors")/

    | filter !isempty(httpStatusCode) and !isempty(@message)

    | parse @message /(?<Message>.*)/

    | stats count(*) as Count by Message
    
    | sort Count desc, Message asc

    #| display Message, Count

    | limit 10000

    ```
    ```sql


    fields @timestamp, @message

    # To find 4xx errors or 5xx errors
        
        | filter @message like /("httpStatusCode":5)/ and  @message like /("errors")/
        
    
        | filter !isempty(httpStatusCode)


    
        | stats count(*) as Count by @message
        | sort Count desc

    # To write the parse query using pg_topkeys
        
        | parse @message '{"httpStatusCode":*,"body":*,"errors":"[{\"httpStatusCode\":*,\"code\":*,\"description\":\"*\",\"userMessage\":\"*\",\"errorDetail\":\"*\",\"externalErrorCode\":\"*\"}*]","applicationName":*,"applicationContext":*,"listOfException":*,"environment":*}:*' as Httpstatuscode, body, httpstatuscode, code, description, usermessage, errorDetail, externalErrorCode, errors_next_json, applicationName, applicationContext, listOfException, environment, ExceptionClass_Json_Packages
    

        | limit 10000
    


    ```




































    ```sql

    fields @timestamp, @message, @requestId

    | filter @requestId !="" | filter @message not like /REPORT RequestId:/ 

    | sort @timestamp desc

    | limit 10000

    ```




    ```sql

    fields @timestamp, @message, @requestId

    #| filter @requestId !="" 

    | filter @message like /Exception: |Caused by:/
    
    | filter @message not like /END RequestId:|START RequestId:|REPORT RequestId:|httpStatusCode":5|httpStatusCode":4|ERROR / 

    | parse @message /(?<Message>.*)/

    | stats count(*) as Count by Message

    | sort Count desc, Message asc

    #| sort @timestamp desc

    | limit 10000


    ```

After same time stamp
```sql

    fields @timestamp, @message

    #filter @message not like /REPORT RequestId:/ 

    | sort @timestamp desc

    | limit 10000

```
```

```