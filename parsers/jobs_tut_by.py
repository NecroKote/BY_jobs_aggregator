from lxml import html


class IndexParser:
    data = ""

    def do_parse(self, data):
        if not data:
            data = self.data

        if not data:
            return None

        root = html.document_fromstring(data.decode('utf-8'))
        props_premium = root.find_class('searchresult__cell m-searchresult__premium')
        props_standart = root.find_class('searchresult__cell m-searchresult_standard')
        props = props_premium + props_standart
        print "Props: %s (%s/%s)" % (len(props), len(props_premium), len(props_standart))

        ret = []
        for prop in props:
            # Basic info
            prop_info = prop.cssselect(
                'div.searchresult__name a.b-vacancy-list-link'
            ).pop()

            prop_name = prop_info.text
            prop_url = prop_info.get('href')

            # Salary
            salary_base = prop.cssselect('div.b-vacancy-list-salary')

            # Company
            #prop_company = prop.cssselect("div.searchresult__placetime a").pop().text
            prop_company = prop.cssselect('a[data-qa="vacancy-serp__vacancy-employer"]')
            if prop_company:
                prop_company = prop_company.pop().text
            else:
                prop_company = ""

            if len(salary_base):
                salary_base = salary_base.pop()
                salary = salary_base.cssselect('meta[itemprop="baseSalary"]').pop().get('content')
                salary_currency = salary_base.cssselect('meta[itemprop="salaryCurrency"]').pop().get('content')
            else:
                salary = ''
                salary_currency = ''
                salary_comments = ''

            ret.append( {
                'url': prop_url,
                'title': prop_name,
                'company': prop_company,
                'salary': salary,
                'currency': salary_currency
            } )

        return ret


def stringify_children(node):
    from lxml.etree import tostring, strip_tags

    strip_tags(node,'*')
    text = tostring(node, method='text', encoding=unicode)

    return text


class VacancyParser:
    data = ""

    def do_parse(self, data):
        if not data:
            data = self.data

        if not data:
            return None

        text = None

        root = html.document_fromstring(data.decode('utf-8'))
        description = root.find_class('b-vacancy-desc-wrapper')
        if len(description):
            description = description.pop()
            text = stringify_children(description)

        return text


