import csv
from time import sleep
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common import exceptions


def create_webdriver_instance():
    driver = Chrome()
    return driver


def login(username, password, driver):
    url = 'https://twitter.com/i/flow/login'
    try:
        driver.get(url)
        xpath_username = '//input[@name="username"]'
        xpath_password = '//input[@name="password"]'
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, xpath_username)))
        uid_input = driver.find_element_by_xpath(xpath_username)
        uid_input.send_keys(username)
        uid_input.send_keys(Keys.RETURN)
        sleep(1)
    except exceptions.TimeoutException:
        print("Timeout while waiting for Login screen to load")
        return False
    
    pwd_input = driver.find_element_by_xpath(xpath_password)
    pwd_input.send_keys(password)
    try:
        pwd_input.send_keys(Keys.RETURN)
        url = "https://twitter.com/home"
        WebDriverWait(driver, 10).until(expected_conditions.url_to_be(url))
    except exceptions.TimeoutException:
        print("Timeout while waiting for home screen to load")
    return True

def find_search_input_and_enter_criteria(search_term, driver):
    xpath_search = '//input[@data-testid="SearchBox_Search_Input"]'
    search_input = driver.find_element_by_xpath(xpath_search)
    search_input.send_keys(search_term)
    search_input.send_keys(Keys.RETURN)
    return True

def find_search_input(driver):
    xpath_search = '//input[@data-testid="SearchBox_Search_Input"]'
    search_input = driver.find_element_by_xpath(xpath_search)
    return search_input


def change_page_sort(driver):
    xpath_tab_state = '//a[@aria-selected="false"]'
    tab = driver.find_element_by_xpath(xpath_tab_state)
    tab.click()

def generate_tweet_id(tweet):
    return ''.join(tweet)


def scroll_down_page(driver, last_position, num_seconds_to_load=0.5, scroll_attempt=0, max_attempts=5):
    end_of_scroll_region = False
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(num_seconds_to_load)
    curr_position = driver.execute_script("return window.pageYOffset;")
    if curr_position == last_position:
        if scroll_attempt < max_attempts:
            end_of_scroll_region = True
        else:
            scroll_down_page(last_position, curr_position, scroll_attempt + 1)
    last_position = curr_position
    return last_position, end_of_scroll_region


def save_tweet_data_to_csv(records, filepath, mode='a+'):
    header = ['User', 'Handle', 'PostDate', 'TweetText', 'ReplyCount', 'RetweetCount', 'LikeCount']
    with open(filepath, mode=mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if mode == 'w':
            writer.writerow(header)
        if records:
            writer.writerow(records)


def collect_all_tweets_from_current_view(driver, lookback_limit=15):
    page_tweets = driver.find_elements_by_xpath('//article[@data-testid="tweet"]')
    if len(page_tweets) <= lookback_limit:
        return page_tweets
    else:
        return page_tweets[-lookback_limit:]


def extract_data_from_current_tweet_card(tweet):
    
    # Username 
    try:
        user = tweet.find_element_by_xpath('.//span').text
    except exceptions.NoSuchElementException:
        user = ""
    except exceptions.StaleElementReferenceException:
        return
    
    # Handle
    try:
        handle = tweet.find_element_by_xpath('.//span[contains(text(), "@")]').text
    except exceptions.NoSuchElementException:
        handle = ""
    
    # PostTime
    try:
        postdate = tweet.find_element_by_xpath('.//time').get_attribute('datetime')
    except exceptions.NoSuchElementException:
        return
    
    # TextContent
    try:
        _content = tweet.find_element_by_xpath('.//div[2]/div[2]/div[2]/div[1]').text
    except exceptions.NoSuchElementException:
        _content = ""
    
    # Responding to or quoted tweet
    try:
        _quoted = tweet.find_element_by_xpath('.//div[2]/div[2]/div[2]/div[2]').text
    except exceptions.NoSuchElementException:
        _quoted = ""
    tweet_text = _content + "\n\n" + _quoted
    
    # Replies or comments to the tweet
    try:
        reply_count = tweet.find_element_by_xpath('.//div[@data-testid="reply"]').text
    except exceptions.NoSuchElementException:
        reply_count = ""
    
    # Retweets
    try:
        retweet_count = tweet.find_element_by_xpath('.//div[@data-testid="retweet"]').text
    except exceptions.NoSuchElementException:
        retweet_count = ""
    
    # Likes
    try:
        like_count = tweet.find_element_by_xpath('.//div[@data-testid="like"]').text
    except exceptions.NoSuchElementException:
        like_count = ""

    # the tweet tuple
    tweet = (user, handle, postdate, tweet_text, reply_count, retweet_count, like_count)
    return tweet


def main(username, password, filepath, search_term):
    # create file for saving records
    save_tweet_data_to_csv(None, filepath, 'w')
    
    last_position = None
    end_of_scroll_region = False
    unique_tweets = set()

    driver = create_webdriver_instance()
    logged_in = login(username, password, driver)
    if not logged_in:
        return

    sleep(3)

    
    search_found = find_search_input_and_enter_criteria(search_term, driver)
    if not search_found:
        return

    sleep(3)

    change_page_sort( driver)

    sleep(3)
    
    tweets_per_term = 0
    while not end_of_scroll_region:
        tweet_cards = collect_all_tweets_from_current_view(driver)
        for tweet_card in tweet_cards:
            try:
                tweet = extract_data_from_current_tweet_card(tweet_card)
            except exceptions.StaleElementReferenceException:
                continue
            if not tweet:
                continue
            tweet_id = generate_tweet_id(tweet)
            if tweet_id not in unique_tweets:
                unique_tweets.add(tweet_id)
                save_tweet_data_to_csv(tweet, filepath)
        last_position, end_of_scroll_region = scroll_down_page(driver, last_position)
        tweets_per_term += 1
        if tweets_per_term > 5000:
            break

        

    driver.quit()


if __name__ == '__main__':
    usr = "PushkarBorkar"
    pwd = "l@Xtwitter$72blr"
    path = './tweets.csv'
    term = 'technology'

    main(usr, pwd, path, term)
