#!/usr/bin/python
import os
import logging
from pathlib import Path
from sys import platform
from typing import Dict, List

from reportlab.lib import fontfinder
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, TTFError

from ruamel.yaml import safe_load, YAMLError
from schema import Schema, And, Optional, SchemaError

font_classes_schema = Schema({
            'family_name': str,
            'takes_lyric': [str],
            'standalone': [str],
            Optional('keep_with_next'): [str],
            Optional('lyric_offsets'): {str: float},
            Optional('accidentals'): [str],
            Optional('martyriae'): [str],
            Optional('tempo_markings'): [str],
            Optional('chronos'): [str],
            Optional('rests'): [str],
            Optional('optional_ligatures'): {str: {And('name'): str, And('component_glyphs'): str}},
            Optional('conditional_neumes'): {str: {And('base_neume'): list, And('component_glyphs'): list, And('replace_glyph'): str, And('draw_glyph'): str}},
        })

font_glyphnames_schema = Schema({
            str: {
                And('family'): str,
                And('codepoint'): str,
                Optional('component_glyphs'): [str],
                Optional('description'): str,
            },
        })


def register_fonts(check_sys_fonts=False) -> Dict:
    """Registers fonts by checking the local font directory and system installed fonts.
    
    :param check_sys_fonts: Whether function should search system folders for fonts.
    :returns: Dict of font configs for all discovered fonts.
    """
    dirs = []

    # Always check local kassia font folder first so that included fonts will have precedence over system fonts
    internal_font_path = os.path.join(str(Path.cwd()), 'fonts')

    neume_font_configs = _get_neume_dict(internal_font_path)
    dirs.append(internal_font_path)

    if check_sys_fonts:
        dirs.extend(_get_system_font_paths())

    for path in dirs:
        register_font_path(path)

    return neume_font_configs


def _get_system_font_paths() -> List[str]:
    """Return list of system font paths, depending on detected OS.

    :return: List of system font paths.
    """
    if platform.startswith('darwin'):
        return ['/Library/Fonts', os.path.expanduser('~/Library/Fonts')]
    elif platform.startswith('win') or platform.startswith('cygwin'):
        return [os.path.join(os.environ['WINDIR'], 'Fonts')]
    elif platform.startswith('linux'):
        return ['/usr/share/fonts', os.path.expanduser('~/.fonts'), os.path.expanduser('~/.local/share/fonts')]


def _get_neume_dict(font_folder_path: str) -> Dict:
    """Search folder path for font configs, load them, and return in Dict.
    """
    font_config_dict = {}
    for glyphname_path in Path(font_folder_path).rglob('glyphnames.yaml'):
        folder = glyphname_path.parent.name
        classes_path = Path.joinpath(glyphname_path.parent, 'classes.yaml')
        font_config = {'glyphnames': _read_font_config(str(glyphname_path), font_glyphnames_schema),
                       'classes': _read_font_config(str(classes_path), font_classes_schema)}
        font_config_dict[folder] = font_config
    return font_config_dict


def _read_font_config(filepath: str, validator: Schema) -> Dict:
    """Read, load, and validate a font configuration, and return it as a Dict.
    """
    font_config = None
    with open(filepath, 'r') as fp:
        try:
            font_config = safe_load(fp)
            validator.validate(font_config)
        except (IOError, YAMLError, SchemaError) as exc:
            logging.error("Problem reading {} font configuration. {}".format(filepath, exc))
            font_config = None
        except Exception as exc:
            raise exc
    return font_config


def register_font_path(font_path: str):
    """Search font_path for TTF's and register them.
    
    Registers discovered fonts as part of family if multiple weights are found.
    ReportLab usually keeps a cache after searching a directory.
    I have this cache disabled because it doesn't seem to work correcty.

    :param font_path: Path to search for fonts.
    """
    ff = fontfinder.FontFinder(useCache=False)
    ff.addDirectory(font_path, recur=True)

    try:
        ff.search()
    except (KeyError, Exception) as fferror:
        logging.warning("Problem parsing font: {}".format(fferror))

    for family_name in ff.getFamilyNames():
        fonts_in_family = ff.getFontsInFamily(family_name)
        for font in fonts_in_family:
            if len(fonts_in_family) == 1:
                try:
                    ttfont = TTFont(family_name.decode("utf-8"), font.fileName)
                    pdfmetrics.registerFont(ttfont)
                    pdfmetrics.registerFontFamily(family_name)
                except TTFError as e:
                    logging.warning("Could not register font {}, {}".format(family_name, e))
                    continue
            elif len(fonts_in_family) > 1:
                '''If font family has multiple weights/styles'''
                font_name = family_name + "-".encode() + font.styleName
                font_name = font_name.decode("utf-8")
                try:
                    ttfont = TTFont(font_name, font.fileName)
                    pdfmetrics.registerFont(ttfont)
                    addMapping(font.familyName, font.isBold, font.isItalic, font_name)
                except TTFError as e:
                    logging.warning("Could not register font {}, {}".format(family_name, e))
                    continue


def is_registered_font(font_name: str) -> bool:
    """Return whether passed font is registered.

    :param font_name: Name of font to check within registered fonts.
    """
    return font_name in pdfmetrics.getRegisteredFontNames()
