# Global instructions (Information Extraction → Instructions box)

Paste this into the agent's **Instructions** field. It maps to the `ai_extract`
`options => map('instructions', ...)` argument and applies to every field.

```
These are retail loan sanction / welcome letters from Indian NBFCs and banks.
Extract only what the document states; if a field is absent, return null and never
invent a value. Money fields: strip 'Rs', 'Rs.', the rupee symbol and thousands
separators, and return a plain number. Dates: output ISO YYYY-MM-DD regardless of the
source format (for example '3rd-July-2025' and '03-Jul-2025' both become 2025-07-03).
emi_due_day: return the integer day of month from ordinal phrasing such as '5th of
every month'. interest_rate_pa: return the numeric percentage only and drop the '%pa'
suffix. Extract PII fields verbatim; masking is handled downstream.
```
