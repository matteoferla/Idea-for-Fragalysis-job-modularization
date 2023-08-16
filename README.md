# Idea for Fragalysis job modularization
A barebone hypothetical example for Fragalysis jobs
for discussion purposes of how a modularised job could look like to avoid continual reinvention and training.

Say I have a simple snippet of code that is independent of the specific details of API dialogue,
in this case [find_neighbors.py](find_neighbors.py) which finds the neighbours of a given molecule.
For example:

```python
from find_neighbors import get_close_names, read_file
from typing import Dict, List
from rdkit import Chem

sdf_filename = 'NCS1.corrected.sdf'
target_name = 'x0115_0A'
distance_threshold = 6.

# Get the neighbours of a molecule
hits: Dict[str, Chem.Mol] = read_file('hits.sdf')
neighbor_names: List[str] = get_close_names(target_name, hits, distance_threshold)
```

To hypothetically deploy it I would need to have it with a clean installation, eg. DockerFile, sure, but also
**I would need standardised input and output, which is the key point of this discussion exercise**.

To this end two things are needed, a generic interface factory that does stuff with standardised inputs and outputs,
which as a content creator would not change, for example [interface_factory.py](interface_factory.py):

```python
from interface_factory import FauxInterfaceFactory, OutputType
from interface_factory import  UserError, IneffectiveSettingsError, InternalError
# FauxInterfaceFactory is just a mockup of what the real deal would do.

# Create the interface
myapp = FauxInterfaceFactory(wrapped_function)
output: OutputType = myapp(inputs)
```

As a content creator I would make an adaptor for my code to this hypothetical interface factory, 
eg. [adaptor.py](adaptor.py), which uses things like standarised errors as discussed,
here is its example code, to do input and output munging.

```python
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
```

The output has to be standardised to a preset group of actions.
Here these are:

```python
from typing import Any, TypedDict

class OutputType(TypedDict):
    """
    A standarized output
    """
    status: str  # 'error' or 'success'
    results: Any  # jsonable
    action: str  # a JS action name (from JSAction enum)
```

Here JSAction is an enum of possible actions that the front end can take, for example:

```python
import enum

class JSAction(enum.Enum):
    show_toast = 0   # show a toast message, good for errors
    show_LHS_hits = 1  # show the hits from the LHS
    add_RHS_hits = 2  # add to RHS tab
    show_modal = 3  # show a modal, example with a table or plotly as defined in HTML passed.
    other_JS = 4  # do some other JS task
```
These would need to be recognised by the front end and say how to process results.
This is all a hypothetical.
The front end would have something like this:

```javascript
jobPromise.then(response => FauxJSInterface[response.action](response.results))
```
Where `FauxJSInterface` is a hypothetical front end class with easy methods.

```javascript
class FauxJSInterface {
    show_toast(message) {
        // show a toast message, good for errors
    }
    show_LHS_hits(names) {
        // show the hits from the LHS
    }
    add_RHS_hits(sdf_block) {
        // add to RHS tab
    }
    show_modal(html) {
        // show a modal, example with a table or plotly as defined in HTML passed.
    }
    other_JS(js_snippet) {
        // do some other JS task
    }
}
```

An alternative could be writing full JS code in the action, but that is painful.
like `FauxJSInterface.showRHSHits(names)` would be something wildly complicated like:

```javascript
const showRHSHit = (name) => {const idx; nameArray.indexOf(name);
                              component.addRepresentation('ball+stick', {sele: `:LIG and :${idx}`});
                              etc.
                              }
response.results.forEach(name => showRHSHit(name);
```

Using the three parts together (the interface factory, the adapter, and the independent code):

```python
from adaptor import main
from interface_factory import FauxInterfaceFactory

interface = FauxInterfaceFactory(main)
interface(request_params)
```
Say `request_params` is `{'target_name': 'x0071_0B', 'sdf_block': '...', 'distance_threshold': 1.}`
I would get `{'status': 'success', 'results': ['x0071_0B', 'x0086_0A', ...],
              'action': 'show_LHS_hits'}`

In terms of front end field population, I believe it is sorted
and already present as a yaml file, which is perfect.
So this is not needed in the discussion,
but here is a crappy way of doing it because it is a related topic.

```python
from adaptor import main
from interface_factory import FauxInterfaceFactory

interface = FauxInterfaceFactory(main)
interface.front_end_fields
```
Which gives:
```json
{'target_name': 'input type="text" name="target_name"',
 'sdf_block': 'input type="text" name="sdf_block"',
 'distance_threshold': 'input type="number" name="distance_threshold"'}
```








