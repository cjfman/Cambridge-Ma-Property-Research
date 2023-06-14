class Element:
    def __init__(self, tag, data=None, **kwargs):
        self.tag   = tag
        self.data  = data or ''
        self.attrs = { k.replace('_', '-'): v for k, v in kwargs.items() }

    def to_html(self):
        ## Handle data
        data = self.data
        if isinstance(data, list):
            data = "\n".join([x.to_html() for x in data])
        elif isinstance(data, Element):
            data = data.to_html()

        attrs = " " + " ".join([f'{k}="{v}"' for k, v in self.attrs.items()])
        if data:
            return f'<{self.tag}{attrs}>{data}</{self.tag}>'

        return f'<{self.tag}{attrs} />'


class LinearGradient(Element):
    def __init__(self, gradient, name=None):
        stops = []
        for i, color in enumerate(gradient.colors):
            offset = round((i + 1)/gradient.size*100, 5)
            stops.append(Element('stop', offset=f"{offset}%", stop_color=color))

        Element.__init__(self, 'lineargradient', stops, id=name)
