# SQL query to fetch proportioning data
query_proportionings= """
SELECT 
    amadeus_proportioning.proportioning_dbid AS "ProportioningDBID",
    amadeus_proportioning.article_dbid AS "ArticleDBID",
    amadeus_proportioning.lot_dbid AS "LotDBID",
    amadeus_proportioning.hAS_vms_data AS "VMSscan",  
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
    amadeus_loggingparam.if_in_typeofdosing AS "TypeOfDosing", 
    amadeus_proportioningrecord.requiredtolerance AS "Tolerance", 
    amadeus_proportioningrecord.manufacturingorderid AS "OrderID"
FROM amadeus_proportioning 
JOIN amadeus_proportioningrecord ON amadeus_proportioning.proportioning_dbid = amadeus_proportioningrecord.proportioning_dbid 
JOIN amadeus_loggingparam ON amadeus_proportioning.proportioning_dbid = amadeus_loggingparam.proportioning_dbid 
JOIN amadeus_article ON amadeus_proportioning.article_dbid = amadeus_article.article_dbid 
JOIN amadeus_lot ON amadeus_proportioning.lot_dbid = amadeus_lot.lot_dbid
ORDER BY amadeus_proportioning.proportioning_dbid DESC;
"""
# SQL query to fetch Analyzer Summary data
query_analyzer_summary = """
SELECT 
    amadeus_proportioning.proportioning_dbid AS "ProportioningDBID",
    amadeus_article.name AS "ArticleName",
    amadeus_lot.lot_id AS "LotID",
    amadeus_proportioning.lot_dbid AS "LotDBID",
    amadeus_proportioningrecord.start_time AS "Dosing Date",
    amadeus_loggingparam.if_in_typeofdosing AS "DosigType", 
    amadeus_proportioningrecord.proportioninglocation AS "DosingLocation", 
    amadeus_proportioningrecord.requestedamount AS "Requested", 
    amadeus_proportioningrecord.actualamount AS "Actual",
    amadeus_proportioningrecord.requiredtolerance AS "Tolerance", 
    amadeus_loggingparam.c1_in_gain AS "Gain",
	amadeus_loggingparam.if_in_source_netweight AS "Source Box NetWeight"
FROM amadeus_proportioning 
JOIN amadeus_proportioningrecord ON amadeus_proportioning.proportioning_dbid = amadeus_proportioningrecord.proportioning_dbid 
JOIN amadeus_loggingparam ON amadeus_proportioning.proportioning_dbid = amadeus_loggingparam.proportioning_dbid 
JOIN amadeus_article ON amadeus_proportioning.article_dbid = amadeus_article.article_dbid 
JOIN amadeus_lot ON amadeus_proportioning.lot_dbid = amadeus_lot.lot_dbid
WHERE amadeus_proportioning.proportioning_dbid = {current_prop};
"""
# SQL query to fetch Analyzer PropRecord data
query_analyzer_propRecord = """
SELECT * FROM public.amadeus_proportioningrecord
JOIN public.amadeus_proportioning ON amadeus_proportioning.proportioning_dbid = amadeus_proportioningrecord.proportioning_dbid
WHERE amadeus_proportioning.proportioning_dbid = {current_prop};
"""
# SQL query to fetch Analyzer LogginParam data
query_analyzer_logginParam = """
SELECT * FROM public.amadeus_loggingparam
JOIN public.amadeus_proportioning ON amadeus_loggingparam.proportioning_dbid = amadeus_proportioning.proportioning_dbid
WHERE amadeus_proportioning.proportioning_dbid = {current_prop};
"""
# SQL query to fetch Analyzer Lot data
query_analyzer_lot = """
SELECT * 
FROM public.amadeus_lot
WHERE article_dbid = (
    SELECT article_dbid 
    FROM public.amadeus_proportioning 
    WHERE proportioning_dbid = {current_prop});

"""

# SQL query to fetch Analyzer Article data
query_analyzer_article = """
SELECT * 
FROM public.amadeus_article
WHERE article_dbid = (
    SELECT article_dbid 
    FROM public.amadeus_proportioning 
    WHERE proportioning_dbid = {current_prop});
 """

#SQL query to fetch Analyzer Graph
query_analyzer_slide_graph= """
SELECT 
    plant_out_slideposition, dc_out_desiredslideposition, logging_dbid, if_out_dosedweight ,dc_out_controlvibrator, dc_out_controlknocker 
    FROM 
    amadeus_logging WHERE proportioning_dbid =  {current_prop} ;
"""

#SQL query to fetch Regressor Graph
query_regressor_graph = """
SELECT
intermediate_dbid, measurement_time, flow, opening
FROM public.amadeus_intermediates
Where lot_dbid = 32;
"""