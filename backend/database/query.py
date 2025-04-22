# SQL query to fetch proportioning data
query_proportionings = """
SELECT 
    amadeus_proportioning.proportioning_dbid AS "ProportioningDBID", 
    amadeus_proportioning.article_dbid AS "ArticleDBID", 
    amadeus_proportioning.lot_dbid AS "LotDBID", 
    amadeus_proportioning.has_vms_data AS "VMSscan", 
    amadeus_article.article_id AS "ArticleID", 
    amadeus_article.name AS "ArticleName", 
    amadeus_lot.lot_id AS "LotID", 
    amadeus_proportioningrecord.requestedamount AS "Requested", 
    amadeus_proportioningrecord.actualamount AS "Actual", 
    amadeus_proportioningrecord.start_time AS "StartTime", 
    amadeus_proportioningrecord.end_time AS "EndTime", 
    amadeus_proportioningrecord.box_id AS "MixBoxID", 
    amadeus_proportioningrecord.ingredientboxid AS "IngBoxID", 
    amadeus_proportioningrecord.proportioninglocation AS "DosingLocation", 
    amadeus_loggingparam.if_in_typeofdosing AS "TypeOfDosing" 
FROM amadeus_proportioning 
JOIN amadeus_proportioningrecord ON amadeus_proportioning.proportioning_dbid = amadeus_proportioningrecord.proportioning_dbid 
JOIN amadeus_loggingparam ON amadeus_proportioning.proportioning_dbid = amadeus_loggingparam.proportioning_dbid 
JOIN amadeus_article ON amadeus_proportioning.article_dbid = amadeus_article.article_dbid 
JOIN amadeus_lot ON amadeus_proportioning.lot_dbid = amadeus_lot.lot_dbid
ORDER BY amadeus_proportioning.proportioning_dbid DESC 
"""