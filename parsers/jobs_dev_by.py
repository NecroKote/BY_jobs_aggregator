from lxml import html


class IndexParser:
    data = ""

    def do_parse(self, data):
        if not data:
            data = self.data

        if not data:
            return None

        root = html.document_fromstring(data.decode('utf-8'))
        props = root.cssselect('div.item-jobs')

        print "Props: %s" % len(props)

        ret = []
        for prop in props:
            # Basic info
            prop_info = prop.cssselect('div.panel-top div.clearfix h3 a').pop()
            prop_name = prop_info.text
            prop_url = 'http://jobs.dev.by' + prop_info.get('href')

            # Salary
            #salary_base = prop.cssselect('div.b-vacancy-list-salary')

            # Company
            prop_company = prop.cssselect("div.panel-top strong a").pop().text

            salary = ''
            salary_currency = ''

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
        description = root.find_class('data-desc blog-node-content')
        if len(description):
            description = description.pop()
            text = stringify_children(description)

        return text


