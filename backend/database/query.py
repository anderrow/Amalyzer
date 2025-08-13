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
ORDER BY amadeus_proportioning.proportioning_dbid DESC
LIMIT 1000;"""
# SQL query to fetch proportioning FILTER data
query_proportionings_filter= """
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
{where_clause}
ORDER BY amadeus_proportioning.proportioning_dbid DESC
LIMIT 5000;"""
# SQL query to fetch Analyzer Summary data
query_analyzer_summary = """
SELECT 
    amadeus_proportioning.proportioning_dbid AS "ProportioningDBID",
    amadeus_article.name AS "ArticleName",
    amadeus_lot.lot_id AS "LotID",
    amadeus_proportioning.lot_dbid AS "LotDBID",
    amadeus_proportioning.proportioning_status as "Status",
    amadeus_proportioningrecord.start_time AS "Dosing Date",
    amadeus_proportioningrecord.end_time AS "Duration", 
    amadeus_proportioningrecord.proportioninglocation AS "DosingLocation", 
    amadeus_proportioningrecord.requestedamount AS "Requested",
    amadeus_loggingparam.if_in_typeofdosing AS "Type Of Dosing", 
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
# SQL query, Valuable information about the PropID
query_valuable_information = """
SELECT 
    amadeus_article.name AS "ArticleName",
    amadeus_lot.lot_id AS "LotID"
FROM amadeus_proportioning 
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
WHERE lot_dbid = (
    SELECT lot_dbid 
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
    plant_out_slideposition, dc_out_desiredslideposition, dc_out_controlvibrator, dc_out_controlknocker 
    FROM 
    amadeus_logging WHERE proportioning_dbid =  {current_prop} ;
"""
#SQl query to fetch Analyzer Graph2 (Dosed Material)
query_analyzer_dosed_material= """
SELECT 
    if_out_dosedweight
    FROM 
    amadeus_logging WHERE proportioning_dbid =  {current_prop} ;
"""
#SQL query to fetch Analyzer Graph3 (Flow)
query_analyzer_flow= """
SELECT 
    dc_out_desiredflow,dc_out_expectedflow, f_out_filteredflow2 
    FROM 
    amadeus_logging WHERE proportioning_dbid =  {current_prop} ;
"""
#SQL query to fetch Regressor Graph
query_regressor_graph = """
SELECT
intermediate_dbid, measurement_time, flow, opening
FROM public.amadeus_intermediates
WHERE lot_dbid = {current_lot};
"""

#SQL query to request lot db id from a proportioning db id
query_lot_db_id = """
SELECT lot_dbid FROM public.amadeus_proportioning
WHERE proportioning_dbid = {current_prop};
"""
#SQL query to request Regression table
query_regression_table = """
SELECT 
     lot_id, lot_dbid, c2_in_flowtablequality, c2_in_measureddensity, c2_in_angleofrepose,c2_in_oscillationfactor,
     c2_in_oscillationmin ,c2_in_oscillationspeed, c1_in_minflow, c1_in_maxflow 
    FROM public.amadeus_lot
WHERE lot_dbid = {current_lot}
"""
#SQL query to request VMS data
query_vms_data = """
SELECT proportioning_dbid, sensor_l, sensor_m, sensor_r 
    FROM public.amadeus_vms_logging
	where proportioning_dbid = 	{current_prop}
	ORDER BY vms_logging_dbid ASC
"""
query_vms_parameters = """
SELECT offset_l_x, offset_l_y, offset_m_x, offset_m_y, offset_r_x, offset_r_y  
    FROM public.amadeus_vms_param
    where proportioning_dbid = {current_prop}
"""