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

  # any these having logs
  fields @timestamp, @message, @logStream
  | filter ((httpStatusCode >= 500 and httpStatusCode < 600)) and @message like /("Internal Server Error - Please try again later|2-CCSB000028|billing-mobile-invoice-nequi-prd-co")/
  | filter !isempty(httpStatusCode) and !isempty(@message)
  | limit 10000

  ```
```sql
    # description	externalErrorCode	applicationName
    # logs should have these
    fields @timestamp, @message, @logStream
    | filter httpStatusCode >= 500 and httpStatusCode < 600
    | filter @message like /Internal Server Error - Please try again later/
    | filter @message like /2-CCSB000028/
    | filter @message like /billing-mobile-invoice-nequi-prd-co/
    | limit 10000

    or

    fields @timestamp, @message, @logStream
    | filter httpStatusCode >= 500 AND httpStatusCode < 600
        and @message like /Internal Server Error - Please try again later/
        and @message like /2-CCSB000028/
        and @message like /billing-mobile-invoice-nequi-prd-co/  
    | sort @timestamp desc
    | limit 10000


```
```sql

    fields @timestamp, @message, @logStream
        | filter httpStatusCode >= 500 AND httpStatusCode < 600
        | sort @timestamp desc
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









# Ex: To find the exact root cause of the particular error and which logstream that error is more
```sql

fields @timestamp, @message, @logStream

| filter !isempty(@message)
#| filter @message like '"httpStatusCode":4'
| filter @message like 'Token is associated with active enrollment, cannot delete the token'
| stats count(*) as Count by @message, @logStream
#| sort Count desc, @message asc
| sort Count desc
| limit 10000

# 2025/11/05/[$LATEST]221c371eee184545a9dfe36b3f5b3286           (has highest count of logstream)


```
#  Taking the highest logstream count 
```sql
fields @timestamp, @message, @logStream
| filter !isempty(@message)
| filter @message like 'Token is associated with active enrollment, cannot delete the token'
| filter @logStream like '2025/11/05/[$LATEST]221c371eee184545a9dfe36b3f5b3286'
| limit 10000

```
```sql
fields @timestamp, @message
| filter !isempty(@message)
| limit 10000ql

```






fields @timestamp, errors, applicationName

    | filter ((httpStatusCode >= 400 and httpStatusCode < 500) or (httpStatusCode >= 500 and httpStatusCode < 600)) and @message like /("errors")/

    | filter !isempty(httpStatusCode) and !isempty(@message)

    | parse errors /(?<Message>.*)/

    | stats count(*) as Count by Message, applicationName
    
    | sort Count desc, Message asc

    #| display Message, Count

    | limit 10000



fields @timestamp, errors

    | filter ((httpStatusCode >= 400 and httpStatusCode < 500) or (httpStatusCode >= 500 and httpStatusCode < 600)) and @message like /("errors")/

    | filter !isempty(httpStatusCode) and !isempty(@message)

    | parse errors /(?<Message>.*)/

    | stats count(*) as Count by Message
    
    | sort Count desc, Message asc

    #| display Message, Count

    | limit 10000





# RDS (Screenshots: cpu,volume,latency,iops,update,delete)
ex: # Time: 2025-12-10T23:33:30.936075Z---> This is the date and time when the slow query was recorded.

    User@Host: PGLambda[PGLambda] @ [10.47.114.126]--->PGLambda is the database user that ran the query.  and The query came from the IP address 10.47.114.126 (your Lambda function).

    Id: 1410379661--->This is the database connection ID used for the query

    Query_time(System given time for the query): 5.748111--->The total time MySQL spent from start to finish = 5.75 seconds.(This includes waiting time + actual run time.)

    Lock_time(wait time): 5.747636--->Out of the total time, 5.74 seconds were spent WAITING because the table/row was locked by another query. Lock time is the waiting time for the query. Lock_time = How long the query waited because something else in the database was locked.

    Rows_sent = how many rows MySQL returned AFTER processing the query. 
    ex: If the query returns 10 rows → Rows_sent = 10
        If INSERT/UPDATE/DELETE → Rows_sent = 0 (because they don’t return rows)

    Rows_examined = how many rows MySQL had to LOOK AT while processing the query. it is the internal scanning work MySQL does.
    Note:
    If `Rows_examined` is very high → MySQL is working hard
    If `Rows_sent` is low → Means MySQL scanned a lot but returned little (This often means query is slow or missing an index)


    Hence Actual execution= Query_time-Lock_time   (With this we can say query process is fast or not)
          Query_time=Lock_time(wait time)+Actual time
          Lock_time(wait time)=Query_time-Actual time (With this we can say how much time query is waiting to process the query)

    
    Query_time  = 5.748111 s
    Lock_time   = 5.747636 s
    Actual time = 5.748111 − 5.747636 = 0.000475 s  (~0.0004 s)

    Actual execution: ~0.0004s → very fast
    Waiting on lock: ~5.74s → this is why it’s logged as a slow query (long total time) the query is intrinsically fast, but it’s observationally slow because it spent almost all its time waiting (Lock_time).






    ```sql
    fields @timestamp, @message, @logStream
    #| filter @logStream = "paymentgateway-prod-dbwrite"
    | parse  "* Query_time: * Lock_time: * Rows_sent: * Rows_examined: * *" as Time_UserHost_Id, Query_time, Lock_time, Rows_sent, Rows_examined, Other
    | sort Query_time desc

    ```

    ```sql
    # fields @timestamp, @message, @logStream
    #     #| filter @logStream = "paymentgateway-prod-dbwrite"
    #     | parse  "* Query_time: * Lock_time: * Rows_sent: * Rows_examined: * *" as Time_UserHost_Id, Query_time, Lock_time, Rows_sent, Rows_examined, Other
    #     | sort Query_time desc

    parse  "* Query_time: * Lock_time: * Rows_sent: * Rows_examined: * *" as Time_UserHost_Id, Query_time, Lock_time, Rows_sent, Rows_examined, Other
    #| sort Query_time desc, Lock_time desc, Rows_sent  desc
    | sort Lock_time asc

    ```



#---------------------------------------------

