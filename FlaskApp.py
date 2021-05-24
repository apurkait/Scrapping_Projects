from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup as bs

final = Flask(__name__)
CORS(final)


@final.route('/', methods=['GET'])
@cross_origin()
def index():
    return render_template('index.html')


@final.route('/reviews', methods=['POST'])
@cross_origin()
def scrapper():
    searchstr = request.form['searchstr']
    searchstr = searchstr.replace(' ', '')
    try:
        hurl = urlopen('https://www.flipkart.com/search?q=' + searchstr)  ##Can use requests module as well
        wpage = hurl.read()
        hurl.close()
        ##wpage = requests.get('https://www.flipkart.com/search?q=' + searchstr).text
        parsedData = bs(wpage, 'html.parser')
        divs = parsedData.find_all('div', {'class': '_1YokD2 _3Mn1Gg'})
        del divs[0]
        allProds = divs[0].find_all('div', {'class': '_1AtVbE col-12-12'})
        firstProd = allProds[0]
        firstUrl = 'https://www.flipkart.com' + firstProd.div.div.div.a['href']
        firstRes = requests.get(firstUrl).text
        modifiedRes = bs(firstRes, 'html.parser')

        allreviewUrlsList = modifiedRes.find('div', {'class': 'col JOpGWq'}).find_all('a')
        overallReviews = allreviewUrlsList[len(allreviewUrlsList) - 1]
        totalReviews = int(overallReviews.div.span.text.split()[1])
        if totalReviews % 10 == 0:
            totalReviewPages = totalReviews // 10
        else:
            totalReviewPages = totalReviews // 10 + 1
        allReviews = []
        for i in range(1, totalReviewPages + 1):
            singleReviewPage = requests.get(
                'https://www.flipkart.com' + overallReviews['href'] + '&page=' + str(i)).text
            pageHTML = bs(singleReviewPage, 'html.parser')
            reviewhtmls = pageHTML.find_all('div', {'class': '_1AtVbE col-12-12'})
            del reviewhtmls[0:4]
            del reviewhtmls[len(reviewhtmls) - 1]

            for ev in reviewhtmls:
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
                                  Comment=comment)
                allReviews.append(reviewDict)

        return render_template('result.html', reviews=allReviews)
    except:
        return 'Aw Snap! Error Encountered'


'''if __name__ == '__main__':
    final.run()'''
