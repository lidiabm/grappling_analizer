from pydantic import BaseModel


class FighterEvolutionRequest(BaseModel):
    old_analysis: dict
    new_analysis: dict


class FighterEvolutionResponse(BaseModel):
    summary: str
    improvements: list[str]
    regressions: list[str]
    stablePatterns: list[str]
    technicalEvolution: str
    tacticalEvolution: str
    recommendedFocus: list[str]
    conclusion: str