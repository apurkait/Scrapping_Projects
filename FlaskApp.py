from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup as bs

final = Flask(__name__)  ##Setting up application name
CORS(final)  ##to avoid certificate issue


@final.route('/', methods=['GET'])  ##default routing
@cross_origin()
def index():
    return render_template('index.html') ##display first web page


@final.route('/reviews', methods=['POST']) ##redirecting to some other page after receiving info from first page
@cross_origin()
def scrapper():
    searchstr = request.form['searchstr'] ##retrieving search string entered by user
    searchstr = searchstr.replace(' ', '') ##removing white spaces
    try:
        hurl = urlopen('https://www.flipkart.com/search?q=' + searchstr)  ##Sending request to a webpage.Can use requests module as well.
        wpage = hurl.read() ##Fetching content of the page
        hurl.close() ##closing the connection
        ##wpage = requests.get('https://www.flipkart.com/search?q=' + searchstr).text
        parsedData = bs(wpage, 'html.parser') ##Getting data in proper HTML format
        divs = parsedData.find_all('div', {'class': '_1YokD2 _3Mn1Gg'}) ##Retrieving info from the content
        del divs[0] ##Delete unnecessary components
        allProds = divs[0].find_all('div', {'class': '_1AtVbE col-12-12'}) ##Retrieve all product divs from search result
        firstProd = allProds[0] ##select first and topmost relevant product matching search criteria
        firstUrl = 'https://www.flipkart.com' + firstProd.div.div.div.a['href'] ##setting the request url for first product
        firstRes = requests.get(firstUrl).text ##Getting page content for first product
        modifiedRes = bs(firstRes, 'html.parser') ##Cleaning the raw data

        allreviewUrlsList = modifiedRes.find('div', {'class': 'col JOpGWq'}).find_all('a') ##select "All reviews" link
        overallReviews = allreviewUrlsList[len(allreviewUrlsList) - 1] ##Omitting non-required entries
        totalReviews = int(overallReviews.div.span.text.split()[1]) ##Getting total no. of reviews for that particular product
        ##Taking care of an extra review page in case totalReviews is not a multiple of 10
        if totalReviews % 10 == 0:
            totalReviewPages = totalReviews // 10
        else:
            totalReviewPages = totalReviews // 10 + 1
        allReviews = [] ##Initialize an empty list object to store reviews
        for i in range(1, totalReviewPages + 1):
            singleReviewPage = requests.get(
                'https://www.flipkart.com' + overallReviews['href'] + '&page=' + str(i)).text ##Retrieving review pages one by one by appending '&page=i'
            pageHTML = bs(singleReviewPage, 'html.parser') ##Parsing HTML content
            reviewhtmls = pageHTML.find_all('div', {'class': '_1AtVbE col-12-12'}) ##Searching for review contents
            del reviewhtmls[0:4] ##removing unnecesary things
            del reviewhtmls[len(reviewhtmls) - 1]

            for ev in reviewhtmls: ##Looping through all 10 reviews
                try:
                    custName = ev.find('p', {'class': '_2sc7ZR _2V5EHH'}).text
                except:
                    custName = 'No Name'

                try:
                    custRating = ev.div.div.div.div.div.text
                except:
                    custRating = 'No Rating'

                try:
                    reviewDate = ev.find_all('p', {'class': '_2sc7ZR'})[1].text
                except:
                    reviewDate = 'No Date mentioned'

                try:
                    reviewHead = ev.div.div.div.p.text
                except:
                    reviewHead = 'Heading not available'

                try:
                    comment = ev.div.div.find('div', {'class': 't-ZTKy'}).div.div.text
                except:
                    comment = 'No Comments'

                reviewDict = dict(Product=searchstr, Name=custName, Rating=custRating, Date=reviewDate,
                                  Heading=reviewHead,
                                  Comment=comment) ##Saving a particular review
                allReviews.append(reviewDict) ##Storing dictionary objects

        return render_template('result.html', reviews=allReviews) ##Reveal all the reviews in a single page

    except:
        return 'Aw Snap! Error Encountered'


if __name__ == '__main__':
    final.run()
