# Company Finder Crew

This crew finds companies matching specific criteria using a two-agent workflow:

## Agents
1. **Companies Search Agent (QueryMaster)**
   - Role: Performs comprehensive web searches
   - Tools: SerperDevTool
   - Searches across: web, news, images, and videos

2. **Companies Data Analyst (DataWeaver)**
   - Role: Scrapes and analyzes company data
   - Tools:
     - ScrapeWebsiteTool (websites)
     - PDFRAGSearchTool (PDFs)
     - YoutubeVideoSearchTool (videos)
     - ImageAnalysisTool (images)

## Tasks
1. **Research Task**
   - Input: User query + current timestamp
   - Output: Markdown list of relevant URLs

2. **Analysis Task**
   - Input: URLs from Research Task
   - Output: Markdown report of company profiles
   - Creates: `knowledge/companies.md` file

## Usage
1. Run the script:
```bash
python main.py
