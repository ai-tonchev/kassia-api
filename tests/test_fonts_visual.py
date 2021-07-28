from pathlib import Path
from diff_pdf_visually import pdfdiff
from kassia import Kassia

def test_chronos(tmp_path: Path):
    output_file_path: str = str(tmp_path) + "/chronos_test_new.pdf"
    Kassia("tests/chronos_test.xml", output_file_path)
    assert pdfdiff("tests/chronos_test.pdf", output_file_path)

def test_dash(tmp_path: Path):
    output_file_path: str = str(tmp_path) + "/dash_test_new.pdf"
    Kassia("tests/dash_test.xml", output_file_path)
    assert pdfdiff("tests/dash_test.pdf", output_file_path)

def test_dropcap(tmp_path: Path):
    output_file_path: str = str(tmp_path) + "/dropcap_test_new.pdf"
    Kassia("tests/dropcap_test.xml", output_file_path)
    assert pdfdiff("tests/dropcap_test.pdf", output_file_path)

def test_fthora(tmp_path: Path):
    output_file_path: str = str(tmp_path) + "/fthora_test_new.pdf"
    Kassia("tests/fthora_test.xml", output_file_path)
    assert pdfdiff("tests/fthora_test.pdf", output_file_path)

def test_martyria(tmp_path: Path):
    output_file_path: str = str(tmp_path) + "/martyria_test_new.pdf"
    Kassia("tests/martyria_test.xml", output_file_path)
    assert pdfdiff("tests/martyria_test.pdf", output_file_path)

def test_underscore(tmp_path: Path):
    output_file_path: str = str(tmp_path) + "/underscore_test_new.pdf"
    Kassia("tests/underscore_test.xml", output_file_path)
    assert pdfdiff("tests/underscore_test.pdf", output_file_path)

def test_examples(tmp_path: Path):
    output_file_path: str = str(tmp_path) + "/sample.pdf"
    Kassia("examples/sample.xml", output_file_path)
    assert pdfdiff("examples/sample.pdf", output_file_path)

    output_file_path: str = str(tmp_path) + "/sample2.pdf"
    Kassia("examples/sample2.xml", output_file_path)
    assert pdfdiff("examples/sample2.pdf", output_file_path)
