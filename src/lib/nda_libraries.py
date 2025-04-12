import os

def nda_libraries_available():
    current_dir = os.sep.join(__file__.split(os.sep)[:-1])
    nda_lib_dir = current_dir + os.sep + "nda_libraries_src"
    return len(os.listdir(nda_lib_dir)) > 1

def safe_import_nda_libraries():
    if (nda_libraries_available()):
        import nda_libraries_src.src as nda_lib
        return nda_lib
    else:
        return None

def run_if_nda_libraries_available(helper_function):
    nda_lib = safe_import_nda_libraries()
    if (nda_lib is not None):
        helper_function(nda_lib)
