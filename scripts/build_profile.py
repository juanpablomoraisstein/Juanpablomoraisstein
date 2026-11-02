#!/usr/bin/env python3
"""Sample Juan's source photograph into ASCII and render self-contained SVGs."""
from __future__ import annotations
from pathlib import Path
from html import escape
import hashlib
import random
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/source/portrait.png'
FONT = "'Liberation Mono', 'DejaVu Sans Mono', Consolas, 'Courier New', monospace"
COLORS = {'bg':'#0c111b','panel':'#101723','bar':'#141d2b','border':'#293547','text':'#e6edf3',
          'muted':'#8796ac','dim':'#53647c','blue':'#66aaff','cyan':'#68d9e9','orange':'#f4ae72'}
# Coordinates refer to the new 960 x 1280 mirror photograph.
CROP = (0, 230, 960, 1280)
# Separate shapes retain the curtain gap between the face and the phone.
SILHOUETTES = [
 [(0,470),(18,416),(51,375),(103,336),(165,301),(216,289),(275,295),
  (333,316),(384,345),(425,388),(457,439),(468,482),(457,527),
  (445,566),(451,606),(447,653),(436,704),(424,754),(406,806),
  (394,844),(421,857),(455,868),(491,892),(552,942),(616,1011),
  (660,1123),(682,1280),(0,1280),(0,990),(46,963),(92,937),
  (131,912),(145,881),(145,841),(131,799),(111,752),(98,732),
  (74,746),(45,733),(30,706),(21,671),(20,638),(11,615),(0,606)],
 [(518,886),(515,743),(506,707),(510,684),(526,668),
  (515,650),(515,591),(525,563),(545,545),(577,537),(736,532),
  (775,540),(797,559),(811,586),(813,875),(839,925),(889,972),
  (960,1041),(960,1280),(744,1280),(702,1243),(673,1215),
  (635,1202),(594,1187),(563,1168),(537,1137),(515,1100),
  (502,1058),(480,1038),(469,1009),(471,982),(490,970),
  (482,951),(468,932),(465,910),(476,890),(497,880)]
]
COLS = 144
ADVANCE = 448 / COLS
LINE = 650 / 128
ROWS = round((CROP[3]-CROP[1])/(CROP[2]-CROP[0])*COLS*ADVANCE/LINE)
RAMP = ' .,:;!iIl1tfjr/\\|()[]{}<>+*rxnvuzXYUJCLQ0OZmwqpdbkhao#MW&8%B@$'


