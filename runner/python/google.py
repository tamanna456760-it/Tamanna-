# google.py - Comprehensive Google Services Integration
import json
import urllib.parse
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

try:
    import gspread
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googlesearch import search as google_search

    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google.oauth2.service_account import Credentials as ServiceAccountCredentials
except ImportError:
    print(
        "Some dependencies missing. Install with: pip install googlesearch-python google-api-python-client gspread google-auth-httplib2 google-auth-oauthlib beautifulsoup4 requests"
    )


class GoogleServices:
    """
    Comprehensive Google Services Integration
    """

    def __init__(self, credentials_path: str = None, api_key: str = None):
        self.credentials_path = credentials_path
        self.api_key = api_key
        self.services = {}

    # ===== GOOGLE SEARCH =====
    def search_web(
        self, query: str, num_results: int = 10, lang: str = "en"
    ) -> List[str]:
        """
        Perform Google web search
        """
        try:
            results = []
            for url in google_search(query, num_results=num_results, lang=lang):
                results.append(url)
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return self._fallback_search(query, num_results)

    def _fallback_search(self, query: str, num_results: int) -> List[str]:
        """
        Fallback search method using requests
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}&num={num_results}"

        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            results = []
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if href.startswith("/url?q="):
                    clean_url = href.split("/url?q=")[1].split("&")[0]
                    if clean_url.startswith("http") and clean_url not in results:
                        results.append(clean_url)
                        if len(results) >= num_results:
                            break
            return results
        except Exception as e:
            print(f"Fallback search error: {e}")
            return []

    def search_with_details(
        self, query: str, num_results: int = 5
    ) -> List[Dict[str, str]]:
        """
        Search with detailed results including titles and snippets
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}&num={num_results}"

        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            results = []
            # Look for search result containers
            for result in soup.find_all("div", class_="g"):
                title_elem = result.find("h3")
                link_elem = result.find("a", href=True)
                snippet_elem = result.find("span", class_="aCOpRe")

                if title_elem and link_elem:
                    title = title_elem.get_text()
                    link = link_elem["href"]
                    snippet = snippet_elem.get_text() if snippet_elem else ""

                    # Clean the link
                    if link.startswith("/url?q="):
                        link = link.split("/url?q=")[1].split("&")[0]

                    results.append({"title": title, "link": link, "snippet": snippet})

            return results
        except Exception as e:
            print(f"Detailed search error: {e}")
            return []

    # ===== GOOGLE SHEETS =====
    def setup_sheets(
        self, credentials_file: str, sheet_name: str = None, sheet_url: str = None
    ):
        """
        Setup Google Sheets connection
        """
        try:
            scope = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = ServiceAccountCredentials.from_service_account_file(
                credentials_file, scopes=scope
            )
            client = gspread.authorize(creds)

            if sheet_url:
                sheet = client.open_by_url(sheet_url).sheet1
            elif sheet_name:
                sheet = client.open(sheet_name).sheet1
            else:
                raise ValueError("Either sheet_name or sheet_url must be provided")

            self.services["sheets"] = sheet
            return sheet
        except Exception as e:
            print(f"Sheets setup error: {e}")
            return None

    def read_sheet_data(self, sheet=None) -> List[Dict]:
        """
        Read all data from Google Sheet
        """
        try:
            if not sheet:
                sheet = self.services.get("sheets")
                if not sheet:
                    raise ValueError("No sheet provided or setup")

            return sheet.get_all_records()
        except Exception as e:
            print(f"Read sheet error: {e}")
            return []

    def write_to_sheet(self, data: List[List], sheet=None, cell_range: str = "A1"):
        """
        Write data to Google Sheet
        """
        try:
            if not sheet:
                sheet = self.services.get("sheets")
                if not sheet:
                    raise ValueError("No sheet provided or setup")

            sheet.update(cell_range, data)
            return True
        except Exception as e:
            print(f"Write sheet error: {e}")
            return False

    # ===== GOOGLE DRIVE =====
    def setup_drive(self, credentials_file: str):
        """
        Setup Google Drive connection
        """
        try:
            SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
            creds = ServiceAccountCredentials.from_service_account_file(
                credentials_file, scopes=SCOPES
            )
            service = build("drive", "v3", credentials=creds)
            self.services["drive"] = service
            return service
        except Exception as e:
            print(f"Drive setup error: {e}")
            return None

    def list_drive_files(
        self, folder_id: str = None, file_type: str = None
    ) -> List[Dict]:
        """
        List files from Google Drive
        """
        try:
            service = self.services.get("drive")
            if not service:
                raise ValueError("Drive service not setup")

            query = []
            if folder_id:
                query.append(f"'{folder_id}' in parents")
            if file_type:
                query.append(f"mimeType='{file_type}'")

            query_str = " and ".join(query) if query else ""

            results = (
                service.files()
                .list(
                    q=query_str,
                    pageSize=100,
                    fields="files(id, name, mimeType, createdTime, modifiedTime)",
                )
                .execute()
            )

            return results.get("files", [])
        except Exception as e:
            print(f"List drive files error: {e}")
            return []

    def download_drive_file(self, file_id: str, download_path: str) -> bool:
        """
        Download a file from Google Drive
        """
        try:
            service = self.services.get("drive")
            if not service:
                raise ValueError("Drive service not setup")

            request = service.files().get_media(fileId=file_id)
            with open(download_path, "wb") as file:
                file.write(request.execute())
            return True
        except Exception as e:
            print(f"Download error: {e}")
            return False

    # ===== GOOGLE CUSTOM SEARCH API =====
    def custom_search(
        self, query: str, search_engine_id: str, num_results: int = 10
    ) -> List[Dict]:
        """
        Use Google Custom Search JSON API
        Requires API key and Search Engine ID
        """
        if not self.api_key:
            raise ValueError("API key required for custom search")

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": search_engine_id,
            "q": query,
            "num": min(num_results, 10),  # API max is 10
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            results = []
            for item in data.get("items", []):
                results.append(
                    {
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet"),
                        "displayLink": item.get("displayLink"),
                    }
                )

            return results
        except Exception as e:
            print(f"Custom search error: {e}")
            return []

    # ===== UTILITY METHODS =====
    def save_results_to_file(
        self, results: List, filename: str = "google_results.json"
    ):
        """
        Save search results to JSON file
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Save error: {e}")

    def print_results(self, results: List):
        """
        Pretty print search results
        """
        for i, result in enumerate(results, 1):
            if isinstance(result, str):
                print(f"{i}. {result}")
            elif isinstance(result, dict):
                print(f"{i}. {result.get('title', 'No title')}")
                print(f"   URL: {result.get('link', 'No link')}")
                if result.get("snippet"):
                    print(f"   Description: {result.get('snippet')}")
                print()


# ===== USAGE EXAMPLES =====
def main():
    """
    Demonstration of all Google services
    """
    google = GoogleServices(api_key="YOUR_API_KEY_HERE")

    print("=== GOOGLE WEB SEARCH ===")
    results = google.search_web("Python programming", 5)
    google.print_results(results)

    print("\n=== DETAILED SEARCH ===")
    detailed_results = google.search_with_details("machine learning", 3)
    google.print_results(detailed_results)

    # Save results to file
    google.save_results_to_file(detailed_results, "search_results.json")

    print("\n=== CUSTOM SEARCH API ===")
    # You need to set up Custom Search Engine first
    # custom_results = google.custom_search(
    #     "artificial intelligence",
    #     "YOUR_SEARCH_ENGINE_ID",
    #     5
    # )
    # google.print_results(custom_results)

    print("\n=== GOOGLE SHEETS (requires credentials) ===")
    # sheet = google.setup_sheets('credentials.json', 'My Sheet')
    # if sheet:
    #     data = google.read_sheet_data(sheet)
    #     print(f"Read {len(data)} rows from sheet")

    print("\n=== GOOGLE DRIVE (requires credentials) ===")
    # drive = google.setup_drive('credentials.json')
    # if drive:
    #     files = google.list_drive_files()
    #     print(f"Found {len(files)} files in Drive")


if __name__ == "__main__":
    main()


# ===== QUICK USAGE FUNCTIONS =====
def quick_search(query: str, num_results: int = 10) -> List[str]:
    """Quick one-line search function"""
    return GoogleServices().search_web(query, num_results)


def search_and_save(query: str, filename: str = "results.json", num_results: int = 10):
    """Search and save results to file"""
    google = GoogleServices()
    results = google.search_with_details(query, num_results)
    google.save_results_t