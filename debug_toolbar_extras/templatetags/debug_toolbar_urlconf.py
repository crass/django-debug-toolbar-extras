
from django import template
from django.core.urlresolvers import RegexURLResolver, RegexURLPattern
from django.utils.html import conditional_escape

register = template.Library()

@register.tag
def urlconf_display(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, urlpatterns = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    return URLconfDisplayNode(urlpatterns)

class URLconfDisplayNode(template.Node):
    def __init__(self, urlpatterns):
        self.urlpatterns = template.Variable(urlpatterns)
    
    def render(self, context):
        try:
            urlpatterns = self.urlpatterns.resolve(context)
            ret_html = self.__urlpatternsToHtml(urlpatterns)
            return '\n'.join(ret_html)
        except template.VariableDoesNotExist:
            return ''
    
    def __urlpatternsToHtml(self, urlpatterns):
        html = []
        html.append("<ol>")
        for pattern in urlpatterns:
            html.append("<li>")
            html.append(conditional_escape(pattern.regex.pattern))
            if isinstance(pattern, RegexURLResolver):
                html.append("(%s:%s)" % (pattern.app_name, pattern.namespace))
                html += self.__urlpatternsToHtml(pattern.url_patterns)
            elif isinstance(pattern, RegexURLPattern):
                if pattern.name:
                    html.append("[name='%s']" % pattern.name)
            else:
                html.append("Error: Pattern %s not valid" % pattern)
            html.append("</li>")
        html.append("</ol>")
        return html
