import nbformat
import pickle
import numpy as np
from nbconvert import PythonExporter


def nbconvert_python(path):
    """Use nbconvert to convert jupyter notebook to python code.
    Return the string of python code. You can then excute it with `exec()`.

    Args:
        path (str): Path of jupyter notebook

    Returns:
        str: The string of python code converted from notebook
    
    """
    with open(path) as f:
        nb = nbformat.read(f, as_version=4)
    body, _ = PythonExporter().from_notebook_node(nb)
    return body


def is_picklable(obj):
    """Check if an obj can be dumped into a pickle file.

    Args:
        obj : The Object to be judged
    
    Returns:
        bool: The result if the input can be picklable

    """
    try:
        pickle.dumps(obj)
    except Exception:
        return False
    return True


def filter_pickable(global_vars):
    """Filter the variables that are pickable

    Args:
        global_vars (array-like): The names of variables to get
    
    Returns:
        dict: Dictionary containing names of objects and their values
    
    """
    bk = {}
    for k in global_vars:
        obj = global_vars[k]
        if is_picklable(obj):
            try:
                bk.update({k: obj})
            except TypeError:
                pass
    return bk


def notebook_to_pickable_dict(path):
    """Excute jupyter notebook and then save variables defined in notebook.
    This function converts notebook to python code and then excutes the code.
    Finally it put all public variables that defined in notebook into dictionary 
    and return it.
    Parameters
    ----------
    path : str
        Path of jupyter notebook
    Returns
    -------
    bk : :dict
        Dictionary containing names of variables and variables that defined in notebook.
    """
    # Step 1: Convert notebook to script
    code = nbconvert_python(path)
    code = code.replace("get_ipython()", "# get_ipython()")

    # Step 2: Execute script and save variables in dictionary
    d= {}
    exec(code, d)
    d.pop("__builtins__")

    # Step 3: Filter for pickable variables
    bk = filter_pickable(d)
    return bk


def save_to_pkl(path, obj):
    """Save object to pickle file.
    
    Args:
        path (str): Path to save pickle file
        obj : Object to be saved
        
    """
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def basic_type_or_list(obj):
    return not np.asanyarray(obj).dtype.hasobject


def flatten_to_dict(obj):
    def _flatten(value, key):
        if isinstance(value, (list, tuple, set)):
            if basic_type_or_list(value):
                return {key: value} if key is not None else value
            else:
                tile_d = dict()
                for i, v in enumerate(value):
                    tile_d.update(_flatten(v, f"{key}_{i}"if key is not None else i))
                return tile_d
        elif isinstance(value, dict):
            tile_d = dict()
            for k, v in value.items():
                tile_d.update(_flatten(v, f"{key}_{k}" if key is not None else k))
            return tile_d
        else:
            return {key: value} if key is not None else value

    return _flatten(value = obj, key = None)


def notebook_exec_result_flattened(path):
    # Step 1: Convert notebook to script
    code = nbconvert_python(path)
    code = code.replace("get_ipython()", "# get_ipython()")

    # Step 2: Execute script and save variables in dictionary
    d= {}
    exec(code, d)
    d.pop("__builtins__")

    # Step 3: Flatten all variables
    bk = flatten_to_dict(d)

    # Step 4: Filter for variables which is basic type or list of basic type
    bk_filted = {k:v for k,v in bk.items() if basic_type_or_list(v)}
    return bk_filted


def main():
    # excute jupyter notebook and save global variables
    notebook_path = "docs\\getting_started.ipynb"

    bk = notebook_exec_result_flattened(notebook_path)

    # to save session
    save_path = "pydsge/tests/resources/getting_started_stable.npz"
    with open(save_path, "wb") as f:
        np.savez_compressed(f, **bk)


if __name__ == "__main__":
    main()
