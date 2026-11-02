#!/usr/bin/env python3
"""Validate the static GitHub assets, source provenance and exact profile facts."""
from pathlib import Path
import hashlib
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_HASH='06b519e1c5050caa06157802d2cf1f0f76cdcd4bed549452c0b83f309f7fe8d6'
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
 assert len(ascii_lines)==128 and max(map(len,ascii_lines))==144
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
  for node in root.iter():
   assert not any(key.endswith('href') for key in node.attrib),'External resource reference found'
  print('PASS:',file,'— all exact facts; ASCII portrait; no scripts, raster or external resources')
 readme=(ROOT/'README.md').read_text()
 assert '<source media="(max-width: 768px)"' in readme
 for path in re.findall(r'(?:src|srcset)="([^"]+)"',readme):assert (ROOT/path).is_file(),path
 assert 'https://instagram.com/juan_stein' in readme
 assert 'mailto:juanpablomoraisstein@gmail.com' in readme
 print('PASS: original photo hash, 144×128 ASCII, responsive sources, accessible text and contact links')

if __name__=='__main__':main()
