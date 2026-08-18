example:

URL: [+*https://*|https://%2A/]{baseUrl}/pg/reports?reportName={reportName}&countryCode={countryCode}&reconciliationDate={reconcillationDate}

Ex: *+[https://]

{baseUrl}
+*/pg/reports?reportName=BO-PaymentTokens&countryCode=BO&reconciliationDate=2025-11-14

For generate all different country report you need date wise Api call as per below are parameters for API for reconciliation date you can pass any of date like (YYYY-mm-dd) format, which store in particular month folder as reconciliation date mentioned

Sr No	RepoertName	Country code	Reconciliation Date
1	BO-Enrollments	BO	2025-11-14
2	CO-Enrollments	CO	2025-11-15
3	CR-Enrollments	CR	2025-11-16
4	GT-Enrollments	GT	2025-11-17
5	HN-Enrollments	HN	2025-11-18
6	NI-Enrollments	NI	2025-11-19
7	PA-Enrollments	PA	2025-11-20
8	PY-Enrollments	PY	2025-11-21
9	SV-Enrollments	SV	2025-11-22
10	BO-PaymentTokens	BO	2025-11-23
11	CO-PaymentTokens	CO	2025-11-24
12	CR-PaymentTokens	CR	2025-11-25
13	GT-PaymentTokens	GT	2025-11-26
14	HN-PaymentTokens	HN	2025-11-27
15	NI-PaymentTokens	NI	2025-11-28
16	PA-PaymentTokens	PA	2025-11-29
17	PY-PaymentTokens	PY	2025-11-30
18	SV-PaymentTokens	SV	2025-12-01



1. Apt-Gateway path:  API Gateway->APIs->PaymentGateway-prod (etmsu5l0ak)->/->/pg->/reports->GET
   
   - Later go to `Test`

2. In the query string we need to pass under `Test method`

   ``
   reportName=BO-PaymentTokens&countryCode=BO&reconciliationDate=2025-11-14

   ``
   - Later click on `Test` button
   - Later we need to check `Satus` --> 200 (Then it is successful)
                                        504 (Timeout) but no problem the report will generate

            Other than these codes if we get anything then we need to inform Pratik(PG related)

3. Later go the path which they given 
ex: https://us-east-1.console.aws.amazon.com/s3/buckets/paymentgateway-billingsystem-v2-prod?region=us-east-1