def calibrated_glyphs():
    candidates = [Path('/usr/share/fonts/liberation/LiberationMono-Regular.ttf'),
                  Path('C:/Windows/Fonts/consola.ttf'),
                  Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')]
    font_path = next((p for p in candidates if p.is_file()), None)
    if font_path is None:
        raise SystemExit('Install Liberation Mono / DejaVu Sans Mono, or supply Consolas on Windows.')
    font = ImageFont.truetype(str(font_path), 24)
    values = []
    for char in dict.fromkeys(RAMP):
        tile = Image.new('L', (15, 30))
        ImageDraw.Draw(tile).text((0, 0), char, fill=255, font=font)
        values.append((sum(tile.tobytes())/(255*15*30), char))
    return sorted(values)

INFO = [
 ('Name', ['Juan Pablo Morais Stein']),
 ('Age', ['18 years old']),
 ('Location', ['Gaspar, Santa Catarina, Brazil']),
 ('Education', ['Computer Science Student at FURB']),
 ('OS', ['Omarchy / Arch Linux']),
 ('Editor', ['Visual Studio Code']),
 ('Focus', ['Web Development']),
 ('Programming Languages', ['Java']),
 ('Languages', ['Portuguese (Native)']),
]


def portrait():
    source = Image.open(SOURCE).convert('RGB')
    mask = Image.new('L', source.size)
    for silhouette in SILHOUETTES:
        ImageDraw.Draw(mask).polygon(silhouette, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(5))
    cut = source.crop(CROP)
    matte = mask.crop(CROP).resize((COLS,ROWS),Image.Resampling.LANCZOS)
    gray = ImageOps.autocontrast(ImageOps.grayscale(cut),cutoff=(1,1))
    gray = ImageEnhance.Contrast(gray).enhance(1.22)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=8, percent=130, threshold=3))
    tone = gray.resize((COLS,ROWS),Image.Resampling.LANCZOS)
    # The actual photo supplies the geometry and every tonal sample.
    chars, inks = [], []
    glyphs=calibrated_glyphs()
    for row in range(ROWS):
        text, colors = '', []
        for col in range(COLS):
            alpha = matte.getpixel((col,row))/255
            value = (tone.getpixel((col,row))/255)**.65
            if alpha < .4:
                text += ' ';colors.append(None);continue
            ink = (.14 + .86*value**.8)*glyphs[-1][0]
            char = min(glyphs,key=lambda item:abs(item[0]-ink))[1]
            text += char
            # Cool hair/shadows, warm face highlights: restrained terminal colors.
            stops = [(89,126,164),(116,169,195),(166,199,207),(217,207,188),(248,225,195)]
            bucket = min(4,int(value*5))
            rgb=stops[bucket]
            # Feather the real shoulder/neck outline instead of cutting a hard edge.
            strength=min(1,alpha/.95)
            rgb=tuple(round(bg+(fg-bg)*strength) for bg,fg in zip((13,20,31),rgb))
            colors.append('#%02x%02x%02x'%rgb)
        chars.append(text.rstrip());inks.append(colors)
    return chars,inks


def text(x,y,value,size=18,fill=None,weight=None,extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill or COLORS["text"]}"'+(f' font-weight="{weight}"' if weight else '')+f' {extra}>{escape(value)}</text>'


def ascii_group(chars,inks,x,y,scale=1):
    elements=[f'<g aria-label="ASCII portrait converted from Juan’s own photograph" transform="translate({x} {y}) scale({scale})" font-size="5.185185" xml:space="preserve">']
    for row,line in enumerate(chars):
        spans=[];start=0
        while start < len(line):
            color=inks[row][start];end=start+1
            while end<len(line) and inks[row][end]==color:end+=1
            segment=line[start:end]
            if color and segment.strip():
                positions=' '.join(f'{index*ADVANCE:g}' for index in range(start,end))
                spans.append(f'<tspan x="{positions}" fill="{color}">{escape(segment)}</tspan>')
            start=end
        elements.append(f'<text y="{row*LINE:g}">'+''.join(spans)+'</text>')
    elements.append('</g>');return '\n'.join(elements)


def source_points(points):
    return ' '.join(f'{(x-CROP[0])/(CROP[2]-CROP[0])*448:.2f},{(y-CROP[1])/(CROP[3]-CROP[1])*ROWS*LINE:.2f}' for x,y in points)


def matrix_defs(width,height,mobile):
    # Fade the rain behind the information; keep the portrait and text in front.
    gradient = ('<linearGradient id="rain-strength" x1="0" y1="0" x2="0" y2="1">'
                '<stop offset="0" stop-color="white"/><stop offset="0.40" stop-color="white"/>'
                '<stop offset="0.45" stop-color="white" stop-opacity=".07"/>'
                '<stop offset="1" stop-color="white" stop-opacity=".07"/></linearGradient>') if mobile else (
                '<linearGradient id="rain-strength"><stop offset="0" stop-color="white"/>'
                '<stop offset=".41" stop-color="white"/><stop offset=".45" stop-color="white" stop-opacity=".07"/>'
                '<stop offset="1" stop-color="white" stop-opacity=".07"/></linearGradient>')
    result = [gradient,
       f'<clipPath id="rain-bounds"><rect x="18" y="137" width="{width-36}" height="{height-208}" rx="8"/></clipPath>',
       f'<mask id="rain-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="{width}" height="{height}"><rect width="{width}" height="{height}" fill="url(#rain-strength)"/></mask>']
    return ''.join(result)


