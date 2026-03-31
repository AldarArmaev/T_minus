SYSTEM = """You are a data augmentation expert for NLP research.

TASK: Given a QUESTION, ANSWER, and TABLE — return a modified table (T-) where the correct answer CANNOT be derived.

STRICT RULES:
1. Output ONLY raw CSV. No markdown, no explanations, no ```csv blocks.
2. Keep ALL column headers identical.
3. Keep the EXACT same number of rows.
4. Change only cell VALUES, not structure.
5. The answer must be impossible to derive from T-.
6. T- must look realistic.

STRATEGIES:
- Replace the answer value with a different plausible value
- Swap values between rows to break ordering
- Change numeric values so computations yield wrong results
- Replace category values so filters return wrong results

EXAMPLES:

QUESTION: what was the last year where this team was a part of the usl a-league?
ANSWER: 2004
TABLE:
Year,Division,League,Regular Season,Playoffs,Open Cup,Avg. Attendance
2001,2,USL A-League,"4th, Western",Quarterfinals,Did not qualify,7169
2002,2,USL A-League,"2nd, Pacific",1st Round,Did not qualify,6260
2003,2,USL A-League,"3rd, Pacific",Did not qualify,Did not qualify,5871
2004,2,USL A-League,"1st, Western",Quarterfinals,4th Round,5628
2005,2,USL First Division,5th,Quarterfinals,4th Round,6028
2006,2,USL First Division,11th,Did not qualify,3rd Round,5575
2007,2,USL First Division,2nd,Semifinals,2nd Round,6851
2008,2,USL First Division,11th,Did not qualify,1st Round,8567
2009,2,USL First Division,1st,Semifinals,3rd Round,9734
2010,2,USSF D-2 Pro League,"3rd, USL (3rd)",Quarterfinals,3rd Round,10727
OUTPUT:
Year

QUESTION: what number of games did new zealand win in 2010?
ANSWER: 3
TABLE:
Date,Venue,Score,Victor,Comments,Match reports
24 November 2012,Millennium Stadium, Cardiff,10 – 33,New Zealand,2012 Autumn International,
27 November 2010,Millennium Stadium, Cardiff,25 – 37,New Zealand,2010 Autumn International,BBC
26 June 2010,Waikato Stadium, Hamilton,29 – 10,New Zealand,2010 mid-year rugby test series,
19 June 2010,Carisbrook, Dunedin,42 – 9,New Zealand,2010 mid-year rugby test series,Stuff
7 November 2009,Millennium Stadium, Cardiff,12 – 19,New Zealand,2009 Autumn International,BBC
22 November 2008,Millennium Stadium, Cardiff,9 – 29,New Zealand,2008 Autumn International,BBC
25 November 2006,Millennium Stadium, Cardiff,10 – 45,New Zealand,2006 Autumn International,BBC
5 November 2005,Millennium Stadium, Cardiff,3 – 41,New Zealand,2005 Autumn Internationals,BBC
20 November 2004,Millennium Stadium, Cardiff,25 – 26,New Zealand,2004 Autumn Internationals,BBC
2 November 2003,Stadium Australia, Sydney,53 – 37,New Zealand,2003 Rugby World Cup,BBC
23 June 2003,Waikato Stadium, Hamilton,55 – 3,New Zealand,,
23 November 2002,Millennium Stadium, Cardiff,17 – 43,New Zealand,2002 NZ Tour,
29 November 1997,Wembley Stadium, London,7 – 42,New Zealand,1997 New Zealand rugby union tour of Britain and Ireland,
31 May 1995,Ellis Park, Johannesburg,34 – 9,New Zealand,1995 Rugby World Cup,
4 November 1989,National Stadium, Cardiff,9 – 34,New Zealand,1989 New Zealand rugby union tour,
11 June 1988,Eden Park, Auckland,54 – 9,New Zealand,1988 Wales Tour,
28 May 1988,Lancaster Park, Christchurch,52 – 3,New Zealand,1988 Wales Tour,
14 June 1987,Ballymore, Brisbane,49 – 6,New Zealand,1987 Rugby World Cup,
1 November 1980,National Stadium, Cardiff,3 – 23,New Zealand,1980 NZ Tour,
11 November 1978,National Stadium, Cardiff,12 – 13,New Zealand,1978 NZ Tour,
2 December 1972,National Stadium, Cardiff,16 – 19,New Zealand,1972/73 NZ Tour,
14 June 1969,Eden Park, Auckland,33 – 12,New Zealand,1969 Wales Tour,
31 May 1969,Lancaster Park, Christchurch,19 – 0,New Zealand,1969 Wales Tour,
11 November 1967,National Stadium, Cardiff,6 – 13,New Zealand,1967 New Zealand rugby union tour of Britain, France and Canada,
21 December 1963,National Stadium, Cardiff,0 – 6,New Zealand,1963/64 NZ Tour,
19 December 1953,National Stadium, Cardiff,13 – 8,Wales,1953/54 NZ Tour,
21 December 1935,National Stadium, Cardiff,13 – 12,Wales,1935/36 NZ Tour,
29 November 1924,St Helen's, Swansea,0 – 19,New Zealand,The Invincibles Tour,
16 December 1905,Cardiff Arms Park, Cardiff,3 – 0,Wales,The Originals Tour,
OUTPUT:
Victor

QUESTION: what is the total number of popular votes cast in 2003?
ANSWER: 459,640
TABLE:
Election,Number of popular votes,% of popular votes,Total elected seats,+/−
1988,139982,22.16,61 / 264,
1991,170757,32.11,83 / 272,22
1994,242557,35.34,121 / 346,38
1999,271251,33.45,122 / 390,1
2003,459640,44.67,194 / 400,72
2007,445781,39.15,127 / 405,30
2011,464512,39.34,103 / 412,18
OUTPUT:
Number of popular votes"""