CloudWatch log insights : `*[CloudWatch log insights|link]*`

ex:
*[CloudWatch Log Insights|https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:logs-insights$3FqueryDetail$3D~(end~'2026-02-16T05*3a55*3a00.000Z~start~'2026-02-15T12*3a40*3a00.000Z~timeType~'ABSOLUTE~tz~'UTC~editorString~'fields*20*20*40timestamp*2c*20*40message*2c*20path*2c*20requestId*2c*20ip*2c*20caller*2c*20user*2c*20requestTime*2c*20httpMethod*2c*20resourcePath*2c*20status*2c*20protocol*2c*20responseLength*2c*20accessKey*0a*0a*20*20*20*20*0a*20*20*20*20*7c*20filter*20*40message*20like*20*2f*28*22status*22*3a*225*29*2f*0a*0a*20*20*20*20*0a*20*20*20*20*7c*20stats*20count*28*2a*29*20as*20Count*20by*20httpMethod*2c*20resourcePath*2c*20status*0a*0a*0a*20*20*20*20*7c*20filter*20*21isempty*28status*29*0a*0a*20*20*20*20*7c*20sort*20Count*20desc*0a*20*20*20*20*0a*20*20*20*20*7c*20limit*2010000~queryId~'6c584ad0-336a-47aa-9b0d-15756d9848fd~source~(~'API-Gateway-Access-Logs_etmsu5l0ak*2fprod)~lang~'CWLI~logClass~'STANDARD~queryBy~'logGroupName)]*


*[Sample CloudWatch Log:|https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:logs-insights$3FqueryDetail$3D~(end~'2026-02-16T05*3a55*3a00.000Z~start~'2026-02-15T12*3a40*3a00.000Z~timeType~'ABSOLUTE~tz~'UTC~editorString~'fields*20*20*40timestamp*2c*20*40message*2c*20path*2c*20requestId*2c*20ip*2c*20caller*2c*20user*2c*20requestTime*2c*20httpMethod*2c*20resourcePath*2c*20status*2c*20protocol*2c*20responseLength*2c*20accessKey*0a*0a*20*20*20*20*0a*20*20*20*20*7c*20filter*20*40message*20like*20*2f*28*22status*22*3a*225*29*2f*0a*0a*20*20*20*20*0a*20*20*20*20*7c*20stats*20count*28*2a*29*20as*20Count*20by*20httpMethod*2c*20resourcePath*2c*20status*0a*0a*0a*20*20*20*20*7c*20filter*20*21isempty*28status*29*0a*0a*20*20*20*20*7c*20sort*20Count*20desc*0a*20*20*20*20*0a*20*20*20*20*7c*20limit*2010000~queryId~'6c584ad0-336a-47aa-9b0d-15756d9848fd~source~(~'API-Gateway-Access-Logs_etmsu5l0ak*2fprod)~lang~'CWLI~logClass~'STANDARD~queryBy~'logGroupName)]*








errors.0.httpStatusCode | errors.1.httpStatusCode	errors.0.description | errors.1.description	 errors.0.externalErrorCode | errors.1.externalErrorCode	applicationName


errors.0.httpStatusCode     errors.0.description            errors.0.externalErrorCode      applicationName



--------------------------------------------------------------------------------------------------------------------------------
1. PaymentGateway-prod-Payment-Token-Microservice-Exceptions|Communications link failure

This ticket is created to record the exceptions of PaymentGateway-prod-Payment-Token-Microservice-Exceptions on 2026-04-15T00:00:00 UTC to 2026-04-16T19:00:00 UTC in our AWS console.

Analysis:
Time:   2026-04-15T00:00:00 UTC to 2026-04-16T19:00:00 UTC 

Please find the table below:
Sno	        Error type	                Cause	                                                                                     Count
1	        Communications link failure	Caused by: com.mysql.cj.jdbc.exceptions.CommunicationsException: Communications link failure
                                        Caused by: com.mysql.cj.exceptions.CJCommunicationsException: Communications link failure	  56



aws link-1: CloudWatch Log Insights

https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:logs-insights$3FqueryDetail$3D~(end~'2026-04-16T19*3a00*3a00.000Z~start~'2026-04-15T00*3a00*3a00.000Z~timeType~'ABSOLUTE~tz~'UTC~editorString~'fields*20*40timestamp*2c*20*40message*2c*20*40logStream*2c*20*40log*0a*23*7c*20filter*20*40message*20like*20*27Communications*20link*20failure*27*23140*0a*23*7c*20filter*20*40message*20like*20*2f*28Exception*7cError*7cFail*7ctimed*20out*29*2f*0a*0a*7c*20filter*20*40message*20like*20*27Caused*20by*3a*20com.mysql.cj.jdbc.exceptions.CommunicationsException*3a*20Communications*20link*20failure*27*2356*0a*23*7c*20filter*20*40message*20like*20*27Caused*20by*3a*20com.mysql.cj.exceptions.CJCommunicationsException*3a*20Communications*20link*20failure*27*23*2056*0a*23*7c*20filter*20*40message*20like*20*27ERROR*20o.h.engine.jdbc.spi.SqlExceptionHelper*20*3a*20Communications*20link*20failure*27*20*2328*0a*23*7c*20filter*20*40message*20like*20*27Caused*20by*3a*20java.net.ConnectException*3a*20Connection*20timed*20out*27*0a*0a*23*7c*20filter*20*40message*20like*20*27Caused*20by*3a*20org.hibernate.exception.JDBCConnectionException*3a*20Unable*20to*20acquire*20JDBC*20Connection*27*0a*23*7c*20filter*20*40message*20like*20*27Caused*20by*3a*20java.net.ConnectException*3a*20Connection*20timed*20out*20*28Connection*20timed*20out*29*27*0a*7c*20sort*20*40timestamp*20desc*0a*7c*20limit*2010000~queryId~'d00f0be4-a125-4817-98c1-605cb0e2f11e~source~(~'*2faws*2flambda*2fPaymentGateway-prod-Payment-Token-Microservice)~lang~'CWLI~logClass~'STANDARD~queryBy~'logGroupName)


Sample CloudWatch Log:




While reviewing the CloudWatch logs, we observed that the Payment‑Token‑Microservice Lambda failed, the Lambda attempted to initiate a database transaction; however, it was unable to establish a connection with the MySQL database. The database driver reported a “Communications link failure”, followed by a connection timeout, indicating that the database server did not respond. This is explicitly indicated by the following log entries:

ERROR o.h.engine.jdbc.spi.SqlExceptionHelper : Communications link failure
SQLState: 08S01
As a consequence of this connectivity failure, the Lambda was unable to open the JPA EntityManager, which led to a JDBCConnectionException and subsequently a CannotCreateTransactionException. Due to this failure, the request processing was aborted, and the Payment‑Token‑Microservice returned a 500 Internal Server Error.

Reason: Database connectivity failure, the Lambda was unable to connect to the MySQL database due to a connection timeout

---------------

2. tigo-cognito-prod-master-Monitoring-6I7LSTA3KZJH-DARApiGateway4XXErrorAlarm-1RU6CTB3HN9ZJ

This ticket is created to record the errors/exceptions of tigo-cognito-prod-master-Monitoring-6I7LSTA3KZJH-DARApiGateway4XXErrorAlarm-1RU6CTB3HN9ZJ on 2026-03-24T03:55:00 UTC to 2026-03-24T07:40:00 UTC in our AWS console.


Analysis:
Time:  2026-03-24T03:55:00 UTC to 2026-03-24T07:40:00 UTC

While checking the CloudWatch Logs of 4xx Errors, more numbers of errors throw on the lambda "TigoID-Functional-API-prod "

Please find the below table for your reference:
httpMethod	      resourcePath	                apiKey	     status	  count
POST	          /v4/public/auth/login/phone	****bzP8PB	 400	  432511

CloudWatch Log Insights:
https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:logs-insights$3FqueryDetail$3D~(end~'2026-03-24T07*3a40*3a00.000Z~start~'2026-03-24T03*3a55*3a00.000Z~timeType~'ABSOLUTE~tz~'UTC~editorString~'fields*20*20*40timestamp*2c*20*40message*2c*20apiKey*2c*20requestId*2c*20ip*2c*20requestTime*2c*20httpMethod*2c*20resourcePath*2c*20status*2c*20protocol*2c*20responseLength*0a*0a*20*20*20*20*23*7c*20filter*20*28status*20*3e*3d*20400*20and*20status*20*3c*20500*29*20or*20*28status*20*3e*3d*20500*20and*20status*20*3c*20600*29*0a*20*20*20*20*23*7c*20filter*20*40message*20like*20*2f*28*22status*22*3a*224*7c*22status*22*3a*225*29*2f*0a*20*20*20*20*7c*20filter*20*40message*20like*20*2f*28*22status*22*3a*224*29*2f*0a*0a*20*20*20*20*23*7c*20stats*20count*28*2a*29*20as*20Count*20by*20bin*281d*29*20as*20Date*2c*20apiKey*2c*20requestId*2c*20ip*2c*20requestTime*2c*20httpMethod*2c*20resourcePath*2c*20status*2c*20protocol*2c*20responseLength*0a*20*20*20*20*23*7c*20stats*20count*28*2a*29*20as*20Count*20by*20bin*281d*29*20as*20Date*2c*20httpMethod*2c*20resourcePath*2c*20status*2c*20apiKey*0a*20*20*20*20*7c*20stats*20count*28*2a*29*20as*20Count*20by*20httpMethod*2c*20resourcePath*2c*20apiKey*2c*20status*0a*0a*20*20*20*20*7c*20filter*20*21isempty*28status*29*0a*0a*20*20*20*20*7c*20sort*20Count*20desc*0a*20*20*20*20*23*7c*20sort*20by*20resourcePath*2c*20httpMethod*2c*20status*0a*20*20*20*20*23*7c*20sort*20by*20httpMethod*2c*20resourcePath*2c*20status*0a*0a*20*20*20*20*7c*20limit*2010000~queryId~'54317473b9ef4b9-84af276-49c153-1e527b-7d64bfa6f13e3838543a1e45~source~(~'API-Gateway-Access-Logs_x05o36zvli*2fprod)~lang~'CWLI~logClass~'STANDARD~queryBy~'logGroupName)


Based on our investigation, we could see OTP login flow initialized correctly, then failed at external billing sync due to missing/expired auth token and a config fallback. 

error Code: EXTERNAL-APIS:BILLING-SYSTEM-GET-ACCOUNTS-API-RETURNED-NON-TIGO-NUMBER
error Details: "Billing system get accounts api returned given msisdn as non tigo number."

CloudWatch Log Insights:
https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:logs-insights$3FqueryDetail$3D~(end~'2026-03-24T07*3a40*3a00.000Z~start~'2026-03-24T03*3a55*3a00.000Z~timeType~'ABSOLUTE~tz~'UTC~editorString~'fields*20*40timestamp*2c*20*40message*2c*20*40logStream*0a*20*20*20*20*7c*20filter*20statusCode*20*3e*3d*20400*20AND*20statusCode*20*3c*20500*0a*20*20*20*20*20*20*20*20and*20*40message*20like*20*27POST*3a*2fv4*2fpublic*2fauth*2flogin*2fphone*27*0a*20*20*20*20*20*20*20*20and*20*20*40message*20not*20like*20*27POST*3a*2fv4*2fpublic*2fauth*2flogin*2fphone*2fhe*27*0a*20*20*20*20*20*20*20*20and*20*40message*20like*20*2fBilling*20system*20get*20accounts*20api*20returned*20given*20msisdn*20as*20non*20tigo*20number.*2f*0a*20*20*20*20*20*20*20*20and*20*40message*20like*20*2fEXTERNAL-APIS*3aBILLING-SYSTEM-GET-ACCOUNTS-API-RETURNED-NON-TIGO-NUMBER*2f*0a*20*20*20*20*20*20*20*20*23and*20*40message*20like*20*2fSomething*20went*20wrong*2c*20please*20try*20after*20some*20time*2f*0a*0a*20*20*20*20*7c*20sort*20*40timestamp*20desc*0a*20*20*20*20*7c*20limit*2010000~queryId~'54317473b9ef4b9-84af276-49c153-1e527b-7d64bfa6f13e3838543a1e45~source~(~'*2faws*2flambda*2fTigoID-Functional-API-prod)~lang~'CWLI~logClass~'STANDARD~queryBy~'logGroupName)




Analysis:
Time:  2026-03-24T03:55:00 UTC to 2026-03-24T07:40:00 UTC
Based on our investigation, while reviewing the CloudWatch Logs for 4xx errors, we observed a higher frequency of errors originating from the Lambda function "TigoID-Functional-API-prod" and we could see OTP login flow initialized correctly, then failed at external billing sync due to missing/expired auth token and a config fallback.

error Code: EXTERNAL-APIS:BILLING-SYSTEM-GET-ACCOUNTS-API-RETURNED-NON-TIGO-NUMBER
error Details: "Billing system get accounts api returned given msisdn as non tigo number."

Method	 path	                    creationChannel	 apiKey	      country	api_key_name	                    api_key_app_group
 POST	/v4/public/auth/login/phone	oneapp	         ****bzP8PB	  CO	    ak-oneapp-prd-public-dar-api-co-3	oneapp
Please verify from your end and confirm whether this is the expected behavior. Additionally, let us know if you need any further information.

CC: Shital Chavan, Akash Gohel, Khajamohiyoddin Valsangkar,  Ankit Saxena


3. tigo-cognito-prod-master-Monitoring-6I7LSTA3KZJH-DARApiGateway4XXErrorAlarm-1RU6CTB3HN9ZJ|/v4/trusted/users|429

Analysis:
Time:    2026-05-07T01:10:00 UTC to 2026-05-07T01:45:00 UTC

Based on our investigation, we can see that API key exceeded the allowed request rate for /v4/trusted/users, which triggered API throttling (slowing or blocking request when it comes too fast) and resulted in HTTP 429 (Too Many Request). Here the affected country is GT

Method	resourcePath	    creationChannel	 maskedApiKey	 country	api_key_name	   api_key_channel	    api_key_app_group
 GET	/v4/trusted/users	oneapp	         ****D7CbMn	     GT	        ak-oneapp-prd-trusted-dar-api-gt	oneapp-prd-trusted-dar-api-gt	  oneapp
Please verify from your end and confirm whether this is the expected behavior. Additionally, let us know if you need any further information.

----------------------------
4. 

CC: @Roman Piñango , @ShitalC hexaware , @khajamohiyoddinv hexaware , @ShalinShalinS hexaware , @AnkitS4@hexaware.com , @NihalN hexaware  