def binary_stream(x,y,step,count,rng,animated=False,distance=0,duration=12,opacity=.4,size=12):
    digits=''.join(rng.choice('01') for _ in range(count))
    spans=''.join(f'<tspan x="{x:g}" y="{y+i*step:g}" fill="{("#99ffbf" if i==count-1 else "#31d971")}" opacity="{.22+.78*(i/(count-1))**1.8:.2f}">{digit}</tspan>' for i,digit in enumerate(digits))
    animation=(f'<animateTransform attributeName="transform" type="translate" from="0 {-count*step-40:g}" '
               f'to="0 {distance:g}" dur="{duration:g}s" begin="{-rng.uniform(0,duration):.2f}s" repeatCount="indefinite"/>') if animated else ''
    return f'<g opacity="{opacity}" font-size="{size}">{animation}<text>{spans}</text></g>'


def matrix_background(width,height,mobile):
    rng=random.Random(7319)
    output=['<g id="matrix-rain" aria-label="Subtle falling green binary digits" clip-path="url(#rain-bounds)" mask="url(#rain-mask)">']
    for animated,klass in [(True,'rain-motion'),(False,'rain-still')]:
        output.append(f'<g class="{klass}">')
        # Deliberately sparse so this reads as a terminal rather than a wallpaper.
        for x in range(31,width-22,26):
            count=rng.randrange(12,25)
            y=0 if animated else rng.randrange(160,height-260)
            output.append(binary_stream(x,y,19,count,rng,animated,height-130,
                rng.randrange(14,25),rng.uniform(.42,.68),14))
        output.append('</g>')
    output.append('</g>');return ''.join(output)


def portrait_knockout(x,y):
    # The rain passes behind the real silhouette, never through the face/neck.
    shapes=''.join(f'<polygon points="{source_points(shape)}" fill="#0d1420"/>' for shape in SILHOUETTES)
    return f'<g transform="translate({x} {y})">{shapes}</g>'


def header(width):
    return f'''<rect x="1" y="1" width="{width-2}" height="64" rx="17" fill="{COLORS['bar']}"/>
<path d="M1 48H{width-1}V65H1Z" fill="{COLORS['bar']}"/>
<path d="M1 65H{width-1}" stroke="{COLORS['border']}"/>
<circle cx="29" cy="32" r="5" fill="#ed8b8b"/>
<circle cx="49" cy="32" r="5" fill="#e9bd76"/>
<circle cx="69" cy="32" r="5" fill="#8dbb9f"/>
{text(width/2,38,'juan — ~',15,COLORS['muted'],extra='text-anchor="middle"')}
{text(width-28,38,'UTF-8',12,COLORS['dim'],extra='text-anchor="end"')}'''


def svg(chars,inks,mobile=False):
    width,height=(720,1887) if mobile else (1240,900)
    out=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">Juan Pablo Morais Stein — terminal profile</title>
