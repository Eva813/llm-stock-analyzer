# FastAPI API endpoints
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.internal.llm.chain import (
    build_stock_analysis_chain_with_retry,
    get_analysis_prompt_template,
    get_llm_client,
)

router = APIRouter()
logger = logging.getLogger(__name__)


class StockAnalysisRequest(BaseModel):
    stock_id: str


class StockAnalysisResponse(BaseModel):
    stock_id: str
    suggestion: str
    reason: str
    reason_zh_tw: str


@router.post("/stock/llm-report", response_model=StockAnalysisResponse)
async def get_stock_llm_report(request: StockAnalysisRequest):
    """
    Generate a stock analysis report using LLM based on technical indicators.
    Returns a clear, actionable trading suggestion and rationale.
    """
    logger.info(f"Starting LLM analysis for stock: {request.stock_id}")
    
    try:
        # Initialize components
        logger.info("Initializing LLM client...")
        llm_client = get_llm_client()
        
        logger.info("Loading prompt template...")
        prompt_template = get_analysis_prompt_template()
        
        logger.info("Building analysis chain...")
        chain = build_stock_analysis_chain_with_retry(llm_client, prompt_template)
        
        # Execute chain
        logger.info("Executing analysis chain...")
        llm_result = await chain.ainvoke(request.stock_id)
        
        logger.info("Analysis completed successfully")
        
        # Ensure the response is in the expected JSON format
        response = StockAnalysisResponse(
            stock_id=llm_result.get("stock_id", request.stock_id),
            suggestion=llm_result.get("suggestion", ""),
            reason=llm_result.get("reason", ""),
            reason_zh_tw=llm_result.get("reason_zh_tw", ""),
        )
        
        logger.info(f"Returning response for {request.stock_id}")
        return response
        
    except Exception as e:
        logger.error(f"LLM analysis failed for {request.stock_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")
