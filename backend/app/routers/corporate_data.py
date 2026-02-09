"""Corporate data API endpoints."""
from fastapi import APIRouter, HTTPException
from ..models.corporate import CorporateDataResponse
from ..services.corporate_service import fetch_all_corporate_data

router = APIRouter(prefix="/api/corporate-data", tags=["Corporate Data"])


@router.get("/{ticker}", response_model=CorporateDataResponse)
async def get_corporate_data(ticker: str):
    """Fetch corporate communications (earnings, press releases, news) for a ticker."""
    ticker = ticker.upper()

    docs = await fetch_all_corporate_data(ticker)

    if not docs:
        raise HTTPException(
            status_code=404,
            detail=f"No corporate data found for {ticker}. Check FMP_API_KEY.",
        )

    return CorporateDataResponse(
        ticker=ticker,
        documents=docs,
        total=len(docs),
    )
