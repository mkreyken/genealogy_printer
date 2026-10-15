## Genealogy Project
* This reads a set of JSON files that contain all the family relationships
* 

## structured files:
* each person can have detail or refer to an id that is unique somewhere, and although there is a risk of circular references, it allows for a merge of trees

        "id" : "A unique id, optional , but needed to reference otherwise",
        "name": "Fullname (Birth last name)",
        "mom": "Mother id",
        "dad": "Father id",
        "years": "date of brith - date of death in form DD.MM.YYYY",
        "married": "date of mariage in form DD.MM.YYYY",
        "sex": "f or m to determine "dad" or "mom",
        "spouse": "Spouse id",
        "children": [ "child 1", "child 2", "child 3"]

  * Alternate format using embedded JSON (id's and embedded can be mixed, and embedded can have embedded)
  * 
        "id" : "A unique id, optional , but needed to reference otherwise",
        "name": "Fullname (Birth last name)",
        "mom": { ... },
        "dad": { ... },
        "years": "date of brith - date of death in form DD.MM.YYYY",
        "married": "date of mariage in form DD.MM.YYYY",
        "sex": "f or m to determine "dad" or "mom",
        "spouse": { ... },
        "children": [ { ... }, { ... }, { ... }]
  
  * Any other fields are possible:
 
        "born_location": "location",
        "died_location": "location",

     