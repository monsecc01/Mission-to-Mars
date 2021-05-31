# #!/usr/bin/env python
# # coding: utf-8

# # Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemisphere_images": hemisphere(browser),
        "last_modified": dt.datetime.now()
    }
    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    #convert the browser html to a soup object adn then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

     # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
    
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None
        
    return news_title, news_p

# Visit URL
def featured_image(browser):
    url = 'https://spaceimages-mars.com'
    browser.visit(url)


    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()


    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

def hemisphere(browser):

    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)


    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    h_soup = soup(html, 'html.parser')
    hemisphere_names = []

    # Search for the names of all four hemispheres
    results = h_soup.find_all('div', class_="collapsible results")
    hemispheres = results[0].find_all('h3')

    # Get text and store in list
    for name in hemispheres:
        hemisphere_names.append(name.text)
    # hemisphere_names

    # Search for thumbnail links
    thumbnail_results = results[0].find_all('a')
    thumbnail_links = []

    for thumbnail in thumbnail_results:
        
        # If the thumbnail element has an image...
        if (thumbnail.img):
            
            # then grab the attached link
            thumbnail_url = 'https://marshemispheres.com/' + thumbnail['href']
            
            # Append list with links
            thumbnail_links.append(thumbnail_url)

    # thumbnail_links
    
    full_imgs = []
    for url in thumbnail_links:
        
        # Click through each thumbanil link
        browser.visit(url)
        
        html = browser.html
        t_soup = soup(html, 'html.parser')
        
        # Scrape each page for the relative image path
        results = t_soup.find_all('img', class_='wide-image')
        relative_img_path = results[0]['src']
        
        # Combine the reltaive image path to get the full url
        img_link = 'https://marshemispheres.com/' + relative_img_path
        
        # Add full image links to a list
        full_imgs.append(img_link)

    # full_imgs

    # Zip together the list of hemisphere names and hemisphere image links
    mars_hemi_zip = zip(full_imgs, hemisphere_names)

    # Iterate through the zipped object
    for img, title in mars_hemi_zip:
        mars_hemi_dict = {}
        
        # Add image url to dictionary
        mars_hemi_dict['img_url'] = img
        
        # Add hemisphere title to dictionary
        mars_hemi_dict['title'] = title
            
        # Append the list with dictionaries
        hemisphere_image_urls.append(mars_hemi_dict)

    # 4. Print the list that holds the dictionary of each image url and title.
    return hemisphere_names, thumbnail_links, full_imgs, hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())