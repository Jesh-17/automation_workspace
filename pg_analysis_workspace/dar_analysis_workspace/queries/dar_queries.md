# For 4xx and 5xx
1. ## API-Gateway-Access-Logs_x05o36zvli/prod      (Log groups)
    ```sql

    fields  @timestamp, @message, apiKey, requestId, ip, requestTime, httpMethod, resourcePath, status, protocol, responseLength

    #| filter (status >= 400 and status < 500) or (status >= 500 and status < 600)
    #| filter @message like /("status":"4|"status":"5)/
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
    #| filter @message like /("status":"4|"status":"5)/
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
    #| filter @message like /("status":"4|"status":"5)/
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
    #| filter @message like /("status":"4|"status":"5)/
    #| filter @message not like 'POST:/v4/public/auth/login/phone/he'
    #| filter @message like 'error: ' and  @message like /("statusCode":4|"statusCode":5)/ and  @message not like 'POST:/v4/public/auth/login/phone/he'
    | filter @message like 'error: ' and  @message like /("statusCode":4)/ and  @message not like 'POST:/v4/public/auth/login/phone/he'

    | filter !isempty(statusCode) and !isempty(@message)

    | parse @message /(?<Message>.*)/

    | stats count(*) as Count by bin(1d) as Date, Message

    | filter !isempty(Message)

    | sort Date, Count desc

    | limit 10000

    ```
    ```sql
    # To find unique logs
    
    fields @timestamp, @message


    #| filter @message like 'error: ' and  @message like /("statusCode":4|"statusCode":5)/ and  @message not like 'POST:/v4/public/auth/login/phone/he'

    | filter @message like 'error: ' and  @message like /("statusCode":4)/ and  @message not like 'POST:/v4/public/auth/login/phone/he'

    | filter !isempty(statusCode) and !isempty(@message)

    | parse @message /(?<Message>.*)/

    | stats count(*) as Count by Message

    | filter !isempty(Message)

    | sort Count desc, Message asc

    | limit 10000

    ```

-------------------------------------------------------------------
# for party api  /aws/lambda/TigoID-Party-API-prod
```sql
fields @timestamp, @message, @logStream
    | filter @message like "error: POST:"
    #| filter statusCode >= 400 AND statusCode < 500
          #and @message like "error: POST:"
        # and @message like 'POST:/v4/public/users/me/identifications'
        # and  @message not like 'POST:/v4/public/auth/login/phone/he'
        # and @message like "7dFsLv"

        #and @message like /Billing system get accounts api returned given msisdn as non tigo number./
        #and @message like /EXTERNAL-APIS:BILLING-SYSTEM-GET-ACCOUNTS-API-RETURNED-NON-TIGO-NUMBER/
        #and @message like /Something went wrong, please try after some time/

    | sort @timestamp desc
    | limit 10000

```

# for me api /aws/lambda/TigoID-Me-API-prod
```sql
fields @timestamp, @message, @logStream
    | filter statusCode >= 400 AND statusCode < 500
          and @message like "error: POST:"
        # and @message like 'POST:/v4/public/users/me/identifications'
        # and  @message not like 'POST:/v4/public/auth/login/phone/he'
        # and @message like "7dFsLv"

        #and @message like /Billing system get accounts api returned given msisdn as non tigo number./
        #and @message like /EXTERNAL-APIS:BILLING-SYSTEM-GET-ACCOUNTS-API-RETURNED-NON-TIGO-NUMBER/
        #and @message like /Something went wrong, please try after some time/

    | sort @timestamp desc
    | limit 10000
```

# for functional api 
```sql
fields @timestamp, @message, @logStream
    | filter statusCode >= 400 AND statusCode < 500
        and @message like 'POST:/v4/public/auth/login/phone'
        and  @message not like 'POST:/v4/public/auth/login/phone/he'
        #and @message like "7dFsLv"

        #and @message like /Billing system get accounts api returned given msisdn as non tigo number./
        #and @message like /EXTERNAL-APIS:BILLING-SYSTEM-GET-ACCOUNTS-API-RETURNED-NON-TIGO-NUMBER/
        #and @message like /Something went wrong, please try after some time/

    | sort @timestamp desc
    | limit 10000

```

```sql
SOURCE "/aws/lambda/TigoID-OTP-Queue-Worker-prod" START=-21600s END=0s |
fields @timestamp, @message, @logStream
#| filter @message like 'country:co:kannel-api-helper:sendSms:EXTERNAL-APIS:KANNEL-SEND-SMS-API-FAILED'
| parse '*:version:*:event:*:phone:*:templateId:*:country:*:*:*::*' as logType, version, EventType, phone, templateId, country, Type, Response, ErrorResponse
| filter !isblank(logType)
| stats count(*) as cnt by EventType, templateId, country, Response, ErrorResponse
| sort cnt desc
| limit 10000
```
```sql
fields @timestamp, @message, @logStream
| filter @message like 'phone-send-otp' and @message like 'login_otp' and @message like 'The Service is temporarily unavailable'
| limit 10000
```