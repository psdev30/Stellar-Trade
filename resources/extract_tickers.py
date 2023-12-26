import requests
from bs4 import BeautifulSoup

def get_sp500_symbols(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table containing the S&P 500 symbols
        table = soup.find('table', {'class': 'wikitable sortable'})

        # Extract symbols from the table
        symbols = [row.find_all('td')[0].text.strip() for row in table.find_all('tr')[1:]]

        return symbols
    else:
        print(f"Failed to retrieve data. Status Code: {response.status_code}")
        return []

# URL of the Wikipedia page listing S&P 500 companies
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

# Get the S&P 500 symbols
sp500_symbols = get_sp500_symbols(url)

# Print the list of symbols
print(sp500_symbols)
