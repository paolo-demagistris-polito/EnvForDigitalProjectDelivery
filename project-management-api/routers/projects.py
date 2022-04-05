from fastapi import APIRouter

import routers.documents
from datatypes.models import *
from dependencies import *

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[]
)

router.include_router(routers.documents.router, prefix="/{project_name}")


@router.get("/",
            response_model=List[str],
            dependencies=[])
def get_projects(session: Session = Depends(get_session),
                 user: User = Depends(get_current_active_user)):

    return [project.project_name for project in crud.get_projects(session)
            if has_project_permission(session, user, project, Permissions.view)]


@router.post("/",
             response_model=ProjectReturn,
             dependencies=[Depends(require_project_permission(Permissions.create))])
async def create_project(user        : User    = Depends(get_current_active_user),
                         request_body: Dict    = Depends(get_request_body),
                         session     : Session = Depends(get_session)):

    project_name = list(request_body.keys())[0]
    project_body = request_body[project_name]

    if crud.get_project_by_name(session, project_name) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Project already exists")

    project = Project(project_name=project_name, owner_name=user.user_name)
    session.add(project)

    if project_body is not None:
        if project_body['documents'] is not None:
            document_list = [Document(project_name=project_name,
                                      document_name=doc,
                                      author_name=user.user_name,
                                      jsonschema=body)
                             for doc, body in project_body['documents'].items()]
            session.add_all(document_list)

            process_list = []

            def append_process(proc_name, doc_name, doc_role):
                process.documents_processes.append(
                    DocumentProcess(project_name =project_name,
                                    document_name=doc_name,
                                    process_name =proc_name,
                                    document_role=doc_role))

            document_names = map(lambda d: d.document_name, document_list)

            for process_name, process_body in project_body['processes'].items():
                process = Process(project_name=project_name, process_name=process_name)
                if process_body['inputs'] is not None:
                    for document_name in process_body['inputs']:
                        if document_name in document_names:
                            append_process(process_name, document_name, DocumentRole.input)
                if process_body['outputs'] is not None:
                    for document_name in process_body['outputs']:
                        if document_name in document_names:
                            append_process(process_name, document_name, DocumentRole.output)
                process_list.append(process)
            session.add_all(process_list)

            permission_list = []
            for user_name, user_permissions_body in project_body['permissions'].items():
                if crud.get_user(session, user_name) is not None:
                    for document_name, perms in user_permissions_body['documents'].items():
                        for permission_name in perms:
                            if (any(x for x in document_list if x.document_name == document_name)
                                    and any(x for x in DocPermissions if x.name == permission_name)):
                                permission_list.append(
                                    DocumentPermission(project_name =project_name,
                                                       user_name    =user_name,
                                                       document_name=document_name,
                                                       permission   =permission_name))
            session.add_all(permission_list)

    session.commit()

    db_project = crud.get_project_by_name(session, project_name)
    if db_project is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    return db_project


@router.get("/{project_name}",
            response_model=ProjectReturn,
            dependencies=[Depends(get_current_active_user),
                          Depends(require_project_permission(Permissions.view))])
def get_project_by_name(session   : Session = Depends(get_session),
                        user      : User    = Depends(get_current_active_user),
                        db_project: Project = Depends(get_project)):

    ret_proj = ProjectReturn(project_name=db_project.project_name, owner_name=db_project.owner_name)
    ret_proj.documents = [document for document in db_project.documents
                          if has_document_permission(session,
                                                     user,
                                                     db_project,
                                                     document,
                                                     Permissions.view)]
    return ret_proj


@router.delete("/{project_name}",
               status_code=status.HTTP_200_OK,
               dependencies=[Depends(get_current_active_user),
                             Depends(require_project_permission(Permissions.delete))])
def delete_project_by_name(session   : Session = Depends(get_session),
                           db_project: Project = Depends(get_project)):

    session.delete(db_project)
    session.commit()


@router.post("/{project_name}/permissions/",
             dependencies=[Depends(require_project_permission(Permissions.edit_permissions))])
def add_project_permissions(
        proj_permissions: ProjectPermissionsInput,
        session: Session = Depends(get_session),
        db_project: Project = Depends(get_project)):

    for perm in proj_permissions.permissions:
        if crud.get_project_permission(session     =session,
                                       user_name   =proj_permissions.user_name,
                                       project_name=db_project.project_name,
                                       permission  =perm) is None:
            session.add(ProjectPermission(user_name=proj_permissions.user_name,
                                          project_name=db_project.project_name,
                                          permission=perm))
    session.commit()

    perm_list = list(map(lambda item: item.permission,
                         crud.get_project_permissions(session,
                                                      proj_permissions.user_name,
                                                      db_project.project_name)))
    return DocumentPermissionsInput(user_name=proj_permissions.user_name, permissions=perm_list)


@router.delete("/{project_name}/permissions/",
               dependencies=[Depends(require_project_permission(Permissions.edit_permissions))])
def delete_project_permissions(
        proj_permissions: ProjectPermissionsInput,
        session: Session = Depends(get_session),
        db_project: Project = Depends(get_project)):

    for perm in proj_permissions.permissions:
        p = crud.get_project_permission(session     =session,
                                        user_name   =proj_permissions.user_name,
                                        project_name=db_project.project_name,
                                        permission  =perm)
        if p is not None:
            session.delete(p)
    session.commit()

    perm_list = list(map(lambda item: item.permission,
                         crud.get_project_permissions(session,
                                                      proj_permissions.user_name,
                                                      db_project.project_name)))
    return DocumentPermissionsInput(user_name=proj_permissions.user_name, permissions=perm_list)


@router.get("/{project_name}/permissions/{user_name}",
            dependencies=[Depends(require_project_permission(Permissions.edit_permissions))])
def get_project_permissions(
        user_name: str,
        session: Session = Depends(get_session),
        db_project: Project = Depends(get_project)):

    perm_list = list(map(lambda item: item.permission,
                         crud.get_project_permissions(session,
                                                      user_name,
                                                      db_project.project_name)))
    return DocumentPermissionsInput(user_name=user_name, permissions=perm_list)
