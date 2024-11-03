from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
import dateparser
import uvicorn

app = FastAPI(
  title="French Date Parser API",
  description="API to extract due dates and completion dates from French text",
  version="1.0.0"
)

class TextInput(BaseModel):
  text: str

class DateResponse(BaseModel):
  due_date: Optional[datetime]
  completion_date: Optional[datetime]

def parse_french_dates(text: str) -> Dict[str, Optional[datetime]]:
  """
  Parse French text to extract due dates and completion dates.
  Returns a dictionary containing the extracted dates.
  """
  settings = {
      'TIMEZONE': 'Europe/Paris',
      'RETURN_AS_TIMEZONE_AWARE': True,
      'PREFER_DATES_FROM': 'future',
      'LANGUAGES': ['fr']
  }
  
  due_indicators = [
      "à faire avant", "à rendre avant", "date limite", "échéance", 
      "deadline", "dû pour", "à remettre le", "pour le"
  ]
  
  completion_indicators = [
      "terminé le", "fini le", "complété le", "achevé le",
      "fait le", "réalisé le"
  ]
  
  result = {
      'due_date': None,
      'completion_date': None
  }
  
  text = text.lower()
  
  for indicator in due_indicators:
      if indicator in text:
          start_pos = text.find(indicator) + len(indicator)
          date_text = text[start_pos:start_pos + 50].strip()
          parsed_date = dateparser.parse(date_text, settings=settings)
          if parsed_date:
              result['due_date'] = parsed_date
              break
  
  for indicator in completion_indicators:
      if indicator in text:
          start_pos = text.find(indicator) + len(indicator)
          date_text = text[start_pos:start_pos + 50].strip()
          parsed_date = dateparser.parse(date_text, settings=settings)
          if parsed_date:
              result['completion_date'] = parsed_date
              break
  
  return result

@app.post("/parse_dates", response_model=DateResponse)
async def parse_dates(input_data: TextInput):
  try:
      result = parse_french_dates(input_data.text)
      return DateResponse(**result)
  except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
  return {"status": "healthy"}

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8080)