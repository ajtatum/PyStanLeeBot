class SlackQueryResponse(object):
    
    fallback=""
    color="#ff2526"
    author_name="Stan Lee Bot"
    author_link="https://github.com/ajtatum/PyStanLeeBot"
    text=""
    title=""
    title_link=""
    image_url=""
    footer="Marvel"
    footer_icon="https://www.marvel.com/static/images/favicon/mstile-150x150.png"

    def __init__(self):
        pass

    def FromJson(self, json):
        total_items = json['queries']['request'][0]['totalResults']
        search_term = json['queries']['request'][0]['searchTerms']

        if total_items != "0":
            self.fallback = json['items'][0]['snippet'].replace('\n','')
            self.text = json['items'][0]['snippet'].replace('\n',''),
            self.title = json['items'][0]['title'],
            self.title_link = json['items'][0]['link'],
            self.image_url = json['items'][0]['pagemap']['metatags'][0]['og:image']
        else:
            self.fallback = "Unable to find anything about: {}".format(search_term)
            self.text = "Ut oh!"
            self.title = self.fallback
            self.title_link = "https://www.marvel.com/"
            self.image_url = self.footer_icon

    def ToText(self):
        return "*{}*\n{}\n{}\n{}".format(
                            " ".join(str(x) for x in self.title),
                            " ".join(str(x) for x in self.title_link),
                            " ".join(str(x) for x in self.text),
                            " ".join(str(x) for x in self.image_url)),

    def ToJson(self):
        attachments = [
                {
                    "fallback": "".join(str(x) for x in self.text),
                    "color": self.color,
                    "author_name": self.author_name,
                    "author_link": self.author_link,
                    "text": "".join(str(x) for x in self.text),
                    "title": "".join(str(x) for x in self.title),
                    "title_link": "".join(str(x) for x in self.title_link),
                    "image_url": "".join(str(x) for x in self.image_url),
                    "footer": self.footer,
                    "footer_icon": self.footer_icon,
                }
            ]

        return attachments