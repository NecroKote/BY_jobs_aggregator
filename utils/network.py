import urllib2


def download(url):
    data = ""

    try:
        response = urllib2.urlopen(url)
        data = response.read()

    except Exception, e:
        print e
        return None

    return data


class UrlBuilder:

    def Init(self, url=""):
        self.url = url
        self.params = []

        return self

    def CopyInit(self, url_builder):
        self.url = url_builder.url
        self.params = url_builder.params[:]

        return self

    def Build(self):
        ret = self.url

        if len(self.params) >= 1:
            ret += "?" + self.params[0]

        if len(self.params) > 1:
            ret += "&" + "&".join(self.params[1:])

        return ret

    def AddFilter(self, param, value):
        if param:
            self.params.append(param + "=" + value)

        return self


class DevBySearchBuilder(UrlBuilder):

    def Init(self):
        UrlBuilder.Init(self, url="http://jobs.dev.by/")
        return self

    def Build(self):
        ret = UrlBuilder.Build(self)
        return ret.replace("[", "%5B").replace("]", "%5D")

    def AddFilter(self, param, value):
        '''
        Available filters:
            page                [\d+]
            salary              [\d+-\d+]
            city                [Minsk=4429]
            user_level          [Junior=1|Mid=2|Senior=3]
            tech                [\w+]
        '''
        if param == 'page':
            return UrlBuilder.AddFilter(self, param, value)
        else:
            return UrlBuilder.AddFilter(self, "search-jobs[" + param + "]", value)


class JobsTutBySearchBuilder(UrlBuilder):

    def Init(self):
        '''Must be called first'''
        UrlBuilder.Init(self, url="http://jobs.tut.by/search/vacancy")

        #UrlBuilder.AddFilter(self, "currency_code", "USD")

        #UrlBuilder.AddFilter(self, "clusters", "true")
        #UrlBuilder.AddFilter(self, "from", "cluster_specialization")
        #UrlBuilder.AddFilter(self, "specialization", "1.221")
        # (1) IT - (221) Development

        return self

    def Build(self):
        return UrlBuilder.Build(self)

    def AddFilter(self, param, value):
        '''
        Available filters:
            page                [\d+]
            currency_code       [USB|BYR|RUR]
            salary              [\d+]
            only_with_salary    [true|false]
            area                [Minsk=1002]
            experience
                [noExperience|between1And3|between3And6|moreThan6]
            employment          [project|part|full]
            schedule            [fullDay|flexible|remote|shift]
        '''
        return UrlBuilder.AddFilter(self, param, value)
