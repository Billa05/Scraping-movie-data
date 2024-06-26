import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException

def scrape_movie_data(url):
    try:
        headers = {'Accept-Language': 'en-US,en;q=0.9'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        name = "Unknown"
        div_name = soup.find('section', class_='header poster')
        if div_name:
            a_tag = div_name.find('a')
            if a_tag:
                name = a_tag.text.strip()

        release_date = "Unknown"
        release_date_span = soup.find('span', class_='release')
        if release_date_span:
            release_date = release_date_span.text.strip()
        
        rating = "Unknown"
        rating_div = soup.find('div', class_='user_score_chart')
        if rating_div:
            rating = rating_div.get('data-percent')
            if rating:
                rating = float(rating)
        
        duration = "Unknown"
        duration_span = soup.find('span', class_='runtime')
        if duration_span:
            duration = duration_span.text.strip()
        
        genres = [genre.text.replace('\xa0', ' ').strip() for genre in soup.find_all('span', class_='genres')]
        
        director_name = "Unknown"
        profiles = soup.find_all('li', class_='profile')
        for profile in profiles:
            if 'Director' in profile.find('p', class_='character').text.strip():
                director_name = profile.find('a').text.strip()
                break
        
        return {
            'Name': name,
            'Release Date': release_date,
            'Ratings': rating,
            'Duration': duration,
            'Genre': genres,
            'Director': director_name
        }
    except Exception as e:
        print(f"Error scraping movie data: {e}")
        return None

def main():
    try:
        base_url = 'https://www.themoviedb.org/movie/'
        movies_url = []
        movies_data = []
        driver = webdriver.Chrome()
        driver.get(base_url)
        driver.execute_script('window.scrollBy(0, 1000)')
        sleep(1)
        button = driver.find_element(By.XPATH, "//*[@id='pagination_page_1']/p/a")
        button.click()
        
        while True:
            try:
                element = driver.find_element(By.ID, "page_100")
                if element:
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    link_data = soup.find_all("div", class_="wrapper glyphicons_v2 picture grey no_image_holder")
                    for i in link_data:
                        a_tag = i.find('a', class_='image')
                        if a_tag:
                            href_value = a_tag['href']
                            movies_url.append("https://www.themoviedb.org" + href_value)
                    break
            except NoSuchElementException:
                driver.execute_script('window.scrollBy(0, 1000)')
                sleep(1)
      
        for url in movies_url:
            movie_data = scrape_movie_data(url)
            if movie_data:
                movies_data.append(movie_data)
            sleep(random.uniform(1, 3))

        df = pd.DataFrame(movies_data)
        df.to_excel('movie_data.xlsx', index=False)
        print("Data saved to movie_data.xlsx")
    except WebDriverException as e:
        print(f"WebDriver error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()