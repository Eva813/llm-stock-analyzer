"""
LLM chain for stock trend analysis: embeds signal into prompt and queries LLM using Gemini.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import logging

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableSerializable
from langchain_core.runnables.retry import RunnableRetry
from langchain_google_genai import ChatGoogleGenerativeAI

from app.configs.config import Config, get_config
from app.services.analysis.stock_trend_pipeline import analyze_stock_trend_signal

logger = logging.getLogger(__name__)


def get_llm_client(config: Optional[Config] = None) -> ChatGoogleGenerativeAI:
    """Return ChatGoogleGenerativeAI client for stock analysis."""
    if config is None:
        config = get_config()
    
    try:
        api_key = config.gemini.api_key.get_secret_value()
        logger.info(f"Initializing Gemini client with model: {config.gemini.model}")
        logger.debug(f"API key length: {len(api_key) if api_key else 0}")
        
        # Ensure API key is clean (no extra whitespace or newlines)
        api_key = api_key.strip() if api_key else ""
        
        if not api_key:
            raise ValueError("Gemini API key is empty or not configured")
        
        return ChatGoogleGenerativeAI(
            model=config.gemini.model,
            google_api_key=api_key,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
        )
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {str(e)}")
        raise


def load_prompt_template(prompt_file: Path) -> PromptTemplate:
    """Load prompt template from file and return a PromptTemplate for stock analysis."""
    try:
        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_template_str = f.read().strip()
    except Exception:
        raise
    # Ensure prompt template contains {stock_id} and {signal_json} variables
    if (
        "{stock_id}" not in prompt_template_str
        or "{signal_json}" not in prompt_template_str
    ):
        prompt_template_str = (
            prompt_template_str
            + "\n\nStock: {stock_id}\n\nTechnical Indicators:\n```json\n{signal_json}\n```"
        )
    return PromptTemplate(
        input_variables=["stock_id", "signal_json"],
        template=prompt_template_str,
    )


def get_analysis_prompt_template(config: Optional[Config] = None) -> PromptTemplate:
    """Return stock analysis prompt template."""
    if config is None:
        config = get_config()
    return load_prompt_template(Path(config.llm.stock_analyzer_prompt_path))


def build_prompt_formatting_chain(prompt_template: PromptTemplate) -> RunnableLambda:
    """Format prompt for LLM with stock_id and signal_json."""
    import json

    def format_prompt_step(input_data: dict) -> str:
        formatted = prompt_template.format(
            stock_id=input_data["stock_id"],
            signal_json=json.dumps(input_data["signal"], ensure_ascii=False, indent=2),
        )
        return formatted

    return RunnableLambda(format_prompt_step)


def build_llm_call_chain(llm_client: Any) -> RunnableLambda:
    """Call LLM and return response text."""

    def call_llm_step(prompt: str) -> str:
        try:
            logger.info("Calling Gemini LLM...")
            logger.debug(f"Prompt length: {len(prompt)}")
            response = llm_client.invoke(prompt)
            response_text = (
                response.content if hasattr(response, "content") else str(response)
            )
            logger.info("LLM call successful")
            logger.debug(f"Response length: {len(response_text)}")
            return response_text
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            raise

    return RunnableLambda(call_llm_step)


def build_stock_signal_chain() -> RunnableLambda:
    """Chain to produce signal dict from stock_id."""

    def signal_step(stock_id: str) -> Dict[str, Any]:
        try:
            logger.info(f"Analyzing stock signal for: {stock_id}")
            signal = analyze_stock_trend_signal(stock_id)
            logger.info("Stock signal analysis completed")
            return {"stock_id": stock_id, "signal": signal}
        except Exception as e:
            logger.error(f"Stock signal analysis failed for {stock_id}: {str(e)}")
            raise

    return RunnableLambda(signal_step)


def build_json_output_parsing_chain() -> RunnableLambda:
    """Parse LLM response as JSON."""

    def parse_response_step(response_text: str) -> dict:
        parser = JsonOutputParser()
        return parser.parse(response_text)

    return RunnableLambda(parse_response_step)


def build_stock_analysis_chain(
    llm_client: Any, prompt_template: PromptTemplate
) -> RunnableSerializable:
    """Full chain: stock_id → signal → prompt → LLM → JSON parse."""
    return (
        build_stock_signal_chain()
        | build_prompt_formatting_chain(prompt_template)
        | build_llm_call_chain(llm_client)
        | build_json_output_parsing_chain()
    )


def build_stock_analysis_chain_with_retry(
    llm_client: Any, prompt_template: PromptTemplate, config: Optional[Config] = None
) -> RunnableSerializable:
    """Full chain with retry: stock_id → signal → prompt → LLM → JSON parse (with retry)."""
    if config is None:
        config = get_config()
    base_chain = build_stock_analysis_chain(llm_client, prompt_template)
    return RunnableRetry(bound=base_chain, max_attempt_number=config.llm.retry)
