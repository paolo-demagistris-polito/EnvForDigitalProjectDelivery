# Project Management API

Every endpoint and specification is not final, it may change until the development is complete.
For more details about endpoints run FastApi then read the docs at 127.0.0.1:8000/docs

## API Endpoints

| Method          | Endpoint                                                                               | Description                                                | Requires Auth | Requires Perms |
|-----------------|----------------------------------------------------------------------------------------|------------------------------------------------------------|---------------|----------------|
| **POST**        | /register                                                                              | Register User                                              | False         | False          |
| **GET**         | /token                                                                                 | Get Bearer Token                                           | False         | False          |
| **GET**         | /me                                                                                    | Get current authenticated User                             | True          | False          |
| **Projects**    |                                                                                        |                                                            |               |                |
| **GET**         | /projects                                                                              | Get all projects visible to the current authenticated user | True          | True           |
| **POST**        | /projects                                                                              | Create a project (see **[Schemas](#Schemas)** sections)    | True          | True           |
| **GET**         | /projects/**{project_name}**                                                           | Get project by name                                        | True          | True           |
| **DELETE**      | /projects/**{project_name}**                                                           | Delete project by name                                     | True          | True           |
| **POST**        | /projects/**{project_name}**/permissions                                               | Add project permissions                                    | True          | True           |
| **DELETE**      | /projects/**{project_name}**/permissions                                               | Delete project permissions                                 | True          | True           |
| **GET**         | /projects/**{project_name}**/permissions/**{user_name}**                               | Get project permissions for user                           | True          | True           |
| **Documents**   |                                                                                        |                                                            |               |                |
| **POST**        | /projects/**{project_name}**/documents                                                 | Add document schema to project                             | True          | True           |
| **GET**         | /projects/**{project_name}**/documents/**{document_name}**                             | Get document of project                                    | True          | True           |
| **PUT**         | /projects/**{project_name}**/documents/**{document_name}**                             | Insert document content                                    | True          | True           |
| **PATCH**       | /projects/**{project_name}**/documents/**{document_name}**                             | Patch document content                                     | True          | True           |
| **DELETE**      | /projects/**{project_name}**/documents/**{document_name}**                             | Delete document                                            | True          | True           |
| **GET**         | /projects/**{project_name}**/documents/**{document_name}**/**{field}**/**{path}**      | Get document field, specifying the path                    | True          | True           |
| **POST**        | /projects/**{project_name}**/documents/**{document_name}**/last/**{path}**             | Create document content at specifyied path                 | True          | True           |
| **PUT**         | /projects/**{project_name}**/documents/**{document_name}**/last/**{path}**             | Edit document content at specifyied path                   | True          | True           |
| **PATCH**       | /projects/**{project_name}**/documents/**{document_name}**/last/**{path}**             | Patch document content at specifyied path                  | True          | True           |
| **DELETE**      | /projects/**{project_name}**/documents/**{document_name}**/last/**{path}**             | Delete document content at specifyied path                 | True          | True           |
| **POST**        | /projects/**{project_name}**/documents/**{document_name}**/permissions                 | Add document permissions                                   | True          | True           |
| **DELETE**      | /projects/**{project_name}**/documents/**{document_name}**/permissions                 | Delete document permissions                                | True          | True           |
| **GET**         | /projects/**{project_name}**/documents/**{document_name}**/permissions/**{user_name}** | Get document permissions for user                          | True          | True           |
| **MS Projects** |                                                                                        |                                                            |               |                |
| **POST**        | /projects/**{project_name}**/msprojects/                                               | Add ms project file to project                             | True          | True           |
| **GET**         | /projects/**{project_name}**/msprojects/**{ms_project_name}**                          | Get ms project file of project                             | True          | True           |
| **DELETE**      | /projects/**{project_name}**/msprojects/**{ms_project_name}**                          | Delete ms project file of project                          | True          | True           |

## Schemas

### Project POST schema (accepts both YAML/JSON)
YAML example
```yaml
# Project name
project_name: example_project
documents:
  project_charter:
    # jsonschema of the document
    jsonschema:
      properties:
        overview: { type: string }
        impact: { type: string }
        organization: { type: string }
      additionalProperties: false
    computed_fields:
      # computed fields of the document
      scope:
        reference_document: work_breakdown_structure
        jsonpath: $.elements[?(@.level == 1)].name
    ms_computed_fields:
      # ms project computed fields of the document
      scope:
        ms_project_name: example
        field_from: tasks
        jsonpath: $[?(@.level == 1)].name
  work_breakdown_structure:
    jsonschema:
      properties:
        elements:
          type: array
          items:
            properties:
              level: { type: integer }
              code: { type: string }
              name: { type: string }
              description: { type: string }
            additionalProperties: false
        additionalProperties: false
processes:
  # process name
  develop_project_charter:
    inputs:
    outputs: [ project_charter ]
  develop_work_breakdown_structure:
    inputs: [ project_charter ]
    outputs: [ work_breakdown_structure ]
permissions:
  # user name
  doge:
    documents:
      project_charter: [ view, edit, delete ]
      work_breakdown_structure: [ view, edit, delete ]
```

### Document POST schema (accepts both YAML/JSON)

Documents use the [jsonschema](https://json-schema.org/) format in order to validate the insertion of content.
Computed fields are defined as a list of fields that are computed from other documents, using the [jsonpath](https://github.com/json-path/JsonPath) syntax.

**YAML example**
```yaml
project_charter:
  # jsonschema of the document
  jsonschema:
    properties:
      overview: { type: string }
      impact: { type: string }
      organization: { type: string }
    additionalProperties: false
  computed_fields:
    scope:
      reference_document: work_breakdown_structure
      jsonpath: $.elements[?(@.level == 1)].name
  ms_computed_fields:
        # ms project computed fields of the document
        scope:
          ms_project_name: example
          field_from: tasks
          jsonpath: $[?(@.level < 3)].name
```

### Document PUT schema (accepts both YAML/JSON)
**JSON example**
```json
{
  "overview": "Academic research for implementing an environment for digital delivery of projects",
  "impact": "Creation of the environment...",
  "organization": "PoliTo Project Management Lab"
}
```

### Documents returned

Documents use a patch system to track changes. Patches follow the [jsonpatch](http://jsonpatch.com/ "jsonpatch") specification.
Documents are returned in JSON.

```json
{
    "project_name": "example_project",
    "document_name": "project_charter",
    "author_name": "doge",
    "jsonschema": {
        "properties": {
            "overview": {
                "type": "string"
            },
            "impact": {
                "type": "string"
            },
            "organization": {
                "type": "string"
            }
        },
        "additionalProperties": false
    },
    "first": {
        "overview": "Academic research for implementing an environment for digital delivery of projects",
        "impact": "Creation of the environment...",
        "organization": "PoliTo"
    },
    "last": {
        "overview": "Academic research for implementing an environment for digital delivery of projects",
        "impact": "Creation of the environment...",
        "organization": "PoliTo Project Management Lab"
    },
    "creation_date": "2022-04-11T16:05:06.575202",
    "patches": [
        {
            "id": 1,
            "user_name": "doge",
            "updated_date": "2022-04-11T16:05:57.498469",
            "patch": [
                {
                    "op": "replace",
                    "path": "/organization",
                    "value": "PoliTo Project Management Lab"
                }
            ]
        }
    ],
    "computed_fields": {
          "scope": [
              "Task 1",
              "Task 2"
          ]
    },
    "ms_computed_fields": {
          "scope": [
              "2018-PMTermProject_BID_baseline",
              "New production line",
              "M1 - Effective Date",
              "C1 - Start of Activities",
              "Design",
              "C2 - Design completed",
              "Purcahse",
              "Manifacturing",
              "Transportation",
              "Erection phase",
              "Testing",
              "M2 - Owner’s Taking Over",
              "Civil Works",
              "O1 - Permits completed",
              "O2 - Civil works substantial completion"
          ]
    }
}
```
