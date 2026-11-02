#!/usr/bin/env python3
"""Validate the static GitHub assets, source provenance and exact profile facts."""
from pathlib import Path
import hashlib
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_HASH='894ef0f512530349742e5a25d526f749228ca00edc11f73e80de5641cd498436'
EXPECTED=[
 'juan@github','Juan Pablo Morais Stein','18 years old',
 'Gaspar, Santa Catarina, Brazil','Computer Science Student at FURB',
 'Omarchy / Arch Linux','Visual Studio Code','Web Development','Java',
 'Portuguese (Native)','Contact','@juan_stein','juanpablomoraisstein@gmail.com',
 'Name:','Age:','Location:','Education:','OS:','Editor:','Focus:',
 'Programming Languages:','Languages:','Instagram:','Email:'
]
NS='{http://www.w3.org/2000/svg}'

def main():
 assert hashlib.sha256((ROOT/'assets/source/portrait.png').read_bytes()).hexdigest()==EXPECTED_HASH,'Source photo differs from original upload'
 ascii_lines=(ROOT/'assets/portrait.txt').read_text().splitlines()
 assert len(ascii_lines)==96 and max(map(len,ascii_lines))==144
 assert all(ord(char)<128 for line in ascii_lines for char in line),'Not literal ASCII'
 for file in ('terminal-desktop.svg','terminal-mobile.svg'):
  path=ROOT/'assets'/file
  root=ET.parse(path).getroot()
  assert root.tag==NS+'svg' and root.get('viewBox')
  assert root.find(NS+'title') is not None and root.find(NS+'desc') is not None
  info=[node.text for node in root.iter(NS+'text') if node.text]
  for value in EXPECTED:assert value in info,(file,value)
  assert not any(root.iter(NS+'image')),'A raster image is embedded in the SVG'
  assert not any(root.iter(NS+'foreignObject'))
  assert not any(root.iter(NS+'script'))
  assert len(list(root.iter(NS+'tspan')))>500,'Portrait is missing'
  ids={node.get('id') for node in root.iter()}
  assert {'matrix-rain'}.issubset(ids)
  assert 'lens-reflections' not in ids,'Old sunglasses reflection remains on the new photo'
  assert len(list(root.iter(NS+'animateTransform')))>20,'Binary rain animation is missing'
  assert 'prefers-reduced-motion' in path.read_text()
  for node in root.iter():
   assert not any(key.endswith('href') for key in node.attrib),'External resource reference found'
  print('PASS:',file,'— all exact facts; ASCII portrait; no scripts, raster or external resources')
 readme=(ROOT/'README.md').read_text()
 assert '<source media="(max-width: 768px)"' in readme
 for path in re.findall(r'(?:src|srcset)="([^"]+)"',readme):assert (ROOT/path).is_file(),path
 assert 'https://instagram.com/juan_stein' in readme
 assert 'mailto:juanpablomoraisstein@gmail.com' in readme
 print('PASS: original photo hash, 144×96 ASCII, responsive sources, accessible text and contact links')

if __name__=='__main__':main()
