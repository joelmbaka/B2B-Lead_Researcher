from crewai import Agent, Task, Crew
from config.llms import scout_17b, maverick_17b, deepseekR1
from tools.research.PDF_rag_search_tool import PDFRAGSearchTool
from tools.research.scrape_website_tool import ScrapeWebsiteTool
from tools.research.serper_dev_tool import SerperDevTool
from tools.research.youtube_video_search_tool import YoutubeVideoSearchTool
from tools.research.image_analysis_tool import ImageAnalysisTool
import os
import shutil

def main():

    # Agent that prepares diverse SerperDevTool batch queries across search, news, images, and videos
    researcher = Agent(
        role="Companies Search Agent",
        goal=(
            "Use SerperDevTool to craft and run comprehensive web searches. you can also search through youtube videos, images or news only when applicable, relevant or compulsory."
        ),
        backstory=(
            "Your name is QueryMaster. You determine which SerperDevTool search types "
            "('search', 'news', 'images', 'videos') will best surface company information "
            "for the given criteria. You also come up with the most amazing batch queries"
        ),
        llm=deepseekR1,
        function_calling_llm=scout_17b,
        max_iter=20,
        tools=[SerperDevTool()],
        verbose=True
    )

    # Task to generate grouped search results from SerperDevTool
    research_task = Task(
        description="The date is {timestamp}. Use SerperDevTool to locate high-value sources (web pages, news articles, images, or videos) for companies matching the user's query: {task}.",
        expected_output="Markdown list of most relevant url links. No limit to the number on the list.",
        tools=[SerperDevTool()],
        agent=researcher,
    )

    # Agent that scrapes and structures company details
    content_analyst = Agent(
        role="Companies Data Analyst",
        goal="Scrape given URLs to collect required company data-name, revenue, sector, region, or description etc.",
        backstory="Your name is DataWeaver. You scrape websites, PDFs, video or image content for company profile data. ",
        llm=maverick_17b,
        max_iter=40,
        tools=[
            ScrapeWebsiteTool(),
            PDFRAGSearchTool(),
            YoutubeVideoSearchTool(),
            ImageAnalysisTool(),
        ],
        function_calling_llm=scout_17b,
        verbose=True
    )

    # Task to compile final markdown report of the company profiles
    analysis_task = Task(
        description= "1. Scrape 1-5 or more of the sources and write a report to meet the research task: {task}." 
            "You can use any of the provided tools: scrapewebsite for websites, pdfragsearch for PDFs, Youtube search for youtube video links and Imageanalysistool to get detailed descriptions of the visual content in an image. "
            "Always use the exact extracted URLs when making requests - do not modify or re-encode them. "
            "2. write a markdown list report of the companies you found. ",
        expected_output="A markdown report (e.g., lists or tables of company profiles).",
        output_file='knowledge/companies.md',
        tools=[ScrapeWebsiteTool(), PDFRAGSearchTool(), YoutubeVideoSearchTool(), ImageAnalysisTool(),],
        context=[research_task],
        agent=content_analyst,
    )

    # Memory setup (mirroring srs_crew.py)
    storage_dir = os.path.join(os.getcwd(), "mem")
    memory_dir = os.path.join(storage_dir, "store")
    if os.path.exists(memory_dir):
        try:
            shutil.rmtree(memory_dir)
            print(f"Cleaned existing memory directory: {memory_dir}")
        except Exception as e:
            print(f"Warning: Could not clean previous storage: {e}")
    os.makedirs(memory_dir, exist_ok=True)
    norm_path = os.path.normpath(memory_dir).replace('/', '\\')
    os.environ["CREWAI_STORAGE_DIR"] = norm_path
    os.environ["CREWAI_SHORT_TERM_MEMORY_DIR"] = "short_memory"
    os.environ["CREWAI_COLLECTION_NAME"] = "crew_memory"

    crew = Crew(
        agents=[researcher, content_analyst],
        tasks=[research_task, analysis_task],
        memory=True,         
        verbose=True,
    )

    from datetime import datetime
    timestamp = datetime.now().strftime("%d %B %Y").lower()

    crew.kickoff(inputs={
        "task": "latest ycombinator fintech startups that i might be recruiting software engineers",
        "timestamp": timestamp
        })

if __name__ == "__main__":
    main() 
