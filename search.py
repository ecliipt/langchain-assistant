from websearch import Parse
from tool import loadTool
def searchEngine(subject: str) -> str:
    """Search things about current events."""
    
    result = []
    #subject = subject.replace('"', "'")
    subject = subject.split('|') if '|' in subject else [subject]
    # ["search query for single query"]"
    # ["search query", "for multiple", "queries"]

    for query in subject:
        if query.startswith(' '): query = query.replace(' ', '', 1)
        try: value, response = Parse(subject=query)
        except Exception as e: 
            if len(subject) > 1: result.append(f'Search for "{query}": Failed to scrape from search; Error:"{e}".')
            else: result.append(f'Failed to scrape from search; Error:"{e}".')
            continue
        if value and len(response) > 1:
            if '<action:' in response:
                action, response = response.split('>', 1)
                action = action.replace('<action:', '')
                loadTool(action=action)
            if len(subject) > 1: 
                response = '\n'+response if '\n' in response and not response.startswith('\n') else response
                result.append(f'Search for "{query}": {response}')
            else: result.append({response})
        else:
            if len(subject) > 1: result.append(f'No information was found about "{query}".')
            else: result.append("No online information was found!")
    
    print('-'*50)
    try: return '\n'+'\n\n'.join(result) if result != [] else "No online information was found!"
    except: return "No online information was found!"
if __name__ == '__main__':
    print(searchEngine(input('*')))