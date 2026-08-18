SELECT
  ROW_NUMBER() OVER (ORDER BY dt ASC, cnt DESC) AS S_NO,
  DATE_FORMAT(dt, 'yyyy-MM-dd') AS Date,
  msg AS Message,
  cnt AS Count
FROM (
  SELECT DATE_TRUNC('day', `@timestamp`) AS dt, `@message` AS msg, COUNT(*) AS cnt FROM $source
  WHERE ( (httpStatusCode BETWEEN 400 AND 499) OR (httpStatusCode BETWEEN 500 AND 599)) AND `@message` LIKE '%"errors"%'
  GROUP BY DATE_TRUNC('day', `@timestamp`), `@message`
) AS agg
ORDER BY dt ASC, cnt DESC
LIMIT 10000;

----------------------------------

--Date wise count
SELECT
  --ROW_NUMBER() OVER (ORDER BY dt ASC, cnt DESC) AS S_NO,
  DATE_FORMAT(dt, 'yyyy-MM-dd') AS Date,
  msg AS Message,
  cnt AS Count
FROM (
  SELECT DATE_TRUNC('day', `@timestamp`) AS dt, `@message` AS msg, COUNT(*) AS cnt FROM $source
  WHERE ( (httpStatusCode BETWEEN 400 AND 499) OR (httpStatusCode BETWEEN 500 AND 599)) AND `@message` LIKE '%"errors"%' AND `@message` IS NOT NULL AND LENGTH(`@message`) > 0
  GROUP BY DATE_TRUNC('day', `@timestamp`), `@message`
) AS agg
ORDER BY dt ASC, cnt DESC
LIMIT 10000;

------------------------------------
--To get all unique logs

SELECT
  `@message` AS Message,
  COUNT(*)   AS Count
FROM $source
WHERE (
        (httpStatusCode BETWEEN 400 AND 499)
     OR (httpStatusCode BETWEEN 500 AND 599)
      )
  AND `@message` LIKE '%"errors"%'
  AND `@message` IS NOT NULL
  AND LENGTH(`@message`) > 0
GROUP BY `@message`
ORDER BY Count DESC, Message ASC
LIMIT 10000;
---------------------------------------