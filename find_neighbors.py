from rdkit import Chem
from typing import Dict, List
import numpy as np
import numpy.typing as npt

def get_close_names(target_name: str, hitdex: Dict[str, Chem.Mol], distance_threshold: float = 3.) -> List[str]:
    """
    Give a mol named in ``target_name`` and
    a dict of names to Chem.Mol get all names under ``distance_threshold`` Å
    """
    distances: Dict[str, float] = get_distances(target_name, hitdex)
    close_neighbor_distances: Dict[str, float] = {name: distance for name, distance in distances.items() if
                                                  distance <= distance_threshold}
    return list(close_neighbor_distances.keys())

def read_file(sdf_filename) -> Dict[str, Chem.Mol]:
    """
    This function is not used by the final code, but exists because it is part of the code,
    which may have had other roles say.
    Ie. stuff in this file aren't specific to the application.
    """
    with Chem.SDMolSupplier(sdf_filename) as sdfh:
        return {hit.GetProp('_Name'): hit for hit in sdfh}

def get_distances(target_name: str, hitdex: Dict[str, Chem.Mol]) -> Dict[str, float]:
    target: Chem.Mol = hitdex[target_name]
    firt_other_idx: int = target.GetNumAtoms()
    distancedex: Dict[str, npt.NDArray[np.float64]] = {name: Chem.Get3DDistanceMatrix(Chem.CombineMols(target, hit)) for
                                                       name, hit in hitdex.items()}
    # blank self reflections
    for dm in distancedex.values():
        dm[slice(0, firt_other_idx), slice(0, firt_other_idx)] = np.nan
        dm[slice(firt_other_idx, None), slice(firt_other_idx, None)] = np.nan
    distances: Dict[str, float] = {name: float(np.nanmin(dm)) for name, dm in distancedex.items()}
    return distances