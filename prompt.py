SYSTEM = """Given a QUESTION, ANSWER, and TABLE — return a list of key column names without which the correct answer CANNOT be derived.

## STRICT RULES:
1. Output ONLY a comma-separated list of column names. No markdown, no explanations, no extra text.
2. Column names must exactly match the original table headers (case-sensitive, spaces preserved).
3. The answer must be impossible to derive if ANY of the listed columns are removed.
4. The list should be minimal — removing any single column should make the answer impossible to derive.
5. Assume all other columns (not listed) are still present.

## CRITICAL: HANDLE CALCULATIONS AND AGGREGATIONS
- If the question asks for AVERAGE, SUM, MAX, MIN, COUNT → return the numeric column + grouping column if needed
- Example: "average number of years" → return the 'Years' column (the model can calculate average from it)
- Example: "total points" → return the 'Points' column
- Example: "how many games did X win" → return columns for filtering (e.g., 'Winner') + counting (e.g., 'Game')

## CRITICAL: HANDLE COMPARISONS AND SEQUENCES
- "higher than", "less than", "more than" → return columns for comparison values
- "next after X", "previous to X" → return ordering column (e.g., 'Date', 'Rank') + value column
- "largest", "smallest", "least", "most" → return column to compare + column to measure

## CRITICAL: HANDLE MISSING OR SIMILAR COLUMNS
- If exact column name doesn't exist, use the semantically closest column from the available headers
- For "years served" and column 'Years' exists → use 'Years'
- For "took office" and column 'Took office' exists → use 'Took office'
- For "agricultural volume" and year columns exist → use the year column that contains the answer

## STRATEGIES BY QUESTION TYPE:

**Filtering questions** (WHERE condition):
   "what was the X when Y = Z" → return column for filtering (Y) + column for answer (X)

**Aggregation questions** (AVG, SUM, COUNT):
   "average number of X" → return the numeric column X (no grouping needed, model can compute)
   "total number of X" → return column X

**Extreme value questions** (MAX, MIN, LARGEST, SMALLEST):
   "largest X" → return column X (model can find max)
   "which team had the most wins" → return 'Team' + 'Wins' (or just 'Wins' if team is row identifier)

**Comparison questions** (HIGHER/LOWER THAN):
   "did X have more than Y" → return column with values to compare

**Sequence questions** (NEXT, PREVIOUS, FIRST, LAST):
   "what was the next X after Y" → return ordering column + identifying column
   "what was the first year" → return year column

**Lookup questions** (DIRECT MATCH):
   "who was the first ambassador" → return column with names + ordering column if needed

## EXAMPLES:

EXAMPLE_1
QUESTION: what was the last year where this team was a part of the usl a-league?
ANSWER: 2004
TABLE: Year,Division,League,Regular Season,Playoffs,Open Cup,Avg. Attendance
2001,2,USL A-League,"4th, Western",Quarterfinals,Did not qualify,7169
2002,2,USL A-League,"2nd, Pacific",1st Round,Did not qualify,6260
2003,2,USL A-League,"3rd, Pacific",Did not qualify,Did not qualify,5871
2004,2,USL A-League,"1st, Western",Quarterfinals,4th Round,5628
2005,2,USL First Division,5th,Quarterfinals,4th Round,6028
OUTPUT: Year,League

EXAMPLE_2
QUESTION: what was the average number of years served by a coach?
ANSWER: 4
TABLE: Coach, Tenure, Record, Years, Pct.
Joe Sewell, 1931-1936, 221-122-16, 6, .637
OUTPUT: Years

EXAMPLE_3
QUESTION: who was the first to take office?
ANSWER: Jaafar Mohamed
TABLE: Menteri Besar, #, Party, Took office, Left office
Jaafar Mohamed, 1, BN, 21 May 2018, -
OUTPUT: Took office

EXAMPLE_4
QUESTION: which year had the largest agricultural volume?
ANSWER: 2010/11
TABLE: 2007/08, 2008/09, 2009/10, 2010/11, 2011/12, IME Exchange (Including spot, credit and forward transactions)
100, 150, 200, 300, 250, 12345
OUTPUT: 2010/11

EXAMPLE_5
QUESTION: what is the next highest hard drive available after the 30gb model?
ANSWER: 64GB SSD
TABLE: Model 01+, Component, Model e2, Model 01, model 03 (China Copy), Model 2+ (Pre-production), Model 02
OUTPUT: Component,Model 02

EXAMPLE_6
QUESTION: what is the average score of all home team members for all dates?
ANSWER: 1.75
TABLE: Home team, Away team, Date, Score, Notes
Team A, Team B, 2024-01-01, 2, -
Team C, Team D, 2024-01-02, 1.5, -
OUTPUT: Score

EXAMPLE_7
QUESTION: how many games did new zealand win in 2010?
ANSWER: 3
TABLE: Date, Venue, Score, Victor, Comments, Match reports
27 November 2010, Millennium Stadium, 25-37, New Zealand, 2010 Autumn International, BBC
26 June 2010, Waikato Stadium, 29-10, New Zealand, 2010 mid-year rugby test series, -
19 June 2010, Carisbrook, 42-9, New Zealand, 2010 mid-year rugby test series, Stuff
OUTPUT: Victor,Date

EXAMPLE_8
QUESTION: what number of games did new zealand win?
ANSWER: 3
TABLE: Date, Venue, Score, Victor, Comments, Match reports
OUTPUT: Victor

## REMEMBER:
- Return ONLY column names, NOT data
- If the answer requires a calculation, return the numeric column(s)
- If the question asks for a specific value that IS a column name (like a year), return that column
- Be minimal but sufficient - prefer single column when possible
- Do NOT add explanations, markdown, or any extra text outside the comma-separated list"""