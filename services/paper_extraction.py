import scholarly
import arxiv
from Bio import Entrez

#set email for PubMed API

Entrez.email = "utakhouri@gmail.com"

def search_google_scholar(query, num_results=5):
  """
  Searches Google Scholar for academic paper
  """
  print(f"[INFO] Searching Google Scholar for: {query}")
  search_query = scholarly.search_pubs(query)

  papers = []
  for i, result in enumerate(search_query):
    if i>=num_results:
      break
    papers.append({
      "title":result['bib']['title'],
      "author": result['bib'].get('author', 'Unknown'),
      "year": result['bib'].get('pub_year', 'Unknown'),
      "link": result.get('pub_url', 'No URL available')
    })

  return papers

def search_arxiv(query, num_results=5):
  """
  Searches ArXiv for academic papers
  """
  print(f"[INFO] Searching ArXiv for:{query}")
  search = arxiv.Search(
    query=query,
    max_results=num_results,
    sort_by=arxiv.SortCriterion.SubmittedDate
  )

  papers = []
  for result in search.results():
        papers.append({
            "title": result.title,
            "authors": ", ".join([a.name for a in result.authors]),
            "year": result.published.year,
            "abstract": result.summary,  # Include abstract for better summaries
            "pdf_link": result.pdf_url,  # Direct link to PDF
            "arxiv_id": result.entry_id
        })
    
  return papers


