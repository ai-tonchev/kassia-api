#!/usr/bin/python
import logging
import os
from pathlib import Path
from typing import Dict

from reportlab import rl_settings
from reportlab.lib import fontfinder
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFError, TTFont
from ruyaml import YAML, YAMLError
from schema import And, Optional, Schema, SchemaError

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
    Optional('conditional_neumes'): {str: {And('base_neume'): list, And('component_glyphs'):
                                           list, And('replace_glyph'): str, And('draw_glyph'): str}},
})

font_glyphnames_schema = Schema({
    str: {
        And('family'): str,
        And('codepoint'): str,
        Optional('component_glyphs'): [str],
        Optional('description'): str,
    }
})


def _get_neume_dict(font_folder_path: str) -> Dict:
    """Search folder path for font configs, load them, and return in Dict.

    :param font_folder_path: Path to font.
    :return: Dictionary representation of yaml config file.
    """
    font_config_dict = {}
    for glyphname_path in Path(font_folder_path).rglob('glyphnames.yaml'):
        folder = glyphname_path.parent.name
        classes_path = Path.joinpath(glyphname_path.parent, 'classes.yaml')
        font_config = {'glyphnames': _load_font_config(str(glyphname_path), font_glyphnames_schema),
                       'classes': _load_font_config(str(classes_path), font_classes_schema)}
        font_config_dict[folder] = font_config
    return font_config_dict


def _load_font_config(filepath: str, validator: Schema) -> Dict:
    """Read, load, and validate a font configuration (in YAML), and return it as a Dict.

    :param filepath: Path of font config file.
    :param validator: Schema to validate against.
    :return: Font configuration as a dictionary.
    """
    font_config = None
    with open(filepath, 'r') as fp:
        try:
            yaml = YAML(typ='safe', pure=True)
            font_config = yaml.load(fp)
            validator.validate(font_config)
        except (IOError, YAMLError, SchemaError) as exc:
            logging.error("Failed to read {} font configuration. {}".format(filepath, exc))
            font_config = None
        except Exception as exc:
            raise exc
    return font_config


def find_and_register_fonts(check_sys_fonts: bool = False) -> Dict:
    """Search for fonts and register them.

    If check_sys_fonts is false, function will only use fonts in local
    /fonts folder.

    :param check_sys_fonts: Whether to search system for fonts.
    :return: Font configuration as a dictionary.
    """
    ff = fontfinder.FontFinder(useCache=False)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_font_dir = os.path.join(str(base_dir), 'kassia/fonts/')
    logging.info("Searching {} path for local fonts...".format(local_font_dir))
    
    ff.addDirectory(local_font_dir, recur=True)

    if check_sys_fonts:
        system_font_dirs = rl_settings.TTFSearchPath
        ff.addDirectory(system_font_dirs, recur=True)

    try:
        ff.search()
    except (KeyError, Exception) as fferror:
        logging.warning("Font search exception: {}".format(fferror))

    _register_fonts(ff)

    return _get_neume_dict(local_font_dir)


def _register_fonts(font_finder: fontfinder.FontFinder):
    """Search font_path for TTF's and register them.

    Registers discovered fonts as part of family if multiple weights are found.
    ReportLab usually keeps a cache after searching a directory.
    I have this cache disabled because it doesn't seem to work correctly.
    If only one font in family, use family name as font name, otherwise
    use familyname-fontface.

    :param font_finder: Path to search for fonts.
    """
    for family_name in font_finder.getFamilyNames():
        fonts_in_family = font_finder.getFontsInFamily(family_name)
        for font in fonts_in_family:
            if len(fonts_in_family) == 1:
                try:
                    ttfont = TTFont(family_name.decode("utf-8"), font.fileName)
                    pdfmetrics.registerFont(ttfont)
                    pdfmetrics.registerFontFamily(family_name)
                except TTFError as e:
                    logging.warning("Failed to register font {}, {}".format(family_name, e))
                    continue
            elif len(fonts_in_family) > 1:
                font_name = family_name + "-".encode() + font.styleName
                font_name = font_name.decode("utf-8")
                try:
                    ttfont = TTFont(font_name, font.fileName)
                    pdfmetrics.registerFont(ttfont)
                    addMapping(font.familyName, font.isBold, font.isItalic, font_name)
                except TTFError as e:
                    logging.warning("Failed to register font {}, {}".format(family_name, e))
                    continue


def is_registered_font(font_name: str) -> bool:
    """Return whether passed font is registered.

    :param font_name: Name of font to check within registered fonts.
    """
    return font_name in pdfmetrics.getRegisteredFontNames()
