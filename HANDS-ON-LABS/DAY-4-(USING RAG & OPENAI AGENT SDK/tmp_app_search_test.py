import os
os.environ['GROQ_API_KEY'] = 'dummy'

import app
app.SERPAPI_KEY = None
results = app.web_search('Groq AI web search agents')
print('results', results)
print('count', len(results))
