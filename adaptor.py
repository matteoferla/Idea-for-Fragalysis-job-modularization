# ----------- Code to bridge the inputs and outputs and errors ---
from rdkit import Chem
from typing import Dict, List, Tuple

# uses both worlds:
from find_neighbors import get_close_names
from interface_factory import UserError, IneffectiveSettingsError, JSAction

def main(target_name: str, sdf_block: str, distance_threshold: float = 3.) -> Tuple[List[str], JSAction]:
    """
    An adaptor to the interface input/output and the independent get_close_names
    """
    # ## input munging
    # The find_neighbors script has a read_file but not a read_block
    sdfh = Chem.SDMolSupplier()
    sdfh.SetData(sdf_block)
    hitdex: Dict[str, Chem.Mol] = {hit.GetProp('_Name'): hit for hit in sdfh}
    if target_name not in hitdex:
        raise UserError(f'No such {target_name} target_name')
    # ## main call
    close_neighbors: List[str] = get_close_names(target_name, hitdex, distance_threshold)
    # ## output munging
    if len(close_neighbors) == 0:
        raise IneffectiveSettingsError(f'Threshold too strict: no neighbours')
    return close_neighbors, JSAction.show_LHS_hits
