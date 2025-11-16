import subprocess
import io

def tag(content: str, tag: str, params: dict = None) -> str:

    '''
    A function for tagging dinvidual content or blocks of code in XML.

    '''

    

    output = []

    supertag = True if '<' in content else False
    
    if supertag:
        # output.append('\n\t')
        content = '\n\t' + '\n\t'.join(content.split('\n'))

    
    param_list = [f' {k}="{v}"' for k,v in params.items()] if params else []

    if not content:
        return f"<{tag}{''.join(param_list)}/>"

    output.append(f"<{tag}{''.join(param_list)}>")
    output.append(content)
    if supertag:
        output.append('\n')
    output.append(f'</{tag}>')
    

    return ''.join(output)


class Syllable:

    '''
    Contains metadata for a single syllable (lyrics plus note glyph) and is able to parse it into kassia-compatible xml.
    '''

    def __init__(self, text, neumes_raw) -> None:
        self.text = text
        # self.params=params

        neumes = neumes_raw.replace(' ', '').split('-')
        self.neumes = neumes

    def render(self) -> str:
        lyric = tag(self.text, 'lyric')
        
        neume_group = []
        for nm in self.neumes:
            params = {}
            if nm.startswith('m'):
                params['type'] = 'martyria'

            if nm.startswith('f'):
                params['type'] = 'accidental'
            
            neume_render = tag(nm, 'neume', params)
            neume_group.append(neume_render)
        neume_group = '\n'.join(neume_group)
        neume_group = tag(neume_group, 'neume-group')

        syllable = lyric + '\n' + neume_group
        syllable = tag(syllable, 'syllable')

        return syllable

class Score:

    '''
    Contains the syllables and other metadata for a score (a single hymn) and can parse it into kassia-compatible xml.
    '''

    def __init__(self, syllables: list, mode: int = None, mode_base: str = None, dropcap:bool = True) -> None:

        self.dropcap = dropcap

        if mode not in list(range(1,9)) and mode is not None:
            raise Exception(f'Invalid mode: {mode}')
        
        self.mode = mode
        self.mode_base = mode_base

        if not syllables:
            raise Exception('No syllables provided!')

        for s in syllables:
            if not isinstance(s, Syllable):
                raise TypeError(f'Syllable provided not from class Syllable: {s}.')

        self.syllables = syllables

    def render_mode(
            self, 
            lang: str = 'CS', 
            size: int = 30, 
            font_family: str = "KA New Stathis Martyria"
        ) -> str:

        if self.mode is None:
            return ''

        mode_terms = {
            'CS': 'Гла́съ',
            'EL': ' Ἦχος',
            'EN': 'Mode'
        }

        mode_martyries = {
            1: 'i',
            2: 'o',
            3: 'π',
            4: '[',
            5: '/I',
            6: '/O',
            7: '/P',
            8: '{'
        }
        
        content = []
        content.append(mode_terms[lang])
        content.append(tag(
            mode_martyries[self.mode],
            'font',
            params={
                'font_family': font_family,
                'font_size': str(size)
            }
        ))

        if self.mode_base:
            content.append(self.mode_base)

        output = tag('\n'.join(content), 'para', params={'style':"h2"})

        return output


    def render(self) -> str:
        # output = []

        # if self.dropcap:
        #     output.append(
        #         tag(
        #             self.dropcap,
        #             'dropcap'
        #         )
        #     )

        rendered_syls = [s.render() for s in self.syllables]

        
        if self.dropcap:
            dropcap_letter = self.syllables[0].text[0] #first letter of first syllable
            dropcap_render = tag(dropcap_letter, 'dropcap')
            output = [dropcap_render] + rendered_syls
        else:
            output = rendered_syls

        content = '\n'.join(output)
        rend = tag(content, 'score')

        return rend

class Paragraph:

    def __init__(self, content: str, style: str) -> None:

        assert isinstance(content, str), 'Content must be a string.'
        assert isinstance(style, str), 'Style must be a string.'

        self.content = content
        self.style = style

    def render(self) -> str:
        output = tag(
            self.content,
            'para',
            params = {
                'style': self.style
            }
        )

        return output

class Music:

    '''
    Contains header, scores, paragraphs and other metadata and can parse those into a kassia-ready xml file.
    '''

    def __init__(
            self, 
            header: str,
            bnml_version="0.4"
        ) -> None:

        self.header = header
        self.bnml_version = bnml_version

        self.objects = []

    def add_object(self, object):
        
        assert isinstance(object, Paragraph) or isinstance(object, Score), 'Object passed must be of type Score or Paragraph'
        self.objects.append(object)

    def set_header(self, header: str):
        self.header = header

    def render(
            self,
            render_title_martyria = True
        ):

        music_content = []

        #hardcoding bottom page numbering. TODO: Develop a headers and footers infrastructure.
        music_content.append(
            tag(
                tag(
                    '',
                    'page-number',
                    {'align':'center'}
                ),
                'footer'
            )
        )


        for object in self.objects:
            if isinstance(object, Score) and render_title_martyria:
                music_content.append(object.render_mode())
            
            music_content.append(object.render())
        


        content = []
        content.append(self.header)
        content.append(
            tag(
                '\n'.join(music_content),
                'music'
            )
        )

        output = tag('\n'.join(content), 'bnml', params = {'bnml_version': self.bnml_version})

        return output
    
    def write_to_file(self, output_file: str):
        with open(output_file, 'wb') as f:
            f.write(self.render().encode())

    def write(self, buffer):
        buffer.write(self.render().encode())


def score_from_txt(raw_score:str):

    to_clean = [' ', '\n', '\t']
    for char in to_clean:
        raw_score = raw_score.replace(char, '')

    raw_params = raw_score.split('(')[1:]
    raw_params = [p[:p.find(')')] for p in raw_params]
    params = {v.split(':')[0]:v.split(':')[1] for v in raw_params}
    
    split = raw_score.split('[')
    split = split[1:]
    groups = [i[:i.find(']')] for i in split]

    syls = []
    for s in groups:
        s = s.split(':')
        lyr = s[0]
        neumes = s[1]
        syl = Syllable(lyr, neumes)
        syls.append(syl)

    base = params.get('base')
    mode = params.get('mode')

    if isinstance(mode, str) and mode.isdigit():
        mode = int(mode)

    score = Score(syls, mode = mode, dropcap = True, mode_base=base)

    return score

def para_from_txt(raw_para:str):

    # to_clean = [' ', '\n', '\t']
    # for char in to_clean:
    #     raw_para = raw_para.replace(char, '')

    
    raw_params = raw_para.split('(')[1:]
    raw_params = [p[:p.find(')')].strip() for p in raw_params]
    params = {v.split(':')[0].strip():v.split(':')[1].strip() for v in raw_params}
    
    content = raw_para.split(')')[-1].strip()

    style = params.get('style')
    if style is None:
        style =params.get('s')

    # print(style)

    para = Paragraph(
        content = content,
        style = style
    )

    return para

def music_from_txt(raw_music: str, header: str, separator: str = '---'):

    music = Music(header)
    raw_objects = raw_music.split(separator)

    for raw_obj in raw_objects:

        # extract metadata
        # TODO: Make more robust
        raw_params = raw_obj.split('(')[1:]
        raw_params = [p[:p.find(')')].strip() for p in raw_params]
        params = {v.split(':')[0]:v.split(':')[1] for v in raw_params}

        if 's' in params.keys() or 'style' in params.keys():
            obj_type = 'para'
            obj = para_from_txt(raw_obj)
        else:
            obj_type = 'score'
            obj = score_from_txt(raw_obj)

        music.add_object(obj)

    return music

