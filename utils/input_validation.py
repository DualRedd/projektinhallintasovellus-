import re
from services.auth_service import user_exists, authenticate_user
from services.groups_service import get_group_role, get_group_invite
from .permissions import check_csrf_token
from enums.RoleEnum import RoleEnum
from config import config

class ValidationResult:
    def __init__(self, valid : bool, error : str = ""):
        self.valid = valid
        self.error = error

def validate_create_user_form(username : str, password : str, password_check : str) -> ValidationResult:
    if not (res := validate_string_size(username, "username", "Username")).valid:
        return res
    if username[0].isspace() or username[-1].isspace():
        return ValidationResult(False, f"Username cannot start or end with a space!")
    if not check_string_chars(username, "a-zA-Z0-9_\-äöå "):
        return ValidationResult(False, f"Username can only contain characters a-zA-Z0-9_-äöå and spaces!")
    if user_exists(username):
        return ValidationResult(False, "Username has already been taken!")
    if not (res := validate_string_size(password, "password", "Password")).valid:
        return res
    if password != password_check:
        return ValidationResult(False, "Passwords do not match!")
    return ValidationResult(True)

def validate_login_form(username : str, password : str) -> ValidationResult:
    if not authenticate_user(username, password):
        return ValidationResult(False, "Username or password is incorrect!")
    return ValidationResult(True)

def validate_group_details_form(group_name : str, group_desc : str) -> ValidationResult:
    if not check_csrf_token():
        return ValidationResult(False, "Invalid csrf token!")
    if not (res := validate_string_size(group_name, "group_name", "Group name")).valid:
        return res
    if not (res := validate_string_size(group_desc, "group_description", "Group description")).valid:
        return res
    return ValidationResult(True)

def validate_group_invite_form(group_id : int, invitee, role_value_str : int) -> ValidationResult:
    if not check_csrf_token():
        return ValidationResult(False, "Invalid csrf token!")
    if not invitee:
        return ValidationResult(False, "No such user found!")
    if get_group_role(group_id, invitee.username):
        return ValidationResult(False, "The user is already a member of the group!")
    if get_group_invite(group_id, invitee.id):
        return ValidationResult(False, "The user has already been invited!")
    # Check if role input is valid
    try:
        role_value = int(role_value_str)
    except ValueError:
        return ValidationResult(False, "Invalid role!")
    if not RoleEnum.has_value(role_value) or RoleEnum(role_value) == RoleEnum.Owner:
        return ValidationResult(False, "Invalid role!")
    return ValidationResult(True)

def validate_empty_form():
    if not check_csrf_token():
        return ValidationResult(False, "Invalid csrf token!")
    return ValidationResult(True)

# Helper functions
def check_string_chars(string : str, allowed : str) -> bool:
    return bool(re.match(f"^[{allowed}]*$", string))

def validate_string_size(string : str, string_type : str, error_string : str) -> ValidationResult:
    if len(string) < config["MIN_INPUT_SIZES"][string_type]:
        return ValidationResult(False, f"{error_string} cannot be shorter than {config['MIN_INPUT_SIZES'][string_type]} characters!")
    if len(string) > config["MAX_INPUT_SIZES"][string_type]:
        return ValidationResult(False, f"{error_string} cannot be longer than {config['MAX_INPUT_SIZES'][string_type]} characters!")
    return ValidationResult(True)