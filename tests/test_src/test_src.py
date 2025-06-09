import os

def test_src_folder_exists():
    assert os.path.isdir("src"), "Le dossier 'src' doit exister."

def test_main_modules_exist():
    expected = [
        "src/models",
        "src/repositories",
        "src/services",
        "src/api",
        "src/db",
    ]
    for path in expected:
        assert os.path.isdir(path), f"Le dossier '{path}' doit exister."

def test_init_files_exist():
    expected = [
        "src/__init__.py",
        "src/models/__init__.py",
        "src/repositories/__init__.py",
        "src/services/__init__.py",
        "src/api/__init__.py",
        "src/db/init_db.py",
    ]
    for path in expected:
        assert os.path.isfile(path), f"Le fichier '{path}' doit exister."

def test_tests_folder_exists():
    assert os.path.isdir("tests"), "Le dossier 'tests' doit exister."