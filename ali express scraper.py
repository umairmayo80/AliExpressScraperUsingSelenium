#putting all together
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys 

#Path of the chromedriver.exe. 
#Download the chromedriver on your system and Replace this path with the path of the chromedriver.exe on your system
PATH = 'G:/Users/Umair/Downloads/Compressed/chromedriver_win32/chromedriver.exe'

#defining constants
LOAD_PAUSE_TIME = 4
SCROLL_PAUSE_TIME = 1

def get_feadback(dr:webdriver) -> float:
    try:
        feedbackR = dr.find_element_by_css_selector('div[class="store-info-content"] div[class="positive-fdbk"]')
        fdb = feedbackR.get_attribute('textContent')
        return float(fdb.split('%')[0])
    except:
        print('No element found with the div[class="positive-fdbk"]')
        return 0


def get_likes(dr:webdriver, pagelink:str)  -> int:
    try:
        dr.get(pagelink)
        sleep(LOAD_PAUSE_TIME)
        likes = dr.find_element_by_xpath('//span[@class="add-wishlist-num"]')
        print(likes.text)
        if 'K' in likes.text:
            return int(float(likes.text.split('K')[0])*1000)
        return int(likes.text)
    except:
        print('Failed to load the requested item. Kindly consider checking your internet connection or restarting the program.\n',pagelink)
        return 0


def get_products_links(pageLink:str,category:str, filtering_attributes:list=None, sorting_attr:int=None, minFeedback:int=0, minLikes:int=0):
    """Function to fetch all the products in a given page"""
    
    # to start the chrome driver
    driver = webdriver.Chrome(executable_path=PATH)
    driver.get(pageLink)
    sleep(LOAD_PAUSE_TIME)
    if (category != 'SpecificPage'):
        
        try:
            #seachring filtering attributes on page
            ckboxes = driver.find_elements_by_css_selector('div[class="top-container"] input[class="next-checkbox-input"')
            #checkboxes order = sale,spend & Save, free shipping, 4+ rating
            for i in range(0, len(ckboxes)):
                if int(filtering_attributes[i]) == 1:
                    ckboxes[i].click()
                    sleep(LOAD_PAUSE_TIME)
                    print('click')
            if sorting_attr == 1:
                # defining function to get the top
                # //span[@ae_object_value="number_of_orders"] # XPATH to find the sorting_attr by order
                orders_sort_button = driver.find_element_by_xpath('//span[@ae_object_value="number_of_orders"]')
                orders_sort_button.click()
                sleep(LOAD_PAUSE_TIME)
                print('sort')
        except:
            print('no item found')
    
    #scrolling the page to load all the elements
    #Scrolling
    driver.find_element_by_tag_name('body').send_keys(Keys.END) 
    sleep(SCROLL_PAUSE_TIME)
    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
    sleep(SCROLL_PAUSE_TIME)
    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
    sleep(SCROLL_PAUSE_TIME)
    driver.find_element_by_tag_name('body').send_keys(Keys.HOME)
 
    
    #fetching the links of the product on the page
    products_links = driver.find_elements_by_css_selector("div a") #div.JIIxO means div with class JIIxO
    clean_product_list = []
    for pdl in products_links:
        print(pdl.get_attribute('href'))
        if pdl.get_attribute('href') != None:
            if pdl.get_attribute('href').startswith("https://www.aliexpress.com/item/"):
                clean_product_list.append(pdl.get_attribute('href'))


    

    # Open a new window
    driver.execute_script("window.open('');") 
    # Switch to the new window and open new URL
    driver.switch_to.window(driver.window_handles[1])
    

    # driver2 = webdriver.Chrome(executable_path=PATH)
    filteredProducts = []
    for pd in clean_product_list:
        pd_likes = get_likes(driver,pd)
        pd_feedback = get_feadback(driver)
        print('\n\tlikes:',pd_likes,'\n\tfeedback:',pd_feedback)
        if (pd_likes != None) and (pd_feedback != None):
            if pd_likes >= minLikes and pd_feedback >= minFeedback:
                filteredProducts.append((pd,pd_likes,pd_feedback))
    # driver2.quit()
    # Closing new tab
    driver.close()
    # Switching to old tab1
    driver.switch_to.window(driver.window_handles[0])



    #writing the filtered fetched products to the file
    f = open(f'{category} filtered product_links.csv','w')
    f.write('index,likes,feedback,link\n')
    for i in range(len(filteredProducts)):
        f.write(str(i)+","+str(filteredProducts[i][1])+","+str(filteredProducts[i][2])+","+str(filteredProducts[i][0]))
        f.write('\n')
    f.close()
    print(f'\n Links stored in file \'{category} filtered product_links.csv\'')
    sleep(LOAD_PAUSE_TIME)
    driver.quit()
    return None


