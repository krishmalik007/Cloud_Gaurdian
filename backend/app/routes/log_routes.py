"""
Cloud Guardian — Log Ingestion & Query Routes.

REST endpoints for ingesting cloud logs, querying indexed logs,
and retrieving dashboard data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.auth_handler import get_current_user
from app.correlation.correlation_engine import correlation_engine
from app.logger import logger
from app.models.log_models import LogIngestionRequest, LogIngestionResponse, NormalizedLog
from app.normalizer.log_normalizer import log_normalizer
from app.parser.log_parser import log_parser
from app.risk.risk_engine import risk_scoring_engine
from app.services.opensearch_service import opensearch_service

router = APIRouter(prefix="/logs", tags=["Log Management"])

OPENSEARCH_INDEX = "cloud-guardian-logs"


@router.post(
    "/ingest",
    response_model=LogIngestionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest cloud security logs",
)
async def ingest_logs(request: LogIngestionRequest, current_user: dict = Depends(get_current_user)):
    """
    Ingest raw cloud logs. Logs are parsed, normalized, correlated,
    risk-scored, and indexed into OpenSearch.

    Supports:
    - AWS CloudTrail (`cloudtrail`)
    - AWS VPC Flow Logs (`vpc_flow`)
    - Azure Activity Logs (`azure_activity`)
    """
    processed_ids = []
    failed_count = 0

    for raw_log in request.logs:
        try:
            # 1. Parse raw log
            parsed = log_parser.parse(request.log_type, raw_log)

            # 2. Normalize to standard schema
            normalized = log_normalizer.normalize(parsed)

            # 3. Correlate — check for attack patterns
            incidents = correlation_engine.correlate(normalized)
            correlation_boost = sum(inc.get("severity_boost", 0) for inc in incidents)

            if incidents:
                normalized.correlation_id = incidents[0]["incident_id"]

            # 4. Risk score
            normalized.risk_score = risk_scoring_engine.score(normalized, correlation_boost=correlation_boost)

            # 5. Index into OpenSearch
            try:
                opensearch_service.index_document(
                    index=OPENSEARCH_INDEX,
                    body=normalized.model_dump(mode="json"),
                    doc_id=normalized.log_id,
                )
            except Exception as e:
                logger.warning(f"OpenSearch indexing failed (non-critical): {e}")

            processed_ids.append(normalized.log_id)

        except Exception as e:
            logger.error(f"Failed to process log: {e}")
            failed_count += 1

    logger.info(
        f"Ingestion complete: {len(processed_ids)} processed, {failed_count} failed | "
        f"user={current_user['username']}"
    )

    return LogIngestionResponse(
        status="completed",
        processed=len(processed_ids),
        failed=failed_count,
        log_ids=processed_ids,
    )


@router.get(
    "/search",
    summary="Search indexed logs",
)
async def search_logs(
    q: str = Query(default="*", description="Search query string"),
    severity: str | None = Query(default=None, description="Filter by severity (Low, Medium, High, Critical)"),
    cloud_provider: str | None = Query(default=None, description="Filter by cloud provider (AWS, Azure)"),
    limit: int = Query(default=50, ge=1, le=500, description="Maximum results"),
    current_user: dict = Depends(get_current_user),
):
    """
    Search indexed logs in OpenSearch with optional filters.
    """
    must_clauses = []

    if q and q != "*":
        must_clauses.append({"query_string": {"query": q}})

    if severity:
        must_clauses.append({"match": {"severity": severity}})

    if cloud_provider:
        must_clauses.append({"match": {"cloud_provider": cloud_provider}})

    query = {
        "size": limit,
        "sort": [{"timestamp": {"order": "desc"}}],
        "query": {
            "bool": {
                "must": must_clauses if must_clauses else [{"match_all": {}}]
            }
        },
    }

    try:
        results = opensearch_service.search(index=OPENSEARCH_INDEX, query=query)
        hits = results.get("hits", {}).get("hits", [])
        return {
            "total": results.get("hits", {}).get("total", {}).get("value", 0),
            "results": [hit["_source"] for hit in hits],
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")


@router.get(
    "/stats",
    summary="Get log statistics for dashboard",
)
async def get_stats(current_user: dict = Depends(get_current_user)):
    """
    Get aggregated log statistics for the dashboard.
    Returns counts by severity, cloud provider, and event category.
    """
    query = {
        "size": 0,
        "aggs": {
            "by_severity": {"terms": {"field": "severity.keyword"}},
            "by_provider": {"terms": {"field": "cloud_provider.keyword"}},
            "by_category": {"terms": {"field": "event_category.keyword"}},
            "avg_risk_score": {"avg": {"field": "risk_score"}},
            "high_risk_count": {
                "filter": {"range": {"risk_score": {"gte": 70}}}
            },
        },
    }

    try:
        results = opensearch_service.search(index=OPENSEARCH_INDEX, query=query)
        aggs = results.get("aggregations", {})

        return {
            "total_logs": results.get("hits", {}).get("total", {}).get("value", 0),
            "by_severity": {
                b["key"]: b["doc_count"]
                for b in aggs.get("by_severity", {}).get("buckets", [])
            },
            "by_provider": {
                b["key"]: b["doc_count"]
                for b in aggs.get("by_provider", {}).get("buckets", [])
            },
            "by_category": {
                b["key"]: b["doc_count"]
                for b in aggs.get("by_category", {}).get("buckets", [])
            },
            "avg_risk_score": round(aggs.get("avg_risk_score", {}).get("value", 0) or 0, 2),
            "high_risk_count": aggs.get("high_risk_count", {}).get("doc_count", 0),
        }
    except Exception as e:
        logger.error(f"Stats query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {e}")


@router.get(
    "/correlation/rules",
    summary="List all correlation rules",
)
async def list_correlation_rules(current_user: dict = Depends(get_current_user)):
    """Return all active correlation rules."""
    return {"rules": correlation_engine.rules}
