import json
import os
import random
import time
import requests
from bs4 import BeautifulSoup
from copy import deepcopy
import csv

class Crawler:
    def __init__(self):
        # Base URL for IMDb search (set to search for "OMG 2" initially)
        self.base_url = 'https://www.imdb.com/find/?q=OMG%202'
        
        # Headers to mimic a browser request to avoid bot detection
        self.get_headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'csrf-token': '',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        }
        self.session = requests.Session()  # Persistent session for making requests

        # Template object structure to store extracted data
        self.obj = {
            "type": "", "name": "", "description": "", "ratingCount": "", 
            "bestRating": "", "worstRating": "", "ratingValue": "", 
            "datePublished": "", "actor": "", "directors": "", "Writers": "", "url": ""
        }
        self.all_data = []  # List to store all extracted movie data

    # Function to handle GET requests with retries on failure
    def get_request(self, url):
        mycount = 0  # Counter to limit the number of retries
        while True:
            try:
                # Make a GET request with the specified headers
                res = self.session.get(url, headers=self.get_headers)
               
                # If request is successful, return True with the response
                if res.status_code == 200:
                    return True, res
                # Sleep for a random interval between retries
                time.sleep(random.randint(1, 3))
            except Exception as e:
                print(e)  # Print the exception if any error occurs during the request
            
            # Retry the request if it fails
            print("Trying again to fetch data")
            mycount += 1
            
            # Exit loop after 30 failed attempts
            if mycount > 30:
                break
        return False, False  # Return False if all retries fail

    # Function to extract movie details from the links
    def get_details(self, links):
        for link in links:
            # Create a copy of the object structure for each movie
            Obj = deepcopy(self.obj)
            Obj['url'] = link  # Assign the movie URL
            
            try:
                isloaded, res = self.get_request(link)  # Request the movie details page
                if not isloaded:
                    continue  # Skip if the page isn't loaded
                
                soup = BeautifulSoup(res.text, "lxml")  # Parse the page content
                scripts = soup.find_all('script', {'type': 'application/ld+json'})  # Extract JSON-LD data
                
                if not scripts:
                    continue  # Skip if no JSON-LD scripts are found
                
                # Loop through each JSON-LD script found on the page
                for script in scripts:
                    try:
                        json_data = json.loads(script.string)  # Parse JSON data
                        
                        # Skip if the 'actor' field is not present in the JSON
                        if 'actor' not in json_data:
                            continue  
                        
                        # Extract the relevant movie details
                        Obj['type'] = json_data.get('@type', '')
                        Obj['name'] = json_data.get('name', '')
                        Obj['description'] = json_data.get('description', '')

                        # Extract aggregate rating details
                        rating_info = json_data.get('aggregateRating', {})
                        Obj['ratingCount'] = rating_info.get('ratingCount', '')
                        Obj['bestRating'] = rating_info.get('bestRating', '')
                        Obj['worstRating'] = rating_info.get('worstRating', '')
                        Obj['ratingValue'] = rating_info.get('ratingValue', '')
                        Obj['datePublished'] = json_data.get('datePublished', '')
                        
                        # Process actor, director, and writer names and join them as a string
                        Obj['actor'] = ', '.join(
                            actor.get('name', '').strip() 
                            for actor in json_data.get('actor', [])
                            if actor.get('name', '').strip()
                        )
                        Obj['directors'] = ', '.join(
                            director.get('name', '').strip() 
                            for director in json_data.get('director', [])
                            if director.get('name', '').strip()
                        )
                        Obj['Writers'] = ', '.join(
                            creator.get('name', '').strip() 
                            for creator in json_data.get('creator', [])
                            if creator.get('name', '').strip()
                        )
                        
                        # Append the extracted movie details to the data list
                        self.all_data.append(Obj)

                    except (json.JSONDecodeError, KeyError):
                        continue  # Skip if JSON parsing fails or necessary keys are missing

            except Exception as e:
                print(f"Error processing link {link}: {e}")  # Handle errors during data extraction
            
    # Function to write or append movie data to a CSV file
    def write_to_csv(self, filename='imdb_data.csv'):
        file_exists = os.path.isfile(filename)  # Check if the file already exists
        
        # Open the CSV file in append mode
        with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
            # Define the CSV column headers
            fieldnames = ['type', 'name', 'description', 'ratingCount', 'bestRating', 
                          'worstRating', 'ratingValue', 'datePublished', 'actor', 
                          'directors', 'Writers', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write headers if the file does not exist yet
            if not file_exists:
                writer.writeheader()
            
            # Write each row of movie data to the CSV file
            for data in self.all_data:
                writer.writerow(data)
        
        print(f"Data written to {filename}")  # Confirm that data has been written

    # Main process that handles logic for fetching movie links and details
    def process_logic(self):
        keywords = ["omg2", "Ruslaan"]  # Keywords for the movie search
        links = []  # List to store movie links

        # Iterate through each keyword to search IMDb
        for key in keywords:
            time.sleep(2)  # Small delay between searches
            # Format the search URL
            url = f"https://www.imdb.com/find/?q={key.strip().replace('&', '%26')}"
            is_loaded, response = self.get_request(url)  # Perform search request

            # If search request is successful, parse the result page
            if is_loaded:
                soup = BeautifulSoup(response.text, "lxml")
                result_div = soup.find('div', {'class': "sc-e8e4ce7-2 gdpdyr"})  # Locate the search results div
                
                # If results are found, process the movie links
                if result_div:
                    li_tags = result_div.find('ul').find_all('li') if result_div.find('ul') else []
                    for li in li_tags:
                        atag = li.find('a')  # Find the anchor tag containing the movie link
                        if atag:
                            link = 'https://www.imdb.com' + atag.get('href')  # Construct full URL
                            links.append(link)  # Add the movie link to the list
            
            # If any links are found, proceed to extract movie details
            if len(links) > 0:
                self.get_details(links)  # Extract movie details for each link
                self.write_to_csv()  # Write the data to a CSV file
                self.all_data = []  # Clear the data list for the next iteration


if __name__ == "__main__":
    scraper = Crawler()
    scraper.process_logic()  # Start the scraping process
