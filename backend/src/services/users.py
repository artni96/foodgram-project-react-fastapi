from backend.src import constants
from backend.src.exceptions.base import ObjectAlreadyExistsException
from backend.src.exceptions.users import IncorrectPasswordException, UserAlreadyExistsException
from backend.src.repositories.utils.users import PasswordManager
from backend.src.schemas.users import UserListRead, FollowedUserRead, UserCreateRequest, UserCreateResponse, UserCreate, \
    UserLoginRequest, UserPasswordUpdate, UserPasswordChangeRequest, UserReadWithRole
from backend.src.services.base import BaseService


class UserService(BaseService):

    async def get_user_list(
            self,
            current_user: UserReadWithRole,
            router_prefix: str,
            page: int | None = None,
            limit: int | None = None
    ) -> UserListRead:
        if not limit:
            limit = constants.PAGINATION_LIMIT
        if page:
            offset = (page - 1) * limit
        else:
            offset = None

        if current_user:
            current_user_id = current_user.id
        else:
            current_user_id = None
        result = await self.db.users.get_all(
            user_id=current_user_id,
            limit=limit,
            offset=offset,
            page=page,
            router_prefix=router_prefix
        )
        return result

    async def get_current_user(
        self,
        current_user: UserReadWithRole,
    ) -> FollowedUserRead | None:
        current_user_info = await self.db.users.get_one_or_none(user_id=current_user.id)
        return current_user_info

    async def get_user_by_id(
            self,
            id: int,
            options
    ) -> FollowedUserRead | None:
        user_to_get = await self.db.users.get_one(
            user_id=id,
            **options
        )
        return user_to_get

    async def create_new_user(
        self,
        user_data: UserCreateRequest
    ) -> UserCreateResponse:
        hashed_password = PasswordManager().hash_password(user_data.password)
        try:
            _user_data = UserCreate(
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                hashed_password=hashed_password
            )
            new_user = await self.db.users.create(data=_user_data)
            await self.db.commit()
            return new_user
        except ObjectAlreadyExistsException:
            raise UserAlreadyExistsException


    async def login_user(
        self,
        data: UserLoginRequest,
    ):
        access_token = await self.db.users.create_access_token(data=data)
        return access_token

    async def change_password(
        self,
        password_data: UserPasswordUpdate,
        current_user: UserReadWithRole
    ) -> None:
        user = await self.db.users.get_user_hashed_password(id=current_user.id)
        if not PasswordManager().verify_password(
                hashed_password=user.hashed_password,
                plain_password=password_data.current_password
            ):
            raise IncorrectPasswordException
        new_hashed_password = PasswordManager().hash_password(
            password_data.new_password
        )
        password_updated_data = UserPasswordChangeRequest(
            hashed_password=new_hashed_password
        )
        await self.db.users.update(
            id=current_user.id,
            data=password_updated_data,
            exclude_unset=True
        )
        await self.db.commit()
