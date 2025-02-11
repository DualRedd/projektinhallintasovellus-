from sqlalchemy.sql import text
from app import db
from services.auth_service import get_user
from utils.tools import query_res_to_dict
from enums.enums import role_enum

def get_groups(user_id : str, is_invitee : bool) -> list[dict]:
    result = db.session.execute(text("SELECT G.id, G.name, G.description, GR.role \
                                        FROM group_roles GR \
                                        JOIN users U ON U.id = GR.user_id AND U.visible = TRUE \
                                        JOIN groups G ON G.id = GR.group_id AND G.visible = TRUE \
                                        WHERE GR.user_id = :user_id AND GR.is_invitee = :is_invitee \
                                        ORDER BY G.id"), {"user_id":user_id, "is_invitee":is_invitee}).fetchall()
    result = query_res_to_dict(result)
    for group in result: group["role"] = role_enum.get_by_value(int(group["role"]))
    return result

def get_group_members(group_id : int, is_invitee : bool = None) -> list[dict]:
    result = db.session.execute(text(f"SELECT U.id, U.username, GR.role, GR.is_invitee \
                                        FROM group_roles GR \
                                        JOIN users U ON U.id = GR.user_id AND U.visible = TRUE \
                                        JOIN groups G ON G.id = GR.group_id AND G.visible = TRUE \
                                        WHERE GR.group_id = :group_id \
                                        {'AND GR.is_invitee = :is_invitee' if is_invitee is not None else ''} \
                                        ORDER BY U.id"),    
                                        {"group_id":group_id, "is_invitee":is_invitee}).fetchall()
    result = query_res_to_dict(result)
    for member in result: member["role"] = role_enum.get_by_value(int(member["role"]))
    return result

def get_group_details(group_id : int):
    result = db.session.execute(text("SELECT id, name, description FROM groups \
                                    WHERE id = :group_id AND visible = TRUE \
                                    "), {"group_id":group_id}).fetchone()
    return result

def get_group_role(group_id : int, user_id : int, is_invitee : bool = None) -> role_enum | None:
    result = db.session.execute(text(f"SELECT GR.role FROM group_roles GR \
                                    JOIN users U ON U.id = GR.user_id AND U.visible = TRUE \
                                    JOIN groups G ON G.id = GR.group_id AND G.visible = TRUE \
                                    WHERE GR.group_id = :group_id AND U.id = :user_id \
                                    {'AND GR.is_invitee = :is_invitee' if is_invitee is not None else ''}"),
                                    {"group_id":group_id, "user_id":user_id, "is_invitee":is_invitee}).fetchone()
    return role_enum.get_by_value(int(result[0])) if result else None

def create_group(group_name : str, group_desc : str = "") -> int:
    group_id = db.session.execute(text("INSERT INTO groups (name, description) VALUES (:group_name, :group_desc) RETURNING id"),
                                        {"group_name":group_name, "group_desc":group_desc}).fetchone()[0]
    db.session.commit()
    return group_id

def update_group(group_id : int, group_name : str, group_desc : str = ""):
    db.session.execute(text("UPDATE groups SET name = :group_name, description = :group_desc WHERE id = :group_id"),
                            {"group_name":group_name, "group_desc":group_desc, "group_id":group_id})
    db.session.commit()

def delete_group(group_id : int):
    db.session.execute(text("UPDATE groups SET visible = FALSE WHERE id = :group_id"),
                            {"group_id":group_id})
    db.session.commit()

def create_group_role(group_id : int, user_id : int, role : role_enum, is_invitee : bool):
    db.session.execute(text("INSERT INTO group_roles (group_id, user_id, role, is_invitee) VALUES (:group_id, :user_id, :role, :is_invitee)"),
                            {"group_id":group_id, "user_id":user_id, "role":role.value, "is_invitee":is_invitee})
    db.session.commit()

def update_group_role(group_id : int, user_id : int, role : role_enum, is_invitee : bool = None):
    db.session.execute(text(f"UPDATE group_roles SET role = :role{', is_invitee = :is_invitee' if is_invitee is not None else ''} WHERE group_id = :group_id AND user_id = :user_id"),
                            {"group_id":group_id, "user_id":user_id, "role":role.value, "is_invitee":is_invitee})
    db.session.commit()

def delete_group_role(group_id : int, user_id : int):
    db.session.execute(text("DELETE FROM group_roles WHERE group_id = :group_id AND user_id = :user_id"),
                            {"group_id":group_id, "user_id":user_id})
    db.session.commit()