def scrape_by_category():
    print('Enter the Category (or list of Categories separeted by comma) like:\nLaptops,Computer Cables & Connectors')
    # for sub_cat in range(len()):
    target_cat = ['Laptops','Computer Cables & Connectors'] # default categories
    print('Default set categories for testing:\n',target_cat)
    target_cat = input('Enter new category list:').split(',')
    print('Entered categories:\n',target_cat)
    target_cat = [x.lower() for x in target_cat]
    
    print('Select the filtering attributes:\nFiltering Attributes are:\n\tPlus, Sale, Spend & Save, Free shipping, 4+ Star Rating')
    
    while(True):
        filtering_attributes = str(input('Enter the selection as:\n0,1,1,1,1\nNote: 1=Set, 0=Not set\nEnter:')).split(',')
        print(filtering_attributes)
        if len(filtering_attributes)<5:
            print('Enter again')
        else:
            break
    
    print('\nSort by Order:')
    while(True):
        sorting_attibutes = int(input('Note: 1=Set, 0=Not set:'));
        if sorting_attibutes == 1 or sorting_attibutes == 0:
            break
        else:
            print('Enter Again:')

    feedback = int(float(input('Enter Minimum Positive feedback (Integer value between 0 to 100):')))
    likes = int(input('Enter Minimum Likes counts (Integer value like 10 or 1000):'))
    # to start the chrome driver
    driver = webdriver.Chrome(executable_path=PATH)
    categories_page ='https://www.aliexpress.com/all-wholesale-products.html'
    driver.get(categories_page)
    sleep(LOAD_PAUSE_TIME)
    main_cat = driver.find_elements_by_css_selector("li a")
#         print(main_cat)

    #fetching sub-categories
    sub_categories = []
    for ct in main_cat:
    #     print(ct.get_attribute('href'))
        if ct.get_attribute('href').startswith("https://www.aliexpress.com/category/"):
            sub_categories.append(ct)



    #loading target category page
    for sub_cat in sub_categories:
        if sub_cat.text.lower() in target_cat:
            print(sub_cat.get_attribute('href'))
            get_products_links(sub_cat.get_attribute('href'), sub_cat.text,filtering_attributes,sorting_attibutes,feedback,likes)
            

    # to close the chrome window
    driver.quit() 




## driver program
if __name__ == '__main__':
    print("""\t\n Aliexpress Scrapper
        1. Scrape a specific page
        2. Scrape using category name.""")

    choice = int(input("Enter your choice:"))
    while(True):
        if choice == 1:
            print('Paste the page link below:\n')
            pgLink = str(input())
            feedback = int(float(input('Enter Minimum Positive feedback:')))
            likes = int(input('Enter Minimum Likes counts:'))
            get_products_links(pgLink,'SpecificPage',minFeedback=feedback,minLikes=likes)
            break
        elif choice == 2:
            scrape_by_category()
            break
        else:
            print('Please enter correct choice')
    print('\n\n Done')
    #producing beep sound on competion
    import winsound
    frequency = 2500  # Set Frequency To 2500 Hertz
    duration = 1000  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)