<desc id="desc">Neofetch-inspired profile. ASCII portrait sampled from Juan's photograph, including his hairstyle, earbud and phone. Juan is 18 years old, from Gaspar, Santa Catarina, Brazil; a Computer Science Student at FURB focused on Web Development with Java. OS: Omarchy / Arch Linux. Editor: Visual Studio Code. Languages: Portuguese (Native). Instagram: @juan_stein. Email: juanpablomoraisstein@gmail.com.</desc>
<defs><linearGradient id="surface" x2="0" y2="1"><stop stop-color="#101825"/><stop offset="1" stop-color="#0b1019"/></linearGradient>{matrix_defs(width,height,mobile)}</defs>
<style>.rain-still {{ display:none }} @media (prefers-reduced-motion: reduce) {{ .rain-motion {{ display:none }} .rain-still {{ display:inline }} }}</style>
<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="17" fill="url(#surface)" stroke="{COLORS['border']}" stroke-width="2"/>
<g font-family="{FONT}">
{header(width)}''']
    out += [text(32 if mobile else 42,108,'juan@arch',19,COLORS['cyan'],weight=700),
            text(145 if mobile else 155,108,'~',19,COLORS['orange']),
            text(171 if mobile else 181,108,'$ neofetch',19,COLORS['text'])]
    if mobile:
        out.append(matrix_background(width,height,True))
        out.append(portrait_knockout(136,156))
        out.append(ascii_group(chars,inks,136,156,1.0))
        out.append(f'<path d="M36 824H684" stroke="{COLORS["border"]}"/>')
        x,y=36,878
        out += [text(x,y,'juan@github',30,COLORS['cyan'],700),text(x,y+28,'-----------',25,COLORS['muted'])]
        cursor=y+70
        for label,values in INFO:
            out.append(text(x,cursor,label+':',21,COLORS['blue'],700))
            out.append(text(x,cursor+32,values[0],24))
            cursor+=77
        out += [text(x,cursor+13,'Contact',25,COLORS['orange'],700),text(x,cursor+52,'Instagram:',21,COLORS['blue'],700),text(x+164,cursor+52,'@juan_stein',24),text(x,cursor+90,'Email:',21,COLORS['blue'],700),text(x,cursor+122,'juanpablomoraisstein@gmail.com',24)]
        bottom=cursor+174
        # Derive the height from the content to keep the mobile layout compact.
        height=bottom+72
        out[0]=out[0].replace('height="1780"','height="'+str(height)+'"').replace('0 0 720 1780','0 0 720 '+str(height)).replace('height="1778"','height="'+str(height-2)+'"')
        out.append(text(x,bottom,'$ _',22,COLORS['cyan']))
    else:
        out.append(matrix_background(width,height,False))
        out.append(portrait_knockout(44,176))
        out.append(ascii_group(chars,inks,44,176,1.0))
        out.append(f'<path d="M530 163V811" stroke="{COLORS["border"]}"/>')
        x,y=570,179
        out += [text(x,y,'juan@github',27,COLORS['cyan'],700),text(x,y+28,'-----------',22,COLORS['muted'])]
        cursor=y+81
        for label,values in INFO:
            if label=='Programming Languages':
                out.append(text(x,cursor,label+':',21,COLORS['blue'],700));out.append(text(x+315,cursor,values[0],21))
            else:
                out.append(text(x,cursor,label+':',21,COLORS['blue'],700));out.append(text(x+143,cursor,values[0],21))
            cursor+=43
        out += [text(x,cursor+19,'Contact',21,COLORS['orange'],700),
                text(x,cursor+60,'Instagram:',21,COLORS['blue'],700),text(x+143,cursor+60,'@juan_stein',21),
                text(x,cursor+99,'Email:',21,COLORS['blue'],700),text(x+143,cursor+99,'juanpablomoraisstein@gmail.com',21)]
        out.append(text(44,857,'$ _',19,COLORS['cyan']))
        out.append(text(width-40,857,'OMARCHY / ARCH LINUX',12,COLORS['dim'],extra='text-anchor="end"'))
    out.append('</g></svg>');return '\n'.join(out)


def main():
    chars,inks=portrait()
    (ROOT/'assets/portrait.txt').write_text('\n'.join(chars)+'\n',encoding='utf-8')
    (ROOT/'assets/terminal-desktop.svg').write_text(svg(chars,inks),encoding='utf-8')
    (ROOT/'assets/terminal-mobile.svg').write_text(svg(chars,inks,True),encoding='utf-8')
    print(f'Built {COLS} × {ROWS} ASCII from {SOURCE.name}; photo SHA-256 {hashlib.sha256(SOURCE.read_bytes()).hexdigest()}')

if __name__=='__main__':main()
